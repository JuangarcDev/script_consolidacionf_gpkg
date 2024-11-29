import sqlite3
import os

# Ruta al GeoPackage y al archivo de log
gpkg_path = r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_combinado\captura_campo_20240920.gpkg"
log_path = r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_combinado\console_log_val_geo.txt"

# Función para registrar logs
def log_message(message):
    print(message)
    with open(log_path, "a") as log_file:
        log_file.write(message + "\n")

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

def update_related_tables(cursor, conn, config_geom):
    """
    Actualiza los campos relacionados en las tablas según la configuración especificada.
    
    Args:
        cursor: Cursor activo de la conexión SQLite.
        conn: Conexión activa a la base de datos SQLite.
        config_geom (dict): Configuración de las tablas y relaciones.
    """
    log_message("=== Inicio de actualizaciones ===")
    try:
        for table, details in config_geom.items():
            pk_field = details["pk"]
            relaciones = details["relaciones"]

            # Si no hay relaciones o es None, omitir esta tabla
            if not relaciones or not isinstance(relaciones, dict):
                log_message(f"La tabla '{table}' no tiene relaciones definidas. Se omite la actualización DE SUS LLAVES FORANEAS.")
                continue

            # Verificar si la tabla principal tiene registros
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            table_count = cursor.fetchone()[0]
            if table_count == 0:
                log_message(f"La tabla principal '{table}' no tiene registros. Se omite la actualización.")
                continue

            for related_table, related_field in relaciones.items():
                log_message(f"Actualizando {related_table} basado en {table}...")

                # Obtener registros relacionados
                select_query = f"""
                SELECT {related_table}.{related_field}, {related_table}.Ruta
                FROM {related_table}
                INNER JOIN {table}
                ON {table}.T_Id_Cop = {related_table}.{related_field}
                AND {table}.Ruta = {related_table}.Ruta
                WHERE {related_table}.{related_field} IS NOT NULL
                """
                cursor.execute(select_query)
                registros = cursor.fetchall()

                if not registros:
                    log_message(f"No se encontraron registros para actualizar en {related_table} basado en {table}.")
                    continue

                log_message(f"Se encontraron {len(registros)} registros para actualizar en {related_table}.")


                # Realizar el UPDATE con filtro de valores no nulos
                try:
                    # Procesar cada registro
                    for registro in registros:
                        valor_actual = registro[0]
                        ruta_actual = registro[1]

                        # Obtener el nuevo valor desde la tabla principal
                        cursor.execute(f"""
                        SELECT {pk_field}
                        FROM {table}
                        WHERE T_Id_Cop = ? AND Ruta = ?;
                        """, (valor_actual, ruta_actual))
                        resultado = cursor.fetchone()

                        if resultado:
                            nuevo_valor = resultado[0]

                            # Actualizar el registro
                            cursor.execute(f"""
                            UPDATE {related_table}
                            SET {related_field} = ?
                            WHERE {related_field} = ?
                            AND Ruta = ?;
                            """, (nuevo_valor, valor_actual, ruta_actual))

                            conn.commit()
                            log_message(f"Actualizado {related_table}: PARA EL CAMPO: {related_field}, VALOR ANTERIOR: {valor_actual} SE ACTUALIZA A: {nuevo_valor} REGISTRO EN LA Ruta={ruta_actual}")
                        else:
                            log_message(f"No se encontró un valor de actualización para {related_field}={valor_actual}, Ruta={ruta_actual}.")
                
                except sqlite3.Error as e:
                    log_message(f"ERROR: No se pudo realizar la actualización en {related_table}. {e}")
                
                # Registrar datos modificados
                log_message(f"Datos modificados de {related_table}:")
                cursor.execute(f"SELECT * FROM {related_table} LIMIT 10")  # Mostrar solo 10 filas como muestra
                modified_data = cursor.fetchall()
                for row in modified_data:
                    log_message(str(row))

        log_message("SE ACTUALIZARON TODAS LAS TABLAS Y SUS LLAVES FORANEAS CON EXITO")

    except Exception as e:
        log_message(f"ERROR: Ocurrió un error durante el proceso de actualización. {e}")
    finally:
        log_message("=== Fin de actualizaciones ===")


# Ejecución principal
if __name__ == "__main__":
    #PARTE GEOGRAFICA
    log_message("##### INICIANDO ACTUALIZACION DE LLAVES FORANEAS EN LAS TABLAS#######")
    map_tables(cursor, config_geom)
    update_related_tables(cursor, conn, config_geom)
    cursor.close()
    conn.close()
    log_message("Proceso finalizado.")
