from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

#  Vérification de la clé API
try:
    from config import api_key
except ImportError:
    raise RuntimeError(" ERREUR : Impossible de charger `config.py`. Vérifie que ce fichier existe et contient ta clé API.")

app = FastAPI(title="Role 7 - Argumentation Agent Initialization")

#  Modèle pour recevoir une requête
class InitRequest(BaseModel):
    project_id: str

#  Modèle de réponse
class InitResponse(BaseModel):
    project_id: str
    scenarios: list[str]
    options: list[str]


@app.on_event("startup")
async def startup_event():
    print(" FastAPI a bien démarré.")

# Route de test principale
@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Role 7"}

# Vérification de santé
@app.get("/health")
def health_check():
    return {"status": "OK"}

# Fonction pour récupérer les données
def fetch_service_metadata(project_id: str):
    """  Récupère les scénarios depuis l’API Ai-Raison """
    url = f"https://api.ai-raison.com/executions/{project_id}/latest"
    headers = {"x-api-key": api_key, "Accept": "application/json"}

    try:
        print(f" [DEBUG] Requête API : {url}")
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 403:
            raise HTTPException(status_code=403, detail=" Accès refusé. Vérifie ta clé API.")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=" Projet introuvable.")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erreur de connexion : {str(e)}")

# Fonction pour extraire les scénarios et options
def extract_scenarios_and_options(metadata):
    """  Extrait les données reçues """
    elements = metadata.get("elements", [])
    options = metadata.get("options", [])

    if not elements:
        raise HTTPException(status_code=400, detail=" Aucun élément trouvé dans la réponse.")

    scenarios = [item.get("label", "Inconnu") for item in elements]
    options_list = [item.get("id", "Aucune option") for item in options]

    return scenarios, options_list

#  Endpoint principal
@app.post("/initialize", response_model=InitResponse)
def initialize_agent(request: InitRequest):
    """  Initialise l'agent et récupère les scénarios """
    metadata = fetch_service_metadata(request.project_id)
    scenarios, options = extract_scenarios_and_options(metadata)

    return {
        "project_id": request.project_id,
        "scenarios": scenarios,
        "options": options
    }

#  Lancement Uvicorn
if __name__ == "__main__":
    import uvicorn
    print(" Démarrage du serveur Uvicorn...")
    uvicorn.run("main:app", host="127.0.0.1", port=8007, reload=True)
