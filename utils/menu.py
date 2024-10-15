import streamlit as st

def logout(a):
    st.session_state.authentication_status = None
    st.session_state.user_email = None
    st.session_state.role = None
    st.switch_page("main.py")

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

def student_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("pages/explore_tutors.py", label="Explore Tutors")
    # FOR TESTING
    st.sidebar.page_link("main.py", label="Home")

def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    if st.session_state.role=='student':
        student_menu()
        return
    teacher_menu()

def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "role" not in st.session_state or st.session_state.role is None:
        st.switch_page("main.py")
    menu()