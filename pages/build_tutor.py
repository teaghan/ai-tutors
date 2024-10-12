import streamlit as st
import pandas as pd
from utils.tutor_data import write_csv, select_instructions, create_tutor
from utils.user_data import get_api_keys
from utils.api_keys import add_key
from utils.menu import menu
from utils.chatbot_setup import reset_chatboat

# Page configuration
st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/educational-prompt-engineering/main/images/science_tutor_favicon_small.png", layout="wide")

# Page Title
st.markdown("<h1 style='text-align: center; color: grey;'>Build an AI Tutor</h1>", unsafe_allow_html=True)

# Display page buttons
menu()

if "banner" not in st.session_state:
    st.session_state["banner"] = None
if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False

# Load existing tutor data
df_tutors = st.session_state["df_tutors"]

# Example tool
example_name = 'Junior Science Tutor'
example_instructions, example_guidelines, introduction = select_instructions(df_tutors, tool_name=example_name)

with st.expander("**How it all works**"):
    st.markdown('''
When you create a tutor, it will consist of two main components:

1. A **Chatbot Tutor**: This is the AI that provides guidance and answers student questions.

2. A **Moderator**: This component reviews every response from the tutor. If a response is deemed *inappropriate*, 
the moderator will correct it. This moderation process continues until an appropriate response is provided.

To ensure the tutor behaves as you'd like, you need to define two things:

1. **Instructions** for the tutor: These will guide how the tutor interacts with students and answers their questions.

2. **Guidelines** for the moderator: The moderator will check each tutor response against these guidelines. 
If even one guideline is violated, the response will be marked as "inappropriate" and corrected.
    ''')


# User inputs with examples provided
st.header('Tool Name')
new_name = st.text_input(f'Provide a unique name for your tutor (for example, "{example_name}"):')
st.markdown('---')

st.header('Description')
new_descr = st.text_input(f'Describe your tutor in a sentence or two.')
st.markdown('---')

st.header('Introduction')
st.markdown('How will the tutor start the interaction?')
with st.expander("Example Introduction"):
    st.text(introduction)
new_intro = st.text_area("Introduction:", height=400)
col1, col2, col3 = st.columns(3)
with col3:
    with st.popover("Preview Introduction in Markdown", use_container_width=True):
        st.markdown(new_intro)
st.markdown('---')

st.header('Instructions')
st.markdown('Define a set of instructions for your tutor to follow.')
with st.expander("Example Instructions"):
    st.text(example_instructions)
new_instr = st.text_area("Instructions:", height=400)
col1, col2, col3 = st.columns(3)
with col3:
    with st.popover("Preview Instructions in Markdown", use_container_width=True):
        st.markdown(new_instr)
st.markdown('---')

st.header('Guidelines')
st.markdown('Define a set of guidelines for the tutor moderator to follow (see the example below).')
with st.expander("Example Guidelines"):
    st.text(example_guidelines)
new_guide = st.text_area("Guidelines", height=400)
col1, col2, col3 = st.columns(3)
with col3:
    with st.popover("Preview Guidelines in Markdown", use_container_width=True):
        st.markdown(new_guide)
st.markdown('---')


st.header('API Key')
# Load API key for this users email
api_keys = get_api_keys(st.session_state.users_config, st.session_state.user_email)

col1, col2, col3 = st.columns(3)
with col1:
    api_key_name = st.selectbox('API Key', ['None']+[nk[0] for nk in api_keys], label_visibility='hidden')
with col2:
    st.text("")
    st.text("")
    if st.button(r"Add New Key", use_container_width=True):
        add_key()
with col3:
    st.text("")
    st.text("")
    if st.button(r"Manage API Keys", use_container_width=True):
        # Go to teacher dashboard
        st.switch_page("pages/dashboard.py")
if api_key_name=='None':
    st.warning('Without an API Key, your tutor will not be usable!')
    api_key = None
else:
    api_key = dict(api_keys).get(api_key_name)

st.header('Availability')
availability = st.selectbox('Availability', ['Open to Public', 'Available for Viewing', 'Completely Private'], label_visibility='hidden')

with st.expander("**What does this mean?**"):
    st.markdown('''
- **Open to Public**: Your tutor will be accessible to any student. *Note: This means the interactions will use your API Key*.

- **Available for Viewing**: Other teachers can view and interact with your tutor using their own API Key. They can also copy and customize their own version of your tutor.

- **Completely Private**: Only you can access your tutor. It will remain private unless you change its availability or generate an access code for your students.
    ''')

col1, col2, col3 = st.columns(3)
with col1: 
    test_button = st.button("Test Interaction")
with col3:
    create_button = st.button(r"$\textsf{\normalsize Create AI Tutor}$", type="primary")

if test_button or create_button:
    if new_name and new_descr and new_intro and new_instr and new_guide:
        # Check if name exists
        if new_name in df_tutors['Name'].values:
            st.session_state["banner"] = 'name exists'
        else:
            st.session_state["banner"] = 'success'
            st.session_state["tool name"] = new_name
            st.session_state["description"] = new_descr
            st.session_state["introduction"] = new_intro
            st.session_state["instructions"] = new_instr
            st.session_state["guidelines"] = new_guide
            st.session_state["availability"] = availability
            st.session_state["api_key"] = api_key
            if test_button:
                st.session_state["tutor_test_mode"] = True
                reset_chatboat()
                st.switch_page('pages/tutor.py')
            if create_button:
                create_tutor(st.session_state.ai_tutors_data_fn, df_tutors, new_name, new_descr, new_intro, new_instr, 
                             new_guide, api_key, availability, st.session_state.user_email)
    else:
        st.session_state["banner"] = 'missing info'
    st.rerun()

if st.session_state["banner"] is not None:
    if st.session_state["banner"] == 'success':
        st.success("Your AI Tutor is built!")
        if st.button("Load Tutor"):
            st.session_state["tutor_test_mode"] = False
            reset_chatboat()
            st.switch_page('pages/tutor.py')
    elif st.session_state["banner"] == 'missing info':
        st.error("Please provide all of the info below.")
    elif st.session_state["banner"] == 'name exists':
        st.error("This tool name already exists, please choose another one")