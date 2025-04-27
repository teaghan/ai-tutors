import requests
from IPython.display import Markdown, display
from IPython import get_ipython
from typing import Optional

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
            try:
                base_url = 'https://ai-tutors-252d0369f9d6.herokuapp.com/'
                if 'herokuapp.com' in base_url:
                    base_url = base_url.rstrip("/") + '/api'
            except Exception as e:
                print(f"Error loading config, using default local URL: {str(e)}")
                base_url = 'http://localhost:8000'
            
        self.access_code = access_code
        self.base_url = base_url
        self.message_history = []
        self.verbose = verbose
        
        # Tutor information attributes
        self.instructions = ""
        self.guidelines = ""
        self.introduction = ""
        self.knowledge = ""
        self.description = ""
        self.availability = ""
        self.tool_name = ""
        self.teacher_email = ""

        # Check if user is in a Jupyter notebook
        self.is_notebook = False
        try:
            if get_ipython() is not None:
                self.is_notebook = True
        except NameError:
            pass

        # Validate connection by checking API status
        try:
            status_response = requests.get(f"{self.base_url}/")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Could not connect to AI Tutor API at {self.base_url}. "
                "Make sure the API server is running and check your network connection."
            )
        
        # Get tutor information
        try:
            self.load_tutor_info()
            
            if self.verbose:
                if self.is_notebook:
                    printmd('\n\n**AI Tutor:**\n\n'+ self.introduction)
                else:
                    print('\n\nAI Tutor:\n\n'+ self.introduction)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error getting tutor information: {str(e)}")
    
    def load_tutor_info(self) -> None:
        """
        Get tutor information from the API and store it as attributes.
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}/tutor_info"
        params = {"access_code": self.access_code}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            tutor_info = response.json()
            
            # Store tutor information as attributes
            self.instructions = tutor_info.get("instructions", "")
            self.guidelines = tutor_info.get("guidelines", "")
            self.introduction = tutor_info.get("introduction", "")
            self.knowledge = tutor_info.get("knowledge", "")
            self.description = tutor_info.get("description", "")
            self.availability = tutor_info.get("availability", "")
            self.tool_name = tutor_info.get("tool_name", "")
            self.teacher_email = tutor_info.get("teacher_email", "")
            
            return tutor_info
        except Exception as e:
            print(f"Error in load_tutor_info: {str(e)}")
            raise
    
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
                    printmd('\n\n**AI Tutor:**\n\n'+ self.introduction)
                else:
                    print('\n\nAI Tutor:\n\n'+ self.introduction)
            self.message_history = []

        if self.verbose:
            if self.is_notebook:
                printmd('\n\n**Student:** ')
                print(prompt)
            else:
                print('\n\nStudent: ' + prompt)
        
        # API endpoint for querying the model
        url = f"{self.base_url}/query"
        
        # Prepare tutor info
        tutor_info = {
            "instructions": self.instructions,
            "guidelines": self.guidelines,
            "introduction": self.introduction,
            "knowledge": self.knowledge,
            "description": self.description,
            "availability": self.availability,
            "tool_name": self.tool_name,
            "teacher_email": self.teacher_email,
        }
        
        # Prepare payload
        payload = {
            "user_prompt": prompt,
            "access_code": self.access_code,
            "message_history": self.message_history,
            "tutor_info": tutor_info
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
                printmd('\n\n**AI Tutor:**\n\n'+ self.introduction)
            else:
                print('\n\nAI Tutor:\n\n'+ self.introduction)
                
    def display_tutor_info(self) -> None:
        """
        Display the tutor information in a formatted way.
        Uses markdown formatting in Jupyter notebooks and plain text otherwise.
        """
        if self.is_notebook:
            info = f"""
## Tutor Information

**Name:** {self.tool_name}

**Description:** {self.description}

**Instructions:**\n\n{self.instructions}

**Guidelines:**\n\n{self.guidelines}

**Knowledge Base:**\n\n{self.knowledge}
"""
            printmd(info)
        else:
            print("\n===== Tutor Information =====\n")
            print(f"Name: {self.tool_name}")
            print(f"Description: {self.description}")
            print(f"Instructions:\n{self.instructions}")
            print(f"Guidelines:\n{self.guidelines}")
            print(f"Knowledge Base:\n{self.knowledge}")
            print("\n=============================\n")
