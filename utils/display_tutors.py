import streamlit as st
from utils.tutor_data import select_instructions, available_tutors, reset_build, delete_tutor_confirm
from utils.chatbot_setup import reset_chatboat 

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
    st.switch_page('pages/tutor.py')

def load_editor(df_tutors, tool_name):
    (st.session_state["description"],
    st.session_state["introduction"], 
     st.session_state["instructions"], 
     st.session_state["guidelines"], 
     st.session_state["availability"], 
     st.session_state["api_key"]) = select_instructions(df_tutors, 
                                                           tool_name=tool_name)
    st.session_state["tool name"] = tool_name
    st.session_state["tutor_test_mode"] = True
    st.session_state["banner"] = None
    st.switch_page('pages/build_tutor.py')

def display_tools(show_all=True, allow_edit=False):
    if show_all:
        suffix = 'pub'
    else:
        suffix = 'usr'
    df_tutors = st.session_state["df_tutors"]
    avail_tools = available_tutors(df_tutors)
    for name, desc, creator_email in avail_tools:
        # Check if the creator email matches the current user's email
        if creator_email==st.session_state["user_email"] or show_all:
            with st.container():
                st.subheader(name)  # Display tool name
                st.write(desc)      # Display tool description
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Button to load the selected tool
                    if st.button(f"Interact", key=f'{name}_inter_{suffix}', use_container_width=True):
                        reset_chatboat()
                        reset_build()
                        load_tool(df_tutors, name)
                with col2:
                    if allow_edit:
                        if st.button(f"Edit", key=f'{name}_edit_{suffix}', use_container_width=True):
                            reset_chatboat()
                            reset_build()
                            load_editor(df_tutors, name)
                with col3:
                    if allow_edit:
                        if st.button(f"Delete", key=f'{name}_delete_{suffix}', use_container_width=True):
                            reset_chatboat()
                            reset_build()
                            # Dialog box to confirm
                            delete_tutor_confirm(name)
                st.markdown('---')