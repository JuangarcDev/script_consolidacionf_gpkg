import re
import sqlite3
import os

# Ruta al archivo GeoPackage
db_path = r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_combinado\captura_campo_20240920.gpkg"
log_path = os.path.join(os.path.dirname(db_path), "migracion_log.txt")

# Función para escribir mensajes en el archivo de log
def log_message(message):
    with open(log_path, "a") as log_file:
        log_file.write(message + "\n")

# Verificar tablas existentes en la base de datos
def log_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    log_message("Tablas en la base de datos:")
    for table in tables:
        log_message(f"- {table[0]}")

# Diccionarios con las estructuras actuales y nuevas
modelo_union = {
    "cca_adjunto": """CREATE TABLE "cca_adjunto" (
        "T_Id" INTEGER,
        "T_Seq" TEXT,
        "archivo" TEXT,
        "observaciones" TEXT,
        "procedencia" TEXT,
        "tipo_archivo" REAL,
        "relacion_soporte" REAL,
        "dependencia_ucons" REAL,
        "ruta_modificada" TEXT,
        "cca_construccion_adjunto" REAL,
        "cca_fuenteadminstrtiva_adjunto" TEXT,
        "cca_interesado_adjunto" TEXT,
        "cca_unidadconstruccion_adjunto" REAL,
        "cca_predio_adjunto" REAL,
        "cca_puntocontrol_adjunto" TEXT,
        "cca_puntolevantamiento_adjunto" TEXT,
        "cca_puntolindero_adjunto" TEXT,
        "cca_puntoreferencia_adjunto" TEXT
    );"""
}

modelo_ideal = {
    "cca_adjunto": """CREATE TABLE "cca_adjunto" (
        "T_Id" INTEGER NOT NULL,
        "T_Seq" INTEGER,
        "archivo" TEXT(255),
        "observaciones" TEXT(255),
        "procedencia" TEXT(255),
        "tipo_archivo" INTEGER,
        "relacion_soporte" INTEGER,
        "dependencia_ucons" INTEGER,
        "ruta_modificada" TEXT(150),
        "cca_construccion_adjunto" INTEGER,
        "cca_fuenteadminstrtiva_adjunto" INTEGER,
        "cca_interesado_adjunto" INTEGER,
        "cca_unidadconstruccion_adjunto" INTEGER,
        "cca_predio_adjunto" INTEGER,
        "cca_puntocontrol_adjunto" INTEGER,
        "cca_puntolevantamiento_adjunto" INTEGER,
        "cca_puntolindero_adjunto" INTEGER,
        "cca_puntoreferencia_adjunto" INTEGER,
        PRIMARY KEY("T_Id")
    );"""
}

# Función para ejecutar una consulta SQL
def execute_query(conn, query):
    try:
        conn.execute(query)
        conn.commit()
        log_message(f"Consulta ejecutada con éxito: {query}")
    except sqlite3.Error as e:
        log_message(f"Error al ejecutar la consulta: {e}")

def check_records(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    log_message(f"La tabla {table_name} contiene {count} registros antes de la migración.")
    return count

# Función para extraer tipos de datos de cada columna en la estructura de la tabla
def extract_column_types(create_table_sql):
    column_types = {}
    matches = re.findall(r'"(\w+)"\s+(\w+)', create_table_sql)
    for column, data_type in matches:
        column_types[column] = data_type
    return column_types

# Función para crear la tabla con la estructura deseada
def create_new_table(conn, table_name, new_structure):
    try:
        execute_query(conn, f"DROP TABLE IF EXISTS {table_name}_old;")
        execute_query(conn, f"ALTER TABLE {table_name} RENAME TO {table_name}_old;")
        execute_query(conn, new_structure)
    except sqlite3.Error as e:
        log_message(f"Error al renombrar o crear la tabla {table_name}: {e}")

# Función para convertir y migrar los datos automáticamente
def convert_and_migrate_data(conn, table_name, column_types):
    cursor = conn.cursor()
    
    # Obtener los datos de la tabla antigua
    cursor.execute(f"SELECT * FROM {table_name}_old;")
    rows = cursor.fetchall()
    if not rows:
        log_message(f"La tabla {table_name}_old está vacía o no se pudo leer correctamente.")
        return

    log_message(f"Tabla {table_name}_old leída con {len(rows)} registros.")
    
    # Mostrar los primeros 10 registros de la tabla antigua
    for i, row in enumerate(rows[:10]):
        log_message(f"Registro antiguo {i + 1}: {row}")
    
    # Obtener las columnas de la nueva tabla
    new_columns = list(column_types.keys())
    
    # Insertar cada registro en la nueva tabla con conversiones automáticas
    for row in rows:
        converted_row = []
        for idx, column in enumerate(new_columns):
            data_type = column_types[column]
            value = row[idx]
            # Verificación de valor None antes de convertir
            if value is None:
                converted_row.append(None)
            elif data_type == "INTEGER":
                try:
                    converted_row.append(int(float(value)))
                except ValueError:
                    log_message(f"Advertencia: valor '{value}' no es convertible a entero en columna {column}.")
                    converted_row.append(None)
            elif data_type == "REAL":
                converted_row.append(float(value) if value is not None else None)
            elif data_type == "TEXT":
                converted_row.append(str(value) if value is not None else None)
            else:
                converted_row.append(None)  # Si el tipo de datos no coincide, se asigna None por defecto
        
        placeholders = ', '.join(['?' for _ in new_columns])
        query = f"INSERT INTO {table_name} ({', '.join(new_columns)}) VALUES ({placeholders})"
        cursor.execute(query, converted_row)
    
    conn.commit()
    
    # Confirmación de registros migrados a la nueva tabla
    cursor.execute(f"SELECT * FROM {table_name};")
    new_rows = cursor.fetchall()
    log_message(f"Tabla {table_name} tiene {len(new_rows)} registros después de la migración.")
    
    # Mostrar los primeros 10 registros migrados a la nueva tabla
    for i, row in enumerate(new_rows[:10]):
        log_message(f"Registro nuevo {i + 1}: {row}")

# Función principal para realizar la migración completa
def migrate_tables(conn, old_structure, new_structure):
    log_tables(conn)  # Verificar y listar tablas existentes antes de la migración
    for table_name, new_schema in new_structure.items():
        log_message(f"Migrando tabla {table_name}...")
        
        # Extraer tipos de datos de la estructura de la tabla nueva
        column_types = extract_column_types(new_schema)
        
        # Crear nueva tabla y renombrar la tabla antigua
        create_new_table(conn, table_name, new_schema)
        
        # Migrar datos con conversiones automáticas
        convert_and_migrate_data(conn, table_name, column_types)
        
        log_message(f"Tabla {table_name} migrada exitosamente.\n")

# Ejecutar el script de migración
with sqlite3.connect(db_path) as conn:
    # Iniciar el archivo de log
    with open(log_path, "w") as f:
        f.write("Inicio de la migración de tablas\n")

    migrate_tables(conn, modelo_union, modelo_ideal)

log_message("Migración completada.")
print("Migración completada.")

