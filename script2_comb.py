import geopandas as gpd
import fiona
import os
import shutil
import pandas as pd
import sqlite3

#-----PARTE GEOGRAFICA-----

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
    r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_base\modelo_captura_20241029.gpkg",
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

# Diccionario para almacenar capas temporales de registros únicos
combined_layers = {}

# Copiar el archivo base al archivo de salida y comenzar desde este
shutil.copy(gpkg_files[0], output_file)

# Función para copiar archivos de una carpeta DCIM sin duplicados
def copy_dcim_files(dcim_folder, output_dcim_folder):
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

# Copiar archivos DCIM del .gpkg base
base_dcim_folder = os.path.join(os.path.dirname(gpkg_files[0]), "DCIM")
copy_dcim_files(base_dcim_folder, output_dcim_folder)

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
    #dcim_folder = os.path.join(os.path.dirname(gpkg), "DCIM")
    #copy_dcim_files(dcim_folder, output_dcim_folder)

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
                        # Extraer propiedades en un DataFrame
                        df = pd.DataFrame([record['properties'] for record in layer])

                        # Verificación de atributos faltantes y concatenación
                        if layer_name in combined_layers:
                            # Alinear las columnas entre DataFrames
                            combined_df = combined_layers[layer_name]
                            for col in combined_df.columns.difference(df.columns):
                                df[col] = "N/A"
                            for col in df.columns.difference(combined_df.columns):
                                combined_df[col] = "N/A"
                            # Concatenar y eliminar duplicados
                            combined_layers[layer_name] = pd.concat(
                                [combined_df, df], ignore_index=True
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


# --- Parte alfanumérica ---


# Configuración de tablas y relaciones PK-FK
config_tablas = {

    "cca_usuario": {
        "pk": "T_Id", "relaciones": {
            "cca_predio": "usuario"
            }
    },
    "cca_predio": {
        "pk": "T_Id",
        "relaciones": {
            "cca_terreno": "predio",
            "cca_derecho": "predio",
            "cca_construccion": "predio"
        }
    },
    #"cca_terreno": {"pk": "T_Id", "relaciones": {""}}
    # Añadir más tablas y relaciones según sea necesario
}

# Conjunto de IDs para verificar duplicados
id_sets = {table: set() for table in config_tablas}

# Función para obtener el máximo ID en una tabla
def obtener_max_id(conn, table, pk_field):
    cursor = conn.cursor()
    cursor.execute(f"SELECT MAX({pk_field}) FROM {table}")
    max_id = cursor.fetchone()[0]
    return max_id if max_id else 0

# Función para ajustar IDs en la tabla base y registrar la correspondencia en un diccionario
def ajustar_ids(df, offset, pk_field, id_set):
    id_map = {}  # Mapeo de IDs originales a IDs ajustados
    if pk_field not in df.columns:
        log_message(f"Advertencia: El campo PK '{pk_field}' no se encuentra en la tabla.")
        return df, id_map
    for index, row in df.iterrows():
        original_id = row[pk_field]
        new_id = original_id + offset
        
        # Evitar duplicados en el conjunto de IDs
        while new_id in id_set:
            new_id += 1  # Incrementa el nuevo ID si ya existe en el conjunto

        df.at[index, pk_field] = new_id
        id_map[original_id] = new_id  # Mapeo del PK original al nuevo PK
        id_set.add(new_id)  # Añadir el nuevo ID al conjunto para seguimiento
    return df, id_map

# Función para alinear atributos según la estructura del archivo base
def alinear_atributos(df, columnas_base):
    for columna in columnas_base:
        if columna not in df.columns:
            df[columna] = None  # Agrega la columna faltante con valor NULL
    # Ignorar columnas adicionales que no están en el archivo base
    df = df[[col for col in columnas_base if col in df.columns]]
    return df

# Función para actualizar las FKs en las tablas relacionadas usando `id_map`
def actualizar_fk_en_relaciones(df, fk_field, id_map):
    if fk_field not in df.columns:
        log_message(f"Advertencia: El campo FK '{fk_field}' no se encuentra en la tabla relacionada.")
        return df
    # Reemplazar valores de FK según el mapeo original -> ajustado
    df[fk_field] = df[fk_field].map(id_map).fillna(df[fk_field])
    return df

# Procesamiento de tablas con relaciones, sin relaciones y de dominio
with sqlite3.connect(output_file) as conn_dest:
    # Iterar sobre cada archivo .gpkg adicional en gpkg_files
    for gpkg in gpkg_files[1:]:
        if not os.path.exists(gpkg):
            log_message(f"El archivo '{gpkg}' no existe. Se omitirá.")
            continue

        # Conectar al archivo de origen actual
        with sqlite3.connect(gpkg) as conn_src:
            log_message(f"Procesando archivo de origen: '{gpkg}'")

            # Procesar cada tabla en el orden especificado en `config_tablas`
            for tabla, info in config_tablas.items():
                pk_field = info["pk"]
                relaciones = info["relaciones"]

                # Leer la tabla base del GeoPackage de origen
                try:
                    df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn_src)
                    if df.empty:
                        log_message(f"La tabla '{tabla}' está vacía en '{gpkg}'. Se omitirá.")
                        continue
                except Exception as e:
                    log_message(f"Error al leer la tabla '{tabla}' en '{gpkg}': {e}")
                    continue

                # Obtener las columnas base de la tabla en el archivo de destino
                try:
                    df_base = pd.read_sql_query(f"SELECT * FROM {tabla} LIMIT 0", conn_dest)
                    columnas_base = df_base.columns.tolist()
                except Exception as e:
                    log_message(f"Error al obtener columnas base para '{tabla}' en '{output_file}': {e}")
                    continue

                # Alinear atributos con la estructura del .GPKG base
                df = alinear_atributos(df, columnas_base)

                # Ajustar IDs si la tabla tiene PK
                if pk_field:
                    max_id = obtener_max_id(conn_dest, tabla, pk_field)
                    offset = max_id + 1
                    df_ajustada, id_map = ajustar_ids(df, offset, pk_field, id_sets[tabla])
                    log_message(f"Ajustando IDs para la tabla '{tabla}' desde el archivo '{gpkg}' con offset {offset}.")

                    # Actualizar FKs en las tablas relacionadas
                    for fk_table, fk_field in relaciones.items():
                        try:
                            df_fk = pd.read_sql_query(f"SELECT * FROM {fk_table}", conn_src)
                            if fk_field not in df_fk.columns:
                                log_message(f"La columna '{fk_field}' no se encuentra en '{fk_table}' en '{gpkg}'. Se omitirá la actualización de FK.")
                                continue
                            df_fk[fk_field] = df_fk[fk_field].map(id_map).fillna(df_fk[fk_field])
                            df_fk = alinear_atributos(df_fk, columnas_base)
                            df_fk.to_sql(fk_table, conn_dest, if_exists="append", index=False)
                            log_message(f"Actualizando FK en '{fk_table}' para la tabla '{tabla}' desde el archivo '{gpkg}'.")
                        except Exception as e:
                            log_message(f"Error al actualizar FK en '{fk_table}' relacionado con '{tabla}' en '{gpkg}': {e}")
                
                    # Insertar la tabla base ajustada en el archivo de destino
                    try:
                        df_ajustada.to_sql(tabla, conn_dest, if_exists="append", index=False)
                        log_message(f"Insertando registros en '{tabla}' desde '{gpkg}' - Total registros: {len(df_ajustada)}")
                    except sqlite3.IntegrityError as e:
                        log_message(f"Error de duplicado en '{tabla}' desde '{gpkg}' - {e}")
                    except Exception as e:
                        log_message(f"Error general al insertar en '{tabla}' desde '{gpkg}': {e}")
                else:
                    # Para tablas sin PK, insertar directamente
                    try:
                        df = alinear_atributos(df, columnas_base)
                        df.to_sql(tabla, conn_dest, if_exists="append", index=False)
                        log_message(f"Insertando registros en '{tabla}' desde '{gpkg}' - Total registros: {len(df)}")
                    except sqlite3.IntegrityError as e:
                        log_message(f"Error de duplicado en '{tabla}' desde '{gpkg}' - {e}")
                    except Exception as e:
                        log_message(f"Error general al insertar en '{tabla}' desde '{gpkg}': {e}")

log_message("Proceso de unión de tablas alfanuméricas completado.")