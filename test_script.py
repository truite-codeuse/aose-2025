import json
import requests

# URL of the endpoint/match of the service Role 5
url = "http://localhost:8010/pipeline"

header = {
    "Content-Type": "application/json"
}

# Test data
payload = {
    "session_id": "test_aose",
    "user_input": "Hello, I have a problem with my product, I need an intelligent customer service chatbot designed to handle order tracking, returns, refunds, and claims. This is a service request."
}

payload2 = {
    "session_id": "test_aose",
    "user_input": "I have a repair request. Indeed, I'd like to have my computer repaired. The product is under warranty."
}

try:
    response = requests.post(url, json=payload2, headers=header)
    response.raise_for_status()
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print("Error during test:", e)
