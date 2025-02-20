# File: app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from transformers import pipeline
import logging
import threading

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Load the instruction-tuned model from Hugging Face.
# Using google/flan-t5-small as an example model for CPU usage.
try:
    logging.info("Loading model 'google/flan-t5-small'...")
    text_generator = pipeline("text2text-generation", model="google/flan-t5-small", device=-1)
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model: {e}")
    raise e

SYSTEM_PROMPT = (
  "You are a helpful Saloon assistant to book appointments for hair cuts and facials between 10AM to 8PM. "
  "You have the authority to suggest appointment times within that range. Provide a clear, concise response. "
  "If the user asks for an appointment, respond with an appropriate time slot."
)


# Global in-memory session store and lock for thread safety
sessions = {}
sessions_lock = threading.Lock()

app = FastAPI(title="Conversational AI Chatbot with Sessions")

# Pydantic models for request and response validation
class Message(BaseModel):
    role: str = Field(..., example="user")  # Allowed values: "user" or "system"
    content: str = Field(..., example="Hello, I need an appointment.")

class ChatRequest(BaseModel):
    conversation_id: str = Field(..., example="conv123")
    messages: List[Message]
    language: Optional[str] = Field("en", example="en")  # e.g., "en", "es", "fr"

class ChatResponse(BaseModel):
    conversation_id: str
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    # Check for an empty messages list in the new request
    if not chat_request.messages:
        raise HTTPException(status_code=400, detail="Messages list is empty.")

    # Manage the session state: create or update conversation history
    with sessions_lock:
        if chat_request.conversation_id not in sessions:
            sessions[chat_request.conversation_id] = []
        # Append the new messages to the existing session
        sessions[chat_request.conversation_id].extend(chat_request.messages)
        # Create a local copy of the conversation history
        conversation_history = sessions[chat_request.conversation_id]

    # Build the conversation prompt starting with the system prompt.
    conversation_text = SYSTEM_PROMPT + "\n\n"
    for message in conversation_history:
        if message.role.lower() == "user":
            conversation_text += f"User: {message.content}\n"
        elif message.role.lower() == "system":
            conversation_text += f"Assistant: {message.content}\n"
        else:
            conversation_text += f"{message.role}: {message.content}\n"

    # For non-English language, prepend an instruction to respond in that language.
    if chat_request.language and chat_request.language.lower() != "en":
        if chat_request.language.lower() == "es":
            conversation_text = "Por favor, responde en español.\n" + conversation_text
        elif chat_request.language.lower() == "fr":
            conversation_text = "Veuillez répondre en français.\n" + conversation_text
        # Additional languages can be added here.

    # Append the assistant marker to indicate that the model should generate the response.
    conversation_text += "\nAssistant: "

    try:
        # Generate the response using the model.
        generated = text_generator(
            conversation_text,
            max_length=200,
            do_sample=True,
            top_p=0.9,
            temperature=1.0
        )
        generated_text = generated[0]['generated_text']
        # Clean up the generated text by removing the prompt if it's echoed back.
        response_text = generated_text.replace(conversation_text, "").strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {e}")

    # Append the assistant's response to the session for future context
    assistant_message = Message(role="system", content=response_text)
    with sessions_lock:
        sessions[chat_request.conversation_id].append(assistant_message)

    return ChatResponse(conversation_id=chat_request.conversation_id, response=response_text)
