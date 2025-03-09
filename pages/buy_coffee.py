import streamlit as st
from utils.menu import menu
from utils.session import check_state
from utils.stripe import get_create_checkout_session_url, nav_to

# Streamlit page configuration
st.set_page_config(
    page_title='Donate',
    page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

check_state()
menu()

# Title
st.markdown("<h1 style='text-align: center; color: grey;'>Donate to AI Tutors</h1>", unsafe_allow_html=True)

with st.columns((1, 6, 1))[1]:

    with st.container(border=True):


        st.markdown("""
<div style='text-align: center;'>
<h4>If you've enjoyed using the AI Tutors, please consider donating 4 bucks 💰</h4>

<h4>Your support helps me continue developing and improving the platform 🤖 💻</h4>

<h4>Thank you for your support! 🙌</h4>
</div>
        """, unsafe_allow_html=True)
        if st.button("☕ Buy Me a Coffee", type="primary", use_container_width=True):
            url = get_create_checkout_session_url()
            nav_to(url)

