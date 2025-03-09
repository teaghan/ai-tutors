import streamlit as st
from utils.session import check_state
from utils.password import send_email_forgot_password
from utils.user_data import save_yaml

st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png",  layout="wide")
st.markdown("<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)

# If necessary, load tutor data, user data, etc.
check_state(check_user=False, reset_chat=True, rebuild=True, reset_banner=True)

if 'password_sent' not in st.session_state:
    st.session_state['password_sent'] = False

try:
    username_of_forgotten_password, \
    email_of_forgotten_password, \
    new_random_password = st.session_state.authenticator.forgot_password()
    if username_of_forgotten_password:
        send_email_forgot_password(email_of_forgotten_password, new_random_password)
        st.success('New password sent to your email!')
        st.session_state['password_sent'] = True
        save_yaml(st.session_state.users_data_fn, 
                  st.session_state.users_config)
        st.switch_page("pages/login.py")
    elif username_of_forgotten_password == False:
        st.error('Username not found')
except Exception as e:
    st.error(e)