import streamlit as st

from llms.chatbot_llm import AITutor
from llms.moderator_llm import ContentModerator
from llms.models import get_llm

class TutorChain:
    def __init__(self, 
                 instructions, 
                 guidelines,
                 introduction, 
                 knowledge):

        # Initialize the OpenAI LLM
        llm_model = get_llm()
        
        # Initialize the tutor with the LLM and instructions
        self.tutor_llm = AITutor(llm_model, instructions, introduction, guidelines, knowledge, display_system=False)
        self.init_request = self.tutor_llm.message_history[-1].content

        # Create an instance of the ContentModerator class
        self.moderator_llm = ContentModerator(llm_model, guidelines, instructions)

    def get_response(self, student_prompt, moderate=True, max_moderations=3):
        if 'chat_spinner' in st.session_state:
            # Prompt AI tutor
            with st.session_state.chat_spinner, st.spinner('Coming up with a response...'):
                ai_response = self.tutor_llm.get_response(student_prompt)
        else:
            # Prompt AI tutor
            with st.spinner('Coming up with a response...'):
                ai_response = self.tutor_llm.get_response(student_prompt)

        if moderate:
            num_moderations = 0
            needs_checking = True
            responses = []
            feedback = []
            while needs_checking and num_moderations<max_moderations:
                # Moderate response
                results = self.moderator_llm.forward(self.tutor_llm.message_history)
                ai_response = results['final_response']
                # Update chat history
                self.tutor_llm.message_history[-1].content = ai_response

                num_moderations += 1
                responses.append(ai_response)
                feedback.append(results['moderator_feedback'])
                print(results['moderator_feedback'])

                if not results['moderated']:
                    # Response is good to go
                    needs_checking = False

            if needs_checking:
                # If still needs checking, run on last correction
                ai_response = self.moderator_llm.final_correction(self.tutor_llm.message_history, responses, feedback)
                # Update chat history
                self.tutor_llm.message_history[-1].content = ai_response

        return ai_response 



            