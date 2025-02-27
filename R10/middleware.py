from fastapi import FastAPI, HTTPException
import requests
import logging
import uvicorn

app = FastAPI()

# Configure logging
logging.basicConfig(filename="middleware.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Ports for each agent
PORTS = {
    "R1": 8000,
    "R2": 8002,
    "R4": 8004,
    "R5": 8005,
    "R6": 8006,
    "R8": 8008,
    "R10": 8010,
}

# Local storage of RAISON_PROJECTS (project IDs and descriptions)
RAISON_PROJECTS = {
    "PRJ17225": {"title": "Fair Price Negotiation", "description": "Compute-for-hire platform resolving conflicts on work payments."},
    "PRJ15875": {"title": "AI-CHATBOT", "description": "Customer service chatbot handling order tracking, refunds, and claims."},
    "PRJ16725": {"title": "Auto-Moderator", "description": "Streaming platform auto-moderator based on sentiment and emotion analysis."},
    "PRJ17575": {"title": "ARG", "description": "Leave management system ensuring compliance with organizational policies."},
    "PRJ17775": {"title": "Claim Resolver", "description": "Automated system for customer claims processing and decision-making."},
    "PRJ15425": {"title": "Reimbursement", "description": "Reimbursement of employee transport tickets for cost reduction."},
    "PRJ12375": {"title": "CV Sorting Automation", "description": "Automated recruitment system optimizing CV sorting for HR."},
    "PRJ17525": {"title": "Bluesky Automod", "description": "Automatic moderation for Bluesky detecting inappropriate content."}
}

# Function to call agents dynamically
def call_agent(agent_name, endpoint, data=None, method="post"):
    """
    Sends a request to a specified agent with given data.
    Supports both GET and POST requests.
    """
    url = f"http://localhost:{PORTS[agent_name]}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if method == "get":
        response = requests.get(url, headers=headers)
    else:
        response = requests.post(url, headers=headers, json=data)
    
    response.raise_for_status()
    return response.json()

# Middleware function handling process steps
@app.post("/process")
def middleware_handler(step: str, session_id: str, user_message: str, project_id: str = "default_project", max_new_tokens: int = 200, temperature: float = 0.7, repetition_penalty: float = 1.1):
    """
    Handles different steps in the processing pipeline based on the given step parameter.
    Calls different agents dynamically depending on the step type.
    """
    try:
        logging.info(f"Received step: {step} | Session: {session_id} | Project: {project_id} | Message: {user_message}")
        
        if step == "casual conversation":
            result = call_agent("R1", "generate", {
                "session_id": session_id, "user_message": user_message,
                "max_new_tokens": max_new_tokens, "temperature": temperature,
                "repetition_penalty": repetition_penalty
            })
        elif step == "match ad":
            result = call_agent("R2", "match_for_ad", {"user_input": user_message})
        elif step == "match scenario all":
            result = call_agent("R2", "match_for_scenario", {"user_input": user_message, "threshold": 0.5})
        elif step == "match scenario best":
            result = call_agent("R2", "match_for_scenario", {"user_input": user_message, "get_max": True})
        elif step == "sentence matching":
            result = call_agent("R2", "match", {"user_input": user_message})
        elif step == "query classification":
            result = call_agent("R4", "classify_input", {"session_id": session_id, "user_message": user_message})
        elif step == "scenario matching":
            result = call_agent("R5", "match", {"project_id": project_id, "user_input": [user_message]})
        elif step == "scenario extraction":
            result = call_agent("R5", "match_scenarios_with_llm", {"project_id": project_id, "user_input": [user_message]})
        elif step == "solution finding":
            result = call_agent("R6", "find_solution", {"project_id": project_id, "user_input": [user_message], "matched_scenarios": ["scenario1", "scenario2"]})
        elif step == "ad retrieval":
            result = call_agent("R8", "advertisements", method="get")
        elif step == "get projects":
            result = RAISON_PROJECTS  # Returns local project data
        else:
            raise HTTPException(status_code=400, detail=f"Unknown step: {step}")
        
        logging.info(f"Response: {result}")
        return result

    except Exception as e:
        logging.error(f"Error processing step {step}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Main execution block
if __name__ == "__main__":

    # Start the FastAPI application using Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORTS["R10"])
