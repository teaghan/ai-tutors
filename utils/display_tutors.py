import streamlit as st
from utils.tutor_data import select_instructions, available_tutors, reset_build, delete_tutor_confirm, get_creator_email
from utils.chatbot_setup import reset_chatbot 
from utils.access_codes import create_code
from utils.cookies import update_tutor_cookies
import time

def load_tool(df_tutors, tool_name, test_mode=False):

    (st.session_state["description"],
    st.session_state["introduction"], 
     st.session_state["instructions"], 
     st.session_state["guidelines"], 
     st.session_state["availability"], 
     st.session_state["api_key"])= select_instructions(df_tutors, 
                                                           tool_name=tool_name)
    st.session_state["tool name"] = tool_name
    st.session_state["tutor_test_mode"] = test_mode
    update_tutor_cookies()
    st.switch_page('pages/tutor.py')

def load_editor(df_tutors, tool_name, create_copy=False):
    (st.session_state["description"],
    st.session_state["introduction"], 
     st.session_state["instructions"], 
     st.session_state["guidelines"], 
     st.session_state["availability"], 
     api_key) = select_instructions(df_tutors, tool_name=tool_name)
    
    # Check if this user created this tool
    if st.session_state["user_email"] == get_creator_email(df_tutors, tool_name=tool_name):
        st.session_state["api_key"] = api_key
    else:
        st.session_state["api_key"] = None

    if create_copy:
        st.session_state["tool name"] = tool_name + ' (Copy)'
        st.session_state["tutor_test_mode"] = True
    else:
        st.session_state["tool name"] = tool_name
        st.session_state["tutor_test_mode"] = True
    st.session_state["banner"] = None
    update_tutor_cookies()
    st.switch_page('pages/build_tutor.py')

def display_tools(show_all=True, user_display=False, allow_edit=False, 
                  allow_copy=False, access_codes=False):
    if show_all:
        suffix = 'pub'
    else:
        suffix = 'usr'
    df_tutors = st.session_state["df_tutors"]
    avail_tools = available_tutors(df_tutors)
    for name, desc, creator_email,  availability, api_key in avail_tools:
        # Check if the creator email matches the current user's email
        if (user_display and creator_email==st.session_state["user_email"]) or (show_all and availability!='Completely Private'):
            with st.container():
                st.subheader(name)  # Display tool name
                st.markdown(desc)      # Display tool description
                if api_key is None:
                    st.warning('Requires API Key')
                if allow_copy and access_codes:
                    col1, col4, col5, col2, col3 = st.columns(5)
                elif allow_copy and not access_codes:
                    col1, col4, col2, col3 = st.columns(4)
                elif not allow_copy and access_codes:
                    col1, col5, col2, col3 = st.columns(4)
                else:
                    col1, col2, col3 = st.columns(3)
                with col1:
                    # Button to load the selected tool
                    if st.button(f"Interact", key=f'{name}_inter_{suffix}', use_container_width=True):
                        reset_chatbot()
                        reset_build(reset_banner=True)
                        load_tool(df_tutors, name)
                if allow_copy:
                    with col4:
                        if st.button(f"Copy & Edit", key=f'{name}_copy_{suffix}', use_container_width=True):
                            reset_chatbot()
                            reset_build(reset_banner=True)
                            load_editor(df_tutors, name, create_copy=True)
                if access_codes:
                    with col5:
                        if st.button(f"Create Access Code", key=f'{name}_code_{suffix}', use_container_width=True):
                            reset_build(reset_banner=True)
                            create_code(name)
                if allow_edit:
                    with col2:
                        if st.button(f"Edit Original", key=f'{name}_edit_{suffix}', use_container_width=True):
                            reset_chatbot()
                            reset_build(reset_banner=True)
                            load_editor(df_tutors, name)
                    with col3:
                        if st.button(f"Delete", key=f'{name}_delete_{suffix}', use_container_width=True):
                            reset_chatbot()
                            reset_build(reset_banner=True)
                            # Dialog box to confirm
                            delete_tutor_confirm(name)
                st.markdown('---')