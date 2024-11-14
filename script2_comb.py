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
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(message + "\n")
    print(message)

# Inicializar el archivo de log
with open(log_file, "w", encoding="utf-8") as log:
    log.write("Registro de ejecución del script de unión de GPKG\n\n")

# Lista de archivos .gpkg a combinar
gpkg_files = [
    r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_base\modelo_captura_20241029.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\MZ16_FINAL_Correcto_1\MN_00000016_20240923\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\MN_00000009_20240923_2\MN_00000009_20240923-vf\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\MN_00000003_20241009_FINAL_3\MN_00000003_20241009_FINAL\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\MANZANA 8_4\MANZANA 8\MN_00000008_20240923\MN_00000008_20240923\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\00000017-01_5\captura_campo_20240920.gpkg",
    #OTRAS RUTAS
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0003\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0005\MN_00000005_20241011_OK\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0007\MN_00000007_20241015_31\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0008\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0009\MN_00000009_20240923-vf\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0010\MN_00000010_20241105\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0011\MN_00000011_NITOLA\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0012\MN_00000012_20240926\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0014\MN_00000014_20241025\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0015_1\MN_00000015_20241010\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0015_2\MN_00000015_20241105\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0016\MN_00000016_20240923\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0017\00000017-01\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0018\MN_00000018_20240923\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0022\MN_00000022_20240926\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0023\Captura actualizada\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241112_CONSOLIDACION\0025\captura_campo_20240920.gpkg"
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

#AGREGAR CAMPO PROBLEMATICO
# Función para agregar columna a una tabla específica si no existe
def agregar_columna_si_no_existe(gpkg_p, tabla, columna, tipo_dato):
    try:
        conn = sqlite3.connect(gpkg_p)
        cursor = conn.cursor()

        # Verificar si la columna ya existe
        cursor.execute(f"PRAGMA table_info({tabla});")
        columnas = [info[1] for info in cursor.fetchall()]
        if columna not in columnas:
            cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo_dato};")
            log_message(f"Columna '{columna}' añadida a la tabla '{tabla}' en '{gpkg_p}'.")
        else:
            log_message(f"La columna '{columna}' ya existe en la tabla '{tabla}' en '{gpkg_p}', se omite la creación.")

        conn.commit()
        conn.close()
    except Exception as e:
        log_message(f"Error al agregar columna en '{gpkg_p}': {e}")
gpkg_p = "C:\ACC\CONSOLIDACION_MANZANAS\gpkg_base\modelo_captura_20241029.gpkg"
agregar_columna_si_no_existe(gpkg_p, 'cca_usuario', 'municipio_codigo', 'TEXT(100)')

# Lista de capas geográficas específicas a procesar
capas_a_procesar = [
    "cca_construccion",
    "cca_unidadconstruccion",
    "cca_puntocontrol",
    "cca_puntolevantamiento",
    "cca_puntolindero",
    "cca_puntoreferencia"
]

# Función para agregar columnas y actualizar valores usando SQL
def modificar_gpkg_con_sql(gpkg_path, capas):
    try:
        conn = sqlite3.connect(gpkg_path)
        cursor = conn.cursor()

        for capa in capas:
            # Agregar columnas si no existen
            try:
                cursor.execute(f"ALTER TABLE {capa} ADD COLUMN T_Id_Cop INTEGER;")
                cursor.execute(f"ALTER TABLE {capa} ADD COLUMN Ruta TEXT (150);")
                log_message(f"Columnas T_Id_Cop y Ruta añadidas a la capa '{capa}' en '{gpkg_path}'.")
            except sqlite3.OperationalError:
                log_message(f"Las columnas ya existen en la capa '{capa}' de '{gpkg_path}', se omite la creación.")

            # Asignar valores a las columnas
            ruta = os.path.abspath(gpkg_path)
            cursor.execute(f"UPDATE {capa} SET T_Id_Cop = T_Id, Ruta = ?;", (ruta,))
            log_message(f"Valores asignados en la capa '{capa}' de '{gpkg_path}'.")

        conn.commit()
        conn.close()
    except Exception as e:
        log_message(f"Error al modificar '{gpkg_path}': {e}")

