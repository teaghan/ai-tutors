import streamlit as st
import streamlit.components.v1 as components
from utils.tutor_data import select_instructions, create_tutor, ask_for_overwrite, delete_embeddings
from utils.menu import menu
from utils.session import reset_chatbot, reset_build
from utils.session import check_state
from utils.knowledge_files import drop_files, save_files, load_file_to_temp
from utils.styling import scroll_to

example_name = 'Mathematical Reasoning Tutor'
markdown_previews = False

# Page configuration
st.set_page_config(page_title="AI Tutors", page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png", layout="wide")
# Page Title
st.markdown("<h1 style='text-align: center; color: grey;'>&nbsp;&nbsp;&nbsp;Build an AI Tutor</h1>", unsafe_allow_html=True)

# If necessary, load tutor data, user data, etc.
check_state(check_user=True)

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

# Load existing tutor data
df_tutors = st.session_state["df_tutors"]

# Example tool
example_description, example_introduction, example_instructions, example_guidelines, _ = select_instructions(df_tutors, tool_name=example_name)

with st.expander("**How it all works**"):
    st.markdown('''
When you create a tutor, it will consist of two main components:

1. A **Chatbot Tutor**: This is the AI that provides guidance and answers student questions.

2. A **Moderator**: This component reviews every response from the tutor. If a response is deemed *inappropriate*, 
the moderator will correct it. This moderation process continues until an appropriate response is provided.

To ensure the tutor behaves as you'd like, you need to define two things:

1. A **Role** for the tutor: The role will guide the tutor's intention.

2. **Response Criteria**: The tutor will use these criteria to form its responses. The moderator will double-check each tutor response against these criteria. 
If even one criterion is violated, the response will be marked as "inappropriate" and corrected.
    ''')

def reset_banner():
    st.session_state["banner"] = None

# User inputs with examples provided
st.header('Tutor Name')
if st.session_state["tutor_test_mode"]:
    value = st.session_state["tool name"]
else:
    value = ""
st.markdown(f'Provide a unique name for your tutor:')
new_name = st.text_input('Name:',
                         placeholder=f'e.g. "{example_name}"',
                         on_change=reset_banner,
                         value=value, label_visibility='collapsed')
st.markdown('---')

st.header('Description')
if st.session_state["tutor_test_mode"]:
    value = st.session_state["description"]
else:
    value = ""
st.markdown('Describe your tutor in one sentence. This will be used to help users find your tutor.')
new_descr = st.text_input('Description:',
                         placeholder=f'e.g. "{example_description}"',
                         on_change=reset_banner,
                         value=value, label_visibility='collapsed')
st.markdown('---')

st.header('Introduction')
if st.session_state["tutor_test_mode"]:
    value = st.session_state["introduction"]
else:
    value = ""
st.markdown('How will the tutor start the interaction?')
new_intro = st.text_area("Introduction:", height=400,
                         placeholder=f'For example:\n\n{example_introduction}',
                         on_change=reset_banner,
                         value=value, label_visibility='collapsed')
if markdown_previews:
    col1, col2 = st.columns(2)
    with col2:
        with st.popover("Preview Introduction in Markdown", use_container_width=True):
            st.markdown(new_intro)
st.markdown('---')

st.header('Role')
if st.session_state["tutor_test_mode"]:
    value = st.session_state["instructions"]
else:
    value = ""
st.markdown('''
In as few or as many words as you like, describe the role of the tutor and how it should interact with students.

This will guide the tutor's intention and general vibes 🏄‍♂️
''')
with st.expander("Example Role"):
    st.text(example_instructions)
new_instr = st.text_area("Role:", height=400,
                         placeholder=f'For example:\n\n{example_instructions}',
                         on_change=reset_banner,
                         value=value, label_visibility='collapsed')
if markdown_previews:
    col1, col2 = st.columns(2)
    with col2:
        with st.popover("Preview Instructions in Markdown", use_container_width=True):
            st.markdown(new_instr)
st.markdown('---')

st.header('Response Criteria')
if st.session_state["tutor_test_mode"]:
    value = st.session_state["guidelines"]
else:
    value = ""
st.markdown('''
Define a set of criteria for **the tutor and moderator** to follow.

A numbered list works best!

> **Note:** Unless you specifically state otherwise, these criteria will be followed very closely.
''')
with st.expander("Example Guidelines"):
    st.text(example_guidelines)
new_guide = st.text_area("Guidelines:", height=400,
                         placeholder=f'For example:\n\n{example_guidelines}',
                         on_change=reset_banner,
                         value=value, label_visibility='collapsed')
if markdown_previews:
    col1, col2 = st.columns(2)
    with col2:
        with st.popover("Preview Guidelines in Markdown", use_container_width=True):
            st.markdown(new_guide)
st.markdown('---')

#st.header('Knowledge Files (optional)')
#if 'knowledge_file_paths' in st.session_state:
#    value = st.session_state["knowledge_file_paths"]
#else:
#    value = []
#st.markdown('Include any knowledge files that will be useful for the tutor to use as background information.')
#col1, col2 = st.columns(2)
#dropped_files, existing_file_paths_chosen = drop_files(col1, value)
#if dropped_files and st.session_state["banner"] != 'success':
#    st.warning('Note that these new files will not be added to your tutor for testing until you have saved your tutor using the "Launch Tutor" button below.')
#st.markdown('---')
dropped_files = []
existing_file_paths_chosen = []

# Tags Selection
st.header('Tags')
st.markdown('Select a set of tags/categories for your tutor. This will help users more easily find relevant tools.')
grades = ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'Post-Secondary']
subjects = ['Math', 'Science', 'English', 'Computer Science', 'Arts', 
            'Social Studies', 'Languages', 'Career Education']
