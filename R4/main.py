import os
import datetime
import openai
import torch
from fastapi import FastAPI, Body, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Dict, Any
import uvicorn

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
# LLM Setup (Local vs Remote)
# ---------------------------
LLM_LOCAL = False  # Set to True for local LLM call, False for remote LLM call

# Initialize the OpenAI GPT-3 or GPT-4 API Key
openai.api_key = "YOUR_OPENAI_API_KEY"  # Remplace par ta clé API OpenAI

# Function to call GPT-3 or GPT-4 via OpenAI API
def call_LLM_remote(prompt_str: str) -> str:
    """
    Calls the GPT-3 or GPT-4 model via the OpenAI API to generate a response.
    """
    response = openai.Completion.create(
        model="gpt-4",  # Utilise GPT-4, tu peux aussi utiliser "gpt-3.5-turbo" si tu préfères GPT-3.5
        prompt=prompt_str,
        max_tokens=200,  # Max tokens for response
        temperature=0.7,  # Randomness (0.7 for creativity)
        top_p=1,  # Control the diversity of the generated text (optional)
        frequency_penalty=0,  # Penalty for repetition
        presence_penalty=0,  # Penalty to avoid repeating similar concepts
    )
    return response.choices[0].text.strip()

# ---------------------------
# FastAPI Setup
# ---------------------------
app = FastAPI(
    title="LLM Agent – Process User Input",
    description="This API processes user input to determine if it is a casual conversation or a request for service.",
    version="1.0.0",
)

# Function to build the prompt to distinguish conversation types
def build_prompt(user_message: str) -> str:
    """
    Creates a prompt to determine if the user's message is a casual conversation or a service request.
    """
    prompt = f"""
    Here's the user's message: "{user_message}"
    Please determine if this message is a casual conversation or a service request.

    If it's a casual conversation (e.g., a greeting or informal question), reply with "False".
    If it's a service request (e.g., asking for help or a service), reply with "True".
    """
    return prompt

# Pydantic model for receiving the message
class UserMessage(BaseModel):
    message: str

# Endpoint for processing the user input
@app.post("/process_message", response_model=Dict[str, Any])
def process_message(data: UserMessage):
    """
    This function receives a user message, creates a prompt, and uses GPT-3 or GPT-4 to determine if the message
    is a casual conversation or a service request.
    """
    user_message = data.message
    prompt = build_prompt(user_message)
    
    # Call GPT-3 or GPT-4 via OpenAI API
    response_text = call_LLM_remote(prompt)

    # The model should respond with "True" or "False" based on message type
    if "True" in response_text:
        return {"is_service_request": True}
    else:
        return {"is_service_request": False}

# Health check endpoint
@app.get("/health", summary="Check Health of the Service")
def health_check():
    """Return a simple JSON indicating the service is online."""
    return {"status": "OK"}

# Run the FastAPI application with Uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
