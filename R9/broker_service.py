from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import logging
from api import fetch_advertisements, send_to_nassim
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Modèle Pydantic pour la structure des données reçues
class UserRequest(BaseModel):
    user_prompt: str

# Seuil de similarité configurable
SIMILARITY_THRESHOLD = 0.3  # Ajuste ce seuil selon tes besoins

# Fonction pour calculer la similarité cosinus
def calculate_similarity(user_prompt: str, service_description: str) -> float:
    """
    Calcule la similarité cosinus entre la demande de l'utilisateur et la description du service.
    """
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([user_prompt, service_description])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]

# Endpoint pour faire correspondre les demandes de l'utilisateur avec les services disponibles
@app.post("/matchmaking")
async def matchmaking(request: UserRequest):
    try:
        user_prompt = request.user_prompt

        # Étape 1 : Récupérer les publicités des agents d'argumentation (R8)
        logger.info("Récupération des publicités des agents d'argumentation...")
        SERVICE_REPOSITORY = fetch_advertisements()
        if not SERVICE_REPOSITORY:
            return {"status": "Aucune publicité disponible."}

        # Étape 2 : Faire correspondre la demande de l'utilisateur avec les services disponibles
        logger.info("Recherche de services correspondants...")
        matched_services = {}
        for project_id, service_info in SERVICE_REPOSITORY.items():
            # Calculer le score de similarité
            similarity_score = calculate_similarity(user_prompt, service_info["description"])
            if similarity_score > SIMILARITY_THRESHOLD:  # Seuil de similarité
                matched_services[project_id] = {
                    "description": service_info["description"],
                    "scenarios": service_info["scenarios"],
                    "similarity_score": similarity_score
                }

        if not matched_services:
            return {"status": "Aucun service correspondant trouvé."}

        # Étape 3 : Proposer les services pertinents à l'utilisateur
        logger.info("Proposer les services pertinents...")
        return {
            "status": "success",
            "matched_services": matched_services
        }
    except Exception as e:
        logger.error(f"Erreur lors du matchmaking : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du matchmaking : {str(e)}")

# Point d'entrée pour exécuter l'API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
