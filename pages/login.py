import streamlit as st
from utils.user_data import get_email

import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)
from utils.tutor_data import reset_build
from utils.chatbot_setup import reset_chatbot 

st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png",  layout="wide")

st.markdown("<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)

st.markdown("----")

# Reset info
reset_chatbot()
reset_build()


# Creating a login widget
try:
    st.session_state.authenticator.login(fields={'Username':'Email'})
except LoginError as e:
    st.error(e)

# Authenticating user
if st.session_state['authentication_status']:
    # Username and email are the same
    st.session_state.user_email = st.session_state.username
    # Go to teacher dashboard
    st.switch_page("pages/dashboard.py")
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')
