import geopandas as gpd
import fiona
import os
import shutil
import pandas as pd
import sqlite3
import json


#-----PARTE GEOGRAFICA------

# Definir EPSG de destino
TARGET_CRS = "EPSG:9377"

# Archivo de registro de salida
log_file = r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_combinado\log_union_proceso.txt"

# Función para registrar mensajes en el archivo de log
def log_message(message):
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(message + "\n")
    #print(message)

# Inicializar el archivo de log
with open(log_file, "w", encoding="utf-8") as log:
    log.write("Registro de ejecución del script de unión de GPKG\n\n")

# Lista de archivos .gpkg a combinar
gpkg_files = [
    #RUTA GPKG VACIO, QUE TIENE LA ESTRUCTURA DESEADA GPKG BASE
    r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_base\modelo_captura_20241029.gpkg",
    #RUTA GPKG INDUAL, CON INFORMACION QUE SERAN COMPILADOS
    # BERMEJAL
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\Bermejal_1_1 CONSERVACION  JUAN Y JULIAN\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\Bermejal_1_1 CONSERVACION KAREN Y WILLIAN 22-12-2024\1_1\1\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\Bermejal_1_2 conservacion ANDRES Y LUCIA\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\Bermejal_1_3-DAVID\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\Bermejal_1_4 Marlon Valvuena\modelo_captura_20241220.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\Bermejal_2_1 JOHAN\2_1\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\Bermejal_2_2_NATALI\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\Bermejal_2_3 DANIEL\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\Bermejal_2_4 MARLON CARDENAS\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\Bermejal_3_1 JOHAN\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\Bermejal_3_2 SANTIAGO\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\bermejal_3_3 ISRAEL\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\Bermejal_3_4 EDIXON\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\BERMEJAL\Bermejal_3_5_ ALEJANDRA\modelo_captura_20241029.gpkg",
    # CABRERA_FUCHATOQUE
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\ENTREGA_COMPILADO_01022025_CABRERA_FUTACHOQUE\GPKG_UNION\captura_campo_20240920.gpkg",
    #PEÑAS_SALITRE
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_1 SANTIAGO\1\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_2  MARLON CARDENAS\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_3 MARLON VALBUENA\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_4 ISRAEL\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_5 EDYXON\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_6 EDUARDO\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_7 JAVIER\7\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_8_ CAMILA\8\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_9 DANIEL\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_10 MARLOM VALBUENA\10\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_10 SANTIAGO\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_10_12 JOSE\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_11_ARLEY\11\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_12 EDUARDO\12\PENAS\SAL\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_13 CONCEVACION DANIEL\13\PENAS\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_14 EDYXON\14\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_15  CONSERVACION MARGARITA, SERVIO, DUBAN\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_15 CONSERVACION KAREN\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_16 CONSERVACION MICHAEL Y JHON\16\16\modelo_captura_20241029.gpkg",
    r"D:\ACC_2025\CONSOLIDADOS\RURAL_05022024\INSUMOS\PEÑAS SALITRE\PENAS_SALITRE_16 NATALY, DAVID Y ALEJANDRA\16_1\modelo_captura_20241029.gpkg"
]


# Archivo de salida y carpeta DCIM
output_file = r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_combinado\captura_campo_20240920.gpkg"
output_dcim_folder = os.path.join(os.path.dirname(output_file), "DCIM")

# Crear carpeta DCIM de salida si no existe
os.makedirs(output_dcim_folder, exist_ok=True)

# Guardar el diccionario en un archivo JSON
def guardar_desplazamientos(desplazamiento_ruta, nombre_archivo='desplazamientos.json'):
    with open(nombre_archivo, 'w') as file:
        json.dump(desplazamiento_ruta, file)

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
    "cca_terreno",
    "cca_construccion",
    "cca_unidadconstruccion",
    "cca_unidadconstruccionhistorica",
    "cca_puntocontrol",
    "cca_puntolevantamiento",
    "cca_puntolindero",
    "cca_puntoreferencia",
    "cca_adjunto",
    "cca_comisiones",
    "cca_estructuraamenazariesgovulnerabilidad",
    "cca_estructuranovedadfmi",
    "cca_estructuranovedadnumeropredial",
    "cca_fuenteadministrativa_derecho",
    "cca_marcas",
    "cca_miembros",
    "cca_ofertasmercadoinmobiliario",
    "cca_omisiones",
    "cca_predio_copropiedad",
    "cca_predio_informalidad",
    "cca_restriccion",
    "cca_saldosconservacion",
    "col_transformacion",
    "extreferenciaregistralsistemaantiguo",
    "cca_derecho",
    "cca_agrupacioninteresados",
    "cca_fuenteadministrativa",
    "cca_interesado",
    "cca_predio",
    "extdireccion",
    "cca_usuario",
    "cca_caracteristicasunidadconstruccion",
    "cca_calificacionconvencional",
    "cca_areaintervencionespecifica",
    "cca_areaintervenciongeneral",
    "cca_construccionhistorica"
]

