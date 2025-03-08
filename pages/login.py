import streamlit as st
from streamlit_authenticator.utilities import LoginError
from utils.session import check_state

st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png",  layout="wide")

# If necessary, load tutor data, user data, etc.
check_state(reset_chat=True, rebuild=True, reset_banner=True)

st.markdown("<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)

if 'password_sent' in st.session_state and st.session_state['password_sent']:
    st.success('New password sent to your email!')

# Creating a login widget
try:
    st.session_state.authenticator.login(fields={'Username':'Email'})
except LoginError as e:
    st.error(e)

# Authenticating user
if st.session_state['authentication_status']:
    # Username and email are the same
    st.session_state.user_email = st.session_state.username
    if 'password_sent' in st.session_state and st.session_state['password_sent']:
        st.session_state['password_sent'] = False
        st.switch_page("pages/change_password.py")
    else:
        # Go to teacher dashboard
        st.switch_page("pages/dashboard.py")
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')

_, _, _, col4 = st.columns(4)
with col4:
    if st.button(f"Forgot Password?", use_container_width=True):
        st.switch_page("pages/forgot_password.py")