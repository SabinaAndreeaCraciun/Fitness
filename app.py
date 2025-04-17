from flask import Flask, request, jsonify, render_template, redirect, url_for
from maria import connect_db  # Importamos la función de conexión desde maria.py
import bcrypt
import csv
import matplotlib.pyplot as plt
from datetime import datetime

app = Flask(__name__)

# Función para guardar los entrenamientos en el archivo CSV
def guardar_entrenament(entrenament):
    try:
        with open("entrenaments.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            # Si el archivo está vacío, escribir encabezado
            if file.tell() == 0:
                writer.writerow(["usuari", "tipus", "data", "valor", "repeticions"])
            writer.writerow(entrenament.to_list())
    except Exception as e:
        print(f"Error guardando entrenamiento: {e}")

# Función para cargar los entrenamientos desde el archivo CSV
def load_entrenaments():
    entrenaments = []
    try:
        with open("entrenaments.csv", mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                entrenaments.append(row)
    except FileNotFoundError:
        print("No se encontró el archivo de entrenamientos, comenzando desde cero.")
    except Exception as e:
        print(f"Error cargando entrenaments: {e}")
    return entrenaments

# Clase base para los entrenamientos
class Entrenament:
    def __init__(self, usuari, tipus, data, valor):
        self.usuari = usuari
        self.tipus = tipus
        self.data = data
        self.valor = valor
    
    def to_list(self):
        return [self.usuari, self.tipus, self.data, self.valor, ""]

# Clase para entrenamientos de tipo Cardio
class Cardio(Entrenament):
    def __init__(self, usuari, data, km):
        super().__init__(usuari, "Cardio", data, km)
    
    def to_list(self):
        return [self.usuari, self.tipus, self.data, self.valor, ""]

# Clase para entrenamientos de tipo Força (Fuerza)
class Forca(Entrenament):
    def __init__(self, usuari, data, kg, repeticions):
        super().__init__(usuari, "Força", data, kg)
        self.repeticions = repeticions
    
    def to_list(self):
        return [self.usuari, self.tipus, self.data, self.valor, self.repeticions]

# Ruta para el registro de usuario
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre_usuario = request.form["nom"]
        email = request.form["email"]
        contrasenya = request.form["contrasenya"]
        nivell = request.form["nivell"]

        # Encriptar la contraseña
        hashed_contrasenya = bcrypt.hashpw(contrasenya.encode('utf-8'), bcrypt.gensalt())

        # Conectar a la base de datos
        conn = connect_db()
        cursor = conn.cursor()

        try:
            # Intentar insertar los datos en la base de datos
            cursor.execute(
                "INSERT INTO usuaris (nom, email, contrasenya, nivell) VALUES (%s, %s, %s, %s)",
                (nombre_usuario, email, hashed_contrasenya, nivell)
            )
            conn.commit()
            return redirect(url_for("login"))  # Redirigir al login después del registro
        except Exception as e:
            print(f"Error al registrar el usuario: {e}")  # Imprimir el error en la consola
            conn.rollback()  # Revertir los cambios si ocurre un error
            return render_template("register.html", error="Hubo un error al registrar el usuario.")  # Mostrar mensaje de error
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")  # Si es una solicitud GET, muestra el formulario de registro


# Ruta de login para verificar el usuario
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre_usuario = request.form["nom"]
        email = request.form["email"]
        contrasenya = request.form["contrasenya"]

        # Conectar a la base de datos
        conn = connect_db()
        cursor = conn.cursor()

        try:
            # Consultar la contraseña en la base de datos
            cursor.execute("SELECT contrasenya FROM usuaris WHERE nom = %s AND email = %s", 
                           (nombre_usuario, email))
            result = cursor.fetchone()

            # Si la contraseña es correcta
            if result and bcrypt.checkpw(contrasenya.encode('utf-8'), result[0].encode('utf-8')):
                return redirect(url_for("index"))  # Redirigir a la página principal (index) si el login es exitoso
            else:
                # Si las credenciales son incorrectas
                return render_template("login.html", error="Nombre de usuario, email o contraseña incorrectos")
        except Exception as e:
            # En caso de error con la base de datos
            return render_template("login.html", error="Hubo un error al intentar iniciar sesión.")
        finally:
            cursor.close()
            conn.close()

    return render_template("login.html")  # Si es una solicitud GET, muestra el formulario de login




# Ruta principal (index) para agregar entrenamientos
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Recoger los datos del formulario
        usuari = request.form['usuari']
        tipus = request.form['tipus']
        valor = float(request.form['valor'])
        data_str = datetime.now().strftime("%Y-%m-%d")
        
        if tipus == "Cardio":
            entrenament = Cardio(usuari, data_str, valor)
        elif tipus == "Força":
            repeticions = int(request.form['repeticions'])
            entrenament = Forca(usuari, data_str, valor, repeticions)
        else:
            return render_template("index.html", error="Tipo de entrenamiento no válido")

        # Guardar el entrenamiento
        guardar_entrenament(entrenament)
        return redirect(url_for('index'))

    return render_template('index.html')

# Ruta para obtener los progresos de un usuario
@app.route("/user_progress", methods=["GET"])
def user_progress():
    usuari = request.args.get("usuari")
    if not usuari:
        return redirect(url_for('index'))
    
    entrenaments = load_entrenaments()
    user_entrenaments = [t for t in entrenaments if t["usuari"] == usuari]
    
    return render_template("user_progress.html", usuari=usuari, entrenaments=user_entrenaments)

# Ruta para generar el gráfico de progreso de un usuario
@app.route("/plot_progress/<usuari>", methods=["GET"])
def plot_progress(usuari):
    entrenaments = load_entrenaments()
    user_entrenaments = [t for t in entrenaments if t["usuari"] == usuari]
    if not user_entrenaments:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    dates = [t["data"] for t in user_entrenaments]
    valors = [float(t["valor"]) for t in user_entrenaments]
    
    plt.figure()
    plt.plot(dates, valors, marker='o')
    plt.xlabel("Fecha")
    plt.ylabel("Progreso")
    plt.title(f"Progreso de {usuari}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("progress.png")
    return jsonify({"message": "Gráfico generado", "file": "progress.png"}), 200

if __name__ == "__main__":
    app.run(debug=True)
