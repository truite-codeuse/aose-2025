# --- FastAPI microservice setup ---
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import requests
import re
import logging
from config import api_key

# Logging Configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s [Role5] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI(title="Role 5 - Matching Scenarios Service")

# Pydantic models for request/response
class MatchRequest(BaseModel):
    project_id: str
    user_input: list[str]

class MatchResponse(BaseModel):
    project_id: str
    user_input: list[str]
    matched_scenarios: list[str]
    info: str

@app.get("/health")
def health_check():
    return {"status": "OK"}

@app.post("/match", response_model=MatchResponse)
def match_endpoint(request: MatchRequest):
    """
    Receives a project_id and user_input, processes the matching using the LLM,
    and returns the matching result as JSON.
    """
    # Request Logging
    logging.info("Received request for project_id: %s with user_input: %s", request.project_id, request.user_input)
    
    try:
        result = match_scenarios_with_llm(request.project_id, request.user_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Forwarding Logging
    logging.info("Forwarding response: %s", result)
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
    metadata = {}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            metadata = response.json()
        elif response.status_code == 400:
            logging.error("Error 400: Invalid request.")
        else:
            logging.error("Error %s: %s", response.status_code, response.text)
    except Exception as e:
        logging.error("An error occurred: %s", e)

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

def build_prompt(scenarios, user_input):
    """
    Constructs a concise and structured prompt for the LLM to efficiently match 
    user requests with predefined scenarios and return a JSON response.

    Args:
        scenarios (list of str): List of possible scenarios.
        user_input (list of str): User's request.

    Returns:
        str: A well-formatted prompt optimized for fast and accurate matching.
    """
    
    instruction = (
        "You are an AI assistant that matches user requests with predefined scenarios.\n"
        "Your task is to return ONLY the best-matching scenarios from the provided list.\n"
        "The output format must be a valid JSON object with a single key:\n"
        '{ "matched_scenarios": ["Scenario 1", "Scenario 2"] }\n'
        "Strict rules:\n"
        "- Do not include any additional text, explanations, backslash n like \\n or formatting outside the JSON.\n"
        "- Respond with an empty list if no scenario matches.\n"
    )

    scenario_text = ", ".join(f'"{s}"' for s in scenarios)  # Inline for brevity
    user_text = ", ".join(f'"{p}"' for p in user_input)

    full_prompt = (
        f"{instruction}\n\n"
        f"Scenarios: [{scenario_text}]\n"
        f"User Request: [{user_text}]\n\n"
        "Provide the JSON response now:"
    )

    return full_prompt.strip()

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
        "max_new_tokens": 100,
        "temperature": 0.7,
        "repetition_penalty": 1.1
    }
    
    # Log API call details
    logging.debug("Calling LLM API with session_id: %s and payload: %s", session_id, payload)
    
    resp = requests.post(url, json=payload)
    resp.raise_for_status()

    data = resp.json()
    llm_text = data["response"]

    # Log raw LLM output
    logging.debug("LLM raw output: %s", repr(llm_text))

    return llm_text

def match_scenarios_with_llm(project_id, user_input):
    """
    Orchestrates the entire pipeline:
      1) Retrieves scenarios for the given project from Ai-Raison.
      2) Builds a prompt with those scenarios and the user's request.
      3) Calls the LLM API to get a matching result.
      4) Attempts to parse the LLM's answer as JSON.

    Args:
        project_id (str): The project's identifier (e.g. "PRJ15875").
        user_input (list of str): The user's input request.

    Returns:
        dict: A dictionary containing the matched scenarios, for example:
        {
            "project_id" : "",
            "user_input" : ""
            "matched_scenarios": [...],
            "info": "some message if needed"
        }
    """
    # 1) Retrieve scenarios from Ai-Raison
    scenarios = get_project_scenarios(project_id)

    # 2) Build the LLM prompt
    prompt = build_prompt(scenarios, user_input)
    logging.debug("Constructed prompt: %s", prompt)

    # 3) Call the LLM
    llm_output = call_llm(session_id="matching_scenarios_session", prompt=prompt)
    
    # 4) Preprocess with regex to extract only the JSON block
    extracted_json = None
    match_obj = re.search(r'(\{.*\})', llm_output, re.DOTALL)
    if match_obj:
        extracted_json = match_obj.group(1).strip()
        logging.debug("Extracted JSON block from LLM output: %s", extracted_json)
    else:
        logging.error("No JSON object found in LLM response. Raw output: %s", llm_output)
        return {
            "project_id": project_id,
            "user_input": user_input,
            "matched_scenarios": [],
            "info": "No JSON object found in LLM response."
        }

    # Attempt to parse the extracted JSON block
    try:
        result_json = json.loads(extracted_json)
        logging.info("Successfully parsed LLM response. Matched scenarios: %s", result_json.get("matched_scenarios"))
    except json.JSONDecodeError:
        logging.error("JSON parsing failed for extracted JSON: %s", extracted_json)
        result_json = {
            "matched_scenarios": [],
            "info": "Could not parse extracted JSON from LLM response."
        }
    
    # Add the project_id and the user's input to the final result, regardless of parsing success
    result_json["project_id"] = project_id
    result_json["user_input"] = user_input
    result_json["info"] = result_json.get("info", "")

    # Forwarding Logging: Log the final JSON result before returning
    logging.info("Final JSON result: %s", result_json)
    result_json["matched_scenarios"] = [scenario for scenario in result_json["matched_scenarios"] if scenario in scenarios]
    return result_json

# --- Main block to run the service ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("role5_service:app", host="0.0.0.0", port=8005, reload=True)
