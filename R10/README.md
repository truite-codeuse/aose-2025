#R10

## **Author**
**Middleware Agent - Request Router**  
Developed by: **R10 BENLAMARA Kamilia**

---

## **General Description**
The **Middleware Service – Request Router** acts as a central hub to route user requests to the appropriate microservices based on predefined steps.  
This service communicates with various agents (R1, R2, R4, R5, R6, R8, R10) to handle different tasks such as text generation, classification, scenario matching, advertisement retrieval, and more.

### **Key Features:**
- **Dynamic Routing to Agents**: Automatically directs requests to the correct microservice based on the request step.
- **Multi-Agent Communication**: Supports various AI-powered services such as chatbots, classifiers, scenario matchers, and solution finders.
- **Logging Mechanism**: Records all interactions in a log file (`middleware.log`) for debugging and monitoring.
- **Error Handling**: Includes exception handling to manage request failures gracefully.

---

## **Installation**
### **Clone the Repository:**
```bash
git clone https://github.com/your-repo/aose-2025.git
cd R10
```

### **Create and activate a virtual environment:**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### **Install required dependencies:**
```bash
pip install -r requirements.txt
```

### **Run the service:**
```bash
uvicorn middleware:app --host 0.0.0.0 --port 8010 --reload
```

---

## **Project Structure**
This section outlines the project directory structure:

```
R10/
│-- middleware.py   # Main FastAPI service file handling requests
│-- requirements.txt        # Lists all dependencies required for the project
│-- middleware.log          # Log file for monitoring service requests
│-- README.md               # Documentation and setup instructions
```

---

## **Detailed File Descriptions**
- **`middleware.py`**:  
  - Core of the application, initializes the FastAPI service.
  - Defines the `/process` endpoint to handle different request types.
  - Calls external agents (R1, R2, R4, etc.) dynamically based on user input.
  - Includes error handling and logging mechanisms.

- **`requirements.txt`**:  
  - Contains a list of all required Python libraries that can be installed using `pip install -r requirements.txt`.

- **`middleware.log`**:  
  - Stores logs of all received requests and responses for debugging and monitoring.

- **`README.md`**:  
  - Provides a project overview, installation guide, and usage instructions.

---

## **API Endpoints**
### **1. Process Request**
- **Endpoint:** `/process`
- **Method:** `POST`
- **Description:** Handles different steps based on user input and routes requests to the appropriate agent.
- **Request Example:**
```json
{
    "step": "casual conversation",
    "session_id": "12345",
    "user_message": "Hello, how are you?",
    "project_id": "default_project"
}
```
- **Response Example:**
```json
{
    "response": "Hello! How can I assist you today?"
}
```

---

## **Interacting Services**
This middleware interacts with multiple microservices:
| **Agent** | **Port** | **Function** |
|-----------|---------|--------------|
| **R1**    | 8000    | Handles chatbot-style conversations |
| **R2**    | 8002    | Matches ads and scenarios based on user input |
| **R4**    | 8004    | Classifies user queries |
| **R5**    | 8005    | Matches user input with predefined scenarios |
| **R6**    | 8006    | Finds solutions for matched scenarios |
| **R8**    | 8008    | Retrieves advertisements for relevant services |
| **R10**   | 8010    | Runs the middleware service itself |

---

## **Logging & Debugging**
All incoming requests and responses are logged in `middleware.log` for debugging purposes.
To monitor logs in real-time:
```bash
tail -f middleware.log
```

  

