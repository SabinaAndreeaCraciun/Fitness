from pymongo import MongoClient
from datetime import datetime

# Connexió a MongoDB (modifica la URI segons el teu entorn)
client = MongoClient("mongodb+srv://sabinaandreeacraciun:sabina1234@sabinadb.fsxnd.mongodb.net/")
db = client["entrenament_db"]
col_progressos = db["progressos"]
col_comentaris = db["comentaris"]
col_estadistiques = db["estadistiques"]

def afegir_progres(usuari_id, exercici, valor):
    data_actual = datetime.now().strftime("%Y-%m-%d")

    if not exercici or valor is None:
        print("Error: 'exercici' o 'valor' no poden ser buits.")
        return

    nou_progres = {
        "exercici": exercici,
        "data": data_actual,
        "valor": valor
    }

    usuari = col_progressos.find_one({"usuari_id": usuari_id})

    if usuari:
        # Si ja existeix, afegeix el nou progrés
        col_progressos.update_one(
            {"usuari_id": usuari_id},
            {"$push": {"progressos": nou_progres}}
        )
    else:
        # Si no existeix, crea un nou document
        nou_document = {
            "usuari_id": usuari_id,
            "progressos": [nou_progres]
        }
        col_progressos.insert_one(nou_document)

    print(f"Progrés afegit per a l'usuari {usuari_id}")


def afegir_comentari(usuari_id, comentari):
    data_actual = datetime.now().strftime("%Y-%m-%d")

    if not comentari:
        print("Error: El comentari no pot estar buit.")
        return

    nou_comentari = {
        "data": data_actual,
        "comentari": comentari
    }

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

def obtenir_comentaris(usuari_id):
    usuari = col_comentaris.find_one({"usuari_id": usuari_id})
    return usuari.get("notes", []) if usuari else []


  

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
    afegir_progres(usuari_id=2, exercici="Press banca", valor=60)
    afegir_comentari(usuari_id=2, comentari="He augmentat pes en esquats.")
    guardar_estadistiques(usuari_id=2, temps_total=240, calories_totals=15000)
