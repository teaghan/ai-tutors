import requests
from IPython.display import Markdown, display
from IPython import get_ipython
from typing import List, Dict, Any, Optional
from utils.config import open_config
import traceback

# Jupyter notebook print function
def printmd(string: str) -> None:
    display(Markdown(string))

class AITutor:
    """
    Python client for interacting with the AI Tutor API.
    This provides a simple interface for users who install the package to interact with their tutor.
    """
    
    def __init__(self, access_code: str, base_url: Optional[str] = None, verbose: bool = True):
        """
        Initialize the AI Tutor client.
        
        Args:
            access_code (str): Your AI Tutor access code
            base_url (str): The base URL of the API
            verbose (bool): Whether to print responses to console
        """
        if base_url is None:
            # Simple adjustment to automatically handle Heroku and non-Heroku URLs
            base_url = open_config()['domain']['url']
            if 'herokuapp.com' in base_url:
                base_url = base_url.rstrip("/") + '/api'
            
        print(f"Using base URL: {base_url}")
        self.access_code = access_code
        self.base_url = base_url
        self.message_history = []
        self.verbose = verbose

        # Check if user is in a Jupyter notebook
        self.is_notebook = False
        try:
            if get_ipython() is not None:
                self.is_notebook = True
        except NameError:
            pass

        # Validate connection by checking API status
        try:
            requests.get(f"{self.base_url}/")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Could not connect to AI Tutor API at {self.base_url}. "
                "Make sure the API server is running and check your network connection."
            )
        
        # Get initial message
        try:
            self.init_message = self.get_init_request()
            if self.verbose:
                if self.is_notebook:
                    printmd('\n\n**AI Tutor:**\n\n'+ self.init_message)
                else:
                    print('\n\nAI Tutor:\n\n'+ self.init_message)
        except requests.exceptions.RequestException as e:
            print(f"Error getting initial greeting: {str(e)}")
            traceback.print_exc()
            raise ConnectionError(f"Error getting initial greeting: {str(e)}")
        
    def get_init_request(self) -> str:
        """
        Get the initial greeting message from the AI Tutor.
        
        Returns:
            str: The initial greeting message
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}/init_request"
        params = {"access_code": self.access_code}
        response = requests.get(url, params=params)
        print(f"Response: {response}")
        response.raise_for_status()
        result = response.json()
        return result.get("init_request", "")
    
    def get_response(self, prompt: str, restart_chat: bool = False) -> str:
        """
        Send a question or prompt to your AI Tutor and get a response.
        
        Args:
            prompt (str): The question or prompt for your tutor
            restart_chat (bool): If True, restart the conversation from scratch
            
        Returns:
            str: The tutor's response
            
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        # Reset conversation if requested
        if restart_chat:
            if self.verbose:
                if self.is_notebook:
                    printmd('\n\n**AI Tutor:**\n\n'+ self.init_message)
                else:
                    print('\n\nAI Tutor:\n\n'+ self.init_message)
            self.message_history = []

        if self.verbose:
            if self.is_notebook:
                printmd('\n\n**Student:** ')
                print(prompt)
            else:
                print('\n\nStudent: ' + prompt)
        
        # API endpoint for querying the model
        url = f"{self.base_url}/query"
        
        # Prepare payload
        payload = {
            "user_prompt": prompt,
            "access_code": self.access_code,
            "message_history": self.message_history
        }
        
        # Send request to API
        response = requests.post(
            url, 
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Raise exception if request failed
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        # Get the response text
        ai_response = result["response"]
        self.message_history = result["message_history"]

        if self.verbose:
            if self.is_notebook:
                printmd('\n\n**AI Tutor:**\n\n'+ ai_response)
            else:
                print('\n\nAI Tutor:\n\n'+ ai_response)
        return ai_response
        
    def get_message_history(self):
        """
        Get the full conversation history.
        
        Returns:
            list: List of message dictionaries with 'role' and 'content' keys
        """
        return self.message_history 
    
    def reset_chat(self) -> None:
        """
        Reset the conversation history and display the initial greeting.
        """
        self.message_history = []
        if self.verbose:
            if self.is_notebook:
                printmd('\n\n**AI Tutor:**\n\n'+ self.init_message)
            else:
                print('\n\nAI Tutor:\n\n'+ self.init_message)
