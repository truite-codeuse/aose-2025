from fastapi import FastAPI

app = FastAPI()

# Données simulées pour les publicités des services
ADVERTISEMENTS = {
    "PRJ14575": {
        "description": "Service de réparation de voitures.",
        "scenarios": ["Réparation moteur", "Changement pneus"]
    },
    "PRJ13775": {
        "description": "Service de réparation d'ordinateurs.",
        "scenarios": ["Réparation écran", "Nettoyage logiciel"]
    }
}

# Endpoint pour récupérer les publicités
@app.get("/advertisements")
async def get_advertisements():
    return ADVERTISEMENTS

# endpoint
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
