import mariadb
import bcrypt
import sys

# Función para conectar a la base de datos MariaDB
def connect_db():
    try:
        conn = mariadb.connect(
            user="root",  # Usuario de MariaDB
            password="admin1234",  # Contraseña
            host="localhost",
            port=3306,
            database="mariadb"  # Asegúrate de que esta es la base de datos correcta
        )
        return conn
    except mariadb.Error as e:
        print(f"Error conectando a la base de datos MariaDB: {e}")
        sys.exit(1)

# Función para registrar un nuevo usuario en la base de datos
def register_user(nom, email, contrasenya, nivell):
    conn = connect_db()
    cursor = conn.cursor()

    # Validar el nivel (nivel por defecto si no es válido)
    if nivell not in ["Principiante", "Intermedio", "Avanzado"]:
        print(f"❌ Nivel '{nivell}' no válido. Asignando 'Principiante' como nivel por defecto.")
        nivell = "Principiante"

    # Encriptar la contraseña usando bcrypt
    hashed_password = bcrypt.hashpw(contrasenya.encode('utf-8'), bcrypt.gensalt())

    try:
        # Insertar el usuario en la tabla 'usuaris', incluyendo el nombre, email, contraseña encriptada y nivel
        cursor.execute("INSERT INTO usuaris (nom, email, password_hash, nivell) VALUES (%s, %s, %s, %s)", 
                       (nom, email, hashed_password, nivell))  # Cambié 'password' por 'password_hash'
        conn.commit()
        print(f"✅ Usuario '{nom}' registrado correctamente con nivel '{nivell}'.")
    except mariadb.Error as e:
        print(f"❌ Error al registrar el usuario: {e}")
        conn.rollback()  # Revertir cambios si hay un error

    cursor.close()
    conn.close()

# Función para verificar la contraseña de un usuario
def verify_password(email, contrasenya):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Consultar el hash de la contraseña almacenada para el correo dado
        cursor.execute("SELECT password_hash FROM usuaris WHERE email = %s", (email,))
        result = cursor.fetchone()

        if result:
            stored_hash = result[0]
            # Comparar el hash de la contraseña ingresada con el almacenado
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
        # Consultar el nivel del usuario para el correo dado
        cursor.execute("SELECT nivell FROM usuaris WHERE email = %s", (email,))
        result = cursor.fetchone()

        if result:
            return result[0]  # Devuelve el nivel del usuario
        else:
            print("⚠️ No se encontró el usuario.")
            return None
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
        # Obtener todos los usuarios de la tabla 'usuaris'
        cursor.execute("SELECT id, nom, email, nivell FROM usuaris")
        users = cursor.fetchall()

        return users
    except mariadb.Error as e:
        print(f"❌ Error al obtener los usuarios: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
