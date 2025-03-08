import streamlit as st
from llama_index.core.llms import ChatMessage
from llama_index.core.prompts import PromptTemplate

def load_text_file(file_path):
    return open(file_path, 'r').read()

class ContentModerator:
    """

    Attributes:
        llm (Any LLM with a chat and query function): The LLM model used to moderate and correct AI responses
    
    Methods:

    """

    def __init__(self, guidelines, llm_model, chat_engine=None, display_guidelines=False):
        self.llm = llm_model
        self.chat_engine = chat_engine
        # Load pre-defined moderation guidelines
        self.guidelines = guidelines

        # Optionally print out the guidelines
        if display_guidelines:
            print(f"The following guidelines will be used:\n")
            print(self.guidelines)


    def moderate_response(self, chat_history, ai_response):
        """
        Uses the LLM to moderate the AI tutor's response based on the loaded guidelines and the full chat history.
    
        Arguments:
            chat_history (str): The full chat history (formatted as a string).
            ai_response (str): The response provided by the AI tutor that needs moderation.
    
        Returns:
            tuple: 
                - moderator_response (str): Feedback from the moderator explaining the decision.
                - is_appropriate (bool): Indicates whether the AI response is appropriate or not (True for appropriate, False for inappropriate).
        """

        system_prompt = f'''
# Your Task

Based on the moderation guidelines below, your task is to determine if the response from the AI assistant is appropriate given the prior conversation.

# Response Format 

Go through each guideline, one-by-one, and QUICKLY determine whether or not the response violates or does no violate that guideline.

Your response should finish with a clear indictor on a separate line including either

"Yes. The response is appropriate."

or 

"No. The response is not appropriate."

# Moderation Guidelines

{self.guidelines}

### Additional Guidelines to Assess

1. **Math Formatting:**
   - Responses should **NEVER USE `\(`, `\)` OR `\[`, `\]` FORMATTING FOR MATH IN ANY OF MY COMMUNICATION OR CONTENT.** Responses should **STRICTLY USE `$`,`$` OR `$$`,`$$` FORMATTING.**
"
        '''
            
        # Formulate the query for moderation based on the full chat history
        query = f'''
Based on the moderation guidelines, is the following AI response appropriate given the prior conversation?

# Chat History:\n\n
{chat_history}

# AI Response:\n\n
"{ai_response}"
        '''

        message_history = [ChatMessage(role="system", content=system_prompt),
                           ChatMessage(role="user", content=query)]
        
        # Query the moderator LLM with the response
        moderation_result = self.llm.chat(message_history).message.content
        
        # Extract the moderator's feedback from the response (full response)
        moderator_response = moderation_result.strip()
        
        # Check the final line of the response for the appropriateness indicator
        last_line = moderator_response.splitlines()[-1].strip()
        is_appropriate = "yes" in last_line.lower()

        return moderator_response, is_appropriate

    def correct_response(self, chat_history, ai_response, moderator_feedback):
        """
        Generates a corrected response based on the chat history, AI tutor's inappropriate response(s), 
        and moderator feedback(s).
        
        Arguments:
            chat_history (str): The full chat history before the AI response.
            ai_response (str or list): The AI tutor's inappropriate response or a list of responses.
            moderator_feedback (str or list): Feedback explaining why the response(s) were inappropriate 
                                            or a list of feedbacks.
        
        Returns:
            str: The corrected response generated by the LLM, ensuring alignment with the guidelines.
        """

        # Handle ai_response and moderator_feedback being lists or strings
        if isinstance(ai_response, list):
            ai_response = "\n\n".join([f"**AI Response {i+1}**:\n\n \"{resp}\"" for i, resp in enumerate(ai_response)])
        if isinstance(moderator_feedback, list):
            moderator_feedback = "\n\n".join([f"**Moderator Feedback {i+1}**:\n\n {feedback}" for i, feedback in enumerate(moderator_feedback)])

        system_prompt = f'''
# Your Task

You will be given a chat history between a student and an AI assistant along with the moderator's feedback on why the response was inappropriate.

Your task is to take this feedback and create a new response that is appropriate for the conversation and aligns with the moderator guidelines.

The corrected response should CONTINUE THE CONVERSATION BETWEEN THE USER AND ASSISTANT in a way that is aligned with the system instructions and guidelines.

# Response Format 

Respond ONLY WITH THE CORRECTED RESPONSE.

{self.guidelines}
        '''

        # Combine the chat history, AI response, and moderator feedback into a correction prompt
        correction_prompt = f"""
The AI assistant gave the following inappropriate response(s) in this conversation:

### **Chat History**:\n\n{chat_history}\n\n
### **AI Assistant's Response(s)**:\n\n{ai_response}\n\n
### **Moderator's Feedback(s)**:\n\n{moderator_feedback}

Your Task: Provide a corrected response based on the full conversation that is appropriate according to the moderation guidelines. Respond ONLY WITH THE CORRECTED RESPONSE.
        """

        '''
        message_history = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=correction_prompt)
        ]

        # Run the correction prompt through the corrector LLM
        if self.chat_engine is not None:
            corrected_response = self.chat_engine.chat(correction_prompt, message_history[:-1]).response
        else:
            corrected_response = self.llm.chat(message_history).message.content
        '''

        prompt = PromptTemplate(system_prompt+'\n\n'+correction_prompt)

        # Run the correction prompt through the corrector LLM
        if self.chat_engine is not None:
            corrected_response = self.chat_engine.predict(prompt)
        else:
            corrected_response = self.llm.predict(prompt)

        # Optionally remove quotes if they exist in the output
        if corrected_response.startswith('"') and corrected_response.endswith('"'):
            corrected_response = corrected_response[1:-1]

        return corrected_response

    def final_correction(self, chat_history, previous_responses, previous_feedback):
        """
        Moderates and potentially corrects the AI tutor's latest response. If the response is deemed inappropriate, 
        it is corrected based on the moderation feedback.
    
        Arguments:
            chat_history (list): The full chat history (a list of dictionaries containing both student and AI messages).
    
        Returns:
            dict: A dictionary containing:
                - previous_conversation (str): The back-and-forth conversation history up to the latest AI response.
                - ai_response (str): The latest AI response from the chat history.
                - moderator_feedback (str): Feedback explaining the moderation decision.
                - final_response (str): The final response provided to the student (either the original or corrected response).
        """
        # Ensure chat_history is not empty
        if not chat_history:
            raise ValueError("Chat history cannot be empty.")
        
        # Combine all prior messages (before the last AI response) into the conversation context
        previous_conversation = "\n\n".join([f"**{message.role.value}**: {message.content}" for message in chat_history[:-1]])
        
        # If the response is inappropriate, pass it to the corrector LLM
        with st.spinner('Correcting my response...'):
            final_response = self.correct_response(previous_conversation, previous_responses, previous_feedback)
        
        return final_response
    
    
    def forward(self, chat_history):
        """
        Moderates and potentially corrects the AI tutor's latest response. If the response is deemed inappropriate, 
        it is corrected based on the moderation feedback.
    
        Arguments:
            chat_history (list): The full chat history (a list of dictionaries containing both student and AI messages).
    
        Returns:
            dict: A dictionary containing:
                - previous_conversation (str): The back-and-forth conversation history up to the latest AI response.
                - ai_response (str): The latest AI response from the chat history.
                - moderator_feedback (str): Feedback explaining the moderation decision.
                - final_response (str): The final response provided to the student (either the original or corrected response).
        """
        # Ensure chat_history is not empty
        if not chat_history:
            raise ValueError("Chat history cannot be empty.")
        
        # Separate the last message (assumed to be the AI's response)
        latest_message = chat_history[-1]
        
        # Ensure the latest message is from the AI
        if latest_message.role.value != 'assistant':
            raise ValueError("The latest message in the chat history must be from the AI.")
        
        # Extract the AI response
        ai_response = latest_message.content
        
        # Combine all prior messages (before the last AI response) into the conversation context
        previous_conversation = "\n\n".join([f"**{message.role.value}**: {message.content}" for message in chat_history[:-1]])
    
        # Moderate the AI response using the full previous conversation context
        with st.spinner('Considering my response...'):
            moderator_feedback, is_appropriate = self.moderate_response(previous_conversation, ai_response)
        
        # If the response is inappropriate, pass it to the corrector LLM
        if not is_appropriate:
            with st.spinner('Correcting my response...'):
                corrected_response = self.correct_response(previous_conversation, ai_response, moderator_feedback)
            final_response = corrected_response
        else:
            final_response = ai_response
        
        # Return a dictionary detailing the process and result
        return {
            "previous_conversation": previous_conversation,
            "ai_response": ai_response,
            "moderated": not is_appropriate,
            "moderator_feedback": moderator_feedback,
            "final_response": final_response
        }