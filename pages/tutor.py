import streamlit as st
from st_equation_editor import mathfield
import time
from audiorecorder import audiorecorder

from llms.tutor_llm import TutorChain
from utils.menu import menu
from utils.session import check_state, reset_chatbot
from utils.save_to_html import download_chat_button, escape_markdown, send_chat_button
from utils.file_handler import extract_text_from_different_file_types
from utils.speech_to_txt import stt
from utils.styling import button_style, columns_style, scroll_to

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
custom_button = button_style()
custom_columns = columns_style()

# Avatar images
avatar = {"user": "https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_student_avatar1.png",
          "assistant": "https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_avatar2.png"}

# Title
st.markdown(f"<h1 style='text-align: center; color: grey;'>&nbsp;&nbsp;&nbsp;{st.session_state["tool name"]}</h1>", unsafe_allow_html=True)

# Display Tutor Profile Image
tutor_image_url = "https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/AIT_avatar1.png"
st.markdown(f'<div style="display: flex; justify-content: center;"><img src="{tutor_image_url}" style="width: 20%;"></div>', unsafe_allow_html=True)

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
if "file_upload_key" not in st.session_state:
    st.session_state.file_upload_key = 0
if "stream_init_msg" not in st.session_state:
    st.session_state.stream_init_msg = True
if "teacher_email" not in st.session_state:
    st.session_state.teacher_email = None
if "drop_file" not in st.session_state:
    st.session_state.drop_file = False
if "email_sent" not in st.session_state:
    st.session_state.email_sent = False
if "audio_recorder_key" not in st.session_state:
    st.session_state.audio_recorder_key = 0

# Load model
if not st.session_state.model_loaded:
    # Construct pipiline
    st.session_state['tutor_llm'] = TutorChain(st.session_state["instructions"],
                                                st.session_state["guidelines"],
                                                st.session_state["introduction"],
                                                st.session_state["knowledge"])

    init_request = st.session_state.tutor_llm.init_request        
    st.session_state.messages.append({"role": "assistant", "content": init_request})
    st.session_state.model_loaded = True

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
    next_user_message = st.empty()
    next_assistant_message = st.empty()
    st.session_state.chat_spinner = st.container()

# Equation Editor
@st.dialog("Math Editor", width='large')
def equation_editor():
    st.markdown("*Create a math expression, copy it, and paste it into your message.*")
    Tex, MathML = mathfield("")

# Organize buttons based on screen size
on_mobile = st.session_state.get('on_mobile', False)
if on_mobile:
    custom_columns()
    col1, col2, col4, col5, col3 = st.columns((1, 1, 1, 1, 1))
else:
    col1, col2, col3, col4, _, col5 = st.columns((1, 1, 1, 1, 7, 3))

# File upload button
with col1:
    custom_button()
    if st.button("📎", help="Attach file"):
        st.session_state.drop_file = True

# Reset chat button
with col2:
    custom_button()
    if st.button("🔄", use_container_width=False, help="Reset chat"):
        reset_chatbot()
        st.rerun()

# Download chat button
with col3:
    custom_button()
    download_chat_session = download_chat_button(st.session_state["tool name"], 
                                                container=col3,
                                                include_text=False)
    
# Calculator button
with col4:
    custom_button()
    if st.button("![Calculator](https://raw.githubusercontent.com/teaghan/ai-tutors/main/images/calculator.png)",
                 help="Type an equation"):
        equation_editor()

# Send chat to teacher button
if st.session_state.teacher_email:
    with col5:
        st.markdown(' ')
        send_chat_button(st.session_state["tool name"], 
                        container=col5,
                        include_text=False if on_mobile else True)

if st.session_state.drop_file:
    # File uploader
    dropped_files = st.file_uploader("File Uploader",
                help="Drop your work/assignment here!", 
                label_visibility='collapsed',
                accept_multiple_files=True, 
                type=["pdf", "png", "jpg", "docx", "csv", "txt", "rtf", "zip"],
                key=f"file_upload_{st.session_state.file_upload_key}")
else:
    dropped_files = []
# Create a container for both audio and chat input
input_container = st.container()

with input_container:
    # Speech input
    audio = audiorecorder(start_prompt="", stop_prompt="", pause_prompt="",
                            show_visualizer=True, key=f'audio_recorder_{st.session_state.audio_recorder_key}')
    # Text input
    prompt = st.chat_input(key='chat_input_text')

# Speech to Text
audio_prompt = ''
if len(audio) > 0:
    del st.session_state[f'audio_recorder_{st.session_state.audio_recorder_key}']
    st.session_state.audio_recorder_key += 1
    with st.session_state.chat_spinner, st.spinner("Being a good listener..."):
        audio_prompt = stt(audio.export(format="wav").read())
if audio_prompt:
    prompt = audio_prompt
    audio_prompt = ''

if prompt:
    # Process dropped files
    processed_file_text = ''
    if dropped_files:
        for file in dropped_files:
            try:
                with st.session_state.chat_spinner, st.spinner(f"Processing: {file.name}"):
                    extracted_text = extract_text_from_different_file_types(file)
                    processed_file_text += f"\n\n**{file.name}**\n\n{extracted_text}"
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
                st.exception(e)
        del st.session_state[f'file_upload_{st.session_state.file_upload_key}']
        st.session_state.file_upload_key += 1
        st.session_state.drop_file = False

    # Add the uploaded file contents to the prompt
    if processed_file_text:
        prompt_full = prompt + f'\n\n## Uploaded file contents:\n\n{processed_file_text}'
    else:
        prompt_full = prompt

    # Add the user's prompt to the conversation
    st.session_state.messages.append({"role": "user", "content": prompt})
    with next_user_message:
        st.chat_message("user", avatar=avatar["user"]).markdown(escape_markdown(prompt))

    # Get the response from the tutor
    response = st.session_state.tutor_llm.get_response(prompt_full)
    st.session_state.messages.append({"role": "assistant", "content": rf"{response}"})    
    st.session_state.email_sent = False
    # Display the response letter by letter
    with next_assistant_message.chat_message("assistant", avatar=avatar["assistant"]):
        with st.empty():
            for sentence in stream_text(response):
                st.markdown(sentence)
                time.sleep(0.02)

    # Re-run the app to update the conversation
    st.rerun()

st.header(' ', anchor='bottom')
scroll_to('bottom')

# Edit AI Tutor
if st.session_state["tutor_test_mode"]:
    if st.button(r"Edit AI Tutor", type="primary"):
        st.switch_page("pages/build_tutor.py")