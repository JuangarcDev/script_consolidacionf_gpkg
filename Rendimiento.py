import sqlite3
from pathlib import Path

ruta = input("Ingrese las ruta donde tiene almacenado la lista de geopackages:")

carpeta = Path(ruta)
rutas = []
for archivo in carpeta.iterdir():
    if archivo.is_file():
        # Obtener el nombre y la extensión
        name = archivo.stem  # Nombre del archivo sin extensión
        extension = archivo.suffix  # Extensión del archivo
        completo = ruta + '/' +name + extension
        print(f"Ruta: {completo}")
        rutas.append(completo)


# Iterar sobre cada archivo en la lista de rutas y realizar la consulta en cada GeoPackage
for gpkg_path in rutas:
    
    # Conectar al GeoPackage
    try:
        conn = sqlite3.connect(gpkg_path)
        cursor = conn.cursor()

        # Consulta para obtener el nombre del usuario y contar el número de predios
        conteo_predios = """
        SELECT COALESCE(u.nombre, 'Usuario no registrado'), COUNT(p.T_Id)
        FROM cca_predio p
        LEFT JOIN cca_usuario u ON u.T_Id = p.usuario
        GROUP BY u.nombre
        """

        # Ejecutar la consulta
        cursor.execute(conteo_predios)
        resultados = cursor.fetchall()

        # Imprimir los resultados para el GeoPackage actual
        if resultados:
            print(f"Resultados del GeoPackage '{gpkg_path}':")
            for nombre, num_predios in resultados:
                print(f"Usuario: {nombre}, Número de predios: {num_predios}")
        else:
            print(f"No se obtuvo ningún resultado en el GeoPackage '{gpkg_path}'.")

        # Cerrar la conexión a la base de datos
        conn.close()

    except sqlite3.Error as e:
        print(f"Error al conectar o consultar el GeoPackage '{gpkg_path}': {e}")