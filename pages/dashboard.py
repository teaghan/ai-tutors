import streamlit as st
from utils.menu import menu
from utils.display_tutors import display_tools
from utils.access_codes import display_codes
from utils.session import check_state


# Streamlit info
st.set_page_config(page_title='Dashboard', page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png", layout="wide")

# If necessary, load tutor data, user data, etc.
check_state(check_user=True, reset_chat=True, rebuild=True, reset_banner=True)

# Title
st.markdown(f"<h1 style='text-align: center; color: grey;'>Your Dashboard</h1>", unsafe_allow_html=True)

# Display page buttons
menu()

tab1, tab2, tab3 = st.tabs(["**Manage My Tutors**", "**Access Codes**", "**Profile**"])
with tab1:
    display_tools(show_all=False, user_display=True, allow_edit=True, allow_copy=True, access_codes=True)
with tab2:
    display_codes()
with tab3:
    if st.button(f"Change Password", use_container_width=True):
        st.switch_page("pages/change_password.py")