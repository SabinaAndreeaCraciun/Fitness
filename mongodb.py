from pymongo import MongoClient

# Connexió amb MongoDB (per defecte és localhost i port 27017)
client = MongoClient('mongodb://localhost:27017/')

# Seleccionem o creem una base de dades (per exemple, fitness_app)
db = client['fitness_app']

# Seleccionem o creem una col·lecció (per exemple, progressos)
collection = db['progressos']

# Inserir un document (progrés d'entrenament)
document = {
    "usuari": "johndoe",
    "data": "2025-04-18",
    "tipus_entrenament": "Cardio",
    "exercicis": [
        {"nom": "Correr", "sèries": 3, "repeticions": 15},
        {"nom": "Salt de corda", "sèries": 2, "repeticions": 20}
    ],
    "temps_total": 30
}

# Inserim el document a la col·lecció
collection.insert_one(document)

# Recuperar els documents de la col·lecció
progressos = collection.find({"usuari": "johndoe"})

# Mostrar els progressos recuperats
for progrés in progressos:
    print(progrés)
