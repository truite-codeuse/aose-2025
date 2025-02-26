import os
import datetime
import logging
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
# Database Setup (PostgreSQL)
# ---------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/db_name")

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

# Function to detect if the message is a casual conversation or service request
def is_casual_conversation(user_message: str) -> bool:
    """
    Detects if the message from the user is a casual conversation or a service request.
    """
    casual_keywords = ["hello", "hi", "how are you", "how's it going", "tell me"]
    decision_keywords = ["which service", "help me", "decision", "choose", "recommend"]
    
    # Check if the message contains keywords related to casual conversation
    if any(keyword in user_message.lower() for keyword in casual_keywords):
        return False  # Casual conversation
    # Check if the message contains keywords related to a service request
    if any(keyword in user_message.lower() for keyword in decision_keywords):
        return True  # Service request
    return False  # Default to casual conversation if no match

@app.get("/health", summary="Check Health of the Service")
def health_check():
    """Return a simple JSON indicating the service is online."""
    return {"status": "OK"}

@app.post("/process_input", summary="Process user input for casual talk or decision making")
def process_user_input(
    user_input: UserInput,
    db: Session = Depends(get_db),
):
    """
    This function processes the user's input and determines whether it's a casual conversation
    or a request for a service. It responds with a boolean and stores the interaction in the database.
    """
    try:
        # Detect whether the user input is a casual conversation or a service request
        is_service_request = is_casual_conversation(user_input.user_message)
        
        # Save the user's message to the database
        user_msg = Message(session_id=user_input.session_id, role="user", text=user_input.user_message)
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)
        
        # Prepare the response based on the detected message type
        if is_service_request:
            response_text = "C'est une requête de service."
        else:
            response_text = "C'est une conversation normale."
        
        # Save the assistant's response in the database
        assistant_msg = Message(session_id=user_input.session_id, role="assistant", text=response_text)
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)
        
        # Return the response with a boolean and the assistant's message
        return {
            "is_service_request": is_service_request,  # True for service request, False for casual conversation
            "response": response_text,  # Explanation text
            "session_id": user_input.session_id,
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing user input: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
