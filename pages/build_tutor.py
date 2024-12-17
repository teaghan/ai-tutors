import streamlit as st
import streamlit.components.v1 as components
from utils.tutor_data import select_instructions, create_tutor, ask_for_overwrite, reset_build, delete_embeddings
from utils.user_data import get_api_keys
from utils.api_keys import add_key
from utils.menu import menu
from utils.chatbot_setup import reset_chatbot
from utils.session import check_state
from utils.cookies import update_tutor_cookies
from utils.knowledge_files import drop_files, save_files, load_file_to_temp

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
example_name = 'Mathematical Reasoning Tutor'#'Socratic STEM Tutor'
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
'''
st.header('Knowledge Files (optional)')
if 'knowledge_file_paths' in st.session_state:
    value = st.session_state["knowledge_file_paths"]
else:
    value = []
st.markdown('Include any knowledge files that will be useful for the tutor to use as background information.')
col1, col2 = st.columns(2)
dropped_files, existing_file_paths_chosen = drop_files(col1, value)
if dropped_files and st.session_state["banner"] != 'success':
    st.warning('Note that these new files will not be added to your tutor for testing until you have saved your tutor using the "Launch Tutor" button below.')
st.markdown('---')
'''
dropped_files = []
existing_file_paths_chosen = []
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

# Tags Selection
st.header('Tags')
st.markdown('Select a set of tags/categories for your tutor. This will help users more easily find relevant tools.')
grades = ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'Post-Secondary']
subjects = ['Math', 'Science', 'English', 'Computer Science', 'Arts', 
            'Social Studies', 'Languages', 'Career Education']
selected_grades = st.multiselect("Select Grades:", options=grades, 
                                 default=st.session_state.get("grades", grades))
selected_subjects = st.multiselect("Select Subjects:", options=subjects, 
                                   default=st.session_state.get("subjects", subjects))
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
    st.markdown('Select an API Key for your tutor **OR** add a new one.')

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
    col1, col3 = st.columns((2,1))
    with col1:
        api_key_name = st.selectbox('API Key', api_key_name_options, 
                                    label_visibility='hidden', index=index)
    with col3:
        st.text("")
        st.text("")
        if st.button("Add New Key", use_container_width=True):
            add_key()
    #with col3:
    #    st.text("")
    #    st.text("")
    #    if st.button("Manage API Keys", use_container_width=True):
    #        # Go to teacher dashboard
    #        st.switch_page("pages/dashboard.py")
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
    st.session_state["grades"] = selected_grades
    st.session_state["subjects"] = selected_subjects
    if new_name and new_descr and new_intro and new_instr and new_guide:
        if test_button:
            st.session_state["banner"] = None
            st.session_state["tutor_test_mode"] = True
            reset_chatbot()
            update_tutor_cookies()
            delete_embeddings(new_name)
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

                if len(dropped_files)>0:
                    knowledge_file_paths = save_files(new_name, dropped_files)
                if len(existing_file_paths_chosen)>0:
                    # Include existing paths
                    knowledge_file_paths = knowledge_file_paths + existing_file_paths_chosen
                st.session_state["knowledge_file_paths"] = knowledge_file_paths
                # Update tutor file and tutor dataframe
                st.session_state["df_tutors"] = create_tutor(st.session_state.ai_tutors_data_fn, 
                                                            new_name, new_descr, 
                                                            new_intro, new_instr, 
                                                            knowledge_file_paths,
                                                            new_guide, 
                                                            st.session_state["grades"], st.session_state["subjects"],
                                                            api_key, availability, 
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