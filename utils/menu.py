import streamlit as st
from utils.session import user_reset

def logout():
    """
    Clears the session state variables associated with the logged in user.
    """
    st.session_state["authenticator"].authentication_controller.authentication_model.credentials['usernames'][st.session_state['user_email']]['logged_in'] = False
    st.session_state['logout'] = True
    st.session_state['name'] = None
    st.session_state['username'] = None
    st.session_state['authentication_status'] = None
    st.session_state['email'] = None
    st.session_state['roles'] = None
    user_reset()
    st.rerun()

def teacher_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("pages/dashboard.py", label="Dashboard")
    st.sidebar.page_link("pages/explore_tutors.py", label="Explore Tutors")
    st.sidebar.page_link("pages/build_tutor.py", label="Build a Tutor")
    st.sidebar.page_link("pages/buy_coffee.py", label="☕ Buy Me a Coffee")

    if st.session_state.role in ["admin"]:
        st.sidebar.page_link("pages/admin.py", label="Manage Tools")
    st.sidebar.page_link("pages/support.py", label="Get Support")
    if st.sidebar.button('Logout', use_container_width=True, type='primary'):
        logout()


def student_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("pages/explore_tutors.py", label="Explore Tutors")
    st.sidebar.page_link("pages/support.py", label="Support")
    st.sidebar.page_link("main.py", label="Home")

def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    #if "role" not in st.session_state or st.session_state.role is None:
    #    st.switch_page("main.py")
    if st.session_state.role=='student':
        student_menu()
    else:
        teacher_menu()
    return

def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "role" not in st.session_state or st.session_state.role is None:
        st.switch_page("main.py")
    menu()