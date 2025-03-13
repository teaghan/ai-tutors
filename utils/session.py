import streamlit as st
from streamlit_authenticator.utilities import LoginError 

from utils.tutor_data import read_csv
from utils.user_data import read_users
from utils.styling import load_style
from utils.memory_manager import initialize_memory_and_heartbeat, update_session_activity

def load_data():
    # Load tutor data file or cached data
    st.session_state["ai_tutors_data_fn"] = 'ai-tutors/tutor_info.csv'
    st.session_state["df_tutors"] = read_csv(st.session_state["ai_tutors_data_fn"])

    # Load user data file or cached data
    st.session_state["users_data_fn"] = 'ai-tutors/users.yaml'
    st.session_state["users_config"], st.session_state["authenticator"] = read_users(st.session_state["users_data_fn"])

    # Load access codes data file or cached data
    st.session_state["access_codes_data_fn"] = 'ai-tutors/access_codes.csv'
    st.session_state["df_access_codes"] = read_csv(st.session_state["access_codes_data_fn"])

def user_reset():
    st.session_state.authentication_status = None
    st.session_state.user_email = None
    st.session_state.username = None
    st.session_state.role = None

def check_state(check_user=False, reset_chat=False, 
                rebuild=False, reset_banner=False, reset_teacher=True):
    # Load styling
    load_style()

    # Reset info
    if reset_teacher:
        reset_teacher_email()
    if reset_chat:
        reset_chatbot()
    if rebuild:
        reset_build(reset_banner=reset_banner)

    # Start periodic cleanup only once per session
    if "cleanup_initialized" not in st.session_state:
        # Initialize memory and heartbeat managers
        initialize_memory_and_heartbeat()

    # Update activity on any user interaction
    update_session_activity()

    # Load tutor and user data
    load_data()

    # Set user login info
    if "user_email" not in st.session_state:
        user_reset()
    
    # Check if user is signed in
    if check_user:
        if st.session_state.authentication_status is None:
            st.switch_page("main.py")

def login():
    
    # Creating a login widget
    try:
        st.session_state.authenticator.login(fields={'Username':'Email'})
    except LoginError as e:
        st.error(e)
    
    # Authenticating user
    if st.session_state['authentication_status']:
        # Username and email are the same
        st.session_state.user_email = st.session_state.username
    else:
        st.switch_page("main.py")

def reset_build(reset_banner=False):
    st.session_state["tool name"] = None
    st.session_state["description"] = None
    st.session_state["introduction"] = None
    st.session_state["instructions"] = None
    st.session_state["guidelines"] = None
    st.session_state["availability"] = None
    st.session_state["overwrite_dialog"] = False
    st.session_state["overwrite"] = False
    st.session_state["knowledge_file_paths"] = []
    st.session_state["grades"] = ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'Post-Secondary']
    st.session_state["subjects"] = ['Math', 'Science', 'English', 'Computer Science', 'Arts', 
                                    'Social Studies', 'Languages', 'Career Education']
    if reset_banner:
        st.session_state["banner"] = None

def reset_teacher_email():
    st.session_state['teacher_email'] = None

def reset_chatbot():
    st.session_state['model_loaded'] = False
    st.session_state['messages'] = []
    st.session_state['model_loads'] = 0
    st.session_state['file_upload_key'] = 0
    st.session_state['stream_init_msg'] = True