# Función para procesar un GeoPackage y añadir columnas si es necesario
def modificar_gpkg_con_sql(gpkg_path, capas):
    try:
        conn = sqlite3.connect(gpkg_path)
        cursor = conn.cursor()

        # Obtener la lista de tablas en el GeoPackage
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas_disponibles = [tabla[0] for tabla in cursor.fetchall()]

        for capa in capas:
            # Verificar si la capa existe en las tablas disponibles
            if capa not in tablas_disponibles:
                log_message(f"La capa '{capa}' no se encuentra en '{gpkg_path}', se omite.")
                continue

            # Agregar columnas si no existen
            try:
                cursor.execute(f"ALTER TABLE {capa} ADD COLUMN T_Id_Cop INTEGER;")
                cursor.execute(f"ALTER TABLE {capa} ADD COLUMN Ruta TEXT (150);")
                log_message(f"Columnas T_Id_Cop y Ruta añadidas a la capa '{capa}' en '{gpkg_path}'.")
            except sqlite3.OperationalError:
                log_message(f"Las columnas ya existen o hubo un problema al procesar la capa '{capa}' en '{gpkg_path}', se omite.")

            # Asignar valores a las columnas
            ruta = os.path.abspath(gpkg_path)
            try:
                cursor.execute(f"UPDATE {capa} SET T_Id_Cop = T_Id, Ruta = ?;", (ruta,))
                log_message(f"Valores asignados en la capa '{capa}' de '{gpkg_path}'.")
            except sqlite3.OperationalError:
                log_message(f"No se pudo actualizar los valores en la capa '{capa}' de '{gpkg_path}'.")

        conn.commit()
        conn.close()
    except Exception as e:
        log_message(f"Error al modificar '{gpkg_path}': {e}")

# Aplicar las modificaciones a todos los .gpkg com
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
    dcim_folder = os.path.join(os.path.dirname(gpkg), "DCIM")
    copy_dcim_files(dcim_folder, output_dcim_folder)

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
            "cca_adjunto": "cca_fuenteadminstrtiva_adjunto",
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
            "extreferenciaregistralsistemaantiguo": "cca_predio_referencia_registral_sistema_antiguo"
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
            "cca_caracteristicasunidadconstruccion": "calificacion_convencional"
            }
    }

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
    }
}

# CONFIGURACION ATRIBUTOS PROBLEMATICOS
atributos_mapping = {
    ("cca_usuario", "municipio_codigo"): "departamento_municipio_codigo",  # ejemplo de conflicto en tabla_origen_1  
    # ("tabla_origen_2", "nombre_cliente"): "cliente_nombre",  # ejemplo de conflicto en tabla_origen_2
    # Añadir más campos que se muevan entre los archivos
}

# Conjunto de IDs para verificar duplicados
id_sets = {table: set() for table in config_tablas}

def ajustar_columnas(df_fuente, columnas_destino):
    """
    Ajusta las columnas del DataFrame fuente para que coincidan con las columnas de la tabla destino.
    - Agrega columnas faltantes con valores NULL.
    - Elimina columnas sobrantes.
    :param df_fuente: DataFrame de la tabla fuente.
    :param columnas_destino: Lista de columnas de la tabla destino.
    :return: DataFrame ajustado.
    """
    columnas_fuente = df_fuente.columns.tolist()
    columnas_faltantes = [col for col in columnas_destino if col not in columnas_fuente]
    columnas_sobrantes = [col for col in columnas_fuente if col not in columnas_destino]

    # Agregar columnas faltantes con valores NULL
    for col in columnas_faltantes:
        df_fuente[col] = None

    # Eliminar columnas sobrantes
    df_fuente = df_fuente[[col for col in df_fuente.columns if col not in columnas_sobrantes]]

    # Reordenar columnas según las de destino
    df_fuente = df_fuente[columnas_destino]

    return df_fuente

