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

    "cca_terreno": {
        "pk": "fid",
        "relaciones": {}
    },

    "extdireccion": {
        "pk": "fid",
        "relaciones": {}
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





# PARTE 0: CORRREGIR REGISTROS CON RELACIONES ROTAS:
def validate_and_fix_broken_relations(cursor, conn, config_geom):
    """
    Valida y corrige relaciones rotas entre las tablas principales y relacionadas.

    Args:
        cursor: Cursor activo de la conexión SQLite.
        conn: Conexión activa a la base de datos SQLite.
        config_geom (dict): Configuración de las tablas y relaciones.
    """
    log_message("=== Validación y corrección de relaciones rotas ===")
    try:
        for table, details in config_geom.items():
            pk_field = details["pk"]
            relaciones = details["relaciones"]

            if not relaciones:
                log_message(f"La tabla '{table}' no tiene relaciones definidas. Se omite.")
                continue

            for related_table, related_field in relaciones.items():
                log_message(f"Validando relaciones entre {table} y {related_table}...")

                # Logs iniciales para registros válidos
                select_query = f"""
                SELECT COUNT(*)
                FROM {related_table}
                WHERE {related_table}.{related_field} IS NOT NULL
                """
                cursor.execute(select_query)
                initial_count = cursor.fetchone()[0]
                log_message(f"Registros válidos iniciales en {related_table}: {initial_count}")

                # Identificar y actualizar relaciones rotas directamente
                update_query = f"""
                UPDATE {related_table}
                SET {related_field} = NULL
                WHERE {related_field} IS NOT NULL
                AND EXISTS (
                    SELECT 1
                    FROM {table}
                    WHERE {table}.T_Id_Cop = {related_table}.{related_field}
                    AND {table}.Ruta IS NOT NULL
                    AND {table}.Ruta != {related_table}.Ruta
                )
                """
                cursor.execute(update_query)
                conn.commit()

                # Logs después de la actualización
                cursor.execute(f"SELECT COUNT(*) FROM {related_table} WHERE {related_field} IS NOT NULL")
                updated_count = cursor.fetchone()[0]
                log_message(f"Registros válidos después de la corrección en {related_table}: {updated_count}")

        log_message("=== Finalizada la validación y corrección de relaciones rotas ===")

    except sqlite3.Error as e:
        log_message(f"ERROR: Ocurrió un error durante la validación y corrección. {e}")



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

def actualizar_por_ruta(cursor, conn, config_geom):
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
            incremento = 1000

            for idx, (ruta,) in enumerate(rutas):
                offset = incremento * (idx + 1)
                log_message(f"Procesando Ruta='{ruta}' con offset={offset}")

                # Actualizar PK en la tabla principal
                update_pk_query = f"""
                UPDATE {table}
                SET {pk_field} = T_Id_Cop + ?
                WHERE Ruta = ?;
                """
                cursor.execute(update_pk_query, (offset, ruta))
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
                        cursor.execute(update_related_query, (offset, ruta))
                        conn.commit()

                        log_message(f"Actualizados registros en {related_table} para Ruta='{ruta}' con offset={offset}")

        log_message("=== Actualización completada exitosamente ===")

    except sqlite3.Error as e:
        log_message(f"ERROR durante la actualización por ruta: {e}")
    except Exception as e:
        log_message(f"ERROR inesperado: {e}")
    finally:
        log_message("=== Fin del proceso de actualización ===")

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
    #PARTE DE AVERIGUAR MAXIMO
    resultados = verificar_maximos(cursor, config_geom)

    if resultados:
        log_message("Resultados:")
        log_message(f"Máximos por tabla: {resultados['maximos_por_tabla']}")
        log_message(f"Máximo total: {resultados['max_total']}")
        log_message(f"Milésima superior: {resultados['max_milesima']}")
    else:
        log_message("Ocurrió un error durante la verificación.")
        
        
    #PARTE GEOGRAFICA

#    log_message("##### INICIANDO VALIDACIÓN Y CORRECCIÓN DE RELACIONES ROTAS #####")
#    validate_and_fix_broken_relations(cursor, conn, config_geom)
    log_message("##### INICIANDO SUMA DE VALORES EN  LLAVES FORANEAS EN LAS TABLAS#######")    
    actualizar_por_ruta(cursor, conn, config_geom)
    log_message("##### INICIANDO ACTUALIZACION DE LLAVES FORANEAS EN LAS TABLAS#######")
    map_tables(cursor, config_geom)
    update_related_tables(cursor, conn, config_geom)
    cursor.close()
    conn.close()
    log_message("Proceso finalizado.")
