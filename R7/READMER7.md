## Argumentation Agent Initialization API
### Author
Role R7: Lynda BENKERROU

## Description

This project provides a FastAPI allowing you to initialize an argumentation agent with scenarios and options extracted from an `Ai-Raison` service. This API receives a project identifier (`project_id`) and returns the associated scenarios and options for that project.

The API exposes the following endpoints:
- **/initialize**: Initializes the agent by retrieving the scenarios and options associated with a given project.
- **/health**: Allows you to check if the server is functioning properly.

## Prerequisites

Before starting, make sure you have the following:

- **Python 3.7+**
- **Pip** (Python package manager)
- A `config.py` file containing a valid API key for the `Ai-Raison` API (the key should be in the form `api_key = 'your_api_key'`).

## Installation

1. Clone this repository:
   ```bash
   git clone https://your-repository-url
   cd role7-argumentation-agent
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

5. Ensure you have a `config.py` file containing your API key, for example:
   ```python
   api_key = 'your_api_key'
   ```

## Run the server

Start the FastAPI server with Uvicorn:

```bash
uvicorn main:app --reload
```

This will start the API on `http://127.0.0.1:8007`.

## Endpoints

### 1. `/initialize` (POST Method)

Initializes the agent by retrieving the scenarios and options associated with a given project.

**Example Request:** 
```json
{
POST http://127.0.0.1:8007/initialize
Content-Type: application/json
}
```
```json

{
  "project_id": "your_project_id"
}
```

**Response:**

```json
{
  "project_id": "your_project_id",
  "scenarios": ["Scenario 1", "Scenario 2", "Scenario 3"],
  "options": ["Option 1", "Option 2"]
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

## Project Structure

The project is organized as follows:

```
/role7-argumentation-agent
│
├── main.py                 # Main file with endpoint definitions
├── config.py               # Contains the API key to access the Ai-Raison API
├── requirements.txt        # List of required Python dependencies
└── README.md               # Project documentation
```

## How it works

1. **Agent Initialization**:
   The API receives a `project_id` via the `/initialize` endpoint. This `project_id` is used to make a request to the `Ai-Raison` API to retrieve the associated scenarios and options.

2. **Retrieving Scenarios and Options**:
   Once the data is fetched from the `Ai-Raison` API, it is extracted and formatted to be sent in the response as scenarios (labels) and options (IDs).

3. **Health Check**:
   The `/health` endpoint allows you to quickly check if the server is functioning correctly.



