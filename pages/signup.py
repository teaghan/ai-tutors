import streamlit as st
from streamlit_authenticator.utilities import RegisterError
from utils.user_data import save_yaml
from utils.session import check_state
from utils.cookies import update_cookies

st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png",  layout="wide")
st.markdown("<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)
st.markdown("----")

# If necessary, load tutor data, user data, and load cookies
check_state()

# Creating a new user registration widget
try:
    (user_email,
     username,
    user_name) = st.session_state.authenticator.register_user(merge_username_email=True, 
                                                              roles=['teacher'],
                                                              fields={'Form name':'Teacher Sign-up', 'Email':'Email', 
                                                                    'Username':'Username', 'Password':'Password',       
                                                                    'Repeat password':'Repeat password', 
                                                                    'Password hint':'Password hint', 
                                                                    'Captcha':'Captcha', 'Register':'Register'})
    if user_email:
        st.success('User registered successfully')
        save_yaml(st.session_state.users_data_fn, 
                  st.session_state.users_config)
        # Username and email are the same
        st.session_state.username = user_email
        st.session_state.user_email = user_email
        st.session_state['authentication_status'] = None
        update_cookies()
        # Go to teacher dashboard
        st.switch_page("pages/login.py")
except RegisterError as e:
    st.error(e)
