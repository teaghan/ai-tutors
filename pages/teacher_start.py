import streamlit as st
from utils.session import check_state
from utils.styling import stream_lines

st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png",  layout="wide")

check_state()

st.markdown("<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)

# Text to be displayed with newlines
text = (
    'Provide realtime feedback\n'
    'Facilitate differentiated instruction\n'
    'Deliver personalized learning\n'
    'Build it your own way'
)
cols = st.columns((1.4, 2, 1.5))
if "slow_write_teacher" not in st.session_state:
    st.session_state["slow_write_teacher"] = True
with cols[1]:
    stream_lines(
        text=text,
        pause_time=0.01,
        initial_pause=0.5,
        slow_write=st.session_state["slow_write_teacher"],
        center=True
    )
    st.session_state["slow_write_teacher"] = False
st.markdown("----")

col1, col2, col3 = st.columns((1.4, 1.5, 1.5))
with col2:
    if st.button(f"Login", type="primary", use_container_width=True):
        st.session_state['authentication_status'] = None
        st.switch_page("pages/login.py")
    if st.button(f"Sign Up", use_container_width=True):
        st.switch_page("pages/signup.py")