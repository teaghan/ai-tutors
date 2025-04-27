from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import logging

# Import the tutor module
from ai_tutors.tutor import load_tutor
from llama_index.core.llms import ChatMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define FastAPI app with metadata
app = FastAPI(
    title="AI Tutors API",
    description="API for interacting with AI Tutors",
    version="1.0.0",
)

# Define a prompt schema for input
class PromptRequest(BaseModel):
    user_prompt: str
    access_code: str
    message_history: Optional[list]

# Utility functions for message conversion
def dict_to_chat_message(msg_dict: Dict[str, str]) -> ChatMessage:
    """Convert a dictionary to a ChatMessage object"""
    return ChatMessage(
        role=msg_dict.get('role', ''),
        content=msg_dict.get('content', '')
    )

def chat_message_to_dict(msg: ChatMessage) -> Dict[str, str]:
    """Convert a ChatMessage object to a dictionary"""
    return {
        "role": msg.role,
        "content": msg.content
    }

# Endpoint to get the initial system prompt/greeting
@app.get("/init_request", summary="Get initial tutor greeting")
async def get_init_request(access_code: str):
    """
    Get the initial greeting message from the AI Tutor.
    
    Args:
        access_code: Your AI Tutor access code
        
    Returns:
        The initial greeting message
    """
    try:
        # Load tutor using the provided access code
        tutor = load_tutor(access_code)
        
        # Get the initial greeting message
        if tutor.tutor_llm.message_history:
            # Get assistant's first message (after system prompt)
            for msg in tutor.tutor_llm.message_history:
                if msg.role == "assistant":
                    return {"init_request": msg.content}
            
            # Fallback to returning the init_request attribute
            return {"init_request": tutor.init_request}
        
        return {"init_request": ""}
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger.error(f"Error in get_init_request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to call the LLM
@app.post("/query", summary="Send a query to the AI tutor")
async def query_model(request: PromptRequest):
    """
    Send a query to the AI tutor and get a response.
    
    Args:
        request: Request object containing user prompt, access code, and optional message history
        
    Returns:
        The tutor's response and updated message history
    """
    try:
        # Load tutor using the provided access code
        tutor = load_tutor(request.access_code)

        if request.message_history:
            # Convert JSON message history to ChatMessage objects
            chat_messages = [dict_to_chat_message(msg) for msg in request.message_history]
            tutor.tutor_llm.message_history = chat_messages
            
        if request.user_prompt:
            response = tutor.tutor_llm.get_response(request.user_prompt)
        else:
            response = ''
        
        # Convert ChatMessage objects to serializable dictionaries
        serialized_history = [chat_message_to_dict(msg) for msg in tutor.tutor_llm.message_history]
        
        # Return the response along with the serialized message history
        return {
            "response": response,
            "message_history": serialized_history
        }
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger.error(f"Error in query_model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint that returns API info
@app.get("/", summary="API info")
async def root():
    """Get API information"""
    return {
        "name": "AI Tutors API",
        "version": "1.0.0",
        "endpoints": {
            "/query": "POST - Send a prompt to the AI tutor",
            "/init_request": "GET - Get the initial greeting message from the tutor"
        }
    }

# Function to run the API server
def run_api(host: str = "0.0.0.0", port: int = 8000) -> None:
    """
    Run the FastAPI server.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
    """
    import uvicorn
    logger.info(f"Starting AI Tutors API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

# Allow running the file directly
if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    run_api(port=port) 