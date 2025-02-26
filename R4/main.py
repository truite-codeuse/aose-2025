from fastapi import FastAPI, Body, Depends
from sqlalchemy.orm import Session
import torch
from transformers import LlamaTokenizer, MistralForCausalLM

# Integration with R1 (LLM Model developed earlier)
from . import R1_model  # Ensure that R1 is properly integrated and accessible.

# Logic to detect the type of user input (Casual vs. Decision Making)
def is_casual_conversation(user_message: str) -> bool:
    """
    Detect if the user's message is a casual conversation or a decision-making request.
    """
    casual_keywords = ["hello", "hi", "how are you", "what's up", "tell me"]
    decision_keywords = ["what service", "help me", "decide", "choose", "recommend"]
    
    # Check if the message contains casual conversation keywords
    if any(keyword in user_message.lower() for keyword in casual_keywords):
        return True
    # Check if the message contains decision-making keywords
    if any(keyword in user_message.lower() for keyword in decision_keywords):
        return False
    return False


# New function to process user input based on type
@app.post("/process_input", summary="Process user input for casual talk or decision making")
def process_user_input(
    session_id: str = Body(..., description="Unique identifier for the conversation session."),
    user_message: str = Body(..., description="User's input message."),
    db: Session = Depends(get_db),
):
    """
    This function processes the user's input and determines whether it is
    a casual conversation or a decision-making request.
    - If it's casual talk, the LLM model is used to respond.
    - If it's a decision-making request, a broker agent is called to
      handle the request.
    """
    # Determine if the user is engaging in casual conversation or requesting a decision
    is_casual = is_casual_conversation(user_message)
    
    # Save the user's message to the database
    user_msg = Message(session_id=session_id, role="user", text=user_message)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    
    if is_casual:
        # Use the LLM model to generate a casual response
        session_history = get_session_history(db, session_id)
        prompt_str = build_prompt(session_history)
        input_ids = R1_model.tokenizer(prompt_str, return_tensors="pt").input_ids.to("cuda")

        with torch.inference_mode():
            generated_ids = R1_model.model.generate(
                input_ids,
                max_new_tokens=200,
                temperature=0.7,
                repetition_penalty=1.1,
                do_sample=True,
                eos_token_id=R1_model.tokenizer.eos_token_id,
            )

        prompt_len = input_ids.shape[-1]
        output_ids = generated_ids[0][prompt_len:]
        response_text = R1_model.tokenizer.decode(
            output_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )

        # Save the assistant's response to the database
        assistant_msg = Message(session_id=session_id, role="assistant", text=response_text)
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)

        return {
            "response": response_text,
            "session_id": session_id,
        }

    else:
        # Handle decision-making request via broker agent
        # (This part should call the broker agent and then the provider agent)
        # Placeholder for interacting with the broker agent and provider agent
        decision = ask_broker_and_provider_agents(user_message)

        # Save the provider agent's response to the database
        assistant_msg = Message(session_id=session_id, role="assistant", text=decision)
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)

        return {
            "response": decision,
            "session_id": session_id,
        }

# Fictitious function to query the broker agent and the provider agent
def ask_broker_and_provider_agents(user_message: str) -> str:
    """
    Processes a decision-making request by querying the broker agent and
    then a provider agent to obtain an appropriate response.
    """
    # Call the broker agent and get a response from a provider agent
    # This part is a placeholder and should be integrated with the broker and provider agents.
    return "Here is the decision after consulting the broker and provider."


