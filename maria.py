import mariadb
import bcrypt
import sys

# Primero conectamos sin especificar base de datos para poder crearla
def connect_server():
    try:
        conn = mariadb.connect(
            user="root",
            password="admin1234",
            host="localhost",
            port=3306
        )
        return conn
    except mariadb.Error as e:
        print(f"❌ Error conectando al servidor MariaDB: {e}")
        sys.exit(1)

# Luego conectamos a la base de datos ya creada
def connect_db():
    try:
        conn = mariadb.connect(
            user="root",
            password="admin1234",
            host="localhost",
            port=3306,
            database="mariadb"
        )
        return conn
    except mariadb.Error as e:
        print(f"❌ Error conectando a la base de datos MariaDB: {e}")
        sys.exit(1)

# Crear la base de datos si no existe
def create_database_if_not_exists():
    conn = connect_server()
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS mariadb")
        print("✅ Verificación completa: base de datos 'mariadb' lista.")
    except mariadb.Error as e:
        print(f"❌ Error al crear la base de datos: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

# Crear las tablas si no existen
def create_tables_if_not_exists():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercicis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                tipus VARCHAR(100),
                unitat VARCHAR(100)
               
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuaris (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                contrasenya VARCHAR(255) NOT NULL,
                nivell VARCHAR(50) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rutines (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuari_id INT NOT NULL,
                exercici_id INT NOT NULL,
                series INT NOT NULL,
                repeticions INT NOT NULL,
                FOREIGN KEY (usuari_id) REFERENCES usuaris(id),
                FOREIGN KEY (exercici_id) REFERENCES exercicis(id)
            )
        """)
        conn.commit()
        print("✅ Las tablas fueron creadas o ya existían.")
    except mariadb.Error as e:
        print(f"❌ Error al crear las tablas: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

# Llama a las funciones iniciales al arrancar la aplicación
create_database_if_not_exists()
create_tables_if_not_exists()


# Función para registrar un nuevo usuario
def register_user(nom, email, contrasenya, nivell="Principiante"):
    conn = connect_db()
    cursor = conn.cursor()

    if nivell not in ["Principiante", "Intermedio", "Avanzado"]:
        print(f"❌ Nivel '{nivell}' no válido. Asignando 'Principiante' como nivel por defecto.")
        nivell = "Principiante"

    hashed_password = bcrypt.hashpw(contrasenya.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute(
            "INSERT INTO usuaris (nom, email, contrasenya, nivell) VALUES (%s, %s, %s, %s)", 
            (nom, email, hashed_password, nivell)
        )
        conn.commit()
        print(f"✅ Usuario '{nom}' registrado correctamente con nivel '{nivell}'.")
    except mariadb.Error as e:
        print(f"❌ Error al registrar el usuario: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Función para verificar la contraseña
def verify_password(email, contrasenya):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT contrasenya FROM usuaris WHERE email = %s", (email,))
        result = cursor.fetchone()

        if result:
            stored_hash = result[0]
            if bcrypt.checkpw(contrasenya.encode('utf-8'), stored_hash.encode('utf-8')):
                print("✅ Contraseña verificada correctamente.")
                return True
            else:
                print("❌ Contraseña incorrecta.")
                return False
        else:
            print("⚠️ No se encontró el usuario.")
            return False
    except mariadb.Error as e:
        print(f"❌ Error al verificar la contraseña: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# Función para recuperar el nivel de un usuario
def get_user_level(email):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT nivell FROM usuaris WHERE email = %s", (email,))
        result = cursor.fetchone()
        return result[0] if result else None
    except mariadb.Error as e:
        print(f"❌ Error al recuperar el nivel del usuario: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# Función para obtener todos los usuarios registrados
def get_all_users():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, nom, email, nivell FROM usuaris")
        users = cursor.fetchall()
        return users
    except mariadb.Error as e:
        print(f"❌ Error al obtener los usuarios: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# ---------------------------------
# Funciones relacionadas con rutinas
# ---------------------------------

# Agregar una rutina
def add_routine(usuari_id, exercici_id, series, repeticions):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO rutines (usuari_id, exercici_id, series, repeticions) VALUES (%s, %s, %s, %s)",
            (usuari_id, exercici_id,series, repeticions)
        )
        conn.commit()
        print(f"✅ Rutina agregada para el usuario con ID: {usuari_id}")
    except mariadb.Error as e:
        print(f"❌ Error al agregar la rutina: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Obtener rutinas por usuario
def get_user_routines(usuari_id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(""" 
            SELECT e.nom, r.series, r.repeticions 
            FROM rutines r 
            JOIN exercicis e ON r.exercici_id = e.id 
            WHERE r.usuari_id = %s
        """, (usuari_id,))
        routines = cursor.fetchall()
        return routines
    except mariadb.Error as e:
        print(f"❌ Error al obtener las rutinas: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_all_exercises():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, nom, tipus FROM exercicis")
        exercises = cursor.fetchall()
        return exercises
    except mariadb.Error as e:
        print(f"❌ Error al obtener los ejercicios: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


