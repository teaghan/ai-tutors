import streamlit as st
from utils.menu import menu
from utils.display_tutors import display_tools

# Streamlit
st.set_page_config(page_title='AI Tutors', page_icon="https://raw.githubusercontent.com/teaghan/educational-prompt-engineering/main/images/science_tutor_favicon_small.png", layout="wide")

# Title
st.markdown(f"<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)

# Display sidebar menu
menu()

# Create tabs for Public Tutors and My Tutors
if st.session_state.role == 'student':
    tab1, tab2 = st.tabs(["Access Code", "Public Tutors"])
    # Display Public Tutors in tab2 
    with tab2:
        display_tools(show_all=True)
else:
    tab1, tab2 = st.tabs(["Public Tutors", "My Tutors"])
    # Display Public Tutors in tab1 (includes all tools, regardless of the creator)
    with tab1:
        display_tools(show_all=True)

    # Display My Tutors in tab2 (only tools created by the current user)
    with tab2:
        display_tools(show_all=False, allow_edit=True)
