import streamlit as st
from utils.session import user_reset
from utils.cookies import clear_cookies, update_cookies, cookie_manager

def logout(a):
    #st.write('AA',st.session_state.username)
    #st.session_state["authenticator"].authentication_controller.logout()
    #st.session_state["authenticator"].cookie_controller.delete_cookie()
    user_reset()
    update_cookies()
    #clear_cookies()
    st.switch_page("main.py")
    return

# Dialog window to ask for single-use API Key
@st.dialog("Support")
def support_window():
    st.markdown("""
Please email build.ai.tutors@gmail.com if you have a

- question to ask
- feature to request
- bug to report
    """)
    if st.button(f"Close", use_container_width=True, type='primary'):
        st.rerun()

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
    # FOR TESTING
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