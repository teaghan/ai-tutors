import streamlit as st
from utils.menu import menu

# Streamlit info
st.set_page_config(page_title='Dashboard', page_icon="https://raw.githubusercontent.com/teaghan/educational-prompt-engineering/main/images/science_tutor_favicon_small.png", layout="wide")

# Title
st.markdown(f"<h1 style='text-align: center; color: grey;'>Your Dashboard</h1>", unsafe_allow_html=True)

# Display page buttons
menu()
