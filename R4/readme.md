## Process User Input
### Author
Role R4: Thanina AIT FERHAT
 

This is a FastAPI application designed to process user input and classify it as either a casual conversation or a service request. The application interacts with two APIs:

### 1. **R1 API**
A language model API that classifies the user's input and generates responses based on the type of interaction.

### 2. **Broker API**
An API that processes decision-making requests from users, helping to make informed decisions based on their input.

The application saves conversation histories in a PostgreSQL database, which can be queried to retrieve the conversation history for a given session.

## Features

- Classifies user input as either a casual conversation or a decision-making request.
- Calls the **R1 API** for natural language generation.
- Interacts with the **Broker API** for decision-making requests.
- Stores conversation history in a PostgreSQL database.
- Exposes an endpoint to process user input and respond accordingly.

## Requirements

- Python 3.7+
- PostgreSQL
- FastAPI
- SQLAlchemy
- Pydantic
- Requests


## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/r4-process-user-input.git
cd r4-process-user-input
```
2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install Dependencies
```bash
pip install -r requirements.txt
```
4. Set Up the Database
Ensure that you have a PostgreSQL instance running. Create a new database and update the DATABASE_URL in the .env file with the appropriate credentials.


# Example DATABASE_URL in .env file
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
```
Run the following command to create the necessary tables in the database:

```bash
python main.py
```
5. Running the Application
To start the FastAPI server, run:

```bash
uvicorn app.main:app --reload
```
The application will be available at http://127.0.0.1:8004.

6. Testing the API
To test the /process_input endpoint, you can send a POST request with the following JSON body:

```bash
{
    "session_id": "session123",
    "user_message": "Can you help me choose a restaurant?"
}
```
Example cURL request:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8004/process_input' \
  -H 'Content-Type: application/json' \
  -d '{
  "session_id": "session123",
  "user_message": "Can you help me choose a restaurant?"
}'
```
7. Response Format
The response will be a JSON object with the following structure:

```bash
{
    "response": "Sure, I can help you with that!",
    "session_id": "session123"
}
```
1. Classify User Input
L'application commence par classer l'entrée de l'utilisateur en utilisant la fonction classify_input. Cette fonction détermine si l'entrée correspond à :

Une conversation informelle (casual).
Une demande de service (decision-making request).
Si l'entrée contient des mots-clés associés à la prise de décision, elle sera classée comme une demande de service. Sinon, elle sera considérée comme une conversation informelle.

2. Casual Conversation
Si l'entrée est classée comme une conversation informelle :

L'application envoie l'entrée à l'API R1, qui génère une réponse appropriée.
Cette interaction est ensuite enregistrée dans la base de données, y compris la réponse générée par l'assistant.
3. Decision Request
Si l'entrée est classée comme une demande de service :

L'application envoie l'entrée à l'API Broker pour traiter la demande.
La réponse générée par l'API Broker est ensuite envoyée à l'API R1, qui transforme cette réponse en langage naturel.
Enfin, la réponse finale est enregistrée dans la base de données, y compris la réponse générée par l'assistant.


