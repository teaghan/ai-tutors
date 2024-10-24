import streamlit as st
import streamlit.components.v1 as components
from utils.tutor_data import select_instructions, create_tutor, ask_for_overwrite, reset_build
from utils.user_data import get_api_keys
from utils.api_keys import add_key
from utils.menu import menu
from utils.chatbot_setup import reset_chatbot
from utils.session import check_state
from utils.cookies import update_tutor_cookies

# Clear memory
#import gc
#gc.collect()

# Page configuration
st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png", layout="wide")
# Page Title
st.markdown("<h1 style='text-align: center; color: grey;'>&nbsp;&nbsp;&nbsp;Build an AI Tutor</h1>", unsafe_allow_html=True)

# If necessary, load tutor data, user data, and load cookies
check_state(keys=['authentication_status', 'user_email', 'role', 'username', 'email', 'tool name', 
                  'introduction', 'instructions', 'guidelines', 'api_key', 'tutor_test_mode'], 
            check_user=True)

# Display page buttons
menu()

if "banner" not in st.session_state:
    st.session_state["banner"] = None
if "model_loaded" not in st.session_state:
    st.session_state["model_loaded"] = False
if "tutor_test_mode" not in st.session_state:
    st.session_state["tutor_test_mode"] = False

if not st.session_state.tutor_test_mode:
    reset_build()


def scroll_to(element_id):
    components.html(f'''
        <script>
            var element = window.parent.document.getElementById("{element_id}");
            element.scrollIntoView({{behavior: 'smooth'}});
        </script>
    '''.encode())

# Load existing tutor data
df_tutors = st.session_state["df_tutors"]

# Example tool
example_name = 'Socratic STEM Tutor'
_, example_introduction, example_instructions, example_guidelines, _, _ = select_instructions(df_tutors, tool_name=example_name)

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
if st.session_state["tutor_test_mode"]:
    value = st.session_state["tool name"]
else:
    value = ""
st.markdown(f'Provide a unique name for your tutor (for example, "{example_name}"):')
new_name = st.text_input('Name:',
                         value=value, label_visibility='hidden')
st.markdown('---')

st.header('Description')
if st.session_state["tutor_test_mode"]:
    value = st.session_state["description"]
else:
    value = ""
st.markdown('Describe your tutor in a sentence or two.')
new_descr = st.text_input('Description:',
                         value=value, label_visibility='hidden')
st.markdown('---')

st.header('Introduction')
if st.session_state["tutor_test_mode"]:
    value = st.session_state["introduction"]
else:
    value = ""
st.markdown('How will the tutor start the interaction?')
with st.expander("Example Introduction"):
    st.text(example_introduction)
new_intro = st.text_area("Introduction:", height=400,
                         value=value)
col1, col2 = st.columns(2)
with col2:
    with st.popover("Preview Introduction in Markdown", use_container_width=True):
        st.markdown(new_intro)
st.markdown('---')

st.header('Instructions')
if st.session_state["tutor_test_mode"]:
    value = st.session_state["instructions"]
else:
    value = ""
st.markdown('Define a set of instructions for your tutor to follow.')
with st.expander("Example Instructions"):
    st.text(example_instructions)
new_instr = st.text_area("Instructions:", height=400,
                         value=value)
col1, col2 = st.columns(2)
with col2:
    with st.popover("Preview Instructions in Markdown", use_container_width=True):
        st.markdown(new_instr)
st.markdown('---')

st.header('Guidelines')
if st.session_state["tutor_test_mode"]:
    value = st.session_state["guidelines"]
else:
    value = ""
st.markdown('Define a set of guidelines for the tutor moderator to follow (see the example below).')
with st.expander("Example Guidelines"):
    st.text(example_guidelines)
new_guide = st.text_area("Guidelines:", height=400,
                         value=value)
col1, col2 = st.columns(2)
with col2:
    with st.popover("Preview Guidelines in Markdown", use_container_width=True):
        st.markdown(new_guide)
st.markdown('---')


st.header('Availability')
availability_list = ['Open to Public', 'Available for Viewing', 'Completely Private']
if st.session_state["tutor_test_mode"] and (st.session_state["availability"] is not None):
    index = availability_list.index(st.session_state["availability"])
else:
    index = 0
availability = st.selectbox('Availability', availability_list, 
                            label_visibility='hidden', index=index)

with st.expander("**What does this mean?**"):
    st.markdown('''
- **Open to Public**: Your tutor will be accessible to any student. *Note: This means the interactions will use your API Key*.

- **Available for Viewing**: Other teachers can view and interact with your tutor using their own API Key. They can also copy and customize their own version of your tutor.

- **Completely Private**: Only you can access your tutor. It will remain private unless you change its availability or generate an access code for your students.
    ''')

st.markdown('---')

