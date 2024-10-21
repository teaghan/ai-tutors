import os
import streamlit as st
from llama_index.core import SimpleDirectoryReader

from llms.tutor_llm import TutorChain
from utils.menu import menu
from utils.api_keys import ask_for_api
from utils.session import check_state
from utils.cookies import cookies_to_session, update_tutor_cookies
from utils.save_to_html import download_chat_button
import time
from tempfile import NamedTemporaryFile

# Clear memory
#import gc
#gc.collect()

if "tool name" in st.session_state:
    page_name = st.session_state["tool name"]
else:
    page_name = 'AI Tutor'

st.set_page_config(page_title=page_name, page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png", 
                    layout="wide")


# If necessary, load tutor data, user data, and load cookies
check_state(keys=['authentication_status', 'user_email', 'role', 'username', 'email',
                  'tool name', 'introduction', 'instructions', 'guidelines', 'api_key', 'tutor_test_mode'])

if st.session_state['tool name'] is None:
    st.switch_page("pages/explore_tutors.py")


menu()

# Avatar images
avatar = {"user": "https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_student_avatar1.png",
          "assistant": "https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_avatar2.png"}

# Title
st.markdown(f"<h1 style='text-align: center; color: grey;'>&nbsp;&nbsp;&nbsp;{st.session_state["tool name"]}</h1>", unsafe_allow_html=True)

# Display Tutor Profile Image
tutor_image_url = "https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_avatar1.png"
col1, col2, col3 = st.columns(3)
col2.image(tutor_image_url, use_column_width=True)

# Interaction Tips
with st.expander("Tips for Interacting with AI Tutors"):
    st.markdown("""
- Try to learn and understand the material, not just to get the answers.
- Ask the tutor to explain how things work instead of just giving the solution.
- Be as clear as you can when asking questions to get the best help.
- If you're still unsure, don’t be afraid to ask more questions.
- To help type math symbols, use these keyboard shortcuts:
    - Addition (+): Use the + key.
    - Subtraction (-): Use the - key.
    - Multiplication (×): Use the * key.
    - Division (÷): Use the / key.
    - Equals (=): Use the = key.
    - Greater Than (>): Use the > key.
    - Less Than (<): Use the < key.
    - Powers (3²): Use the ^ symbol followed by the exponent. For example: 3^2
    - Square Root: Type \sqrt{} using the {} brackets to enclose the number. For example: \sqrt{4}
- Example Prompts to Get Started:
    - "What role does the Sun play in the water cycle?"
    - "Can you help me understand how photosynthesis works?"
    - "Can you help me with problem 6 on the attached assignment?
    - "Can you help me understand how the states of matter change from one form to another?"
    - "How do living organisms adapt to their environment to survive?"
    - "Can you help me understand how simple machines like levers and pulleys make work easier?"
    - "Can you help me understand how the movement of tectonic plates causes earthquakes?"
    - "Can you help me understand how the digestive system breaks down food in the human body?"
    """)


if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "model_loads" not in st.session_state:
    st.session_state["model_loads"] = 0

# The following code handles dropping a file from the local computer
if "drop_file" not in st.session_state:
    st.session_state.drop_file = False
if "zip_file" not in st.session_state:
    st.session_state.zip_file = False
if "invalid_filetype" not in st.session_state:
    st.session_state.invalid_filetype = False
drop_file = st.sidebar.button("Attach a file", 
                      type="primary")
if drop_file:
    st.session_state.drop_file = True
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0
if st.session_state.drop_file:
    dropped_files = st.sidebar.file_uploader("Drop a file or multiple files (.txt, .rtf, .pdf, .csv, .docx)", 
                                            accept_multiple_files=True,
                                            key=st.session_state.file_uploader_key)
    
    # Validate file extensions
    invalid_files = []
    if dropped_files:
        for uploaded_file in dropped_files:
            extension = uploaded_file.name.split(".")[-1].lower()
            if extension not in ['txt', 'rtf', 'pdf', 'csv', 'docx']:
                invalid_files.append(uploaded_file.name)

    # If invalid files are found, clear the uploaded files and show a warning
    if invalid_files:
        dropped_files = []  # Clear the uploaded files
        st.session_state.invalid_filetype = True
    else:
        st.session_state.invalid_filetype = False

    # Load file contents
    prompt_f =""
    if dropped_files != []:
        # Collect temporary file paths
        list_of_file_paths = []
        if dropped_files:
            for uploaded_file in dropped_files:
                # Create a temporary file for each uploaded file
                with NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                    temp_file.write(uploaded_file.getbuffer())  # Write uploaded content to temp file
                    list_of_file_paths.append(temp_file.name)  # Store temp file path

        # Use the temporary files with SimpleDirectoryReader
        reader = SimpleDirectoryReader(input_files=list_of_file_paths)
        documents = reader.load_data()

        for doc in documents:
            prompt_f += f'**Document File Name**: {doc.metadata['file_name']}'
            if 'page_label' in doc.metadata:
                prompt_f += f' Page {doc.metadata['page_label']}\n\n'
            else:
                prompt_f += '\n\n'
            prompt_f += f'**Document Content**:\n\n {doc.text}\n\n'
else:
    st.session_state.invalid_filetype = False

# Display conversation
if len(st.session_state.messages)>0:
    for msg in st.session_state.messages:
        st.chat_message(msg["role"], avatar=avatar[msg["role"]]).markdown(rf"{msg["content"]}")

# The following code is for saving the messages to a html file.
col1, col2, col3 = st.columns(3)
download_chat_session = download_chat_button(st.session_state["tool name"], st.session_state.messages, container=col3)

if st.session_state.invalid_filetype:
    st.warning(f"Invalid file(s): {', '.join(invalid_files)}. Please remove this one and upload an accepted file type.")

api_key = st.session_state["api_key"]
if api_key is None:
    ask_for_api()


# Load model
if not st.session_state.model_loaded:
    with st.spinner('Loading...'):
        # Construct pipiline
        st.session_state['tutor_llm'] = TutorChain(st.session_state["instructions"],
                                                   st.session_state["guidelines"],
                                                   st.session_state["introduction"], 
                                                   api_key)
        st.session_state.model_loads +=1

        init_request = st.session_state.tutor_llm.init_request        
        st.session_state.messages.append({"role": "assistant", "content": init_request})

        st.session_state.model_loaded = True
        st.session_state["model_loads"] += 0
        st.rerun()

# Function to stream text letter by letter
def stream_text(text):
    sentence = ""
    for letter in text:
        sentence += letter
        yield sentence#.replace("\n", "<br>") 

if (prompt := st.chat_input()) and (not st.session_state.invalid_filetype):
    if st.session_state.drop_file is True and len(prompt_f)>10:
        prompt_full = prompt + f'\n\n## Uploaded file contents:\n\n{prompt_f}'
    else:
        prompt_full = prompt

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar=avatar["user"]).write(prompt)

    # Use a spinner to indicate processing and display the assistant's response after processing
    #with st.spinner('Thinking...'):
    response = st.session_state.tutor_llm.get_response(prompt_full)
    st.session_state.messages.append({"role": "assistant", "content": rf"{response}"})    
    
    #st.chat_message("assistant", avatar=avatar["assistant"]).markdown(rf"{response}")
    with st.chat_message("assistant", avatar=avatar["assistant"]):
        with st.empty():
            for sentence in stream_text(response):
                st.markdown(sentence)
                time.sleep(0.02)
    
    st.rerun()

if st.session_state["tutor_test_mode"]:
    if st.button(r"Edit AI Tutor", type="primary"):
        st.switch_page("pages/build_tutor.py")