# Aplicar las modificaciones a todos los .gpkg
for i, gpkg in enumerate(gpkg_files):
    if not os.path.exists(gpkg):
        log_message(f"El archivo '{gpkg}' no existe. Se omitirá.")
        continue

    log_message(f"Modificando '{gpkg}' con SQL...")
    modificar_gpkg_con_sql(gpkg, capas_a_procesar)

log_message("Modificaciones completadas en todos los .gpkg.")

# Diccionario para mapear T_Id a nuevo fid
id_map_geo = {}

# Función para eliminar columnas de paso al final del proceso
def eliminar_columnas_de_paso(gpkg_path, capas):
    try:
        conn = sqlite3.connect(gpkg_path)
        cursor = conn.cursor()

        for capa in capas:
            try:
                cursor.execute(f"ALTER TABLE {capa} DROP COLUMN T_Id_Cop;")
                cursor.execute(f"ALTER TABLE {capa} DROP COLUMN Ruta;")
                log_message(f"Columnas T_Id_Cop y Ruta eliminadas de la capa '{capa}' en '{gpkg_path}'.")
            except sqlite3.OperationalError:
                log_message(f"No se pueden eliminar columnas de la capa '{capa}' en '{gpkg_path}'.")

        conn.commit()
        conn.close()
    except Exception as e:
        log_message(f"Error al eliminar columnas en '{gpkg_path}': {e}")

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

                        if 'T_Id' in gdf.columns:
                        # Mapeo y ajuste de IDs
                            for index, row in gdf.iterrows():
                                original_id = row['T_Id']
                                if original_id not in id_map_geo:
                                    new_fid = len(id_map_geo) + 1  # Generar nuevo fid único
                                    id_map_geo[original_id] = {"fid": new_fid, "origen": gpkg}
                                    gdf.at[index, 'T_Id'] = new_fid  # Actualizar T_Id en el DataFrame
                                    continue

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

# Imprimir el contenido de id_map_geo en el log y en la consola
log_message("Contenido del diccionario id_map_geo:")
for original_id, info in id_map_geo.items():
    log_message(f"T_Id original: {original_id}, Nuevo fid: {info['fid']}, Origen: {info['origen']}")

log_message(f"Proceso de combinación completado. Archivo guardado en: {output_file}")


# --- Parte alfanumérica ---


