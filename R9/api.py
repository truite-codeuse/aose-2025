import requests
import logging
from private_information import RAISON_SERVICE_URL

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


