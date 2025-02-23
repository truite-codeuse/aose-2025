# --- FastAPI microservice setup ---
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import requests
import re
from config import api_key

app = FastAPI(title="Role 5 - Matching Scenarios Service")

# Pydantic models for request/response
class MatchRequest(BaseModel):
    project_id: str
    user_phrases: list[str]

class MatchResponse(BaseModel):
    project_id: str
    matched_scenarios: list[str]
    info: str = ""

@app.get("/health")
def health_check():
    return {"status": "OK"}

@app.post("/match", response_model=MatchResponse)
def match_endpoint(request: MatchRequest):
    """
    Receives a project_id and user_phrases, processes the matching using the LLM,
    and returns the matching result as JSON.
    """
    try:
        result = match_scenarios_with_llm(request.project_id, request.user_phrases)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Optionally, send the result to Role 6 (currently commented out)
    # send_to_role6(result)
    
    # For now, simply display the result (or return it)
    print("Result to be sent to Role 6 (not sent):", result)
    return result


# --- Pipeline functions ---

def extract_elements_and_options(metadata):
    """
    Extracts element labels/IDs (scenarios) and a list of options (IDs) from a 'metadata' structure.

    Args:
        metadata (dict): The project data containing 'elements' and 'options'.

    Returns:
        tuple: 
            - A dictionary { element_label: element_id }.
            - A list of dictionaries [{"id": X}, ...] for the options.
    """
    elems = {}  # {label: id}
    opts = []   # [{"id": X}, ...]

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
            metadata = response.json()
        elif response.status_code == 400:
            print("Error 400: Invalid request.")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")
        metadata = {}

    return metadata

def get_project_scenarios(project_id):
    """
    Retrieves all possible scenarios for a given project from Ai-Raison.
    Example endpoint: https://api.ai-raison.com/executions/<project_id>/latest

    Args:
        project_id (str): The identifier of the project (e.g. "PRJ15875").

    Returns:
        list: A list of scenario labels (strings) associated with the project.
    """
    base_url = "https://api.ai-raison.com/executions"
    url = f"{base_url}/{project_id}/latest"

    metadata = get_data_api(url, api_key)
    elems, _ = extract_elements_and_options(metadata)

    # We only take the scenario labels as a list.
    scenarios = list(elems.keys())

    return scenarios

def build_prompt(scenarios, user_phrases):
    """
    Builds a textual prompt to send to the LLM.

    The LLM does not need the project ID itself, only the list of scenarios and user phrases.
    We instruct the LLM to match user phrases to the relevant scenario(s) and respond in JSON.

    Args:
        scenarios (list of str): The list of possible scenarios.
        user_phrases (list of str): The user's input phrases.

    Returns:
        str: The complete prompt text to send to the LLM.
    """
    instruction = (
        "You are an assistant specialized in matching user phrases with a list of scenarios.\n\n"
        "You are given multiple potential scenarios and some user phrases.\n"
        "Your goal: determine which scenarios best match the user's phrases.\n"
        "Please respond in JSON format and nothing else, for example:\n"
        "{\n"
        '  "matched_scenarios": ["Scenario 1", "Scenario 2"]\n'
        "}\n"
        "Return only the relevant scenarios.\n"
        "Do NOT provide any additional commentary or text outside of the JSON.\n"
    )
    scenario_text = "\n".join(f"- {s}" for s in scenarios)
    user_text = "\n".join(f"- {p}" for p in user_phrases)
    full_prompt = (
        f"{instruction}\n\n"
        f"LIST OF SCENARIOS:\n{scenario_text}\n\n"
        f"USER PHRASES:\n{user_text}\n\n"
        "Please provide the matching scenarios in JSON format.\n"
    )
    return full_prompt

def call_llm(session_id, prompt, host="http://localhost:8000"):
    """
    Sends the constructed prompt to the locally hosted LLM API (FastAPI) at /generate.

    Args:
        session_id (str): A unique identifier for the conversation.
        prompt (str): The text to be processed by the LLM.
        host (str): The base URL of the LLM API (default: http://localhost:8000).

    Returns:
        str: The raw response text generated by the LLM.
    """
    url = f"{host}/generate"
    payload = {
        "session_id": session_id,
        "user_message": prompt,
        "max_new_tokens": 200,
        "temperature": 0.7,
        "repetition_penalty": 1.1
    }

    resp = requests.post(url, json=payload)
    resp.raise_for_status()

    data = resp.json()
    llm_text = data["response"]

    return llm_text

def match_scenarios_with_llm(project_id, user_phrases):
    """
    Orchestrates the entire pipeline:
      1) Retrieves scenarios for the given project from Ai-Raison.
      2) Builds a prompt with those scenarios and the user's phrases.
      3) Calls the LLM API to get a matching result.
      4) Attempts to parse the LLM's answer as JSON.

    Args:
        project_id (str): The project's identifier (e.g. "PRJ15875").
        user_phrases (list of str): The user's input phrases.

    Returns:
        dict: A dictionary containing the matched scenarios, for example:
        {
            "matched_scenarios": [...],
            "info": "some message if needed"
        }
    """
    # 1) Retrieve scenarios from Ai-Raison
    scenarios = get_project_scenarios(project_id)

    # 2) Build the LLM prompt
    prompt = build_prompt(scenarios, user_phrases)

    # 3) Call the LLM
    llm_output = call_llm(session_id="matching_scenarios_session", prompt=prompt)
    print("DEBUG - LLM raw output:", repr(llm_output))

    # 4) Preprocess with regex to extract only the JSON block
    extracted_json = None
    match_obj = re.search(r'(\{.*\})', llm_output, re.DOTALL)
    if match_obj:
        # Retrieve only the part between the first '{' and the last '}'
        extracted_json = match_obj.group(1).strip()

    if not extracted_json:
        return {
            "project_id": project_id,
            "matched_scenarios": [],
            "info": "No JSON object found in LLM response."
        }
    
    # Attempt to parse the extracted JSON block
    try:
        result_json = json.loads(extracted_json)
    except json.JSONDecodeError:
        result_json = {
            "matched_scenarios": [],
            "info": "Could not parse extracted JSON from LLM response."
        }
    
    # Add the project_id to the final result, regardless of parsing success
    result_json["project_id"] = project_id

    return result_json

# --- Functions for communication with Role 6 ---
def send_to_role6(result_json):
    """
    Sends the result JSON to Role 6 via an HTTP POST.
    
    """
    ROLE6_URL = "http://localhost:8006/receive_result"  # Placeholder URL
    try:
        response = requests.post(ROLE6_URL, json=result_json)
        response.raise_for_status()
        return response.json()  # Optionally, return Role 6's response
    except Exception as e:
        print(f"Error sending to Role 6: {e}")
        return None

# --- Main block to run the service ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("role5_service:app", host="0.0.0.0", port=8005, reload=True)
