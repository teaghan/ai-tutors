import streamlit as st
from llms.tutor_llm import TutorChain
from utils.menu import menu
from utils.session import check_state, reset_chatbot
from utils.save_to_html import download_chat_button, escape_markdown, send_chat_button
from utils.calculator import equation_creator
import time
from utils.file_handler import extract_text_from_different_file_types

pause_time_between_chars = 0.01

if "tool name" in st.session_state:
    page_name = st.session_state["tool name"]
else:
    page_name = 'AI Tutor'

st.set_page_config(page_title=page_name, page_icon="https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_favicon4.png", 
                    layout="wide", initial_sidebar_state="collapsed")

# If necessary, load tutor data, user data, etc.
check_state(check_user=True, reset_teacher=False)

menu()

# Avatar images
avatar = {"user": "https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_student_avatar1.png",
          "assistant": "https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_avatar2.png"}

# Title
st.markdown(f"<h1 style='text-align: center; color: grey;'>&nbsp;&nbsp;&nbsp;{st.session_state["tool name"]}</h1>", unsafe_allow_html=True)

# Display Tutor Profile Image
tutor_image_url = "https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_avatar1.png"
col1, col2, col3 = st.columns(3)
col2.image(tutor_image_url, use_container_width=True)

# Interaction Tips
with st.expander("💡 **Tips** for interacting with AI Tutors"):
    st.markdown("""
- Ask the tutor to explain how things work instead of just giving the solution.
- Be as clear as you can when asking questions to get the best help.
- If you're still unsure, don't be afraid to ask more questions.
- **Example prompts** to get started:
    - "Can you help me with problem 6 on the attached assignment?
    - "What role does the Sun play in the water cycle?"
    - "Can you help me understand how photosynthesis works?"
    - "Can you help me identify the key themes in the poem I'm analyzing?"
- To help type **math symbols**, use these keyboard shortcuts:
    - Multiplication (×): Use the `*` key.
    - Division (÷): Use the `/` key.
    - Powers (3²): Use the `^` symbol followed by the exponent. For example: `3^2`
    - Square Root: Type `\sqrt{}` using the `{}` brackets to enclose the number. For example: `\sqrt{4}`
    """)


if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "model_loads" not in st.session_state:
    st.session_state["model_loads"] = 0
if "file_upload_key" not in st.session_state:
    st.session_state.file_upload_key = 0
if "stream_init_msg" not in st.session_state:
    st.session_state.stream_init_msg = True
if "teacher_email" not in st.session_state:
    st.session_state.teacher_email = None

# Function to stream text letter by letter
def stream_text(text):
    sentence = ""
    for letter in text:
        sentence += letter
        yield sentence

# Display conversation
if len(st.session_state.messages)>0:
    if st.session_state.stream_init_msg:
        msg = st.session_state.messages[0]
        with st.chat_message(msg["role"], avatar=avatar[msg["role"]]):
            intro_msg = rf"{msg["content"]}"
            with st.empty():
                for char in stream_text(intro_msg):
                    st.markdown(char)
                    time.sleep(pause_time_between_chars)
        st.session_state.stream_init_msg = False
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.chat_message(msg["role"], avatar=avatar[msg["role"]]).markdown(escape_markdown(rf"{msg["content"]}"))
            else:
                st.chat_message(msg["role"], avatar=avatar[msg["role"]]).markdown(rf"{msg["content"]}")

# The following code is for saving the messages to a html file.
col1, col2, col3 = st.columns((1.5, 0.5, 0.5))
download_chat_session = download_chat_button(st.session_state["tool name"], container=col3)

if st.session_state.teacher_email:
    send_chat_button(st.session_state["tool name"], container=col3)

# Button for resetting the chat.
if col2.button("🔄 Reset Chat", use_container_width=True, help="Reset chat"):
    reset_chatbot()
    st.rerun()

dropped_files = col1.file_uploader("File Uploader",
            help="Drop your work/assignment here!", 
            label_visibility='collapsed',
            accept_multiple_files=True, 
            type=["pdf", "png", "jpg", "docx", "csv", "txt", "rtf", "zip"],
            key=f"file_upload_{st.session_state['file_upload_key']}"
        )
# Load model
if not st.session_state.model_loaded:
    with st.spinner('Loading...'):
        # Construct pipiline
        st.session_state['tutor_llm'] = TutorChain(st.session_state["tool name"],
                                                   st.session_state["instructions"],
                                                   st.session_state["guidelines"],
                                                   st.session_state["introduction"],
                                                   st.session_state["knowledge_file_paths"])
        st.session_state.model_loads +=1

        init_request = st.session_state.tutor_llm.init_request        
        st.session_state.messages.append({"role": "assistant", "content": init_request})

        st.session_state.model_loaded = True
        st.session_state["model_loads"] += 0

prompt = st.chat_input()
if prompt:
    # Process dropped files
    processed_file_text = ''
    if dropped_files:
        for file in dropped_files:
            try:
                with st.spinner(f"Processing: {file.name}"):
                    extracted_text = extract_text_from_different_file_types(file)
                    processed_file_text += f"\n\n**{file.name}**\n\n{extracted_text}"
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
                st.exception(e)
        st.session_state["file_upload_key"] += 1

    # Add the uploaded file contents to the prompt
    if processed_file_text:
        prompt_full = prompt + f'\n\n## Uploaded file contents:\n\n{processed_file_text}'
    else:
        prompt_full = prompt

    print(prompt_full)

    # Add the user's prompt to the conversation
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar=avatar["user"]).markdown(escape_markdown(prompt))

    # Get the response from the tutor
    response = st.session_state.tutor_llm.get_response(prompt_full)
    st.session_state.messages.append({"role": "assistant", "content": rf"{response}"})    
    
    # Display the response letter by letter
    with st.chat_message("assistant", avatar=avatar["assistant"]):
        with st.empty():
            for sentence in stream_text(response):
                st.markdown(sentence)
                time.sleep(0.02)

    # Re-run the app to update the conversation
    st.rerun()

# Equation Creator
with st.sidebar:
    with st.expander("Equation Creator"):
        equation_creator()

# Edit AI Tutor
if st.session_state["tutor_test_mode"]:
    if st.button(r"Edit AI Tutor", type="primary"):
        st.switch_page("pages/build_tutor.py")