# Función para ajustar IDs según el índice del .gpkg
def ajustar_ids_por_indice(df, pk_field, id_set, indice):
    """
    Ajusta los IDs en la tabla base para que sean únicos y añade un desplazamiento según el índice del .gpkg.
    :param df: DataFrame de la tabla base.
    :param pk_field: Nombre del campo PK en la tabla base.
    :param id_set: Conjunto de IDs ya usados en la base de datos.
    :param indice: Índice del archivo .gpkg para calcular el desplazamiento.
    :return: DataFrame con IDs ajustados y mapeo de IDs originales a nuevos.
    """
    log_message(f"Ajustando IDs únicos en DataFrame con {len(df)} registros. Índice de .gpkg: {indice}.")
    
    desplazamiento = (indice + 5) * 25000  # Incremento basado en el índice
    id_map = {}  # Mapeo de IDs originales a IDs ajustados
    ultimo_id_asignado = max(id_set) if id_set else 0  # Último ID asignado en el conjunto

    for index, row in df.iterrows():
        original_id = row[pk_field]
        new_id = original_id + desplazamiento  # Aplicar desplazamiento

        # Asegurarse de que el ID es único
        while new_id in id_set:
            log_message(f"Conflicto de ID encontrado: {new_id}. Incrementando para evitar duplicados.")
            new_id += 1

        # Actualizar el ID en el DataFrame
        df.at[index, pk_field] = new_id
        id_map[original_id] = new_id
        id_set.add(new_id)
        ultimo_id_asignado = max(ultimo_id_asignado, new_id)

        log_message(f"ID ajustado para índice {index}: Original: {original_id}, Nuevo: {new_id}.")

    log_message("Ajuste de IDs completado.")
    return df, id_map, desplazamiento

# Función para obtener el máximo ID en una tabla
def obtener_max_id(conn, table, pk_field):
    log_message(f"Obteniendo el máximo ID en la tabla '{table}' para el campo '{pk_field}'.")
    cursor = conn.cursor()
    cursor.execute(f"SELECT MAX({pk_field}) FROM {table}")
    max_id = cursor.fetchone()[0]
    log_message(f"Máximo ID obtenido de la tabla '{table}', campo '{pk_field}': {max_id}.")
    return max_id if max_id else 0

def actualizar_fk_en_relaciones(df, fk_field, id_map, ruta_actual):
    """
    Actualiza las claves foráneas en una tabla relacionada con los nuevos valores de PK,
    asegurando que solo se actualicen los registros correspondientes a la ruta actual.
    :param df: DataFrame de la tabla relacionada.
    :param fk_field: El nombre del campo FK en la tabla relacionada.
    :param id_map: Diccionario de mapeo de IDs originales a nuevos.
    :param ruta_actual: Ruta del archivo .gpkg actual para filtrar los registros.
    :return: DataFrame actualizado con las nuevas claves foráneas.
    """
    log_message(f"Actualizando claves foráneas en DataFrame con {len(df)} registros para la ruta '{ruta_actual}'.")
    
    if fk_field not in df.columns or 'Ruta' not in df.columns:
        log_message(f"Advertencia: El campo FK '{fk_field}' o 'Ruta' no se encuentra en la tabla.")
        return df

    # Filtrar los registros correspondientes a la ruta actual
    df_ruta_actual = df[df['Ruta'] == ruta_actual]
    log_message(f"Registros filtrados para la ruta '{ruta_actual}': {len(df_ruta_actual)}.")

    # Actualizar las claves foráneas utilizando el mapeo de IDs
    df_ruta_actual[fk_field] = df_ruta_actual[fk_field]

    # Reemplazar los registros actualizados en el DataFrame completo
    df.update(df_ruta_actual)
    log_message(f"Actualización de claves foráneas completada para el campo '{fk_field}' y ruta '{ruta_actual}'.")
    return df

def actualizar_registros(conn_dest, tabla_base, pk_field, relaciones, id_map, ruta_actual):
    """
    Actualiza las tablas relacionadas con el nuevo T_Id de la tabla base,
    asegurando que solo se modifiquen registros correspondientes al archivo actual.
    :param conn_dest: Conexión a la base de datos destino.
    :param tabla_base: Nombre de la tabla base (ej. 'cca_predio').
    :param pk_field: Nombre del campo PK en la tabla base (ej. 'T_Id').
    :param relaciones: Diccionario con las relaciones FK.
    :param id_map: Mapeo de IDs originales a nuevos.
    :param ruta_actual: Ruta del archivo .gpkg actual.
    """
    log_message(f"Iniciando actualización de registros en '{tabla_base}'.")
    log_message(f"Campo PK: '{pk_field}', relaciones: {relaciones}, mapeo de IDs: {id_map}.")

    if not relaciones or relaciones == {None}:
        log_message(f"'{tabla_base}' no tiene relaciones. Se insertarán los registros sin actualizar claves foráneas.")
        return
        
    # Procesar las tablas relacionadas
    for fk_table, fk_field in relaciones.items():
        log_message(f"Procesando tabla relacionada '{fk_table}', campo FK: '{fk_field}' EN LA RUTA {ruta_actual}.")
        try:
            df_fk = pd.read_sql_query(f"SELECT * FROM {fk_table}", conn_dest)
            log_message(f"Tabla '{fk_table}' cargada con {len(df_fk)} registros.")


            if fk_field not in df_fk.columns:
                log_message(f"La columna '{fk_field}' no se encuentra en '{fk_table}'. Se omitirá la actualización.")
                continue

            # Actualizar el campo FK solo para los registros correspondientes a la ruta actual
            df_fk = actualizar_fk_en_relaciones(df_fk, fk_field, id_map, ruta_actual)

            # Insertar la tabla relacionada con los cambios
            df_fk.to_sql(fk_table, conn_dest, if_exists="replace", index=False)
            log_message(f"Actualizando FK en '{fk_table}' para los registros de '{tabla_base}'.")
        except Exception as e:
            log_message(f"Error al actualizar FK en '{fk_table}': {e}")


