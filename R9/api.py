import requests
import logging
from private_information import RAISON_SERVICE_URL, NASSIM_API_URL

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_advertisements():
    """
    Récupère les publicités des agents d'argumentation (R8) via une API.
    """
    try:
        response = requests.get(f"{RAISON_SERVICE_URL}/advertisements")
        if response.status_code == 200:
            return response.json()  # Retourne les publicités sous forme de dictionnaire
        else:
            logger.error(f"Erreur lors de la récupération des publicités : {response.status_code}")
            return {}
    except Exception as e:
        logger.error(f"Exception lors de la récupération des publicités : {e}")
        return {}

def send_to_nassim(project_id: str, user_input: List[str]) -> bool:
    """
    Envoie les résultats à Nassim via une API HTTP POST.
    """
    try:
        response = requests.post(
            f"{NASSIM_API_URL}/receive_ad",
            json={
                "project_id": project_id,
                "user_input": user_input
            }
        )
        if response.status_code == 200:
            logger.info(f"Résultats envoyés à Nassim pour le projet {project_id}.")
            return True
        else:
            logger.error(f"Erreur lors de l'envoi à Nassim : {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Exception lors de l'envoi à Nassim : {e}")
        return False