# Configuración de tablas y relaciones PK-FK
config_tablas = {

    "cca_adjunto": {
        "pk": "T_Id", 
        "relaciones": {
            None
            }
    },

    "cca_comisiones": {
        "pk": "fid", 
        "relaciones": {
            None
            }
    },

    "cca_estructuraamenazariesgovulnerabilidad": {
        "pk": "T_Id", 
        "relaciones": {
            None
            }
    },

    "cca_estructuranovedadfmi": {
        "pk": "T_Id", 
        "relaciones": {
           None
            }
    },

    "cca_estructuranovedadnumeropredial": {
        "pk": "T_Id", 
        "relaciones": {
            None
            }
    },

    "cca_fuenteadministrativa_derecho": {
        "pk": "T_Id", 
        "relaciones": {
            None
            }
    },

    "cca_marcas": {
        "pk": "fid", 
        "relaciones": {
            None
            }
    },

    "cca_miembros": {
        "pk": "T_Id", 
        "relaciones": {
            None
            }
    },

    "cca_ofertasmercadoinmobiliario": {
        "pk": "T_Id", 
        "relaciones": {
            None
            }
    },

    "cca_omisiones": {
        "pk": "T_Id", 
        "relaciones": {
            None
            }
    },

    "cca_predio_copropiedad": {
        "pk": "T_Id", 
        "relaciones": {
            None
            }
    },

    "cca_predio_informalidad": {
        "pk": "T_Id", 
        "relaciones": {
            None
            }
    },

    "cca_restriccion": {
        "pk": "T_Id", 
        "relaciones": {
            None
            }
    },

    "cca_saldosconservacion": {
        "pk": "fid", 
        "relaciones": {
            None
            }
    },

    "col_transformacion": {
        "pk": "fid", 
        "relaciones": {
            None
            }
    },

    "extreferenciaregistralsistemaantiguo": {
        "pk": "T_Id", 
        "relaciones": {
            None
            }
    },

    "cca_derecho": {
        "pk": "T_Id", 
        "relaciones": {
            "cca_fuenteadministrativa_derecho": "derecho"
            }
    },

    "cca_agrupacioninteresados": {
        "pk": "T_Id", 
        "relaciones": {
            "cca_derecho": "agrupacion_interesados",
            "cca_miembros": "agrupacion"
            }
    },

    "cca_fuenteadministrativa": {
        "pk": "T_Id", 
        "relaciones": {
            "cca_adjunto": "cca_fuenteadministrativa_adjunto",
            "cca_fuenteadministrativa_derecho": "fuente_administrativa"
            }
    },

    "cca_interesado": {
        "pk": "T_Id", 
        "relaciones": {
            "cca_adjunto": "cca_interesado_adjunto",
            "cca_derecho": "interesado",
            "cca_miembros": "interesado"
            }
    },

    "cca_predio": {
        "pk": "T_Id",
        "relaciones": {
            "cca_terreno": "predio",
            "cca_derecho": "predio",
            "cca_construccion": "predio",
            "cca_adjunto": "cca_predio_adjunto",
            "cca_estructuraamenazariesgovulnerabilidad": "cca_predio_amenazariesgovulnerabilidad",
            "cca_estructuranovedadfmi": "cca_predio_novedad_fmi",
            "cca_estructuranovedadnumeropredial": "cca_predio_novedad_numeros_prediales",
            "cca_ofertasmercadoinmobiliario": "predio",
            "cca_predio_copropiedad": "unidad_predial",
            "cca_predio_copropiedad": "matriz",
            "cca_predio_informalidad": "cca_predio_formal",
            "cca_predio_informalidad": "cca_predio_informal",
            "cca_restriccion": "predio",
            "extdireccion": "cca_predio_direccion",
            "extreferenciaregistralsistemaantiguo": "cc_predio_referencia_registral_sistema_antiguo"
        }
    },

    "cca_usuario": {
        "pk": "T_Id", 
        "relaciones": {
            "cca_predio": "usuario"
            }
    },

    "cca_caracteristicasunidadconstruccion": {
        "pk": "T_Id", 
        "relaciones": {
            "cca_unidadconstruccion": "caracteristicasunidadconstruccion"
            }
    },


    "cca_calificacionconvencional": {
        "pk": "T_Id", 
        "relaciones": {
            "cca_caracteristicasunidadconstruccion": "calificacionconvencional"
            }
    },

}

config_geom = {
    #GEOGRAFICAS:

    "cca_unidadconstruccion": {
        "pk": "fid", 
        "relaciones": {
            "cca_adjunto": "cca_unidadconstruccion_adjunto"
            }
    },

    "cca_construccion": {
        "pk": "fid", 
        "relaciones": {
            "cca_adjunto": "cca_construccion_adjunto",
            "cca_unidadconstruccion": "construccion"
            }
    },

    "cca_puntocontrol": {
        "pk": "fid", 
        "relaciones": {
            "cca_adjunto": "cca_puntocontrol_adjunto"
            }
    },

    "cca_puntolevantamiento": {
        "pk": "fid", 
        "relaciones": {
            "cca_adjunto": "cca_puntolevantamiento_adjunto"
            }
    },

    "cca_puntolindero": {
        "pk": "fid", 
        "relaciones": {
            "cca_adjunto": "cca_puntolindero_adjunto"
            }
    },

    "cca_puntoreferencia": {
        "pk": "fid", 
        "relaciones": {
            "cca_adjunto": "cca_puntoreferencia_adjunto"
            }
    },
}

