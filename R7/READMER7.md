# R7 - Argumentation Agent Initialization API

Cette API permet d'initialiser un agent d'argumentation en récupérant les scénarios et options d'un projet depuis l'API **Ai-Raison**.

## Prérequis

Avant de démarrer l'API, assurez-vous d'avoir les éléments suivants :

- **Python 3.11 ou supérieur** : Assurez-vous d'avoir Python installé sur votre machine.
- **Clé API** pour accéder à l'API **Ai-Raison** : Vous devez disposer d'une clé API valide.

## 🏁 Installation

### Étape 1 : Installer les dépendances

Assurez-vous d'avoir `pip` installé et exécutez la commande suivante pour installer les dépendances nécessaires à l'API.

    ```bash
     pip install fastapi uvicorn requests

### Étape 2 : Créer le fichier config.py
Dans le même dossier que main.py, créez un fichier config.py contenant votre clé API.
