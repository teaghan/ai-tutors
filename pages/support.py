import streamlit as st
from utils.menu import menu
from utils.session import check_state
import time

# Streamlit page configuration
st.set_page_config(
    page_title='Support',
    page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced visuals
st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        color: #2F4F4F;
        font-size: 48px;
        font-weight: bold;
        margin-top: 50px;
    }
    .contact-card {
        background-color: #E0F2E9;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        text-align: left;
        margin-top: 30px;
    }
    .email-link {
        color: #A8D5BA;
        text-decoration: none;
        font-weight: bold;
    }
    .email-link:hover {
        color: #2F4F4F;
    }
    ul {
        text-align: left;
        margin: auto;
        width: 80%;
    }
    </style>
    """, unsafe_allow_html=True
)

# Title
st.markdown("<h1 style='text-align: center; color: grey;'>Support</h1>", unsafe_allow_html=True)

# Display menu buttons
menu()

cols = st.columns((1.4, 2, 1.4))

with cols[1]:
    # Contact Information Section
    st.markdown(
        """
        <div class='contact-card'>
            <p>Email us at <a href='mailto:build.ai.tutors@gmail.com' class='email-link'>build.ai.tutors@gmail.com</a> if you:</p>
            <ul>
                <li>Have a question</li>
                <li>Want to request a feature</li>
                <li>Found a bug to report</li>
            </ul>
        </div>
        """, unsafe_allow_html=True
    )
