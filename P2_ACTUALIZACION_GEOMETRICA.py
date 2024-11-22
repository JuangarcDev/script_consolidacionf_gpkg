import sqlite3
import os

# Conexión al archivo GeoPackage
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

    "cca_puntoreferencia": {
        "pk": "fid", 
        "relaciones": {
            "cca_adjunto": "cca_puntoreferencia_adjunto"
            }
    }
}

# Iterar sobre cada capa geográfica en la configuración
for capa, datos in config_geom.items():
    log_message(f"\n### PROCESANDO CAPA: {capa} ###")

    # Paso 1: Seleccionar todos los registros e imprimir (sin geom)
    try:
        cursor.execute(f"SELECT * FROM {capa}")
        columnas = [desc[0] for desc in cursor.description]
        registros = cursor.fetchall()
        registros_sin_geom = [{col: val for col, val in zip(columnas, row) if col != "geom"} for row in registros]
        log_message(f"Total de registros en {capa}: {len(registros_sin_geom)}")
        for registro in registros_sin_geom:
            log_message(str(registro))
    except sqlite3.Error as e:
        log_message(f"ERROR al seleccionar registros de {capa}: {e}")
        continue

    # Paso 2: Extraer rutas presentes en el campo "Ruta"
    try:
        cursor.execute(f"SELECT DISTINCT Ruta FROM {capa}")
        rutas = [row[0] for row in cursor.fetchall()]
        log_message(f"Rutas encontradas en {capa}: {rutas}")
    except sqlite3.Error as e:
        log_message(f"ERROR al extraer rutas de {capa}: {e}")
        continue

    # Iterar sobre cada ruta
    for ruta in rutas:
        log_message(f"\n### PROCESANDO RUTA: {ruta} ###")

        # Paso 3: Seleccionar registros de la ruta
        try:
            cursor.execute(f"SELECT * FROM {capa} WHERE Ruta = ?", (ruta,))
            registros_ruta = [{col: val for col, val in zip(columnas, row) if col != "geom"} for row in cursor.fetchall()]
            log_message(f"Total de registros para TABLA {capa} EN la ruta {ruta}: {len(registros_ruta)}")
            for registro in registros_ruta:
                log_message(str(registro))
        except sqlite3.Error as e:
            log_message(f"ERROR al seleccionar registros de la ruta {ruta} en {capa}: {e}")
            continue

        # Paso 4: Mapear fid y T_Id_Cop
        mapeo_fid_tid = {
            registro[datos["pk"]]: (registro["T_Id_Cop"], registro["Ruta"])
            for registro in registros_ruta if datos["pk"] in registro and "T_Id_Cop" in registro and "Ruta" in registro
        }

        for fid, T_Id_Cop in mapeo_fid_tid.items():
            log_message(f"fid {fid} tiene un T_Id_Cop de {T_Id_Cop} en la tabla {capa} en la ruta {ruta}")

        # Paso 5: Procesar las relaciones
        for tabla_relacion, atributo_union in datos["relaciones"].items():
            log_message(f"Procesando relación: {tabla_relacion} -> {atributo_union}")

            try:
                # Seleccionar registros relacionados en la tabla de relación
                for fid, (T_Id_Cop, ruta_actual) in mapeo_fid_tid.items():
                    cursor.execute(
                        f"SELECT * FROM {tabla_relacion} WHERE {atributo_union} = ? AND Ruta = ?",
                        (T_Id_Cop, ruta_actual),
                    )
                    resultados_relacion = cursor.fetchall()
                    log_message(f"Registros encontrados en {tabla_relacion} para {atributo_union} = {T_Id_Cop} y Ruta = {ruta_actual}: {resultados_relacion}")

                    # Actualizar valores en la tabla de relación
                    for resultado in resultados_relacion:
                        nuevo_valor = fid  # Asignar fid como el nuevo valor del campo de unión
                        cursor.execute(
                            f"UPDATE {tabla_relacion} SET {atributo_union} = ? WHERE {atributo_union} = ? AND Ruta = ?",
                            (nuevo_valor, T_Id_Cop, ruta_actual),
                        )
                        log_message(f"Actualización realizada en {tabla_relacion}: {atributo_union} = {nuevo_valor} para T_Id_Cop {T_Id_Cop} y Ruta {ruta_actual}")
                
                # Confirmar los cambios
                conn.commit()

            except sqlite3.Error as e:
                log_message(f"ERROR al procesar relación con {tabla_relacion}: {e}")
                continue

        # Vaciar mapeos para evitar errores
        mapeo_fid_tid.clear()
        log_message("Mapeo de fid y T_Id_Cop limpiado.")

# Cerrar la conexión
conn.close()
log_message("\nProceso completado. Conexión cerrada.")

