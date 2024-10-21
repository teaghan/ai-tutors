import streamlit as st
from utils.session import user_reset
from utils.cookies import clear_cookies, update_cookies

def logout(a):
    try:
        st.session_state["authenticator"].authentication_controller.logout()
        st.session_state["authenticator"].cookie_controller.delete_cookie()
    except:
        pass
    user_reset()
    update_cookies()
    clear_cookies()
    # Delete all the items in Session state
    for key in st.session_state.keys():
        del st.session_state[key]
    st.switch_page("main.py")
    return

def teacher_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("pages/dashboard.py", label="Dashboard")
    st.sidebar.page_link("pages/explore_tutors.py", label="Explore Tutors")
    st.sidebar.page_link("pages/build_tutor.py", label="Build a Tutor")
    
    if st.session_state.role in ["admin"]:
        st.sidebar.page_link("pages/admin.py", label="Manage Tools")
    st.sidebar.page_link("pages/support.py", label="Support")
    if st.session_state.user_email is not None:
        st.session_state.authenticator.logout(location='sidebar', callback=logout)
    #if st.sidebar.button('Logout'):
    #    logout()


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