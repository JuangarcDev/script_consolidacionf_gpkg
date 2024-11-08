import geopandas as gpd
import fiona
import os
import shutil
import pandas as pd
import sqlite3

# Definir EPSG de destino
TARGET_CRS = "EPSG:9377"

# Archivo de registro de salida
log_file = r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_combinado\log_union_proceso.txt"

# Función para registrar mensajes en el archivo de log
def log_message(message):
    with open(log_file, "a") as log:
        log.write(message + "\n")
    print(message)

# Inicializar el archivo de log
with open(log_file, "w") as log:
    log.write("Registro de ejecución del script de unión de GPKG\n\n")

# Lista de archivos .gpkg a combinar
gpkg_files = [
    r"C:\ACC\CONSOLIDACION_MANZANAS\MZ16_FINAL_Correcto_1\MN_00000016_20240923\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\MN_00000009_20240923_2\MN_00000009_20240923-vf\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\MN_00000003_20241009_FINAL_3\MN_00000003_20241009_FINAL\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\MANZANA 8_4\MANZANA 8\MN_00000008_20240923\MN_00000008_20240923\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\00000017-01_5\captura_campo_20240920.gpkg"
]

# Archivo de salida y carpeta DCIM
output_file = r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_combinado\captura_campo_20240920.gpkg"
output_dcim_folder = os.path.join(os.path.dirname(output_file), "DCIM")
os.makedirs(output_dcim_folder, exist_ok=True)
shutil.copy(gpkg_files[0], output_file)

# Diccionario para almacenar capas temporales de registros únicos
combined_layers = {}

# Función para transformar CRS
def ensure_target_crs(gdf, layer_name):
    if gdf is not None and not gdf.empty:
        if gdf.crs is None:
            gdf.set_crs(TARGET_CRS, inplace=True)
            log_message(f"CRS indefinido en '{layer_name}'. Se estableció a {TARGET_CRS}.")
        elif gdf.crs != TARGET_CRS:
            gdf = gdf.to_crs(TARGET_CRS)
            log_message(f"Transformando CRS de '{layer_name}' a {TARGET_CRS}.")
    return gdf

# Función para insertar registros en SQLite con transformación de tipos de datos
def insert_into_sqlite(layer, layer_name, gpkg_path):
    try:
        conn = sqlite3.connect(gpkg_path)
        
        # Crear tabla intermedia para transformar tipos de datos a formatos compatibles
        temp_table = f"{layer_name}_temp"
        rows = [dict(record['properties']) for record in layer]
        df = pd.DataFrame(rows)
        
        # Convertir tipos de columnas para evitar errores con tipos VARCHAR y NUMERIC
        for column in df.columns:
            if df[column].dtype == 'object':  # Si es texto
                df[column] = df[column].astype(str)  # Convertir a texto
            elif pd.api.types.is_numeric_dtype(df[column]):
                df[column] = pd.to_numeric(df[column], errors='coerce')  # Convertir a float
        
        # Crear tabla temporal con tipos compatibles
        df.to_sql(temp_table, conn, if_exists='replace', index=False)
        
        # Insertar en la tabla final
        restored_df = pd.read_sql_query(f"SELECT * FROM {temp_table}", conn)
        restored_df.to_sql(layer_name, conn, if_exists='append', index=False)

        conn.close()
        log_message(f"Registros de '{layer_name}' insertados en la base de datos.")
    except Exception as e:
        log_message(f"Error al insertar en '{layer_name}': {e}")

# Procesar cada archivo .gpkg
for gpkg in gpkg_files[1:]:
    if not os.path.exists(gpkg):
        log_message(f"El archivo '{gpkg}' no existe. Se omitirá.")
        continue

    # Copiar archivos DCIM
    dcim_folder = os.path.join(os.path.dirname(gpkg), "DCIM")
    if os.path.exists(dcim_folder) and os.path.isdir(dcim_folder):
        for root, _, files in os.walk(dcim_folder):
            for file in files:
                source_file = os.path.join(root, file)
                destination_file = os.path.join(output_dcim_folder, file)
                if os.path.exists(destination_file):
                    base, ext = os.path.splitext(file)
                    counter = 1
                    while os.path.exists(destination_file):
                        destination_file = os.path.join(output_dcim_folder, f"{base}_{counter}{ext}")
                        counter += 1
                shutil.copy2(source_file, destination_file)
                log_message(f"Archivo '{file}' copiado a la carpeta DCIM combinada.")

    try:
        # Listar las capas
        layers = fiona.listlayers(gpkg)
        log_message(f"Procesando '{gpkg}' con las capas: {layers}")

        for layer_name in layers:
            try:
                with fiona.open(gpkg, layer=layer_name) as layer:
                    geom_type = layer.schema['geometry']
                    has_geometry = geom_type is not None
                    log_message(f"Cargando '{layer_name}' con geometría '{geom_type}'")

                    if has_geometry:
                        # Procesar capas con geometría
                        gdf = gpd.read_file(gpkg, layer=layer_name)
                        gdf = ensure_target_crs(gdf, layer_name)

                        # Almacenar o combinar en diccionario temporal
                        if layer_name in combined_layers:
                            combined_layers[layer_name] = pd.concat([combined_layers[layer_name], gdf], ignore_index=True).drop_duplicates()
                        else:
                            combined_layers[layer_name] = gdf

                    else:
                        # Procesar capas sin geometría con fiona
                        insert_into_sqlite(layer, layer_name, output_file)

            except Exception as e:
                log_message(f"Error al procesar la capa '{layer_name}': {e}")

    except Exception as e:
        log_message(f"Error al procesar el archivo '{gpkg}': {e}")

# Guardar las capas combinadas de vuelta en el GeoPackage de salida
for layer_name, gdf in combined_layers.items():
    if gdf.empty:
        log_message(f"La capa '{layer_name}' está vacía y no se guardará.")
        continue
    gdf.to_file(output_file, layer=layer_name, driver="GPKG")

log_message("Proceso completado.")