# R7 - Argumentation Agent Initialization API

This API is used to initialize an argumentation agent by fetching scenarios and options for a project from the **Ai-Raison** API.

## Prerequisites

Before running the API, ensure you have the following:

- **Python 3.11 or higher**: Ensure Python is installed on your machine.
- **API Key** for accessing the **Ai-Raison** API: You need to have a valid API key.

## 🏁 Installation

### Step 1: Install dependencies

Ensure that `pip` is installed, then run the following command to install the required dependencies:

    ```bash
    pip install fastapi uvicorn requests

### Step 2: Create the config.py file
In the same directory as main.py, create a config.py file containing your API key.

    ``` python
    api_key = "YOUR_API_KEY_HERE"
    
Replace "YOUR_API_KEY_HERE" with the API key you received from Ai-Raison.

### Step 3: Run the API
Run the API with the following command:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8007 --reload
    
This will start the server at http://127.0.0.1:8007 and enable auto-reloading during development.
