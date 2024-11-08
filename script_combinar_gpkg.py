import geopandas as gpd
import fiona
import os
import shutil
import warnings
import pandas as pd

# Definir EPSG de destino
TARGET_CRS = "EPSG:9377"

# Archivo de registro de salida
log_file = r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_combinado\log_union_proceso.txt"

# Función para registrar mensajes en el archivo de log
def log_message(message):
    with open(log_file, "a") as log:
        log.write(message + "\n")
    print(message)  # También imprime el mensaje en la consola

# Inicializar el archivo de log (limpiar contenido anterior)
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

# Crear carpeta DCIM de salida si no existe
os.makedirs(output_dcim_folder, exist_ok=True)

# Copiar el archivo base al archivo de salida y comenzar desde este
shutil.copy(gpkg_files[0], output_file)

# Diccionario para almacenar capas temporales de registros únicos
combined_layers = {}

# Función para verificar si dos registros son idénticos
def are_identical(record1, record2):
    return record1 == record2

# Función para transformar CRS
def ensure_target_crs(gdf, layer_name):
    if gdf.crs is None:
        gdf.set_crs(TARGET_CRS, inplace=True)
        log_message(f"CRS indefinido en '{layer_name}'. Se estableció a {TARGET_CRS}.")
    elif gdf.crs != TARGET_CRS:
        gdf = gdf.to_crs(TARGET_CRS)
        log_message(f"Transformando CRS de '{layer_name}' a {TARGET_CRS}.")
    return gdf

# Procesar cada archivo .gpkg (omitimos el primero porque ya es la base)
for gpkg in gpkg_files[1:]:
    if not os.path.exists(gpkg):
        log_message(f"El archivo '{gpkg}' no existe. Se omitirá.")
        continue

    # Copiar archivos DCIM asociados al .gpkg actual
    dcim_folder = os.path.join(os.path.dirname(gpkg), "DCIM")
    if os.path.exists(dcim_folder) and os.path.isdir(dcim_folder):
        for root, dirs, files in os.walk(dcim_folder):
            for file in files:
                source_file = os.path.join(root, file)
                destination_file = os.path.join(output_dcim_folder, file)
                # Evitar duplicados en la carpeta DCIM
                if os.path.exists(destination_file):
                    base, ext = os.path.splitext(file)
                    counter = 1
                    while os.path.exists(destination_file):
                        destination_file = os.path.join(output_dcim_folder, f"{base}_{counter}{ext}")
                        counter += 1
                shutil.copy2(source_file, destination_file)
                log_message(f"Archivo '{file}' copiado a la carpeta DCIM combinada.")

    try:
        # Listar las capas usando fiona
        layers = fiona.listlayers(gpkg)
        log_message(f"Procesando '{gpkg}' con las capas: {layers}")

        for layer_name in layers:
            try:
                with fiona.open(gpkg, layer=layer_name) as layer:
                    geom_type = layer.schema['geometry']
                    schema = layer.schema
                    log_message(f"Cargando '{layer_name}' con geometría '{geom_type}'")

                    # Procesar capas sin geometría como tablas con pandas
                    if geom_type is None:
                        df = pd.DataFrame([record['properties'] for record in layer])
                        if layer_name in combined_layers:
                            combined_layers[layer_name] = pd.concat(
                                [combined_layers[layer_name], df], ignore_index=True
                            ).drop_duplicates()
                        else:
                            combined_layers[layer_name] = df
                        log_message(f"Capas de tabla '{layer_name}' procesada y unida.")
                    else:
                        # Procesar capas con geometría
                        gdf = gpd.read_file(gpkg, layer=layer_name)
                        gdf = ensure_target_crs(gdf, layer_name)
                        
                        if layer_name in combined_layers:
                            gdf_existing = combined_layers[layer_name]
                            gdf_combined = pd.concat(
                                [gdf_existing, gdf], ignore_index=True
                            ).drop_duplicates()
                            combined_layers[layer_name] = gdf_combined
                            log_message(f"Registros únicos añadidos a la capa '{layer_name}'.")
                        else:
                            combined_layers[layer_name] = gdf
                            log_message(f"Añadiendo nueva capa '{layer_name}' de '{gpkg}'.")

            except Exception as e:
                log_message(f"Error al leer la capa '{layer_name}' en '{gpkg}': {e}")

    except Exception as e:
        log_message(f"Error al abrir '{gpkg}': {e}")

# Guardar todas las capas en el archivo combinado final
with fiona.Env():
    for layer_name, layer_data in combined_layers.items():
        try:
            if isinstance(layer_data, pd.DataFrame):
                # Guardar las tablas sin geometría como tablas en GPKG
                gdf_empty = gpd.GeoDataFrame(layer_data)
                gdf_empty.to_file(output_file, layer=layer_name, driver="GPKG")
            elif isinstance(layer_data, gpd.GeoDataFrame):
                layer_data.to_file(output_file, layer=layer_name, driver="GPKG")
            log_message(f"Capa '{layer_name}' guardada exitosamente en '{output_file}'.")
        except Exception as e:
            log_message(f"Error al guardar la capa '{layer_name}': {e}")

log_message(f"Proceso de combinación completado. Archivo guardado en: {output_file}")
