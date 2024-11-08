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

    "cca_predio": {
        "pk": "T_Id",
        "relaciones": {
            "cca_terreno": "predio",
            "cca_derecho": "predio",
            "cca_construccion": "predio"
        }
    },

    "cca_usuario": {
        "pk": "T_Id", 
        "relaciones": {
            "cca_predio": "usuario"
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

# Función para verificar y ajustar IDs en la tabla base
def ajustar_ids_unicos(df, pk_field, id_set):
    """
    Ajusta los IDs en la tabla base para que no haya duplicados en las tablas relacionadas.
    :param df: DataFrame de la tabla base.
    :param pk_field: El nombre del campo PK en la tabla base.
    :param id_set: Conjunto de IDs ya usados en la base de datos.
    :return: DataFrame con IDs ajustados.
    """
    id_map = {}  # Mapeo de IDs originales a IDs ajustados
    for index, row in df.iterrows():
        original_id = row[pk_field]
        new_id = original_id
        
        # Verificar que el nuevo ID no esté duplicado en las tablas relacionadas
        while new_id in id_set:
            new_id += 1  # Incrementar el nuevo ID si ya existe en el conjunto

        df.at[index, pk_field] = new_id
        id_map[original_id] = new_id
        id_set.add(new_id)
    
    return df, id_map

def alinear_atributos(df, columnas_base):
    """
    Alinea las columnas del DataFrame con la estructura base.
    :param df: DataFrame de la tabla a alinear.
    :param columnas_base: Lista de columnas en la tabla base.
    :return: DataFrame alineado.
    """
    for columna in columnas_base:
        if columna not in df.columns:
            df[columna] = None  # Agregar columna faltante con valores NULL
    # Ignorar columnas adicionales que no están en la base
    df = df[[col for col in columnas_base if col in df.columns]]
    return df

def actualizar_fk_en_relaciones(df, fk_field, id_map):
    """
    Actualiza las claves foráneas en una tabla relacionada con los nuevos valores de PK.
    :param df: DataFrame de la tabla relacionada.
    :param fk_field: El nombre del campo FK en la tabla relacionada.
    :param id_map: Diccionario de mapeo de IDs originales a nuevos.
    :return: DataFrame actualizado con las nuevas claves foráneas.
    """
    if fk_field not in df.columns:
        log_message(f"Advertencia: El campo FK '{fk_field}' no se encuentra en la tabla.")
        return df
    
    # Actualizar las claves foráneas utilizando el mapeo de IDs
    df[fk_field] = df[fk_field].map(id_map).fillna(df[fk_field])
    
    return df

def actualizar_registros(conn_dest, tabla_base, pk_field, relaciones, id_map):
    """
    Actualiza las tablas relacionadas con el nuevo T_Id de la tabla base.
    :param conn_dest: Conexión a la base de datos destino.
    :param tabla_base: Nombre de la tabla base (ej. 'cca_predio').
    :param pk_field: Nombre del campo PK en la tabla base (ej. 'T_Id').
    :param relaciones: Diccionario con las relaciones FK.
    :param id_map: Mapeo de IDs originales a nuevos.
    """
    # Procesar las tablas relacionadas
    for fk_table, fk_field in relaciones.items():
        try:
            df_fk = pd.read_sql_query(f"SELECT * FROM {fk_table}", conn_dest)
            if fk_field not in df_fk.columns:
                log_message(f"La columna '{fk_field}' no se encuentra en '{fk_table}'. Se omitirá la actualización.")
                continue
            
            # Actualizar el campo FK con el nuevo T_Id
            df_fk = actualizar_fk_en_relaciones(df_fk, fk_field, id_map)

            # Insertar la tabla relacionada con los cambios
            df_fk.to_sql(fk_table, conn_dest, if_exists="replace", index=False)
            log_message(f"Actualizando FK en '{fk_table}' para los registros de '{tabla_base}'.")
        except Exception as e:
            log_message(f"Error al actualizar FK en '{fk_table}': {e}")

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
                        log_message(f"La tabla '{tabla}' está vacía. Se omitirá.")
                        continue
                except Exception as e:
                    log_message(f"Error al leer la tabla '{tabla}': {e}")
                    continue

                # Ajustar IDs en la tabla base
                max_id = obtener_max_id(conn_dest, tabla, pk_field)
                offset = max_id + 1
                df_ajustada, id_map = ajustar_ids_unicos(df, pk_field, id_sets[tabla])

                # Actualizar las tablas relacionadas con el nuevo T_Id
                actualizar_registros(conn_dest, tabla, pk_field, relaciones, id_map)

                # Insertar la tabla base ajustada
                try:
                    df_ajustada.to_sql(tabla, conn_dest, if_exists="append", index=False)
                    log_message(f"Insertando registros en '{tabla}' - Total registros: {len(df_ajustada)}")
                except Exception as e:
                    log_message(f"Error al insertar registros en '{tabla}': {e}")

log_message("Proceso de unión de tablas alfanuméricas completado.")