# CONFIGURACION ATRIBUTOS PROBLEMATICOS
atributos_mapping = {
    ("cca_usuario", "municipio_codigo"): "departamento_municipio_codigo",  # ejemplo de conflicto en tabla_origen_1  
    # ("tabla_origen_2", "nombre_cliente"): "cliente_nombre",  # ejemplo de conflicto en tabla_origen_2
    # Añadir más campos que se muevan entre los archivos
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

        # Si el campo PK es 'fid', saltar inserciones y solo actualizar relaciones
        if pk_field == 'fid':
            # Saltar la inserción y solo mapear las relaciones
            id_map[original_id] = original_id
            continue

        new_id = original_id
        # Verificar que el nuevo ID no esté duplicado en las tablas relacionadas
        while new_id in id_set:
            new_id += 1  # Incrementar el nuevo ID si ya existe en el conjunto

        df.at[index, pk_field] = new_id
        id_map[original_id] = new_id
        id_set.add(new_id)
    
    return df, id_map

def alinear_atributos(df, tabla_origen, columnas_base, atributos_mapping):
    """
    Alinea las columnas del DataFrame con la estructura base,
    usando el mapeo para adaptar los nombres de los atributos si es necesario.
    :param df: DataFrame de la tabla a alinear.
    :param tabla_origen: El nombre de la tabla de origen, usado para identificar los conflictos.
    :param columnas_base: Lista de columnas en la tabla base.
    :param atributos_mapping: Diccionario de mapeo de nombres de campos problemáticos.
    :return: DataFrame alineado.
    """
    # Filtrar solo los atributos que son específicos para la tabla de origen
    mapping_especifico = {campo_origen: campo_destino for (tabla, campo_origen), campo_destino in atributos_mapping.items() if tabla == tabla_origen}

    # Renombrar las columnas según el mapeo
    df.rename(columns=mapping_especifico, inplace=True)
    
    # Agregar columnas faltantes con valores NULL
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
    if not relaciones or relaciones == {None}:
        log_message(f"'{tabla_base}' no tiene relaciones. Se insertarán los registros sin actualizar claves foráneas.")
              
    else:

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
                offset = int(max_id) + 1
                df_ajustada, id_map = ajustar_ids_unicos(df, pk_field, id_sets[tabla])

                # Actualizar las tablas relacionadas con el nuevo T_Id
                actualizar_registros(conn_dest, tabla, pk_field, relaciones, id_map)

                # Insertar la tabla base ajustada
                try:
                    df_ajustada.to_sql(tabla, conn_dest, if_exists="append", index=False)
                    log_message(f"Insertando registros en '{tabla}' - Total registros: {len(df_ajustada)}")
                except Exception as e:
                    log_message(f"Error al insertar registros en '{tabla}': {e}")
        
            # Procesamiento de relaciones geográficas después de las tablas base
            for tabla_geom, geom_info in config_geom.items():
                pk_field = geom_info["pk"]
                relaciones = geom_info.get("relaciones", {})

                # Actualizar las relaciones si existen
                if relaciones:
                    for related_table, fk_field in relaciones.items():
                        log_message(f"Actualizando relaciones geográficas para la tabla '{related_table}' en base a '{tabla_geom}'")

                        # Consulta para seleccionar los registros que serán actualizados
                        select_query = f"""
                            SELECT rt.rowid AS rt_rowid, rt.{fk_field} AS old_fk_value, bt.{pk_field} AS new_fk_value
                            FROM {related_table} AS rt
                            JOIN {tabla_geom} AS bt
                            ON rt.{fk_field} = bt.T_Id_Cop
                            WHERE bt.Ruta = '{gpkg}'
                            AND rt.{fk_field} IS NOT NULL
                        """

                        try:
                            # Obtener los registros que serán actualizados y mostrar sus cambios
                            rows_to_update = conn_dest.execute(select_query).fetchall()
                            
                            # Mostrar en consola los cambios específicos
                            if rows_to_update:
                                log_message(f"Se encontraron {len(rows_to_update)} registros en '{related_table}' para actualizar el campo '{fk_field}'")
                                for row in rows_to_update:
                                    rt_rowid, old_fk_value, new_fk_value = row
                                    log_message(f"Registro ID {rt_rowid} en '{related_table}': valor actual '{old_fk_value}', nuevo valor '{new_fk_value}'")
                                
                                # Ejecutar la actualización de los registros seleccionados usando subconsulta
                                for row in rows_to_update:
                                    rt_rowid, _, new_fk_value = row
                                    update_query = f"""
                                        UPDATE {related_table} 
                                        SET {fk_field} = ?
                                        WHERE rowid = ?
                                    """
                                    conn_dest.execute(update_query, (new_fk_value, rt_rowid))
                                
                                conn_dest.commit()
                                log_message(f"Actualización completada en '{related_table}' para la relación '{fk_field}' basada en '{tabla_geom}'")
                            else:
                                log_message(f"No se encontraron registros para actualizar en '{related_table}' para la relación '{fk_field}' basada en '{tabla_geom}'")

                        except Exception as e:
                            log_message(f"Error al actualizar la relación '{fk_field}' en '{related_table}': {e}")
        
        eliminar_columnas_de_paso(gpkg, capas_a_procesar)

                    

log_message("Proceso de unión de tablas alfanuméricas completado.")