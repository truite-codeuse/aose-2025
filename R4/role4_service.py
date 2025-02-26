import os
import datetime
import logging
import requests
from fastapi import FastAPI, Body, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# ---------------------------
# Logging Setup
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# Configuration
# ---------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/db_name")
R1_API_URL = "http://localhost:8000/generate"  # URL of the R1 API
BROKER_API_URL = "http://localhost:8001/process_request"  # URL of the broker agent

# ---------------------------
# Database Setup (PostgreSQL)
# ---------------------------
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)  # 'user' or 'assistant'
    text = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_session_history(db: Session, session_id: str):
    """Retrieve the conversation history for the given session_id."""
    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at)
        .all()
    )
    return [(msg.role, msg.text) for msg in messages]

# ---------------------------
# FastAPI Application Setup
# ---------------------------
app = FastAPI(title="R4 - Process User Input", description="Detects user input type: conversation or service request", version="1.0.0")

# Pydantic model for the user input
class UserInput(BaseModel):
    session_id: str
    user_message: str

# ---------------------------
# Helper Functions
# ---------------------------
def classify_input(user_input: str) -> str:
    prompt = (
        f"Can you tell me if the following user input is a service request or an informal conversation? "
        f"Reply 'true' if it's a service request, 'false' otherwise. "
        f"User input: {user_input}"
    )

    try:
        response = call_r1_api("classification_session", prompt)
        
        if "vrai" in response.lower():
            return "decision"
        else:
            return "casual"
    except Exception as e:
        logger.error(f"Error calling R1 API for classification: {e}")
        decision_keywords = ["decide", "choose", "option", "recommend", "help me decide"]
        if any(keyword in user_input.lower() for keyword in decision_keywords):
            return "decision"
        else:
            return "casual"

def call_r1_api(session_id: str, user_message: str) -> str:
    payload = {
        "session_id": session_id,
        "user_message": user_message,
    }
    response = requests.post(R1_API_URL, json=payload, timeout=5)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Failed to call R1 API: {response.status_code} - {response.text}")

def call_broker_api(user_input: str) -> str:
    payload = {
        "user_input": user_input,
    }
    response = requests.post(BROKER_API_URL, json=payload, timeout=5)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Failed to call broker API: {response.status_code} - {response.text}")

# ---------------------------
# Main Functions for R4
# ---------------------------
def handle_casual_conversation(session_id: str, user_input: str, db: Session) -> str:
    response_text = call_r1_api(session_id, user_input)
    assistant_msg = Message(session_id=session_id, role="assistant", text=response_text)
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)
    return response_text

def handle_decision_request(session_id: str, user_input: str, db: Session) -> str:
    broker_response = call_broker_api(user_input)
    final_response = call_r1_api(session_id, broker_response)
    assistant_msg = Message(session_id=session_id, role="assistant", text=final_response)
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)
    return final_response

@app.post("/process_input", summary="Process user input for casual talk or decision making")
def process_user_input(user_input: UserInput, db: Session = Depends(get_db)):
    try:
        input_type = classify_input(user_input.user_message)
        if input_type == "casual":
            response_text = handle_casual_conversation(user_input.session_id, user_input.user_message, db)
        elif input_type == "decision":
            response_text = handle_decision_request(user_input.session_id, user_input.user_message, db)
        else:
            response_text = "Sorry, I couldn't understand your request."
        
        return {
            "response": response_text,
            "session_id": user_input.session_id,
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing user input: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/classify_input", summary="Returns true for a service query, false for casual talk", response_model=bool)
def classify_user_input(user_input: UserInput) -> bool:
    input_type = classify_input(user_input.user_message)
    return input_type == "decision"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8004, reload=False)
