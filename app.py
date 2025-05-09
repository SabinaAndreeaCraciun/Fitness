from flask import Flask, request, render_template, redirect, url_for, session
from database import conectar_db, registrar_usuari, afegir_exercici, afegir_rutina, eliminar_exercici  # Asegúrate de que este archivo tenga la conexión
import bcrypt
import csv
import matplotlib.pyplot as plt

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

    def guardar(self):     
        try: 
            registrar_usuari(self.nom, self.email, self.contrasenya, self.nivell)
            return True
        except Exception as e:
            print(f"❌ Error guardando el usuario: {e}")
            return False

# --------------------------
# Clases Entrenament y Subclases
# --------------------------

class Entrenament:
    def __init__(self, usuari, tipus, data, valor):
        self.usuari = usuari
        self.tipus = tipus
        self.data = data
        self.valor = valor

    def per_llistar(self):
        return [self.usuari, self.tipus, self.data, self.valor, ""]

class Cardio(Entrenament):
    def __init__(self, usuari, data, km):
        super().__init__(usuari, "Cardio", data, km)

class Forca(Entrenament):
    def __init__(self, usuari, data, kg, repeticions):
        super().__init__(usuari, "Força", data, kg)
        self.repeticions = repeticions

    def per_llistar(self):
        return [self.usuari, self.tipus, self.data, self.valor, self.repeticions]


# --------------------------
# Funciones para guardar entrenamientos
# --------------------------
#To do esta funcio no se utilitza (modificar para mongodb o borrar)
def guardar_entrenament(entrenament):
    try:
        with open("entrenaments.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["usuari", "tipus", "data", "valor", "repeticions"])
            writer.writerow(entrenament.to_list())
    except Exception as e:
        print(f"Error guardando entrenamiento: {e}")
        
#Aixo es deberia de carregar desde mongodb no desde un csv (si se utilitza)
def carregar_entrenaments():
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
        return render_template("crear_rutina.html")

    elif request.method == "POST":
        exercici_nombre = request.form['exercici']
        tipus = request.form['tipus']
        estimul = request.form.get('estimul', 'No especificado')
        series = int(request.form['series'])
        repeticions = int(request.form['repeticions'])

    exercici_id = afegir_exercici(exercici_nombre, tipus, estimul)    
    # Insertar en rutines
    usuari_id = session.get("user_id")
    afegir_rutina(usuari_id, exercici_id, series, repeticions)
    return redirect(url_for("rutinas"))

@app.route("/rutinas")
def rutinas():
    # Verificar que el usuario esté autenticado
    if 'user_id' not in session:
        return redirect(url_for("login"))

    user_id = session['user_id']
    user_name = session['user_name']  # Obtener el nombre desde la sesión

    # Conectar a la base de datos
    conn = conectar_db()
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
        conn = conectar_db()
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
    entrenaments = carregar_entrenaments()
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

@app.route('/eliminar_exercici/<int:id>', methods=['DELETE'])
def eliminar_exercici_route(id):
    resultat = eliminar_exercici(id)  # Crida a la funció que elimina l'exercici
    if resultat:
        return f"Exercici {id} eliminat", 200
    else:
        return "Error al eliminar", 500

# --------------------------
# Main
# --------------------------

if __name__ == "__main__":
    app.run(debug=True)