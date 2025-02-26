# R4 - Process User Input

This is a FastAPI application designed to process user input and classify it as either a casual conversation or a service request. The application interacts with two APIs:

1. **R1 API**: A language model API that classifies the user's input and generates responses based on the type of interaction.
2. **Broker API**: An API that processes decision-making requests from users, helping to make informed decisions based on their input.

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
The application will be available at http://127.0.0.1:8000.

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
  'http://127.0.0.1:8000/process_input' \
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
Application Workflow
Classify User Input: The application uses the classify_input function to determine if the input is a casual conversation or a decision-making request. If the input contains keywords associated with decision-making, it will be processed as a service request.

Casual Conversation: If the input is classified as casual, it is sent to the R1 API, which generates a response, and the interaction is stored in the database.

Decision Request: If the input is classified as a decision-making request, it is sent to the Broker API to process the request. The broker's response is then passed to the R1 API to generate a natural language response, which is stored in the database.

Database Schema
The database has a table named messages, with the following columns:

id: Primary key (integer)
session_id: Unique identifier for the conversation session (string)
role: Role of the message sender (either 'user' or 'assistant')
text: The message text (string)
created_at: Timestamp when the message was created (datetime)
Logging
The application uses Python's built-in logging module to log important events. Logs will be printed to the console by default.

Contributing
Fork this repository.
Create a new branch (git checkout -b feature-name).
Commit your changes (git commit -am 'Add new feature').
Push to the branch (git push origin feature-name).
Open a pull request.
License
This project is licensed under the MIT License - see the LICENSE file for details.
