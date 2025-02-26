# Broker Agent – Matchmaking Service

## Author

R9- Beddouihech Maram

## General Description

The Broker Agent – Matchmaking Service is used for routing requests to appropriate argumentation agents based on their advertised capabilities. This microservice employs text analysis techniques to match user inquiries with the most suitable services offered by argumentation agents. It interacts with the rAIson platform to ensure efficient and accurate service matching.

## Installation

### Clone the Repository:

    ```bash
    git clone https://github.com/marambeddouihech/aose-2025.git
    cd R9
    
### Create and activate a virtual environment:
      ```bash
      python -m venv venv
      source venv\Scripts\activate

### Install required dependencies:

    ```bash
    pip install -r requirements.txt

### Run the service:

    uvicorn broker_service:app --host 0.0.0.0 --port 8003 --reload

## Key Features:

### Advertisement Retrieval (R8):

Fetches advertisements from argumentation agents via an API.

Stores advertisements in a repository for comparison with user requests.

### Similarity Calculation:

Uses cosine similarity to calculate the similarity between the user's request and service descriptions.

Configurable similarity threshold to adjust result relevance.

## Project Structure

This section outlines the organization of the project directory, providing a clear view of the file system and their purposes:

R9/ |-- api.py # Handles API communication with external services |-- broker_service.py # Main service file initializing FastAPI and endpoints |-- private_info.py # Contains sensitive API key, not tracked by version control |-- requirements.txt # Lists all dependencies needed to run the project |-- README.md # Provides project overview and setup instructions.


### Detailed File Descriptions

- **`api.py`**: This file is responsible for all backend logic that deals with external API requests. It fetches and processes data required for the matchmaking operations.

- **`broker_service.py`**: The core of the application, this script initializes the FastAPI application, defines API routes, and includes the server's main event loop.

- **`private_info.py`**: Stores configuration details such as API keys and other sensitive information, ensuring they are kept secure and out of version control.

- **`requirements.txt`**: Contains a list of all Python libraries that the project depends on, which can be installed using `pip`.

- **`README.md`**: Serves as the manual for the project, providing a description, installation instructions, usage guide, and additional information necessary for other developers to understand and use the project.



