from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import requests
import re
from api import *
import uvicorn

app = FastAPI(title="Role 6 - Solving Problems")

# Pydantic models for request/response
class MatchRequest(BaseModel):
    project_id: str
    user_input:list[str]
    matched_scenarios: list[str]  
    info: str

class MatchResponse(BaseModel):
    text : str
    
@app.get("/health")
def health_check():
    return {"status": "OK"}

@app.post("/find_solution", response_model=MatchResponse)
def match_endpoint(request: MatchRequest):
    try:
        result = find_solution_llm(request.project_id, request.matched_scenarios, request.user_input)
    except Exception as e:
        print(f"REQUEST RECUE = {request}")
        print(f"Error occurred: {str(e)}")  # Log l'erreur
        raise HTTPException(status_code=500, detail="An error occurred on the server.")
    
    # Optionally, send the result to Role 6 (currently commented out)
    # send_to_role6(result)
    
    # For now, simply display the result (or return it)
    print("Result to be sent to user (not sent):", result)
    return MatchResponse(text=result)


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

def build_prompt(options, user_input):
    """
    Builds a textual prompt to send to the LLM.

    The LLM will transform an option and its corresponding user request into a clear explanatory text that summarizes the option.
    For example, if the option is 'refund' and users ask about getting their money back, the response should be:
    "You have requested a refund, and we will process it as soon as possible."

    Args:
        options (list of dict): List of options with a description and matching phrase for the LLM to respond with.
        user_input (list of str): The user's input request.

    Returns:
        str: The complete prompt text to send to the LLM.
    """
    instruction = (
        "You are an assistant that converts predefined decisions of a decision policy into concise explanatory responses.\n\n"
        "For each decision, generate a natural language explanation that summarizes the decision in a way that directly addresses the user’s intent.\n"
        "Ensure the response is clear, relevant, and directly addresses the user's concern.\n"
        "Return only the generated response and avoid any additional commentary."
    )
    
    # Format options and user request into strings
    option_text = "\n".join([f"- {o}" for o in options])
    user_text = "\n".join(f"- {p}" for p in user_input)
    
    # Construct the full prompt
    full_prompt = (
        f"{instruction}\n\n"
        f"LIST OF OPTIONS:\n{option_text}\n\n"
        f"USER REQUEST:\n{user_text}\n\n"
        "Please generate the appropriate response."
    )
    
    return full_prompt

def find_solution_llm(project_id, matched_scenarios, user_input):

    solution = call_api(project_id, matched_scenarios)
    print(solution)
    
    prompt = build_prompt(solution, user_input) 
    print(f"PROMPT {prompt}")
    llm_output = call_llm(session_id="explain_solutions_session", prompt=prompt)

    return llm_output

# --- Main block to run the service ---
if __name__ == "__main__":
    uvicorn.run("role6_service:app", host="0.0.0.0", port=8006, reload=True)