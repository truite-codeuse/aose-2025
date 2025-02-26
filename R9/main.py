from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import requests

app = FastAPI()

# Modèle Pydantic pour la structure des données reçues
class UserRequest(BaseModel):
    user_prompt: str

# Fonction pour récupérer les publicités des agents d'argumentation (R8)
def fetch_advertisements():
    try:
        response = requests.get("http://127.0.0.1:8004/advertisements")
        if response.status_code == 200:
            return response.json()  # Retourne les publicités sous forme de dictionnaire
        else:
            print(f"Erreur lors de la récupération des publicités : {response.status_code}")
            return {}
    except Exception as e:
        print(f"Exception lors de la récupération des publicités : {e}")
        return {}

# Endpoint pour faire correspondre les demandes de l'utilisateur avec les services disponibles
@app.post("/matchmaking")
async def matchmaking(request: UserRequest):
    try:
        user_prompt = request.user_prompt

        # Étape 1 : Récupérer les publicités des agents d'argumentation (R8)
        print("Récupération des publicités des agents d'argumentation...")
        SERVICE_REPOSITORY = fetch_advertisements()
        if not SERVICE_REPOSITORY:
            return {"status": "Aucune publicité disponible."}

        # Étape 2 : Faire correspondre la demande de l'utilisateur avec les services disponibles
        print("Recherche de services correspondants...")
        matched_services = {}
        for project_id, service_info in SERVICE_REPOSITORY.items():
            # Simuler un score de similarité (à remplacer par un vrai algorithme de matching)
            similarity_score = 0.5  # Exemple de score
            if similarity_score > 0.2:  # Seuil de similarité
                matched_services[project_id] = {
                    "description": service_info["description"],
                    "scenarios": service_info["scenarios"],
                    "similarity_score": similarity_score
                }

        if not matched_services:
            return {"status": "Aucun service correspondant trouvé."}

        # Étape 3 : Proposer les services pertinents à l'utilisateur
        print("Proposer les services pertinents...")
        return {
            "status": "success",
            "matched_services": matched_services
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du matchmaking : {str(e)}")

# Point d'entrée pour exécuter l'API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
