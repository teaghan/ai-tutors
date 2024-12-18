import streamlit as st
from utils.menu import menu
from utils.display_tutors import display_tools
from utils.user_data import get_api_keys
from utils.api_keys import add_key, delete_key
from utils.access_codes import display_codes
from utils.tutor_data import reset_build
from utils.chatbot_setup import reset_chatbot 
from utils.session import check_state

# Clear memory
#import gc
#gc.collect()

# Streamlit info
st.set_page_config(page_title='Dashboard', page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png", layout="wide")
# Title
st.markdown(f"<h1 style='text-align: center; color: grey;'>Your Dashboard</h1>", unsafe_allow_html=True)
st.markdown("----")

# If necessary, load tutor data, user data, and load cookies
check_state(check_user=True)

# Display page buttons
menu()

# Reset info
reset_chatbot()
reset_build(reset_banner=True)

def delete_this_key(username, name):
    def inside_fn():
        delete_key(username, name)
    return inside_fn

tab1, tab2, tab3, tab4 = st.tabs(["API Keys", "Manage My Tutors", "Access Codes", "Profile"])

# API functionality
with tab1:
    with st.expander("What is an API key?"):
        st.markdown("""
            Large language models (LLMs) require substantial compute power and energy to process data and generate responses, and the API key 
            authorizes your access to these resources. Without an API key, LLM-powered tutors cannot function.
        """)

    with st.expander("How to obtain an API key?"):
        st.markdown("""
            Follow these steps to get your API key from OpenAI:

            1. **Sign up with OpenAI**: [Create an account](https://platform.openai.com/signup) if you don’t already have one (you don't need ChatGPT-Plus).
            2. **Set your monthly usage limit**: After signing in, navigate to your [usage settings](https://platform.openai.com/usage) 
            to define how much you're willing to spend each month to avoid unexpected charges.            
            3. **Purchase tokens**: Pre-purchase tokens or set up a billing plan under the [billing section](https://platform.openai.com/settings/organization/billing/overview).
            4. **Create a new API key**: Visit the [API keys section](https://platform.openai.com/api-keys) and click "Create new secret key." 
            
            Once your API key is generated, copy it and paste it in the "Add New Key" section below.
        """)

    with st.expander("How is my API key used?"):
        st.markdown("""
            Your API key is securely stored and will only be used in two cases:

            1. **For Public Tutors**: If you create a tutor that is marked as "Public," your API key will be used to allow others 
            to interact with the tutor.
            2. **For Class Tutors with Access Codes**: If you generate an **access code** to give your students access to a tutor.

            **Note**: We do not share your key with anyone.
        """)

    st.header('My API Keys')
    # Load API key for this users email
    api_keys = get_api_keys(st.session_state.users_config,
                            st.session_state.user_email)

    # Display a table with columns: Name, Key, Check Status button, and Delete button
    if api_keys is not None:
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            st.subheader('Name')
        with col2:
            st.subheader('Secret Key')
        with col3:
            st.subheader('')
        with col4:
            st.subheader('')
        st.markdown('---')
        for name, key in api_keys:
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                st.markdown(name)
            with col2:
                st.markdown(f'{key[:4]}***{key[-4:]}') 
            #with col3:
            #    if st.button(f"Check Status", key=f'{name}_status'):
            #        (total_amount, total_usage, 
            #         remaining, can_access) = check_billing(key)
            #        st.write(f"[*]Total amount: {total_amount:.2f} USD\n[*]Total usage: {total_usage:.2f} USD\n[*]Remaining amount: {remaining:.2f} USD\n{'[-]' if not can_access else '[+]'}API Key: {api_key} {'can' if can_access else 'cannot'} access GPT-4\n")
            with col4:
                if st.button(f"Delete", key=f'{name}_delete', type="primary", on_click=delete_this_key(st.session_state.user_email, name)):
                    pass
            st.markdown('---')

    if st.button(r"Add New Key", type="primary"):
        add_key()
# Display My Tutors in tab2 (only tools created by the current user)
with tab2:
    display_tools(show_all=False, user_display=True, allow_edit=True, allow_copy=True, access_codes=True)

with tab3:
    display_codes()

with tab4:
    if st.button(f"Change Password", use_container_width=True):
        st.switch_page("pages/change_password.py")