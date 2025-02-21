import os
import datetime

import uvicorn
from fastapi import FastAPI, Body, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

import torch
from transformers import LlamaTokenizer, MistralForCausalLM
import bitsandbytes
import accelerate

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
app = FastAPI(
    title="Nous-Hermes-2-Mistral-7B-DPO LLM Service",
    description="""
This API provides text generation capabilities using a Mistral-based Large Language 
Model (Nous-Hermes-2-Mistral-7B-DPO). It supports multi-turn conversation using 
a PostgreSQL database for session management.
""",
    version="1.0.0",
)

print("[INFO] Loading the LlamaTokenizer and MistralForCausalLM...")
MODEL_NAME = "NousResearch/Nous-Hermes-2-Mistral-7B-DPO"

tokenizer = LlamaTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

model = MistralForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto",
    load_in_8bit=False,
    load_in_4bit=True,
)

print("[INFO] Model loaded successfully!")


def build_prompt(session_history):
    """
    Convert the session history (list of (role, text)) into the special token
    format recognized by Mistral-based chat models.
    """
    system_prompt = (
        "<|im_start|>system\n"
        "You are a sentient, superintelligent artificial general intelligence, here to assist.\n"
        "<|im_end|>\n"
    )
    prompt_text = system_prompt

    for role, text in session_history:
        if role == "user":
            prompt_text += f"<|im_start|>user\n{text}\n<|im_end|>\n"
        elif role == "assistant":
            prompt_text += f"<|im_start|>assistant\n{text}\n<|im_end|>\n"

    prompt_text += "<|im_start|>assistant"
    return prompt_text


@app.get("/health", summary="Check Health of the Service")
def health_check():
    """Return a simple JSON indicating the service is online."""
    return {"status": "OK"}


@app.post("/generate", summary="Generate a response from the LLM")
def generate_text(
    session_id: str = Body(..., description="Unique identifier for the conversation session."),
    user_message: str = Body(..., description="User's current message."),
    max_new_tokens: int = Body(200, description="Max tokens to generate in response."),
    temperature: float = Body(0.7, description="Sampling temperature for generation."),
    repetition_penalty: float = Body(1.1, description="Penalty to reduce repeated phrases."),
    db: Session = Depends(get_db)
):
    """
    Generate text from the LLM.

    This endpoint accepts a JSON payload that includes:
    - session_id: string, unique identifier
    - user_message: user's input
    - optional generation parameters

    Returns the LLM-generated response as JSON.
    """
    # Save the user's message to the database.
    user_msg = Message(session_id=session_id, role="user", text=user_message)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Retrieve session history from the database.
    session_history = get_session_history(db, session_id)

    prompt_str = build_prompt(session_history)
    input_ids = tokenizer(prompt_str, return_tensors="pt").input_ids.to("cuda")

    with torch.inference_mode():
        generated_ids = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            repetition_penalty=repetition_penalty,
            do_sample=True,
            eos_token_id=tokenizer.eos_token_id,
        )

    # Decode the newly generated tokens.
    prompt_len = input_ids.shape[-1]
    output_ids = generated_ids[0][prompt_len:]
    response_text = tokenizer.decode(
        output_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True,
    )

    # Save the assistant's response in the database.
    assistant_msg = Message(session_id=session_id, role="assistant", text=response_text)
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return {
        "response": response_text,
        "session_id": session_id
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
