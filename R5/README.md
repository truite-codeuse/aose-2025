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

- **Output:** The final output is a JSON object that contains a list of matched scenarios. The structure of the response will thus include the **matched_scenarios** key, which holds relevant scenarios, based on the user's input. 
Below is a global structure for the final output:
    ```json
    {
        "matched_scenarios": [
            "scenario1", "scenario2", ...
        ]
    }
    ```

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

- **Regex Preprocessing:**\
    Before attempting to parse the LLM response, a regex is used to extract only the JSON block from the raw output to handle any extra text returned by the model.

## Setup Instructions

### 1. Configuration:
Create a `config.py` file (or similar) that includes your sensitive information such as:
```python
# config.py
api_key = "YOUR_API_KEY_HERE"
```
*Note:* Make sure this file is not shared or pushed to public repositories.

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

### 4. Run the Script:
Execute the script `python scenario_matcher.py` to perform the matching process.

## Example Usage

For testing, if you run the script with:

- Project ID: `"PRJ15875"`
- User Phrases: `["I'd like to have my computer repaired"]`

You might receive an output like:
```json
{
    "matched_scenarios": [
        "repair request"
    ]
}
```
This JSON output can then be forwarded to Role 6 as needed.

## Notes

- **Prompt Engineering:**\
    The prompt provided to the LLM is crucial. Ensure it clearly instructs the LLM to return only valid JSON and no additional commentary.

- **Error Handling:**\
    The script includes basic error handling in case the LLM response cannot be parsed as JSON. You may further enhance this with more robust logging and recovery strategies.

- **Customization:**\
    Adjust the API URLs, generation parameters (e.g., max_new_tokens, temperature), and other configurations according to your environment and requirements.