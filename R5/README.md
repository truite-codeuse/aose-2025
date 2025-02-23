# Role 5 - Matching Scenarios

**Author: Nassim Lattab**

**Purpose:**
This script implements Role 5 in our multi-role system. It is responsible for matching user input phrases with scenarios associated with a specific project. The script:

1. **Retrieves** the list of scenarios for a given project from the Ai-Raison API.
2. **Builds** a prompt that combines the retrieved scenarios with user phrases.
3. **Sends** the prompt to a locally hosted LLM API (via FastAPI) for matching.
4. **Extracts** and returns the matching scenarios from the LLM’s JSON response.
5. **Formats** the output as JSON to be forwarded to Role 6.

## Project Overview

In our multi-role architecture, **Role 5** handles the scenario matching process:

- **Input:**
    - A project identifier (e.g., `"PRJ15875"`) used to retrieve project metadata from Ai-Raison.
    - A list of user phrases (e.g., `["I'd like to have my computer repaired"]`).

- **Process:**
    - The script constructs an API URL using the project ID and fetches metadata from the Ai-Raison API.
    - It extracts scenario labels from the metadata.
    - It builds a detailed prompt combining the list of scenarios and the user phrases, instructing the LLM to return a JSON object with the matched scenarios.
    - It calls the LLM API (running locally at `http://localhost:8000/generate`) to get a response.
    - The raw LLM output is preprocessed using regex to extract only the JSON block.
    - The extracted JSON is parsed and returned as a dictionary.

- **Output:**\
The final output is a JSON object that contains:
  - **project_id**: The project identifier.
  - **matched_scenarios**: An array containing the scenarios that best match the user's input.
  - **info**: A string field for additional information (e.g., error messages or processing details). This field may be empty on success.
Below is a global structure for the final output:

    ```json
    {
        "project_id": "PRJID05",
        "matched_scenarios": [
            "scenario1", "scenario2"
        ],
        "info": "..."
    }
    ```
    *Note* : The list may include additional scenario names.

## Code Structure

- **Configuration:**
    Sensitive data such as the API key are stored in a separate configuration file `(config.py)`.
    Note: Ensure that this file is excluded from version control (e.g., via .`gitignore`).

- **Functions:**
    - `extract_elements_and_options(metadata)`\
        Extracts scenario labels (elements) and options from the metadata.

    - `get_data_api(url, api_key)`\
        Retrieves JSON data from the Ai-Raison API.

    - `get_project_scenarios(project_id)`\
        Constructs the URL and extracts a list of scenario labels for the specified project.

    - `build_prompt(scenarios, user_phrases)`\
        Creates a prompt that instructs the LLM to perform scenario matching using only JSON output.

    - `call_llm(session_id, prompt, host)`\
        Sends the prompt to the local LLM API endpoint and retrieves the response.

    - `match_scenarios_with_llm(project_id, user_phrases)`\
        Orchestrates the entire process from retrieving scenarios to parsing the LLM's JSON response.
    
    - `send_to_role6(result_json)`\
        Sends the result to Role 6 via an HTTP POST.

- **Regex Preprocessing:**\
    Before attempting to parse the LLM response, a regex is used to extract only the JSON block from the raw output to handle any extra text returned by the model.

## Running and Communication
### Launching the Service

To launch the Role 5 service, run the following command in your project directory:
```bash
uvicorn role5_service:app --host 0.0.0.0 --port 8005 --reload
```
This starts the service on port **8005**, making the following endpoints available:

- Health Check: `http://localhost:8005/health`
- Matching Endpoint: `http://localhost:8005/match`

### Communication Between Roles

- **Input Reception:**\
    Role 5 exposes an endpoint `/match` that receives a JSON payload containing:
    - **project_id:** The identifier of the project.
    - **user_phrases:** A list of user input phrases.

    This data can be sent by another role (e.g., Role 2) without needing further configuration on Role 5's side. Role 5 simply listens on this endpoint.

- **Output Delivery:**\
    The matching result is returned as a JSON response, which also includes the project_id along with the matched_scenarios and info fields. In addition, the service is set up to send this result to Role 6 via an HTTP POST.

## Setup Instructions

### 1. Configuration:
Create a `config.py` file (or similar) that includes your sensitive information such as:
```python
# config.py
api_key = "YOUR_API_KEY_HERE"
```
*Note* : Make sure this file is not shared or pushed to public repositories.

### 2. Dependencies:
Install the required packages using:
```bash
pip install requests
```

### 3. LLM API:
>**Important:** Role 5 depends on the Role 1 LLM Service to be running.

Ensure Role 1 is set up according to its README and that your local LLM API (R1) is running. You can start it with:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Verify that the health endpoint (`http://localhost:8000/health`)  returns the expected JSON response (e.g., `{"status": "OK"}`). You can check it with the following command:
```bash
curl http://localhost:8000/health
```

### 4. Run the Service:
Start the Role 5 service with:
```bash
uvicorn role5_service:app --host 0.0.0.0 --port 8005 --reload
```

### 5. Testing the Communication:

You can test the service with a separate Python script (e.g., test_role5.py) that sends a POST request with hard-coded values:
```python
import json
import requests

url = "http://localhost:8005/match"

payload = {
    "project_id": "PRJ15875",
    "user_phrases": ["I'd like to have my computer repaired"]
}

try:
    response = requests.post(url, json=payload)
    response.raise_for_status()
    result = response.json()
    print("Matched Scenarios Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print("Error during test:", e)

```
Run this script with:
```bash
python test_role5.py
```

## Example Usage

For testing, if you send the following input:

- Project ID: `"PRJ15875"`
- User Phrases: `["I'd like to have my computer repaired"]`

You might receive an output like:
```json
{
    "project_id": "PRJ15875",
    "matched_scenarios": [
        "repair request"
    ],
    "info": ""
}
```
This JSON output can then be forwarded to Role 6 once it is configured.

## Notes

- **Prompt Engineering:**\
    The prompt provided to the LLM is crucial. Ensure it clearly instructs the LLM to return only valid JSON and no additional commentary.

- **Error Handling:**\
    The script includes basic error handling in case the LLM response cannot be parsed as JSON. You may further enhance this with more robust logging and recovery strategies.

- **Customization:**\
    Adjust the API URLs, generation parameters (e.g., max_new_tokens, temperature), and other configurations according to your environment and requirements.