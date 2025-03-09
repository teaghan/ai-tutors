import streamlit as st
from utils.menu import menu
from utils.user_data import save_yaml
from utils.session import check_state

st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png",  layout="wide")
st.markdown("<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)
st.markdown("----")

# If necessary, load tutor data, user data, etc.
check_state(check_user=True)

# Display page buttons
menu()

if st.session_state['authentication_status']:
    try:
        if st.session_state.authenticator.reset_password(st.session_state['username']):
            st.success('Password modified successfully')
            save_yaml(st.session_state.users_data_fn, 
                  st.session_state.users_config)
            # Go to teacher dashboard
            st.switch_page("pages/dashboard.py")
    except Exception as e:
        st.error(e)
