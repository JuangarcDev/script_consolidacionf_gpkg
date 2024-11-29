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

                # Verificar si hay coincidencias antes del UPDATE
                match_query = f"""
                SELECT COUNT(*)
                FROM {table}
                INNER JOIN {related_table}
                ON {table}.T_Id_Cop = {related_table}.{related_field}
                AND {table}.Ruta = {related_table}.Ruta
                WHERE {related_table}.{related_field} IS NOT NULL
                """
                cursor.execute(match_query)
                matches = cursor.fetchone()[0]
                
                if matches == 0:
                    log_message(f"No se encontraron coincidencias para actualizar {related_table} basado en {table}. Se omite.")
                    continue

                log_message(f"Se encontraron {matches} registros coincidentes para actualizar en {related_table}.")

                # Realizar el UPDATE con filtro de valores no nulos
                try:
                    update_query = f"""
                    UPDATE {related_table}
                    SET {related_field} = (
                        SELECT {pk_field}
                        FROM {table}
                        WHERE {table}.T_Id_Cop = {related_table}.{related_field}
                        AND {table}.Ruta = {related_table}.Ruta
                    )
                    WHERE {related_field} IS NOT NULL
                    AND EXISTS (
                        SELECT 1
                        FROM {table}
                        WHERE {table}.T_Id_Cop = {related_table}.{related_field}
                        AND {table}.Ruta = {related_table}.Ruta
                    )
                    """
                    cursor.execute(update_query)
                    conn.commit()
                    
                    affected_rows = cursor.rowcount
                    log_message(f"Actualización completada para {related_table}. Filas afectadas: {affected_rows}.")
                
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
