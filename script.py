import subprocess

def ejecutar_sql():
    try:
        # Ejecutar el archivo SQL desde Python
        subprocess.run(['mysql', '-u', 'root', '-p', 'mariadb', '<', 'mariadb.sql'], check=True)
        print("Base de datos y tablas configuradas correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Hubo un error ejecutando el script SQL: {e}")

# Llamar a la función para ejecutar el script
ejecutar_sql()
