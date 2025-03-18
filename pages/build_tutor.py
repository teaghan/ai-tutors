import streamlit as st
import streamlit.components.v1 as components
from utils.tutor_data import select_instructions, create_tutor, ask_for_overwrite
from utils.menu import menu
from utils.session import reset_chatbot, reset_build
from utils.session import check_state
from utils.styling import scroll_to
from utils.file_handler import extract_text_from_different_file_types
from utils.config import open_config

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
if "knowledge_upload_key" not in st.session_state:
    st.session_state["knowledge_upload_key"] = 0

if not st.session_state.tutor_test_mode:
    reset_build()

# Load existing tutor data
df_tutors = st.session_state["df_tutors"]

# Example tool
example_description, example_introduction, example_instructions, example_guidelines, _, _ = select_instructions(df_tutors, tool_name=example_name)

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
st.session_state["tool name"] = new_name
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
st.session_state["description"] = new_descr
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
st.session_state["introduction"] = new_intro
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
st.session_state["instructions"] = new_instr
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
st.session_state["guidelines"] = new_guide
if markdown_previews:
    col1, col2 = st.columns(2)
    with col2:
        with st.popover("Preview Guidelines in Markdown", use_container_width=True):
            st.markdown(new_guide)
st.markdown('---')

st.header('Knowledge Base (optional)')
if 'knowledge' in st.session_state:
    new_knowledge = st.session_state["knowledge"]
else:
    new_knowledge = ''

st.markdown('Include any knowledge files that will be useful for the tutor to use as background information.')

# Extract existing knowledge file names
existing_file_names = []
if new_knowledge:
    for line in new_knowledge.split('\n'):
        if line.startswith('-----') and line.endswith('-----'):
            existing_file_names.append(line.replace('-', '').strip())

# File uploader section
dropped_files = st.file_uploader(
    "File Uploader",
    help="Drop your files here!", 
    label_visibility='collapsed',
    accept_multiple_files=True, 
    type=["pdf", "png", "jpg", "docx", "csv", "txt", "rtf", "zip"],
    key=f"knowledge_upload_{st.session_state.knowledge_upload_key}"
)

# Process files button only shows when files are uploaded
if dropped_files:
    with st.columns((1,1,1))[1]:
        if st.button("Add to Knowledge Base", type="primary", 
                     use_container_width=True, on_click=reset_banner):
            processed_file_text = ''
            max_knowledge_chars = open_config()['llm']['max_knowledge_chars']
            
            # Process all uploaded files
            for file in dropped_files:
                try:
                    with st.spinner(f"Processing: {file.name}"):
                        extracted_text = extract_text_from_different_file_types(file)
                        processed_file_text += f"----- {file.name} -----\n\n{extracted_text}\n\n"
                except Exception as e:
                    st.error(f"Error processing {file.name}: {str(e)}")
            
            # Check if adding new content would exceed character limit
            total_length = len(new_knowledge) + len(processed_file_text)
            if total_length > max_knowledge_chars:
                st.error(f"Your knowledge base would be too large. Please reduce the size of your files.")
            else:
                # Update knowledge base and clear file uploader
                new_knowledge += processed_file_text
                st.session_state["knowledge"] = new_knowledge
                del st.session_state[f'knowledge_upload_{st.session_state.knowledge_upload_key}']
                st.session_state.knowledge_upload_key += 1
                st.rerun()

# Display existing files with delete buttons
if existing_file_names:
    st.markdown("#### Current Knowledge Files:")
    for file_name in existing_file_names:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.markdown(f'  - **{file_name}**')
        with col2:
            if st.button("Delete", key=f"delete_{file_name}", 
                         use_container_width=True, 
                         on_click=reset_banner):
                # Remove the file and its content from knowledge base
                lines = new_knowledge.split('\n')
                new_lines = []
                skip = False
                for line in lines:
                    if line.strip() == f"----- {file_name} -----":
                        skip = True
                        continue
                    if skip and line.startswith('-----'):
                        skip = False
                    if not skip:
                        new_lines.append(line)
                new_knowledge = '\n'.join(new_lines)
                st.session_state["knowledge"] = new_knowledge
                st.rerun()

st.markdown('---')


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
st.session_state["availability"] = availability
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

st.session_state["tutor_test_mode"] = True

if test_button or create_button or st.session_state["overwrite"]:
    st.session_state["grades"] = selected_grades
    st.session_state["subjects"] = selected_subjects

    if dropped_files:
        st.session_state["banner"] = 'files uploaded'
    elif st.session_state["tool name"] and st.session_state["description"] and st.session_state["introduction"] and st.session_state["instructions"] and st.session_state["guidelines"]:
        if test_button:
            st.session_state["banner"] = None
            st.session_state["tutor_test_mode"] = True
            reset_chatbot()
            st.switch_page('pages/tutor.py')
            
        # Check if name exists
        name_exists = st.session_state["tool name"] in df_tutors['Name'].values
        if name_exists and not st.session_state["overwrite"]:
            name_match_index = df_tutors.index[df_tutors['Name'] == st.session_state["tool name"]].tolist()[0]
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
                                                            st.session_state["tool name"], 
                                                            st.session_state["description"], 
                                                            st.session_state["introduction"], 
                                                            st.session_state["instructions"], 
                                                            st.session_state["knowledge"], 
                                                            st.session_state["guidelines"], 
                                                            st.session_state["grades"], 
                                                            st.session_state["subjects"],
                                                            st.session_state["availability"], 
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
            st.session_state["tutor_test_mode"] = False
            st.switch_page('pages/tutor.py')
        if exit_button.button("Return to Dashboard", use_container_width=True):
            st.switch_page('pages/dashboard.py')
    elif st.session_state["banner"] == 'missing info':
        banner_text.error("Please provide all of the info below.")
    elif st.session_state["banner"] == 'name exists':
        banner_text.error("This tool name already exists, please choose another one")
    elif st.session_state["banner"] == 'files uploaded':
        banner_text.error("You have files in the queue that need to either be added to your knowledge base or deleted.")