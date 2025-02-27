## Role 6 - Solving Problems

### Author

Role R6, Mohamed Azzaoui

### General Description

This service is a microservice that finds solutions based on user input and matched scenarios with the platform AI Raison. It interacts with an LLM to generate clear and relevant explanatory responses. The service communicates with an LLM provided by **Role R2** to retrieve relevant information and receives input data (you can see it below) from **Role R5** via a dedicated endpoint.

### Installation

#### Clone this repository:
```bash
git clone <https://github.com/truite-codeuse/aose-2025.git>
cd <R6>
```

#### Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install required dependencies:
```bash
pip install -r requirements.txt
```

#### Create an API key:
If you don’t have an API key, follow the instructions on **AI Raison's website** to generate one.

Create a file private_information.py at the project root containing your API key:

api_key = "YOUR_API_KEY"


### Run the service:
```bash
uvicorn role6_service:app --host 0.0.0.0 --port 8006 --reload
```

### API Endpoints

#### Health Check
- **Route:** `/health`
- **Method:** `GET`
- **Description:** Checks if the service is running.
- **Response:**
```json
{"status": "OK"}
```

#### Find a Solution
- **Route:** `/find_solution`
- **Method:** `POST`
- **Description:** Finds a solution based on user input and provided scenarios. This endpoint receives information from **Role R5** and processes it by calling an **LLM from Role R2** to generate an appropriate response.

##### Request of R5 (JSON):
```json
{
  "project_id": "project_id",
  "user_input": ["example user input"],
  "matched_scenarios": ["scenario1", "scenario2"],
  "info": "additional information"
}
```

##### Response of R6 (JSON):
```json
{
  "text": "Generated AI response"
}
```

### Process Explanation

1. The endpoint receives data from **Role R5**.
2. It calls the `find_solution_llm` function to retrieve a solution using an **LLM from Role R2**.
3. If an error occurs, it logs the request and returns a server error message.
4. Otherwise, it returns the generated solution to the user.

#### Endpoint Code:
```python
@app.post("/find_solution", response_model=MatchResponse)
def match_endpoint(request: MatchRequest):
    try:
        result = find_solution_llm(request.project_id, request.matched_scenarios, request.user_input)
    except Exception as e:
        print(f"REQUEST RECEIVED = {request}")
        print(f"Error occurred: {str(e)}")  # Log the error
        raise HTTPException(status_code=500, detail="An error occurred on the server.")
    
    return MatchResponse(text=result)
```

### Key Features

#### AI Raison API Integration:
- Retrieve project metadata.

```python
def get_data_api(url, api_key):
    """
    Retrieves data from the API and extracts labels and IDs.

    Parameters:
        url (str): The API URL.
        api_key (str): API key for authentication.

    Returns:
        metadata: Returned metadata
    """
    headers = {"x-api-key": api_key}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            print("Error 400: Invalid request.")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None
```

- Extract associated elements and options.

```python
def extract_elements_and_options(metadata):
    """
    Extracts labels and IDs of elements, as well as the IDs of options.

    Parameters:
        metadata (dict): Data containing 'elements' and 'options' sections.

    Returns:
        tuple:
            - A dictionary {label: id} for elements.
            - A list of dictionaries [{"id": id}] for options.
    """
    elems = {}  # Stores labels and IDs of elements
    opts = []   # Stores IDs of options

    elem_items = metadata.get('elements', [])
    opts_items = metadata.get('options', [])

    for item in elem_items:
        label = item.get("label")
        id_value = item.get("id")
        elems[label] = id_value

    for item in opts_items:
        id_value = item.get("id")
        opts.append({"id": id_value})

    return elems, opts
```

- Send scenarios to the API to evaluate valid solutions.

```python
def call_api(project_id, scenario):
    """
    Calls the API to evaluate scenarios and returns valid options.

    Parameters:
        project_id (str): The ID of the project.
        scenario (list): List of labels of elements to include in the scenario.

    Returns:
        list: Valid solutions or None if none.
    """
    base_url = "https://api.ai-raison.com/executions"
    url = f"{base_url}/{project_id}/latest"

    metadata = get_data_api(url, api_key)
    elements, options = extract_elements_and_options(metadata)

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    ids = [{"id": elements[case]} for case in scenario]

    payload = {
        "elements": ids,
        "options": options,
        "limit": len(options)
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            metadata = response.json()
        elif response.status_code == 400:
            print("Error 400: Invalid request.")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return check_solutions(metadata)
```

###### Request of R5 (JSON):
the url for the request is "https://api.ai-raison.com/executions/{project_id}/latest"

```json
{
  "elements": "example_scenario",
  "options": "example_possible_results",
  "limit": "max_number_of_solutions"
}
```
###### Response of Ai-Raison (JSON):
```json
{
  "options": "dictionary_of_options_with_boolean_values"
}
```

#### LLM Interaction (Role R2):
- Build a structured prompt using user requests and available options.
- Send the prompt to an LLM model to generate an explanatory response.

#### Middleware & FastAPI API:
- REST interface allowing users to send requests and receive solutions.
- Logging and error handling for service robustness.
- Direct communication with **Role R5** for input data retrieval.

### Project Structure
```
R6/
|-- role6_service.py        # Initializes the FastAPI service and uses my microservice when listening to a request          
|-- test.py                 # Testing my work independently
|-- api.py                  # Connects and extracts data from AI Raison API
|-- requirements.txt        # List of dependencies
|-- private_information.py  # File containing the API key (not versioned)
```

### Requirements File (`requirements.txt`)
```txt
fastapi
uvicorn
requests
pydantic
```