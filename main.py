import time
import streamlit as st
from utils.tutor_data import read_csv
from utils.menu import menu

# Load tutor data
st.session_state["ai_tutors_data_fn"] = 'data/tutor_info.csv'#'ai-tutors/tutor_info.csv'
st.session_state["df_tutors"] = read_csv(st.session_state["ai_tutors_data_fn"])

# Page info
st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/educational-prompt-engineering/main/images/science_tutor_favicon_small.png", layout="wide")
st.markdown("<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)

# Display intro text
intro_text = 'Super simple, kinda slow, pretty reliable.'
def stream_text():
    for word in intro_text.split(" "):
        yield word + " "
        time.sleep(0.2)
col1, col2, col3 = st.columns(3)
col2.write_stream(stream_text)

# FOR TESTING
if "user_email" not in st.session_state:
    st.session_state.user_email = 'obriaintb@gmail.com'

# Select role
col1, col2, col3 = st.columns(3)
with col2:
    if st.button(f"Teachers"):
        st.session_state.role = 'teacher'
        st.switch_page("pages/login.py")
    if st.button(f"Students"):
        st.session_state.role = 'student'
        st.switch_page("pages/explore_tutors.py")