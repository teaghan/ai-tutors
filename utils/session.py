import streamlit as st
from utils.tutor_data import read_csv
from utils.user_data import read_users
from utils.cookies import cookies_to_session, clear_cookies#, NEW_CM
#from streamlit_cookies_controller import CookieController
import time

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
    return

def check_state(check_user=False, keys=None, reset_cookies=False, cookies_working=False):

    # Load tutor and user data
    load_data()

    if cookies_working:
        if "cookie_manager" not in st.session_state:
            cookie_manager = NEW_CM()#CookieController()
            st.session_state['cookie_manager'] = cookie_manager
            #st.session_state["authenticator"].login()
        if reset_cookies:
            clear_cookies()

    #st.write(st.session_state['cookie_manager'].cookies)

    # Set user login info
    if "user_email" not in st.session_state:
        user_reset()

    ## Collect cookies
    if cookies_working:
        if keys is None:
            cookies_to_session()
        else:
            cookies_to_session(keys=keys)
    
    # Check if user is signed in
    if check_user:
        if st.session_state.authentication_status is None:
            st.switch_page("main.py")
            #login()

    return 

from streamlit_authenticator.utilities import LoginError 
from utils.cookies import update_cookies

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
        update_cookies()
    else:
        st.switch_page("main.py")