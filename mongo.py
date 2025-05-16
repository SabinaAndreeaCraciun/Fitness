from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# Connexió a MongoDB (modifica la URI segons el teu entorn)
client = MongoClient("mongodb://localhost:27017/")
db = client["entrenament_db"]
col_progressos = db["progressos"]
col_comentaris = db["comentaris"]
col_estadistiques = db["estadistiques"]

def afegir_progres(usuari_id, exercici, series, repeticions):
    data_actual = datetime.now().strftime("%Y-%m-%d")

    if not exercici or series is None or repeticions is None:
        print("Error: 'exercici', 'series' i 'repeticions' no poden ser buits.")
        return

    valor_text = f"{series} sèries x {repeticions} repeticions"

    nou_progres = {
        "exercici": exercici,
        "data": data_actual,
        "valor": valor_text
    }

    usuari = col_progressos.find_one({"usuari_id": usuari_id})

    if usuari:
        col_progressos.update_one(
            {"usuari_id": usuari_id},
            {"$push": {"progressos": nou_progres}}
        )
    else:
        nou_document = {
            "usuari_id": usuari_id,
            "progressos": [nou_progres]
        }
        col_progressos.insert_one(nou_document)

    print(f"Progrés afegit per a l'usuari {usuari_id}")
    
def afegir_comentari(usuari_id, comentari, ejercicio_id=None):
    data_actual = datetime.now().strftime("%Y-%m-%d")

    if not comentari:
        print("Error: El comentari no pot estar buit.")
        return

    nou_comentari = {
        "data": data_actual,
        "comentari": comentari
    }
    if ejercicio_id:
        nou_comentari["ejercicio_id"] = ejercicio_id  # Guardamos el ID del ejercicio relacionado

    usuari = col_comentaris.find_one({"usuari_id": usuari_id})

    if usuari:
        col_comentaris.update_one(
            {"usuari_id": usuari_id},
            {"$push": {"notes": nou_comentari}}
        )
    else:
        nou_document = {
            "usuari_id": usuari_id,
            "notes": [nou_comentari]
        }
        col_comentaris.insert_one(nou_document)

    print(f"Comentari afegit per a l'usuari {usuari_id}")

def convertir_objectid_a_str(comentaris):
    for comentari in comentaris:
        for key, valor in comentari.items():
            if isinstance(valor, ObjectId):
                comentari[key] = str(valor)
    return comentaris

def obtenir_comentaris(usuari_id):
    usuari = col_comentaris.find_one({"usuari_id": usuari_id})
    notes = usuari.get("notes", []) if usuari else []
    notes = convertir_objectid_a_str(notes)
    return notes

def guardar_estadistiques(usuari_id, temps_total, calories_totals):
    if temps_total is None or calories_totals is None:
        print("Error: Les estadístiques no poden estar buides.")
        return

    dades = {
        "usuari_id": usuari_id,
        "temps_entrenament_total": temps_total,
        "calories_burned": calories_totals
    }

    col_estadistiques.update_one(
        {"usuari_id": usuari_id},
        {"$set": dades},
        upsert=True
    )

    print(f"Estadístiques guardades per a l'usuari {usuari_id}")

# Exemple d’ús
if __name__ == "__main__":
    afegir_progres(usuari_id=2, exercici="Curl", series=4, repeticions=10)
    afegir_comentari(usuari_id=2, comentari="He augmentat pes en esquats.")
    guardar_estadistiques(usuari_id=2, temps_total=240, calories_totals=15000)
