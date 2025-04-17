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
    def __init__(self, nom, email, contrasenya, nivell="Principiante"):
        self.nom = nom
        self.email = email
        self.contrasenya = contrasenya
        self.nivell = nivell

    def encriptar_contrasenya(self):
        return bcrypt.hashpw(self.contrasenya.encode('utf-8'), bcrypt.gensalt())

    def guardar(self):
        conn = connect_db()
        cursor = conn.cursor()

        if self.nivell not in ["Principiante", "Intermedio", "Avanzado"]:
            self.nivell = "Principiante"

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
# Clase Entrenament y subclases
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
        cursor.execute("SELECT id, nom FROM usuaris")  # Obtiene los nombres y IDs de los usuarios
        usuaris = cursor.fetchall()

        # Obtener los ejercicios de la base de datos
        cursor.execute("SELECT id, nom, tipus, unitat FROM exercicis")  # Obtiene los ejercicios
        exercicis = cursor.fetchall()

        cursor.close()
        conn.close()

        # Pasar los datos a la plantilla
        return render_template("crear_rutina.html", usuaris=usuaris, exercicis=exercicis)

    elif request.method == "POST":
        usuari_id = request.form['usuari']
        exercici_id = request.form['exercici']
        series = int(request.form['series'])
        repeticions = int(request.form['repeticions'])

        # Guardar la rutina en la base de datos
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO rutines (usuari_id, exercici_id, series, repeticions) VALUES (%s, %s, %s, %s)",
            (usuari_id, exercici_id, series, repeticions)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Redirigir a la página de inicio o a donde desees
        return redirect(url_for("index"))


# --------------------------
# Rutas adicionales
# --------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom = request.form["nom"]
        email = request.form["email"]
        contrasenya = request.form["contrasenya"]
        nivell = request.form["nivell"]

        usuari = Usuari(nom, email, contrasenya, nivell)
        if usuari.guardar():
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="Error al registrar el usuario.")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        contrasenya = request.form["contrasenya"]

        if Usuari.verificar(email, contrasenya):
            session["user_id"] = Usuari.obtenir_id(email)
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Credenciales incorrectas.")
    return render_template("login.html")

@app.route("/entrenament", methods=["POST"])
def entrenament():
    usuari = request.form['usuari']
    tipus = request.form['tipus']
    valor = float(request.form['valor'])
    data = datetime.now().strftime("%Y-%m-%d")

    if tipus == "Cardio":
        entrenament = Cardio(usuari, data, valor)
    elif tipus == "Força":
        repeticions = int(request.form['repeticions'])
        entrenament = Forca(usuari, data, valor, repeticions)
    else:
        return redirect(url_for("home"))

    guardar_entrenament(entrenament)
    return redirect(url_for("home"))

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
