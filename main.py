import time
import streamlit as st

# Page info
st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png", layout="wide")
st.markdown("<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)

from utils.session import check_state, user_reset
from utils.cookies import update_cookies

# If necessary, load tutor data, user data, and load cookies
check_state()

# Text to be displayed with newlines
text = 'Built by teachers for students.'
# Function to stream text letter by letter
def stream_text(text):
    sentence = ""
    for letter in text:
        sentence += letter
        yield sentence.replace("\n", "<br>")

cols = st.columns((1.4, 2, 1.4))
if "slow_write_main" not in st.session_state:
    st.session_state["slow_write_main"] = True
if st.session_state.slow_write_main:
    time.sleep(0.7)
    with cols[1]:
        with st.empty():
            for sentence in stream_text(text):
                st.markdown(f"<h4 style='text-align: center; color: grey;'>{sentence}</h4>", unsafe_allow_html=True)
                time.sleep(0.02)
    st.session_state.slow_write_main = False
else:
    with cols[1]:
        st.markdown(f"<h4 style='text-align: center; color: grey;'>{text}</h4>", unsafe_allow_html=True)
st.markdown("----")

# Select role
col1, col2, col3 = st.columns((1.3, 2, 1.4))
with col2:
    if st.button(f"Teachers", use_container_width=True):
        st.session_state.role = 'teacher'
        update_cookies()
        if st.session_state['authentication_status']:
            st.switch_page("pages/dashboard.py")
        else:
            st.switch_page("pages/teacher_start.py")
    if st.button(f"Students", use_container_width=True):
        user_reset()
        st.session_state.role = 'student'
        update_cookies()
        st.switch_page("pages/explore_tutors.py")
