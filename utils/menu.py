import streamlit as st

def teacher_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("pages/dashboard.py", label="Your Dashboard")
    st.sidebar.page_link("pages/explore_tutors.py", label="Explore Tutors")
    st.sidebar.page_link("pages/create_tutor.py", label="Build a Tutor")
    # FOR TESTING
    st.sidebar.page_link("main.py", label="Home")
    if st.session_state.role in ["admin"]:
        st.sidebar.page_link("pages/admin.py", label="Manage Tools")

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