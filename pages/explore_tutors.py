import streamlit as st
from utils.menu import menu
from utils.display_tutors import display_tools
from utils.access_codes import use_code
from utils.tutor_data import reset_build
from utils.chatbot_setup import reset_chatbot 

# Streamlit
st.set_page_config(page_title='AI Tutors', page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png",  layout="wide")

# Title
st.markdown(f"<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)

if "user_email" not in st.session_state:
    st.switch_page("main.py")

# Display sidebar menu
menu()

# Reset info
reset_chatbot()
reset_build(reset_banner=True)

# Create tabs for Public Tutors and My Tutors
if st.session_state.role == 'student':
    tab1, tab2 = st.tabs(["Access Code", "Public Tutors"])
    with tab1:
        access_code = st.text_input('Enter your 6-digit access code:')
        if st.button(r"Launch Tutor", type="primary", use_container_width=True):
            use_code(st.session_state.df_access_codes, st.session_state.df_tutors, access_code)
    # Display Public Tutors in tab2 
    with tab2:
        display_tools(show_all=True)
else:
    tab1, tab2 = st.tabs(["Public Tutors", "My Tutors"])
    # Display Public Tutors in tab1 (includes all tools, regardless of the creator)
    with tab1:
        display_tools(show_all=True, allow_copy=True, access_codes=True)

    # Display My Tutors in tab2 (only tools created by the current user)
    with tab2:
        display_tools(show_all=False, user_display=True, allow_edit=True, allow_copy=True, access_codes=True)
