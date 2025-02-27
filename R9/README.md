# Broker Agent – Matchmaking Service

## Author

R9- Beddouihech Maram

## Description

This project provides an API built with FastAPI that matches user prompts to available services based on cosine similarity. It utilizes `TF-IDF` (Term Frequency-Inverse Document Frequency) and `cosine similarity` to compare a user's request to the descriptions of available services.

The API exposes a matchmaking endpoint where users can submit a prompt, and the system will return a list of services that match the prompt based on their descriptions.

## Prerequisites

Before starting, make sure you have the following:

- **Python 3.7+**
- **Pip** (Python package manager)

## Installation

1. Clone this repository:
   ```bash
   git clone https://your-repository-url
   cd argumentation-agent-matchmaking
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On MacOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run the server

Start the FastAPI server with Uvicorn:

```bash
uvicorn role9_service:app --reload
```

This will start the API on `http://127.0.0.1:8009`.

## Endpoints

### 1. `/matchmaking` (POST Method)

This endpoint receives a user prompt and returns a list of services that match the prompt based on cosine similarity.

**Example Request:**

```json
POST http://127.0.0.1:8009/matchmaking
Content-Type: application/json

{
  "user_prompt": "Describe the available options for argumentation agents."
}
```

**Response:**

```json
{
  "status": "success",
  "matched_services": {
    "project_id_1": {
      "description": "A detailed description of service 1.",
      "scenarios": ["Scenario 1", "Scenario 2"],
      "similarity_score": 0.75
    },
    "project_id_2": {
      "description": "A detailed description of service 2.",
      "scenarios": ["Scenario 3", "Scenario 4"],
      "similarity_score": 0.68
    }
  }
}
```

If no matching services are found:

```json
{
  "status": "No matching services found."
}
```

### 2. `/health` (GET Method)

Checks if the server is healthy.

**Response:**

```json
{
  "status": "OK"
}
```

## How It Works

### Agent Initialization:

- The API receives a `user_prompt` via the `/matchmaking` endpoint.
- This `user_prompt` is used to match against service descriptions from available services.

### Retrieving Scenarios, Options, and Description:

- Once the data is fetched, it is compared using **TF-IDF vectorization** and **cosine similarity**.
- The response includes:
  - **Description**: The description of the matching service.
  - **Scenarios**: The scenarios related to the service.
  - **Similarity Score**: The cosine similarity score between the user prompt and service description.

### Health Check:

- The `/health` endpoint allows you to quickly check if the server is functioning correctly.




