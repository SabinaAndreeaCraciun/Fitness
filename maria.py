import mariadb
import sys

# Función para conectar a la base de datos MariaDB
def connect_db():
    try:
        conn = mariadb.connect(
            user="root",  # Asegúrate de usar el nombre de usuario correcto
            password="admin1234",  # Asegúrate de usar la contraseña correcta
            host="localhost",
            port=3306,
            database="tutorial"  # Asegúrate de que el nombre de la base de datos sea correcto
        )
        return conn
    except mariadb.Error as e:
        print(f"Error conectando a la base de datos MariaDB: {e}")
        sys.exit(1)
