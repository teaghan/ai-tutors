import streamlit as st

st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/educational-prompt-engineering/main/images/science_tutor_favicon_small.png", layout="wide")

st.markdown("<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col2:
    if st.button(f"Login"):
        st.switch_page("pages/dashboard.py")
    if st.button(f"Sign Up"):
        st.switch_page("pages/dashboard.py")