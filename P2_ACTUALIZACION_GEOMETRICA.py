import sqlite3
import os
import json


# Ruta al GeoPackage y al archivo de log
gpkg_path = r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_combinado\captura_campo_20240920.gpkg"
log_path = r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_combinado\console_log_val_geo.txt"

# Función para registrar logs
def log_message(message):
    print(message)
    with open(log_path, "a") as log_file:
        log_file.write(message + "\n")

# Función para cargar el diccionario desde un archivo JSON
def cargar_desplazamientos(nombre_archivo='desplazamientos.json'):
    with open(nombre_archivo, 'r') as file:
        return json.load(file)

# Verificar existencia del archivo GeoPackage
if not os.path.exists(gpkg_path):
    log_message(f"ERROR: No se encontró el archivo GeoPackage en la ruta: {gpkg_path}")
    exit()

# Conexión al GeoPackage
try:
    conn = sqlite3.connect(gpkg_path)
    cursor = conn.cursor()
    log_message("Conexión exitosa al archivo GeoPackage.")
except sqlite3.Error as e:
    log_message(f"ERROR: No se pudo conectar al archivo GeoPackage. {e}")
    exit()

# Configuración de las capas y relaciones
config_geom = {
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

    "cca_terreno": {
        "pk": "fid",
        "relaciones": {}
    },

    "extdireccion": {
        "pk": "fid",
        "relaciones": {}
    }
}

