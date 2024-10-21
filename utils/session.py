import streamlit as st
from utils.tutor_data import read_csv
from utils.user_data import read_users
from utils.cookies import cookies_to_session, clear_cookies#, get_manager
from streamlit_cookies_controller import CookieController

#from streamlitextras.cookiemanager import get_cookie_manager
import time

def load_data(force_reload=True):
    #if ("df_tutors" not in st.session_state) or force_reload:
    # Load tutor data
    st.session_state["ai_tutors_data_fn"] = 'ai-tutors/tutor_info.csv'
    st.session_state["df_tutors"] = read_csv(st.session_state["ai_tutors_data_fn"])

    #if ("users_config" not in st.session_state) or force_reload:
    # Load user data
    st.session_state["users_data_fn"] = 'ai-tutors/users.yaml'#'data/users.yaml'
    st.session_state["users_config"], st.session_state["authenticator"] = read_users(st.session_state["users_data_fn"])

    #if ("df_access_codes" not in st.session_state) or force_reload:
    # Load access codes data
    st.session_state["access_codes_data_fn"] = 'ai-tutors/access_codes.csv'#'data/access_codes.csv'
    st.session_state["df_access_codes"] = read_csv(st.session_state["access_codes_data_fn"])

def user_reset():
    st.session_state.authentication_status = False
    st.session_state.user_email = None
    st.session_state.username = None
    st.session_state.role = None
    return

def check_state(check_user=False, keys=None, force_reload=False):

    # Load tutor and user data
    load_data(force_reload=force_reload)

    if "cookie_manager" not in st.session_state:
        #cookie_manager = StLocalStorage()

        cookie_manager = CookieController()
        #time.sleep(1) 
        #cookies = cookie_manager.getAll()
        #time.sleep(3)
        #st.write(cookies)
        #time.sleep(5)
        st.session_state['cookie_manager'] = cookie_manager
        #st.rerun()
        # TESTING
        #clear_cookies()

    # Set user login info
    if "user_email" not in st.session_state:
        user_reset()

    ## Collect cookies
    if keys is None:
        cookies_to_session()
    else:
        cookies_to_session(keys=keys)

    # Check if user is signed in
    if check_user:
        if st.session_state.authentication_status is None:
            st.switch_page("main.py")

    return 