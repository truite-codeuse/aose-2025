import json
import requests

# URL of the endpoint/match of the service Role 5
url = "http://localhost:8005/match"

# Test data
payload = {
    "project_id": "PRJ15875",
    "user_input": ["I'd like to have my computer repaired. The product is not repairable but is under warranty, what can you do for me?"]
}

try:
    response = requests.post(url, json=payload)
    response.raise_for_status()
    result = response.json()
    print("Matched Scenarios Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print("Error during test:", e)
