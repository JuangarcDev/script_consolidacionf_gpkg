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

# Inicialización de variables
capas_geograficas = ["cca_unidadconstruccion"]  # Capas iniciales
relaciones = {"cca_adjunto": "cca_unidadconstruccion_adjunto"}  # Relación entre tablas

# Paso 0: Iterar sobre las capas geográficas
for capa in capas_geograficas:
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
            log_message(f"Total de registros para la ruta {ruta}: {len(registros_ruta)}")
            for registro in registros_ruta:
                log_message(str(registro))
        except sqlite3.Error as e:
            log_message(f"ERROR al seleccionar registros de la ruta {ruta} en {capa}: {e}")
            continue

        # Paso 4: Mapear fid y T_Id_Cop
        mapeo_fid_tid = {
            registro["fid"]: (registro["T_Id_Cop"], registro["Ruta"])
            for registro in registros_ruta if "fid" in registro and "T_Id_Cop" in registro and "Ruta" in registro
        }

        # Iterar sobre el diccionario para procesar la información
        for fid, (T_Id_Cop, ruta_actual) in mapeo_fid_tid.items():
            log_message(f"fid {fid} tiene un T_Id_Cop de {T_Id_Cop} y pertenece a la ruta {ruta_actual}")

            # Procesar relaciones basadas en T_Id_Cop y Ruta
            try:
                # Paso 5: Seleccionar registros de la tabla relacionada
                cursor.execute(
                    f"SELECT * FROM {tabla_relacion} WHERE {atributo_union} = ? AND Ruta = ?",
                    (T_Id_Cop, ruta_actual),
                )
                resultados_relacion = cursor.fetchall()
                log_message(f"Registros seleccionados de {tabla_relacion} para T_Id_Cop {T_Id_Cop} y Ruta {ruta_actual}: {resultados_relacion}")

                # Paso 6: Actualizar valores en la tabla de relación
                for resultado in resultados_relacion:
                    # Obtener el fid correspondiente al T_Id_Cop
                    fid_asociado = [k for k, (tid, ruta) in mapeo_fid_tid.items() if tid == T_Id_Cop and ruta == ruta_actual][0]

                    cursor.execute(
                        f"UPDATE {tabla_relacion} SET {atributo_union} = ? WHERE {atributo_union} = ? AND Ruta = ?",
                        (fid_asociado, T_Id_Cop, ruta_actual),
                    )
                    log_message(f"Actualización realizada en {tabla_relacion}: {atributo_union} actualizado a {fid_asociado}")
                
                # Confirmar cambios
                conn.commit()
            except sqlite3.Error as e:
                log_message(f"ERROR al procesar relación con {tabla_relacion}: {e}")
                continue

# Limpieza del mapeo después de procesar cada ruta
mapeo_fid_tid.clear()
log_message("Mapeo de fid y T_Id_Cop limpiado.")