# Procesamiento de tablas con relaciones y desplazamiento por índice
with sqlite3.connect(output_file) as conn_dest:
    # Diccionario para almacenar los desplazamientos
    desplazamiento_ruta = {}
    # Iterar sobre cada archivo .gpkg adicional en gpkg_files
    for indice, gpkg in enumerate(gpkg_files):
        if not os.path.exists(gpkg):
            log_message(f"El archivo '{gpkg}' no existe. Se omitirá.")
            continue

        # Conectar al archivo de origen actual
        with sqlite3.connect(gpkg) as conn_src:
            log_message(f"Procesando archivo de origen: '{gpkg}' (Índice: {indice})")

            # Procesar cada tabla en el orden especificado en `config_tablas`
            for tabla, info in config_tablas.items():
                pk_field = info["pk"]
                relaciones = info["relaciones"]

                # Leer la tabla base del GeoPackage de origen
                try:
                    df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn_src)
                    df['Ruta'] = gpkg  # Asegurar que cada registro incluye la ruta actual

                    if df.empty:
                        log_message(f"La tabla '{tabla}' está vacía. Se omitirá.")
                        continue
                except Exception as e:
                    log_message(f"Error al leer la tabla '{tabla}': {e}")
                    continue
                # SUMAR LOS INCREMENTOS +1000

                try:
                    # Obtener columnas de la tabla destino
                    cursor = conn_dest.cursor()
                    cursor.execute(f"PRAGMA table_info({tabla})")
                    columnas_destino = [row[1] for row in cursor.fetchall()]

                    # Ajustar columnas de la tabla fuente
                    df = ajustar_columnas(df, columnas_destino)

                    # Ajustar IDs en la tabla base usando el desplazamiento por índice
                    max_id = obtener_max_id(conn_dest, tabla, pk_field)
                    df, id_map, desplazamiento = ajustar_ids_por_indice(df, pk_field, id_sets[tabla], indice)

                    # Actualizar las tablas relacionadas con el nuevo T_Id
                    actualizar_registros(conn_dest, tabla, pk_field, relaciones, id_map, gpkg)

                    # GUARDAR EL DESPLAZAMIENTO EN EL DICCIONARIO
                    ruta_gpkg = df['Ruta'].iloc[0]  # Extrae el primer valor de la columna 'Ruta'
                    desplazamiento_ruta[ruta_gpkg] = desplazamiento

                    df.to_sql(tabla, conn_dest, if_exists="append", index=False)
                    log_message(f"Insertando registros en '{tabla}' - Total registros: {len(df)}")

                except Exception as e:
                    log_message(f"Error al insertar registros en '{tabla}': {e}")

        # Limpieza de columnas temporales
        log_message(f"Iniciando limpieza de columnas temporales en capas procesadas: {capas_a_procesar}")
        #eliminar_columnas_de_paso(gpkg, capas_a_procesar)
        log_message("Limpieza completada.")

    # IMPRIMIR EL MAPEO DE desplazamiento ruta:
    log_message("IMPRIMIENDO VALORES EN DESPLAZAMIENTO POR RUTA: ")
    for ruta_gpkg, desplazamiento in desplazamiento_ruta.items():
        log_message(f"PARA LA RUTA DE .GPKG {ruta_gpkg} TENEMOS UN DESPLAZAMIENTO DE: {desplazamiento}")
    
    # ... Después de procesar el diccionario
    
    guardar_desplazamientos(desplazamiento_ruta)

log_message("Proceso de unión de tablas alfanuméricas completado.")