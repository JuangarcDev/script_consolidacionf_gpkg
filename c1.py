import geopandas as gpd
import sqlite3

# Definir las tablas a migrar
tablas_a_migrar = ["usuario", "predio", "terreno"]

# Ruta de los archivos GeoPackage
geopackage_1 = "path/to/geopackage_1.gpkg"
geopackage_2 = "path/to/geopackage_2.gpkg"
geopackage_destino = "path/to/geopackage_destino.gpkg"

# Verificar la existencia de tablas antes de proceder a migrarlas
def verificar_tabla_existe(geopackage, tabla):
    with sqlite3.connect(geopackage) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabla,))
        return cursor.fetchone() is not None

# Llamar a la función de verificación
if verificar_tabla_existe(geopackage_1, "usuario"):
    usuarios_1 = gpd.read_file(geopackage_1, layer="usuario")


# Función para obtener el máximo `t_id` de una tabla
def obtener_max_id(geopackage, tabla):
    with sqlite3.connect(geopackage) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT MAX(t_id) FROM {tabla}")
        max_id = cursor.fetchone()[0]
    return max_id if max_id else 0

# Determinar el desplazamiento (offset)
max_usuario_id = obtener_max_id(geopackage_1, "usuario")
max_predio_id = obtener_max_id(geopackage_1, "predio")

# Leer las capas y tablas de los GeoPackages
usuarios_1 = gpd.read_file(geopackage_1, layer="usuario") if "usuario" in tablas_a_migrar else None
usuarios_2 = gpd.read_file(geopackage_2, layer="usuario") if "usuario" in tablas_a_migrar else None
predios_1 = gpd.read_file(geopackage_1, layer="predio") if "predio" in tablas_a_migrar else None
predios_2 = gpd.read_file(geopackage_2, layer="predio") if "predio" in tablas_a_migrar else None
terrenos_1 = gpd.read_file(geopackage_1, layer="terreno") if "terreno" in tablas_a_migrar else None
terrenos_2 = gpd.read_file(geopackage_2, layer="terreno") if "terreno" in tablas_a_migrar else None

# Ajustar `t_id` en el segundo GeoPackage si las tablas existen
if usuarios_2 is not None:
    offset_usuario = max_usuario_id + 1
    usuarios_2["t_id"] += offset_usuario
    predios_2["t_id_usuario"] += offset_usuario

if predios_2 is not None:
    offset_predio = max_predio_id + 1
    predios_2["t_id"] += offset_predio
    terrenos_2["t_id_predio"] += offset_predio

# Guardar las capas y tablas en el nuevo GeoPackage destino
if usuarios_1 is not None:
    usuarios_1.to_file(geopackage_destino, layer="usuario", driver="GPKG")
    usuarios_2.to_file(geopackage_destino, layer="usuario", driver="GPKG", mode="a")

if predios_1 is not None:
    predios_1.to_file(geopackage_destino, layer="predio", driver="GPKG")
    predios_2.to_file(geopackage_destino, layer="predio", driver="GPKG", mode="a")

if terrenos_1 is not None:
    terrenos_1.to_file(geopackage_destino, layer="terreno", driver="GPKG")
    terrenos_2.to_file(geopackage_destino, layer="terreno", driver="GPKG", mode="a")
