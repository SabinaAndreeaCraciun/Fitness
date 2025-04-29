import mariadb
import bcrypt
import sys

DATABASE_NAME = "mariadb"

def connect_server():
    try:
        return mariadb.connect(
            user="root",
            password="admin1234",
            host="localhost",
            port=3306
        )
    except mariadb.Error as e:
        print(f"❌ Error conectando al servidor MariaDB: {e}")
        sys.exit(1)

def connect_db():
    try:
        return mariadb.connect(
            user="root",
            password="admin1234",
            host="localhost",
            port=3306,
            database=DATABASE_NAME
        )
    except mariadb.Error as e:
        print(f"❌ Error conectando a la base de datos '{DATABASE_NAME}': {e}")
        sys.exit(1)

def create_database_if_not_exists():
    conn = connect_server()
    cursor = conn.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
        print(f"✅ Verificación completa: base de datos '{DATABASE_NAME}' lista.")
    except mariadb.Error as e:
        print(f"❌ Error al crear la base de datos: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

def create_tables_if_not_exists():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercicis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                estimul VARCHAR(255) NOT NULL DEFAULT 'No especificado',
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

create_database_if_not_exists()
create_tables_if_not_exists()

def register_user(nom, email, contrasenya, nivell="Principiante"):
    conn = connect_db()
    cursor = conn.cursor()

    if nivell not in ["Principiante", "Intermedio", "Avanzado"]:
        print(f"❌ Nivel '{nivell}' no válido. Asignando 'Principiante'.")
        nivell = "Principiante"

    hashed_password = bcrypt.hashpw(contrasenya.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

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

def get_all_users():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, nom, email, nivell FROM usuaris")
        return cursor.fetchall()
    except mariadb.Error as e:
        print(f"❌ Error al obtener los usuarios: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def add_exercise(nom, tipus=None, unitat=None, estimul='No especificado'):
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO exercicis (estimul, nom, tipus, unitat) VALUES (%s, %s, %s, %s)",
            (estimul, nom, tipus, unitat)
        )
        conn.commit()
        print(f"✅ Ejercicio '{nom}' añadido correctamente.")
        return cursor.lastrowid
    except mariadb.Error as e:
        print(f"❌ Error al crear ejercicio: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_exercises():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, estimul, nom, tipus FROM exercicis")
        return cursor.fetchall()
    except mariadb.Error as e:
        print(f"❌ Error al obtener los ejercicios: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

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
        return cursor.fetchall()
    except mariadb.Error as e:
        print(f"❌ Error al obtener las rutinas: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def show_table_structure():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW CREATE TABLE exercicis")
        print(cursor.fetchone()[1])
    except mariadb.Error as e:
        print(f"❌ Error al obtener estructura de tabla: {e}")
    finally:
        cursor.close()
        conn.close()

# Ejemplo de uso:
if __name__ == "__main__":
    # Verificar estructura de la tabla
    show_table_structure()
    
    # Añadir un ejercicio de prueba
    add_exercise("Flexiones", "Fuerza", "Repeticiones", "Pectorales")
    
    # Mostrar todos los ejercicios
    exercises = get_all_exercises()
    print("\nEjercicios en la base de datos:")
    for exercise in exercises:
        print(exercise)