import sqlite3
import os
import codecs

# Ruta al archivo GeoPackage
db_path = r"C:\ACC\CONSOLIDACION_MANZANAS\gpkg_combinado\captura_campo_20240920.gpkg"
log_path_geo = os.path.join(os.path.dirname(db_path), "migracion_log_geom.txt")
epsg = 9377  # EPSG único nacional para Colombia

# Función para escribir mensajes en el archivo de log
def log_message(message):
    with codecs.open(log_path_geo, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

# Función para ejecutar una consulta SQL
def execute_query(conn, query):
    try:
        conn.execute(query)
        conn.commit()
        log_message(f"Consulta ejecutada con éxito: {query}")
    except sqlite3.Error as e:
        log_message(f"Error al ejecutar la consulta: {e}\nConsulta: {query}")

def migrate_table_with_geometry(conn, table_name, new_table_name):
    cursor = conn.cursor()

    # 1. Crear la nueva tabla con la estructura deseada
    log_message(f"Creando la capa geometrica {new_table_name} con geometría EPSG {epsg}...")
    create_table_query = f"""
    CREATE TABLE extdireccion (
    T_Id INTEGER NOT NULL PRIMARY KEY,
    T_Seq INTEGER NULL,
    tipo_direccion INTEGER NOT NULL CONSTRAINT extdireccion_tipo_direccion_fkey REFERENCES extdireccion_tipo_direccion DEFERRABLE INITIALLY DEFERRED,
    es_direccion_principal BOOLEAN NULL,
    localizacion POINT NULL,
    codigo_postal TEXT(255) NULL,
    clase_via_principal INTEGER NULL CONSTRAINT extdireccion_clase_via_principal_fkey REFERENCES extdireccion_clase_via_principal DEFERRABLE INITIALLY DEFERRED,
    valor_via_principal TEXT(100) NULL,
    letra_via_principal TEXT(20) NULL,
    sector_ciudad INTEGER NULL CONSTRAINT extdireccion_sector_ciudad_fkey REFERENCES extdireccion_sector_ciudad DEFERRABLE INITIALLY DEFERRED,
    valor_via_generadora TEXT(100) NULL,
    letra_via_generadora TEXT(20) NULL,
    numero_predio TEXT(20) NULL,
    sector_predio INTEGER NULL CONSTRAINT extdireccion_sector_predio_fkey REFERENCES extdireccion_sector_predio DEFERRABLE INITIALLY DEFERRED,
    complemento TEXT(255) NULL,
    nombre_predio TEXT(255) NULL,
    cca_predio_direccion INTEGER NULL CONSTRAINT extdireccion_cca_predio_direccion_fkey REFERENCES cca_predio DEFERRABLE INITIALLY DEFERRED
);
"""
    execute_query(conn, create_table_query)

    # 2. Agregar la columna de geometría con el SRID correcto
    log_message(f"Agregando columna de geometría con SRID {epsg}...")
    add_geometry_query = f"SELECT AddGeometryColumn('{new_table_name}', 'geom', {epsg}, 'POINT', 'XY');"
    execute_query(conn, add_geometry_query)