config_tablas = {
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
            "cca_predio_copropiedad": ["unidad_predial", "matriz"],
            "cca_predio_informalidad": ["cca_predio_formal", "cca_predio_informal"],
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

def verificar_maximos(cursor, config_geom):
    """
    Verifica el valor máximo de los atributos de las tablas y relaciones definidas en config_geom,
    imprime los resultados y calcula la milésima superior.

    Args:
        cursor: Cursor activo de la conexión SQLite.
        config_geom (dict): Configuración de las tablas y relaciones.
    """
    log_message("=== Inicio de verificación de máximos ===")
    maximos_por_tabla = {}
    max_total = 0

    try:
        # Iterar por cada tabla en la configuración
        for tabla, detalles in config_geom.items():
            log_message(f"Procesando tabla: {tabla}")
            pk_field = detalles["pk"]

            # Obtener el valor máximo del campo principal
            try:
                cursor.execute(f"SELECT MAX({pk_field}) FROM {tabla}")
                max_pk = cursor.fetchone()[0] or 0
                log_message(f"Máximo valor en {tabla}.{pk_field}: {max_pk}")
                maximos_por_tabla[tabla] = {"max_pk": max_pk}
                max_total = max(int(float(max_total)), int(float(max_pk)))
            except sqlite3.Error as e:
                log_message(f"ERROR al procesar {tabla}: {e}")
                continue

            # Verificar las relaciones solo si están definidas
            max_relaciones = {}
            relaciones = detalles.get("relaciones", {})
            for tabla_rel, campo_rel in relaciones.items():
                if campo_rel:  # Asegurarse de que la relación no sea None
                    try:
                        cursor.execute(f"SELECT MAX({campo_rel}) FROM {tabla_rel}")
                        max_rel = int(float(cursor.fetchone()[0] or 0))
                        log_message(f"Máximo valor en relación {tabla_rel}.{campo_rel}: {max_rel}")
                        max_relaciones[tabla_rel] = max_rel
                        max_total = max(max_total, max_rel)
                    except sqlite3.Error as e:
                        log_message(f"ERROR al procesar relación {tabla_rel}: {e}")
            
            maximos_por_tabla[tabla]["relaciones"] = max_relaciones

        # Calcular la milésima superior del máximo total
        max_milesima = ((max_total // 1000) + 1) * 1000
        log_message(f"Máximo total: {max_total}")
        log_message(f"Milésima superior del máximo total: {max_milesima}")

        # Devolver los resultados
        return {
            "maximos_por_tabla": maximos_por_tabla,
            "max_total": max_total,
            "max_milesima": max_milesima
        }

    except sqlite3.Error as e:
        log_message(f"ERROR en la verificación de máximos: {e}")
        return None

    finally:
        log_message("=== Fin de verificación de máximos ===")

# Parte 1: Mapeo de registros
def map_tables(cursor, config_geom):
    log_message("=== Inicio del mapeo de tablas ===")
    for table, details in config_geom.items():
        log_message(f"   ---MAPEO DE LA TABLA: {table}---   ")
        pk_field = details["pk"]
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        record_count = cursor.fetchone()[0]
        if record_count > 0:
            cursor.execute(f"SELECT {pk_field}, T_Id_Cop, Ruta FROM {table}")
            rows = cursor.fetchall()
            for row in rows:
                log_message(f"({row[0]}) = {{({row[1]}), ({row[2]}), ({table})}}")
        else:
            log_message(f"La tabla {table} no tiene registros.")
    log_message("=== Fin del mapeo de tablas ===")

def actualizar_por_ruta(cursor, conn, config_tablas, desplazamiento_ruta):
    """
    Actualiza las claves primarias y relaciones basadas en los valores de la columna 'Ruta'.

    Args:
        cursor: Cursor activo de la conexión SQLite.
        conn: Conexión activa a la base de datos SQLite.
        config_geom (dict): Configuración de las tablas y relaciones.
    """
    log_message("=== Inicio de actualización por ruta ===")
    try:
        for table, details in config_geom.items():
            pk_field = details["pk"]
            relaciones = details["relaciones"]

            # Obtener rutas únicas en la tabla principal
            cursor.execute(f"SELECT DISTINCT Ruta FROM {table} ORDER BY Ruta")
            rutas = cursor.fetchall()

            if not rutas:
                log_message(f"No se encontraron rutas en la tabla '{table}'.")
                continue

            log_message(f"Rutas encontradas en '{table}': {rutas}")

            for idx, (ruta,) in enumerate(rutas):
                # Obtener el incremento del JSON por la ruta
                incremento = desplazamiento_ruta.get(ruta, 2000)  # Valor por defecto si no se encuentra la ruta
                offset = incremento + idx
                log_message(f"Procesando Ruta='{ruta}' con offset={offset}")

                # Actualizar PK en la tabla principal
                update_pk_query = f"""
                UPDATE {table}
                SET {pk_field} = T_Id_Cop + ?
                WHERE Ruta = ?;
                """
                cursor.execute(update_pk_query, (incremento, ruta))
                conn.commit()

                # Actualizar claves relacionadas en otras tablas
                if relaciones:
                    for related_table, related_field in relaciones.items():
                        log_message(f"Actualizando {related_table} relacionado con {table}...")

                        # Actualizar claves relacionadas
                        update_related_query = f"""
                        UPDATE {related_table}
                        SET {related_field} = {related_field} + ?
                        WHERE Ruta = ?;
                        """
                        cursor.execute(update_related_query, (incremento, ruta))
                        conn.commit()

                        log_message(f"Actualizados registros de {related_field} en {related_table} para Ruta='{ruta}' con Incrementos de ={incremento}")

        log_message("=== Actualización completada exitosamente ===")

    except sqlite3.Error as e:
        log_message(f"ERROR durante la actualización por ruta: {e}")
    except Exception as e:
        log_message(f"ERROR inesperado: {e}")
    finally:
        log_message("=== Fin del proceso de actualización ===")

def actualizar_relaciones(cursor, conn, config_geom, desplazamiento_ruta):
    """
    Actualiza los valores de las relaciones en las tablas relacionadas con base en los valores de desplazamiento
    proporcionados para cada ruta en el JSON.

    Args:
        cursor: Cursor activo de la conexión SQLite.
        conn: Conexión activa a la base de datos SQLite.
        config_geom (dict): Configuración de las tablas y relaciones.
        desplazamiento_ruta (dict): Diccionario con rutas y sus desplazamientos.
    """
    log_message("=== Inicio de actualización de relaciones por ruta ===")

    try:
        # Iterar por cada tabla en la configuración
        for tabla_principal, detalles in config_geom.items():
            relaciones = detalles.get("relaciones", {})

            if not relaciones:
                log_message(f"La tabla '{tabla_principal}' no tiene relaciones definidas. Se omite.")
                continue

            # Obtener rutas únicas en la tabla principal
            cursor.execute(f"SELECT DISTINCT Ruta FROM {tabla_principal} ORDER BY Ruta")
            rutas = cursor.fetchall()

            if not rutas:
                log_message(f"No se encontraron rutas en la tabla '{tabla_principal}'.")
                continue

            log_message(f"Rutas encontradas en '{tabla_principal}': {rutas}")

            # Procesar cada ruta
            for idx, (ruta,) in enumerate(rutas):
                incremento = desplazamiento_ruta.get(ruta, 0)  # Incremento por ruta; 0 si no está definido
                log_message(f"Procesando Ruta='{ruta}' con incremento={incremento}")

                # Actualizar claves relacionadas en las tablas relacionadas
                for tabla_relacionada, campos_relacionados in relaciones.items():
                    # Si hay múltiples campos relacionados, iterar sobre ellos
                    if isinstance(campos_relacionados, list):
                        for campo_relacionado in campos_relacionados:
                            log_message(f"Actualizando relaciones en la tabla '{tabla_relacionada}' para el campo '{campo_relacionado}'...")
                            update_related_query = f"""
                            UPDATE {tabla_relacionada}
                            SET {campo_relacionado} = {campo_relacionado} + ?
                            WHERE {campo_relacionado} IS NOT NULL
                            AND Ruta = ?
                            """
                            cursor.execute(update_related_query, (incremento, ruta))
                            conn.commit()
                            log_message(f"Registros actualizados en '{tabla_relacionada}' para el campo '{campo_relacionado}' con incremento={incremento}")
                    else:
                        # Caso normal si no es una lista
                        campo_relacionado = campos_relacionados
                        log_message(f"Actualizando relaciones en la tabla '{tabla_relacionada}' para el campo '{campo_relacionado}'...")
                        update_related_query = f"""
                        UPDATE {tabla_relacionada}
                        SET {campo_relacionado} = {campo_relacionado} + ?
                        WHERE {campo_relacionado} IS NOT NULL
                        AND Ruta = ?
                        """
                        cursor.execute(update_related_query, (incremento, ruta))
                        conn.commit()
                        log_message(f"Registros actualizados en '{tabla_relacionada}' para el campo '{campo_relacionado}' con incremento={incremento}")

        log_message("=== Actualización de relaciones completada exitosamente ===")

    except sqlite3.Error as e:
        log_message(f"ERROR durante la actualización de relaciones: {e}")
    except Exception as e:
        log_message(f"ERROR inesperado: {e}")
    finally:
        log_message("=== Fin del proceso de actualización de relaciones ===")

def verificar_y_actualizar_campos(cursor, conn, config_geom):
    """
    Verifica y actualiza las tablas en el GeoPackage para asegurarse de que:
    - Si no tienen registros, se ignoran.
    - Si tienen registros:
      - Se verifica si tienen el campo T_Id, y si no, se crea.
      - Se verifica si tienen el campo fid, y se asignan los valores de fid al campo T_Id.

    Args:
        cursor: Cursor activo de la conexión SQLite.
        conn: Conexión activa a la base de datos SQLite.
        config_geom (dict): Configuración de las tablas y relaciones.
    """
    log_message("=== Inicio de verificación y actualización de campos ===")
    for tabla, detalles in config_geom.items():
        try:
            log_message(f"Procesando tabla: {tabla}")

            # Verificar si la tabla tiene registros
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            record_count = cursor.fetchone()[0]
            if record_count == 0:
                log_message(f"La tabla '{tabla}' no tiene registros. Se omite.")
                continue

            # Verificar si el campo T_Id existe
            cursor.execute(f"PRAGMA table_info({tabla})")
            columns = [row[1] for row in cursor.fetchall()]
            if "T_Id" not in columns:
                # Crear el campo T_Id si no existe
                cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN T_Id INTEGER")
                conn.commit()
                log_message(f"Campo 'T_Id' creado en la tabla '{tabla}'.")

            # Verificar si el campo fid existe
            if "fid" in columns:
                # Actualizar el campo T_Id con los valores de fid
                cursor.execute(f"UPDATE {tabla} SET T_Id = fid")
                conn.commit()
                log_message(f"Campo 'T_Id' actualizado con valores de 'fid' en la tabla '{tabla}'.")
            else:
                log_message(f"Advertencia: La tabla '{tabla}' no tiene el campo 'fid'. No se pudo actualizar 'T_Id'.")
        except sqlite3.Error as e:
            log_message(f"ERROR al procesar la tabla '{tabla}': {e}")
    
    log_message("=== Fin de verificación y actualización de campos ===")




# Ejecución principal
if __name__ == "__main__":
    #PARTE DE AVERIGUAR MAXIMO
    resultados = verificar_maximos(cursor, config_geom)

    if resultados:
        log_message("Resultados:")
        log_message(f"Máximos por tabla: {resultados['maximos_por_tabla']}")
        log_message(f"Máximo total: {resultados['max_total']}")
        log_message(f"Milésima superior: {resultados['max_milesima']}")
    else:
        log_message("Ocurrió un error durante la verificación.")
    
    #CARGAR JSON CON AUMENTOS
    log_message("IMPRIMIR DICCIONARIO JSON DE DESPLAZAMIENTOS POR RUTA: ")
    desplazamiento_ruta = cargar_desplazamientos('desplazamientos.json')
    # CARGAR INCREMENTOS POR RUTA
    for ruta_gpkg, desplazamiento in desplazamiento_ruta.items():
        log_message(f"PARA LA RUTA DE .GPKG {ruta_gpkg} TENEMOS UN DESPLAZAMIENTO DE: {desplazamiento}")

        
        
    #PARTE GEOGRAFICA

    log_message("##### INICIANDO SUMA DE VALORES EN PK Y FK PARA LAS TABLAS GEOGRAFICAS#######")    
    actualizar_por_ruta(cursor, conn, config_geom, desplazamiento_ruta)
    log_message("##### INICIANDO ACTUALIZACION DE LLAVES FORANEAS EN LAS TABLAS ALFANUMERUCAS#######")
    map_tables(cursor, config_geom)
    actualizar_relaciones(cursor, conn, config_tablas, desplazamiento_ruta)

#   CREA ATRIBUTO T_ID Y LO IGUALA CON fid.
    verificar_y_actualizar_campos(cursor, conn, config_geom)

    cursor.close()
    conn.close()
    log_message("Proceso finalizado.")