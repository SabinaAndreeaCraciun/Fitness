from flask import Flask, request, render_template, redirect, url_for, session
from maria import connect_db  # Asegúrate de que este archivo tenga la conexión
import bcrypt
import csv
import matplotlib.pyplot as plt
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecreto123"  # Necesario para usar sesiones

# --------------------------
# Clase Usuari
# --------------------------

class Usuari:
    def __init__(self, nom, email, contrasenya, nivell="Principiant"):
        self.nom = nom
        self.email = email
        self.contrasenya = contrasenya
        self.nivell = nivell

    def encriptar_contrasenya(self):
        return bcrypt.hashpw(self.contrasenya.encode('utf-8'), bcrypt.gensalt())

    def guardar(self):
        conn = connect_db()
        cursor = conn.cursor()

        if self.nivell not in ["Principiant", "Intermedi", "Avançat"]:
            self.nivell = "Principiant"

        hashed = self.encriptar_contrasenya()

        try:
            cursor.execute(
                "INSERT INTO usuaris (nom, email, contrasenya, nivell) VALUES (%s, %s, %s, %s)",
                (self.nom, self.email, hashed, self.nivell)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error guardando el usuario: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def verificar(email, contrasenya_entrada):
        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT contrasenya FROM usuaris WHERE email = %s", (email,))
            resultado = cursor.fetchone()

            if resultado:
                contrasenya_guardada = resultado[0]
                if bcrypt.checkpw(contrasenya_entrada.encode('utf-8'), contrasenya_guardada.encode('utf-8')):
                    return True
            return False
        except Exception as e:
            print(f"❌ Error verificando la contraseña: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtenir_id(email):
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM usuaris WHERE email = %s", (email,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
        except Exception as e:
            print(f"❌ Error obteniendo ID del usuario: {e}")
            return None
        finally:
            cursor.close()
            conn.close()


# --------------------------
# Clases Entrenament y Subclases
# --------------------------

class Entrenament:
    def __init__(self, usuari, tipus, data, valor):
        self.usuari = usuari
        self.tipus = tipus
        self.data = data
        self.valor = valor

    def to_list(self):
        return [self.usuari, self.tipus, self.data, self.valor, ""]

class Cardio(Entrenament):
    def __init__(self, usuari, data, km):
        super().__init__(usuari, "Cardio", data, km)

class Forca(Entrenament):
    def __init__(self, usuari, data, kg, repeticions):
        super().__init__(usuari, "Força", data, kg)
        self.repeticions = repeticions

    def to_list(self):
        return [self.usuari, self.tipus, self.data, self.valor, self.repeticions]


# --------------------------
# Funciones para guardar entrenamientos
# --------------------------

def guardar_entrenament(entrenament):
    try:
        with open("entrenaments.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["usuari", "tipus", "data", "valor", "repeticions"])
            writer.writerow(entrenament.to_list())
    except Exception as e:
        print(f"Error guardando entrenamiento: {e}")

def load_entrenaments():
    entrenaments = []
    try:
        with open("entrenaments.csv", mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                entrenaments.append(row)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error cargando entrenamientos: {e}")
    return entrenaments


# --------------------------
# Funciones para crear rutinas
# --------------------------
@app.route("/crear_rutina", methods=["GET", "POST"])
def crear_rutina():
    if request.method == "GET":
        # Obtener los usuarios de la base de datos
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, nom FROM usuaris")
        usuaris = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("crear_rutina.html", usuaris=usuaris)

    elif request.method == "POST":
        exercici_nombre = request.form['exercici']
        tipus = request.form['tipus']
        estimul = request.form.get('estimul', 'No especificado')
        series = int(request.form['series'])
        repeticions = int(request.form['repeticions'])

    conn = connect_db()
    cursor = conn.cursor()

    # Verificar si el ejercicio ya existe
    cursor.execute("SELECT id FROM exercicis WHERE nom = %s", (exercici_nombre,))
    exercici = cursor.fetchone()

    if not exercici:
        try:
            cursor.execute("INSERT INTO exercicis (nom, tipus, unitat, estimul) VALUES (%s, %s, %s, %s)",
                           (exercici_nombre, tipus, 'reps', estimul))
            conn.commit()
            cursor.execute("SELECT id FROM exercicis WHERE nom = %s", (exercici_nombre,))
            exercici_id = cursor.fetchone()[0]
        except Exception as e:
            print(f"❌ Error creando ejercicio: {e}")
            conn.rollback()
            cursor.close()
            conn.close()
            return redirect(url_for("crear_rutina", error="Error creando el ejercicio"))
    else:
        exercici_id = exercici[0]

    # Insertar en rutines
    usuari_id = session.get("user_id")
    try:
        cursor.execute("INSERT INTO rutines (usuari_id, exercici_id, series, repeticions) VALUES (%s, %s, %s, %s)",
                       (usuari_id, exercici_id, series, repeticions))
        conn.commit()
        return redirect(url_for("rutinas"))
    except Exception as e:
        print(f"❌ Error creando la rutina: {e}")
        conn.rollback()
        return redirect(url_for("crear_rutina", error="Error creando rutina"))
    finally:
        cursor.close()
        conn.close()


@app.route("/rutinas")
def rutinas():
    # Verificar que el usuario esté autenticado
    if 'user_id' not in session:
        return redirect(url_for("login"))

    user_id = session['user_id']
    user_name = session['user_name']  # Obtener el nombre desde la sesión

    # Conectar a la base de datos
    conn = connect_db()
    cursor = conn.cursor()

    # Obtener las rutinas del usuario actual
    cursor.execute("""
    SELECT r.id, e.nom, e.estimul, r.series, r.repeticions 
    FROM rutines r
    JOIN exercicis e ON r.exercici_id = e.id
    WHERE r.usuari_id = %s
""", (user_id,))

    rutinas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("rutinas.html", rutinas=rutinas, user_name=user_name)



# --------------------------
# Rutas adicionales
# --------------------------

@app.route("/")
def index():
    # Si no hay sesión de usuario activa, redirige a login
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Si la sesión está activa, redirige a la página principal
    return render_template("index.html", user_name=session['user_name'])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom = request.form["nom"]
        email = request.form["email"]
        contrasenya = request.form["contrasenya"]
        nivell = request.form["nivell"]
        print(nom, email, contrasenya, nivell)

        usuari = Usuari(nom, email, contrasenya, nivell)
        if usuari.guardar():
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="Error al registrar el usuario.")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nom = request.form["nom"]  # Obtener el nombre del formulario
        contrasenya = request.form["contrasenya"]  # Obtener la contraseña del formulario

        # Verificar si el nombre y la contraseña coinciden en la base de datos
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, contrasenya FROM usuaris WHERE nom = %s", (nom,))
        resultado = cursor.fetchone()
        
        if resultado:
            user_id, contrasenya_guardada = resultado
            if bcrypt.checkpw(contrasenya.encode('utf-8'), contrasenya_guardada.encode('utf-8')):
                # Guardar el ID y nombre del usuario en la sesión
                session["user_id"] = user_id
                session["user_name"] = nom  # Guardar el nombre del usuario en la sesión
                cursor.close()
                conn.close()

                # Redirigir a la página de inicio (index.html) después de iniciar sesión
                return redirect(url_for("index"))  # Redirige al index

            else:
                cursor.close()
                conn.close()
                return render_template("login.html", error="Contraseña incorrecta.")
        else:
            cursor.close()
            conn.close()
            return render_template("login.html", error="Nombre de usuario no encontrado.")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()  # Limpia la sesión
    return redirect(url_for("login"))  # Redirige a la página de inicio

    


@app.route("/progress/<usuari>")
def progress(usuari):
    entrenaments = load_entrenaments()
    user_data = [e for e in entrenaments if e["usuari"] == usuari]

    if not user_data:
        return "No hay datos para este usuario."

    fechas = [e["data"] for e in user_data]
    valores = [float(e["valor"]) for e in user_data]

    plt.figure()
    plt.plot(fechas, valores, marker='o')
    plt.title(f"Progreso de {usuari}")
    plt.xlabel("Fecha")
    plt.ylabel("Valor")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("static/progress.png")

    return render_template("user_progress.html", usuari=usuari, grafico="static/progress.png")


# --------------------------
# Main
# --------------------------

if __name__ == "__main__":
    app.run(debug=True)