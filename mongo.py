from pymongo import MongoClient
from datetime import datetime

# Connexió a MongoDB (modifica la URI segons el teu entorn)
client = MongoClient("mongodb+srv://sabinaandreeacraciun:sabina1234@sabinadb.fsxnd.mongodb.net/")
db = client["entrenament_db"]
col_progressos = db["progressos"]

def afegir_progres(usuari_id, exercici, valor):
    data_actual = datetime.now().strftime("%Y-%m-%d")

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

# Exemple d’ús
if __name__ == "__main__":
    afegir_progres(usuari_id=2, exercici="Press banca", valor=60)
