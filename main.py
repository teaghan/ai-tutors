import streamlit as st
# Page info
st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png", layout="wide")

from utils.session import check_state, user_reset
from utils.styling import stream_lines
from utils.access_codes import use_code

# If necessary, load tutor data, user data, styling, memory manager, etc.
check_state()

params = st.query_params
if 'code' in params:
    user_reset()
    st.session_state.role = 'student'
    st.session_state['authentication_status'] = False
    access_code = params["code"]
    use_code(st.session_state.df_access_codes, st.session_state.df_tutors, access_code)

st.markdown("<h1 style='text-align: center; color: grey;'>AI Tutors</h1>", unsafe_allow_html=True)

# Text to be displayed with newlines
text = 'Built by teachers for students.'

if "slow_write_main" not in st.session_state:
    st.session_state["slow_write_main"] = True
cols = st.columns((1.4, 2, 1.4))
with cols[1]:
    stream_lines(
        text=text,
        pause_time=0.02,
        slow_write=st.session_state.slow_write_main,
        center=True
    )
    st.session_state["slow_write_main"] = False
st.markdown("----")

# Select role
col1, col2, col3 = st.columns((1.4, 2, 1.4))
with col2:
    if st.button(f"Students", use_container_width=True, type="primary"):
        user_reset()
        st.session_state.role = 'student'
        st.session_state['authentication_status'] = False
        st.switch_page("pages/explore_tutors.py")
    if st.button(f"Teachers", use_container_width=True):
        st.session_state.role = 'teacher'
        if st.session_state['authentication_status']:
            st.switch_page("pages/dashboard.py")
        else:
            st.switch_page("pages/teacher_start.py")
