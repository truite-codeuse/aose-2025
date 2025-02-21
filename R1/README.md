# R1 LLM Service

This project provides a FastAPI-based API that leverages a Mistral-based Large Language Model (Nous-Hermes-2-Mistral-7B-DPO) for text generation. It supports multi-turn conversations by persisting session history in a PostgreSQL database managed with Docker Compose.

## Features

- **FastAPI Backend:** Provides endpoints for health checking and text generation.
- **LLM Integration:** Uses Hugging Face's Transformers to load and run the Mistral model.
- **Session Management:** Stores conversation history in PostgreSQL using SQLAlchemy.
- **Dockerized Database:** Easily set up and run PostgreSQL with Docker Compose.

## Project Structure

```
my_llm_service/
├── app/
│   └── main.py          # FastAPI application code
├── docker-compose.yml   # Docker Compose configuration for PostgreSQL
├── README.md            # Project documentation (this file)
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (optional)
```

## Setup Instructions

### Prerequisites

- **Python 3.8+**
- **Docker & Docker Compose**  
  [Get Docker](https://docs.docker.com/get-docker/) | [Docker Compose Installation](https://docs.docker.com/compose/install/)

### 1. Clone the Repository

```bash
git clone <repository_url>
cd R1
```

### 2. Create & Activate a Virtual Environment

**On Unix/MacOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)

Create a `.env` file in the project root with the following content:

```dotenv
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
```

*Note:* Adjust the values as necessary.

### 5. Start the PostgreSQL Database with Docker Compose

Ensure Docker is running, then execute:

```bash
docker-compose up -d
```

This command will:
- Download and run the PostgreSQL image.
- Create a database named **db_name** (as specified in the Docker Compose file).
- Expose port `5432` on your host.

### 6. Run the FastAPI Application

Start the API server using Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Your API should now be accessible at [http://0.0.0.0:8000](http://0.0.0.0:8000).

## API Endpoints

### Health Check

- **URL:** `/health`
- **Method:** `GET`
- **Description:** Checks if the service is running.
- **Example:**

  ```bash
  curl http://localhost:8000/health
  ```

  **Response:**

  ```json
  {
    "status": "OK"
  }
  ```

### Generate Text

- **URL:** `/generate`
- **Method:** `POST`
- **Description:** Generates a response from the LLM based on user input.
- **Payload Example:**

  ```json
  {
    "session_id": "example-session",
    "user_message": "Hello, how are you?",
    "max_new_tokens": 200,
    "temperature": 0.7,
    "repetition_penalty": 1.1
  }
  ```

- **Example using curl:**

  ```bash
  curl -X POST "http://localhost:8000/generate" \
       -H "Content-Type: application/json" \
       -d '{
             "session_id": "example-session",
             "user_message": "Hello, how are you?",
             "max_new_tokens": 200,
             "temperature": 0.7,
             "repetition_penalty": 1.1
           }'
  ```

- **Response:**

  ```json
  {
    "response": "Generated response text from the model.",
    "session_id": "example-session"
  }
  ```
