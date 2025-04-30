# mongo.py
from pymongo import MongoClient
from datetime import datetime

# Connexió a MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['fitness_app']

# Funció per guardar el progrés d'un usuari
def guardar_progres(usuari_id, exercici, valor):
    data = datetime.now().strftime("%Y-%m-%d")  # Obtenir la data actual
    document = {
        "usuari_id": usuari_id,
        "progressos": [{"exercici": exercici, "data": data, "valor": valor}]
    }
    # Afegir o actualitzar el document de l'usuari
    db.progressos.update_one({"usuari_id": usuari_id}, {"$push": {"progressos": {"exercici": exercici, "data": data, "valor": valor}}}, upsert=True)

# Funció per recuperar els progressos d'un usuari
def visualitzar_progressos(usuari_id):
    progressos = db.progressos.find_one({"usuari_id": usuari_id})
    if not progressos:
        return "No hi ha progressos registrats."
    
    exercicis = [p['exercici'] for p in progressos['progressos']]
    dates = [p['data'] for p in progressos['progressos']]
    valors = [p['valor'] for p in progressos['progressos']]
    
    return {"exercicis": exercicis, "dates": dates, "valors": valors}

# Funció per afegir comentaris
def afegir_comentari(usuari_id, comentari):
    data = datetime.now().strftime("%Y-%m-%d")
    document = {"data": data, "comentari": comentari}
    db.comentaris.update_one({"usuari_id": usuari_id}, {"$push": {"notes": document}}, upsert=True)
