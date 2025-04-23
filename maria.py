import mariadb
import bcrypt
import sys

# Función para conectar a la base de datos MariaDB
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
            (usuari_id, exercici_id, series, repeticions)
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

# Obtener todos los ejercicios
def get_all_exercises():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, nom FROM exercicis")
        exercises = cursor.fetchall()
        return exercises
    except mariadb.Error as e:
        print(f"❌ Error al obtener los ejercicios: {e}")
        return []
    finally:
        cursor.close()
        conn.close()