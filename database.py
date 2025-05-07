import mariadb
import bcrypt
import sys

DATABASE_NAME = "mariadb"

def conectar_server():
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

def conectar_db():
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

def crear_base_de_dades_si_no_existeix():
    conn = conectar_server()
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

def crear_taules_si_no_existeixen():
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        print("Creando tablas...")

        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS exercicis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                estimul VARCHAR(255) NULL,
                nom VARCHAR(255) NOT NULL,
                tipus ENUM('Cardio', 'Força'), 
                unitat VARCHAR(100)
            )
        """)
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS usuaris (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                contrasenya VARCHAR(255) NOT NULL,
                nivell  ENUM('Principiant', 'Intermedi', 'Avançat')
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
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

crear_base_de_dades_si_no_existeix()
crear_taules_si_no_existeixen()

def registrar_usuari(nom, email, contrasenya, nivell="Principiant"):
    conn = conectar_db()
    cursor = conn.cursor()

    if nivell not in ["Principiant", "Intermedi", "Avançat"]:
        print(f"❌ Nivel '{nivell}' no válido. Asignando 'Principiant'.")
        nivell = "Principiant"

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

