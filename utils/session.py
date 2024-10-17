import streamlit as st
from utils.tutor_data import read_csv
from utils.user_data import read_users
from utils.cookies import cookies_to_session

def load_data():
    if "df_tutors" not in st.session_state:
        # Load tutor data
        st.session_state["ai_tutors_data_fn"] = 'ai-tutors/tutor_info.csv'#'data/tutor_info.csv'
        st.session_state["df_tutors"] = read_csv(st.session_state["ai_tutors_data_fn"])

    if "users_config" not in st.session_state:
        # Load user data
        st.session_state["users_data_fn"] = 'ai-tutors/users.yaml'#'data/users.yaml'
        st.session_state["users_config"], st.session_state["authenticator"] = read_users(st.session_state["users_data_fn"])

    if "df_access_codes" not in st.session_state:
        # Load access codes data
        st.session_state["access_codes_data_fn"] = 'ai-tutors/access_codes.csv'#'data/access_codes.csv'
        st.session_state["df_access_codes"] = read_csv(st.session_state["access_codes_data_fn"])

def user_reset():
    st.session_state.authentication_status = False
    st.session_state.user_email = None
    st.session_state.username = None
    st.session_state.role = None
    return

def check_state(check_user=False, keys=None):

    # Load tutor and user data
    load_data()

    # Set user login info
    if "user_email" not in st.session_state:
        user_reset()

    # Collect cookies
    if keys is None:
        cookies_to_session()
    else:
        cookies_to_session(keys=keys)

    # Check if user is signed in
    if check_user:
        if st.session_state.authentication_status is None:
            st.switch_page("main.py")
    return 