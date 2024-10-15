import time
import streamlit as st
from utils.tutor_data import read_csv
from utils.user_data import read_users

from utils.menu import menu

# Page info
st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/educational-prompt-engineering/main/images/science_tutor_favicon_small.png", layout="wide")
st.markdown("<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)

# Load tutor data
if "ai_tutors_data_fn" not in st.session_state:
    st.session_state["ai_tutors_data_fn"] = 'ai-tutors/tutor_info.csv'#'data/tutor_info.csv'
if "df_tutors" not in st.session_state:
    st.session_state["df_tutors"] = read_csv(st.session_state["ai_tutors_data_fn"])

# Load user data
if "users_data_fn" not in st.session_state:
    st.session_state["users_data_fn"] = 'ai-tutors/users.yaml'#'data/users.yaml'
if "users_config" not in st.session_state:
    st.session_state["users_config"], st.session_state["authenticator"] = read_users(st.session_state["users_data_fn"])

# Load access codes data
if "access_codes_data_fn" not in st.session_state:
    st.session_state["access_codes_data_fn"] = 'ai-tutors/access_codes.csv'#'data/access_codes.csv'
if "df_access_codes" not in st.session_state:
    st.session_state["df_access_codes"] = read_csv(st.session_state["access_codes_data_fn"])

if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "role" not in st.session_state:
    st.session_state.user_email = None

# Display intro text
intro_text = 'Super simple, kinda slow, pretty reliable.'
def stream_text():
    for word in intro_text.split(" "):
        yield word + " "

        time.sleep(0.2)

cols = st.columns((1.5, 1, 1.5))
cols[1].write_stream(stream_text)

st.markdown("----")

# Select role
col1, col2, col3 = st.columns(3)
with col2:
    if st.button(f"Teachers", use_container_width=True):
        st.session_state.role = 'teacher'
        if st.session_state['authentication_status']:
            st.switch_page("pages/dashboard.py")
        else:
            st.switch_page("pages/teacher_start.py")
    if st.button(f"Students", use_container_width=True):
        st.session_state.role = 'student'
        st.switch_page("pages/explore_tutors.py")