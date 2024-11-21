import sqlite3
import os

# Rutas de los archivos .gpkg a evaluar
gpkg_files = [
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0001\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0002\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0003\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0004\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0005\MN_00000005_20241011_OK\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0006\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0007\MN_00000007_20241015_31\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0008\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0009\MN_00000009_20240923-vf\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0010\MN_00000010_20241105\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0011\MN_00000011_NITOLA\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0012\MN_00000012_20240926\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0013\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0014\MN_00000014_20241025\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0015_1\MN_00000015_20241010\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0015_2\MN_00000015_20241105\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0016\MN_00000016_20240923\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0017\00000017-01\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0018\MN_00000018_20240923\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0019\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0020\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0021\captura_campo_20241008.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0022\MN_00000022_20240926\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0023\Captura actualizada\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0024\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0025\MN_00000025_20240926\captura_campo_20240920.gpkg",
    r"C:\ACC\CONSOLIDACION_MANZANAS\20241118_CONSOLIDACION\0026\captura_campo_20241008.gpkg"
]

# Tablas a buscar
tablas_a_buscar = ["col_miembros", "cca_novedadfmi"]

# Listas para almacenar rutas según las tablas encontradas y con registros
rutas_tabla1 = []
rutas_tabla2 = []

# Función para verificar tablas y registros
def verificar_tablas_y_registros(ruta_gpkg, tablas):
    try:
        # Conexión a la base de datos .gpkg
        conn = sqlite3.connect(ruta_gpkg)
        cursor = conn.cursor()

        # Verificar cada tabla
        resultados = {}
        for tabla in tablas:
            # Consultar si la tabla existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (tabla,))
            if cursor.fetchone():
                # Verificar si la tabla contiene registros
                cursor.execute(f"SELECT COUNT(*) FROM {tabla};")
                count = cursor.fetchone()[0]
                resultados[tabla] = count > 0  # True si tiene registros
            else:
                resultados[tabla] = False

        # Cerrar conexión
        conn.close()
        return resultados

    except sqlite3.Error as e:
        print(f"Error al procesar {ruta_gpkg}: {e}")
        return {tabla: False for tabla in tablas}

# Procesar cada archivo .gpkg
for ruta in gpkg_files:
    if not os.path.exists(ruta):
        print(f"El archivo no existe: {ruta}")
        continue

    resultados = verificar_tablas_y_registros(ruta, tablas_a_buscar)

    # Agregar rutas según resultados
    if resultados["col_miembros"]:
        rutas_tabla1.append(ruta)
    if resultados["cca_novedadfmi"]:
        rutas_tabla2.append(ruta)

# Imprimir resultados
print("\nLISTA DE .GPKGS QUE LA TABLA 'col_miembros' EXISTE Y CONTIENE REGISTROS:")
print(", ".join(rutas_tabla1))

print("\nLISTA DE .GPKGS QUE LA TABLA 'cca_novedadfmi' EXISTE Y CONTIENE REGISTROS:")
print(", ".join(rutas_tabla2))
