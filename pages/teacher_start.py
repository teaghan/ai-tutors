import streamlit as st
import time

st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png",  layout="wide")

if "user_email" not in st.session_state:
    st.switch_page("main.py")

st.markdown("<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)

st.markdown("----")

# Text to be displayed with newlines
text = (
    'Provide realtime feedback\n'
    'Facilitate differentiated instruction\n'
    'Deliver personalized learning\n'
    'Build it your own way'
)

# Function to stream text letter by letter
def stream_text(text):
    sentence = ""
    for letter in text:
        sentence += letter
        yield sentence.replace("\n", "<br>")  # Use <br> for new lines
cols = st.columns((2, 2, 1.4))
if "slow_write_teacher" not in st.session_state:
    st.session_state["slow_write_teacher"] = True
if st.session_state.slow_write_teacher:
    with cols[1]:
        with st.empty():
            for sentence in stream_text(text):
                st.markdown(f"<h4 style='color: grey;'>{sentence}</h4>", unsafe_allow_html=True)
                time.sleep(0.01)
    st.session_state.slow_write_teacher = False
else:
    cols[1].markdown(f"<h4 style='color: grey;'>{text.replace("\n", "<br>")}</h4>", unsafe_allow_html=True)

st.markdown("----")

col1, col2, col3 = st.columns((1.4, 1.5, 1.5))
with col2:
    if st.button(f"Login", use_container_width=True):
        st.switch_page("pages/login.py")
    if st.button(f"Sign Up", use_container_width=True):
        st.switch_page("pages/signup.py")