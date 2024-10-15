import streamlit as st

st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png",  layout="wide")

st.markdown("<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)

st.markdown("----")

col1, col2, col3 = st.columns(3)
with col2:
    if st.button(f"Login", use_container_width=True):
        st.switch_page("pages/login.py")
    if st.button(f"Sign Up", use_container_width=True):
        st.switch_page("pages/signup.py")