selected_grades = st.multiselect("Select Grades:", options=grades, 
                                 default=st.session_state.get("grades", grades),
                                 on_change=reset_banner)
selected_subjects = st.multiselect("Select Subjects:", options=subjects, 
                                   default=st.session_state.get("subjects", subjects),
                                   on_change=reset_banner)
st.markdown('---')

st.header('Availability')
availability_list = ['Open to Public', 'Private']
if st.session_state["tutor_test_mode"] and (st.session_state["availability"] is not None):
    index = availability_list.index(st.session_state["availability"])
else:
    index = 0
availability = st.selectbox('Availability', availability_list, 
                            on_change=reset_banner,
                            label_visibility='hidden', index=index)

with st.expander("**What does this mean?**"):
    st.markdown('''
- **Public**: Your tutor will be accessible to any student.

- **Private**: Only those who you share the tutor with will be able to access it.
    ''')

st.markdown('---')

st.header('Finalize', anchor='bottom')

banner_text = st.empty()
col1, col2, col3 = st.columns(3)
with col2:
    final_button = st.empty()
    exit_button = st.empty()
if st.session_state["banner"] != 'success':
    test_button = False
    #test_button = st.button("Test Interaction", use_container_width=True)
    create_button = final_button.button("Save Tutor", 
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
st.session_state["tutor_test_mode"] = True

if test_button or create_button or st.session_state["overwrite"]:
    st.session_state["grades"] = selected_grades
    st.session_state["subjects"] = selected_subjects
    if new_name and new_descr and new_intro and new_instr and new_guide:
        if test_button:
            st.session_state["banner"] = None
            st.session_state["tutor_test_mode"] = True
            reset_chatbot()
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
                else:
                    knowledge_file_paths = []
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
                                                            availability, 
                                                            st.session_state.user_email,
                                                            overwrite=st.session_state["overwrite"])
                st.session_state["banner"] = 'success'
                st.session_state["overwrite"] = False
                reset_chatbot()
    else:
        st.session_state["banner"] = 'missing info'
    st.rerun()

if st.session_state["banner"] is not None:
    scroll_to('bottom')
    if st.session_state["banner"] == 'success':
        banner_text.success("Your AI Tutor is saved!")
        if final_button.button("Load Tutor", 
                        type="primary", use_container_width=True):
            st.session_state["tool name"] = new_name
            st.session_state["description"] = new_descr
            st.session_state["introduction"] = new_intro
            st.session_state["instructions"] = new_instr
            st.session_state["guidelines"] = new_guide
            st.session_state["availability"] = availability
            st.session_state["tutor_test_mode"] = False
            st.switch_page('pages/tutor.py')
        if exit_button.button("Return to Dashboard", use_container_width=True):
            st.switch_page('pages/dashboard.py')
    elif st.session_state["banner"] == 'missing info':
        banner_text.error("Please provide all of the info below.")
    elif st.session_state["banner"] == 'name exists':
        banner_text.error("This tool name already exists, please choose another one")