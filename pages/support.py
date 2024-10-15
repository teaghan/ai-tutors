import streamlit as st
from utils.menu import menu


# Streamlit info
st.set_page_config(page_title='Support', page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png",  layout="wide")

# Title
st.markdown(f"<h1 style='text-align: center; color: grey;'>Support</h1>", unsafe_allow_html=True)

if "user_email" not in st.session_state:
    st.switch_page("main.py")

# Display page buttons
menu()



st.markdown("""
Please email build.ai.tutors@gmail.com if you have a

- question to ask
- feature to request
- bug to report
""")

