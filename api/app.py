from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import sys

# Print debug message to track when this module is imported
print(f"API module imported by: {__name__}", file=sys.stderr)

# Import the tutor module - Fix import path
from api.tutor import load_tutor_info
from llms.tutor_llm import TutorChain
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
    tutor_info: Optional[Dict[str, Any]]

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

# Endpoint to get tutor information
@app.get("/tutor_info", summary="Get tutor information")
async def get_tutor_info(access_code: str):
    """
    Get all information about the tutor associated with the access code.
    
    Args:
        access_code: Your AI Tutor access code
        
    Returns:
        All tutor information needed to instantiate a tutor
    """
    try:
        # Load tutor info using the provided access code
        tutor_info = load_tutor_info(access_code)
        
        # Return all tutor information including the initial request
        return tutor_info
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger.error(f"Error in get_tutor_info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to call the LLM
@app.post("/query", summary="Send a query to the AI tutor")
async def query_model(request: PromptRequest):
    """
    Send a query to the AI tutor and get a response.
    
    Args:
        request: Request object containing user prompt, access code, tutor info, and optional message history
        
    Returns:
        The tutor's response and updated message history
    """
    try:
        # Use the provided tutor_info if available, otherwise load it
        tutor_info = request.tutor_info
        if not tutor_info:
            tutor_info = load_tutor_info(request.access_code)
        
        # Create a TutorChain instance from the tutor info
        tutor = TutorChain(
            instructions=tutor_info.get("instructions", ""),
            guidelines=tutor_info.get("guidelines", ""),
            introduction=tutor_info.get("introduction", ""),
            knowledge=tutor_info.get("knowledge", "")
        )

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
            "/tutor_info": "GET - Get all tutor information",
            "/init_request": "GET - Get the initial greeting message from the tutor (deprecated)"
        }
    }