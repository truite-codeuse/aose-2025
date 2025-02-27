## Argumentation Agent Initialization API
### Author
Role R7: Lynda BENKERROU


## Description

Ce projet fournit une API FastAPI permettant d'initialiser un agent d'argumentation avec des scénarios et des options extraits d'un service `Ai-Raison`. Cette API reçoit un identifiant de projet (`project_id`) et renvoie les scénarios et options associés au projet en question.

L'API expose les points d'entrées suivants :
- **/initialize** : Initialise l'agent en récupérant les scénarios et options associés à un projet donné.
- **/health** : Permet de vérifier si le serveur fonctionne correctement.

## Prérequis

Avant de démarrer, assurez-vous que vous avez les éléments suivants :

- **Python 3.7+**
- **Pip** (gestionnaire de paquets Python)
- Un fichier `config.py` contenant une clé API valide pour l'API `Ai-Raison` (clé sous la forme `api_key = 'votre_clé_api'`).

## Installation

1. Clonez ce repository :
   ```bash
   git clone https://votre-repository-url
   cd role7-argumentation-agent
   ```

2. Créez un environnement virtuel (optionnel mais recommandé) :
   ```bash
   python -m venv venv
   ```

3. Activez l'environnement virtuel :
   - Sous Windows :
     ```bash
     venv\Scripts\activate
     ```
   - Sous MacOS/Linux :
     ```bash
     source venv/bin/activate
     ```

4. Installez les dépendances nécessaires :
   ```bash
   pip install -r requirements.txt
   ```

5. Assurez-vous d'avoir un fichier `config.py` contenant votre clé API, par exemple :
   ```python
   api_key = 'votre_clé_api'
   ```

## Lancer le serveur

Lancez le serveur FastAPI avec Uvicorn :

```bash
uvicorn main:app --reload
```

Cela démarrera l'API sur `http://127.0.0.1:8007`.

## Points d'entrées

### 1. `/initialize` (Méthode POST)

Initialise l'agent en récupérant les scénarios et options associés à un projet donné.

**Exemple de requête :**

```json
POST http://127.0.0.1:8007/initialize
Content-Type: application/json

{
  "project_id": "votre_project_id"
}
```

**Réponse :**

```json
{
  "project_id": "votre_project_id",
  "scenarios": ["Scénario 1", "Scénario 2", "Scénario 3"],
  "options": ["Option 1", "Option 2"]
}
```

### 2. `/health` (Méthode GET)

Vérifie si le serveur est en bonne santé.

**Réponse :**

```json
{
  "status": "OK"
}
```

## Structure du code

Le projet est organisé de la manière suivante :

```
/role7-argumentation-agent
│
├── main.py                 # Le fichier principal avec la définition des endpoints
├── config.py               # Contient la clé API pour accéder à l'API Ai-Raison
├── requirements.txt        # Liste des dépendances Python nécessaires
└── README.md               # Documentation du projet
```

## Fonctionnement

1. **Initialisation de l'agent** :
   L'API reçoit un `project_id` via le point d'entrée `/initialize`. Ce `project_id` est utilisé pour faire une requête à l'API `Ai-Raison` afin de récupérer les scénarios et options associés au projet.

2. **Récupération des scénarios et options** :
   Une fois les données récupérées depuis l'API `Ai-Raison`, elles sont extraites et formatées pour être envoyées dans la réponse sous forme de scénarios (labels) et d'options (identifiants).

3. **Vérification de la santé** :
   Le point d'entrée `/health` permet de vérifier rapidement si le serveur fonctionne correctement.