if availability!='Available for Viewing':

    st.header('API Key')
    # Load API key for this users email
    api_keys = get_api_keys(st.session_state.users_config, st.session_state.user_email)

    api_key_name_options = ['None']
    api_key_options = [None]
    if api_keys is not None:
        api_key_name_options = api_key_name_options+[nk[0] for nk in api_keys]
        api_key_options = api_key_options+[nk[1] for nk in api_keys]
    if st.session_state["tutor_test_mode"]:
        index = api_key_options.index(st.session_state["api_key"])
    else:
        index = 0
    col1, col2, col3 = st.columns(3)
    with col1:
        api_key_name = st.selectbox('API Key', api_key_name_options, 
                                    label_visibility='hidden', index=index)
    with col2:
        st.text("")
        st.text("")
        if st.button("Add New Key", use_container_width=True):
            add_key()
    with col3:
        st.text("")
        st.text("")
        if st.button("Manage API Keys", use_container_width=True):
            # Go to teacher dashboard
            st.switch_page("pages/dashboard.py")
    # Select API Key from list
    api_key = api_key_options[api_key_name_options.index(api_key_name)]
    if api_key is None:
        st.warning('Without an API Key, your tutor will not be usable!')
    st.markdown('---')
else:
    api_key_name = 'None'
    api_key = None


st.header('Finalize', anchor='bottom')

col1, col2, col3 = st.columns(3)
if st.session_state["banner"] != 'success':
    with col2: 
        test_button = st.button("Test Interaction", use_container_width=True)
        create_button = st.button("Launch Tutor", 
                                type="primary", use_container_width=True)
else:
    test_button = False
    create_button = False

# Overwrite parameters
if 'overwrite_dialog' not in st.session_state:
    st.session_state["overwrite_dialog"] = False
if 'overwrite' not in st.session_state:
    st.session_state["overwrite"] = False
if st.session_state["overwrite_dialog"]:
    ask_for_overwrite()

# Set defaults for next re-run
if new_name:
    st.session_state["tool name"] = new_name
if new_descr:
    st.session_state["description"] = new_descr
if new_intro:
    st.session_state["introduction"] = new_intro
if new_instr:
    st.session_state["instructions"] = new_instr
if new_guide:
    st.session_state["guidelines"] = new_guide
if availability:
    st.session_state["availability"] = availability
if api_key:
    st.session_state["api_key"] = api_key
st.session_state["tutor_test_mode"] = True

if test_button or create_button or st.session_state["overwrite"]:
    if new_name and new_descr and new_intro and new_instr and new_guide:
        if test_button:
            st.session_state["banner"] = None
            st.session_state["tutor_test_mode"] = True
            reset_chatbot()
            update_tutor_cookies()
            st.switch_page('pages/tutor.py')
            
        # Check if name exists
        name_exists = new_name in df_tutors['Name'].values
        if name_exists and not st.session_state["overwrite"]:
            name_match_index = df_tutors.index[df_tutors['Name'] == new_name].tolist()[0]
            # Check if the matching tutor is built by user
            if df_tutors.loc[name_match_index, 'Creator Email']==st.session_state.user_email:
                if not test_button:
                    st.session_state["overwrite_dialog"] = True
            else:
                st.session_state["banner"] = 'name exists'
        if not name_exists or st.session_state["overwrite"]:
            if create_button or st.session_state["overwrite"]:
                # Update tutor file and tutor dataframe
                st.session_state["df_tutors"] = create_tutor(st.session_state.ai_tutors_data_fn, 
                                                            new_name, new_descr, 
                                                            new_intro, new_instr, 
                                                            new_guide, api_key, availability, 
                                                            st.session_state.user_email,
                                                            overwrite=st.session_state["overwrite"])
                st.session_state["banner"] = 'success'
                st.session_state["overwrite"] = False
                reset_chatbot()
                update_tutor_cookies()
    else:
        st.session_state["banner"] = 'missing info'
        update_tutor_cookies()
    st.rerun()

if st.session_state["banner"] is not None:
    scroll_to('bottom')
    if st.session_state["banner"] == 'success':
        st.success("Your AI Tutor is built!")
        with col2:
            if st.button("Load Tutor", 
                            type="primary", use_container_width=True):
                st.session_state["tool name"] = new_name
                st.session_state["description"] = new_descr
                st.session_state["introduction"] = new_intro
                st.session_state["instructions"] = new_instr
                st.session_state["guidelines"] = new_guide
                st.session_state["availability"] = availability
                st.session_state["api_key"] = api_key
                st.session_state["tutor_test_mode"] = False
                update_tutor_cookies()
                st.switch_page('pages/tutor.py')
    elif st.session_state["banner"] == 'missing info':
        st.error("Please provide all of the info below.")
    elif st.session_state["banner"] == 'name exists':
        st.error("This tool name already exists, please choose another one")