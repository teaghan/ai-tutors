from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI

def load_text_file(file_path):
    return open(file_path, 'r').read()

class AITutor:
    """
    A class that facilitates a back-and-forth conversation between a student and an AI tutor.
    It uses an LLM (Large Language Model) to guide students through questions, provide feedback, 
    and help them understand science concepts without directly giving them the answers.

    This class is designed to work with any LLM that has a chat function.

    Attributes:
        llm (Any LLM with a chat function): The LLM model used to interact with the student.
        message_history (list): A history of messages exchanged between the student and the tutor.
    
    Methods:
        initiate_conversation(grade, topic): Initiates the tutoring session by asking the student for more details.
        get_response(student_input): Handles student input and provides a response using the LLM.
        get_message_history(): Returns the history of messages in the conversation.
    """

    def __init__(self, llm_model, instructions, introduction, display_system=False):
        self.llm = llm_model
        self.message_history = []
        self.introduction = introduction

        # Add these as a "system prompt"
        system_prompt = "# AI Tutor Instructions\n\n"
        system_prompt += "Below are the guidelines for the tutor's interactions with the user:\n\n"
        system_prompt += f"{instructions}\n\n"
        system_prompt += """
**Math Formatting:**
   - Importantly, **NEVER USE `\(`, `\)` OR `\[`, `\]` FORMATTING FOR MATH IN ANY OF MY COMMUNICATION OR CONTENT. STRICTLY USE `$`,`$` OR `$$`,`$$` FORMATTING.**
   - This is extremely important because the `\(\)` and `\[\]` formatting will not work when displayed to the user.
        """
        system_prompt += "\n\n## Your Task\n\n"
        system_prompt += "You are a helpful AI tutor/assistant. "
        system_prompt += "Following the instructions above, provide supportive assistance to the student user."
        if display_system:
            print(system_prompt)
        
        # Initialize the conversation with the system prompt
        self.message_history.append(ChatMessage(role="system", content=system_prompt))
        
        # Append initial request from AI tutor
        self.initiate_conversation()

    def initiate_conversation(self):
        """
        Initiates the conversation with the student, asking for the grade level and topic they are working on.
        """

        self.message_history.append(ChatMessage(role="assistant", content=self.introduction))

    def get_response(self, student_input):
        """
        Handles student input and provides a response.
        The LLM will respond based on the system instructions, conversation history, and the input provided by the student.
        """
        # Add the student's message to the history
        self.message_history.append(ChatMessage(role="user", content=student_input))
        
        # Get the response from the LLM
        response = self.llm.chat(self.message_history).message.content
        
        # Add the AI's response to the history
        self.message_history.append(ChatMessage(role="assistant", content=response))
        
        return response