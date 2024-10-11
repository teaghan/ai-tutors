import streamlit as st
import pandas as pd
from utils.tutor_data import write_csv, select_instructions
from utils.menu import menu

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

# User inputs with examples provided
st.header('Tool Name')
new_name = st.text_input(f'Provide a unique name for your tutor (for example, "{example_name}"):')
st.markdown('---')

st.header('Description')
new_descr = st.text_input(f'Describe your tutor in a sentence or two.')
st.markdown('---')

st.header('Introduction')
st.markdown('How will the tutor start the interaction? (see the example below).')
with st.expander("Example Introduction"):
    st.text(introduction)
new_intro = st.text_area("Introduction:", height=400)
col1, col2, col3 = st.columns(3)
with col3:
    with st.popover("Preview Introduction in Markdown"):
        st.markdown(new_intro)
st.markdown('---')

st.header('Instructions')
st.markdown('Define a set of instructions for your tutor to follow (see the example below).')
with st.expander("Example Instructions"):
    st.text(example_instructions)
new_instr = st.text_area("Instructions:", height=400)
col1, col2, col3 = st.columns(3)
with col3:
    with st.popover("Preview Instructions in Markdown"):
        st.markdown(new_instr)
st.markdown('---')

st.header('Guidelines')
st.markdown('Define a set of guidelines for the tutor moderator to follow (see the example below).')
with st.expander("Example Guidelines"):
    st.text(example_guidelines)
new_guide = st.text_area("Guidelines", height=400)
col1, col2, col3 = st.columns(3)
with col3:
    with st.popover("Preview Guidelines in Markdown"):
        st.markdown(new_guide)
st.markdown('---')

col1, col2, col3 = st.columns(3)
with col2:
    if st.button(r"$\textsf{\normalsize Create AI Tutor}$", type="primary"):
        if new_name and new_instr and new_guide:
            print(new_name)
            # Check if name exists
            if new_name in df_tutors['Name'].values:
                st.session_state["banner"] = 'name exists'
                st.error("This tool name already exists, please choose another one")

            else:
                # Create a new row as a DataFrame
                new_row = pd.DataFrame({"Name": [new_name], 
                                        "Description": [new_descr],
                                        "Introduction": [new_intro],
                                        "Instructions": [new_instr], 
                                        "Guidelines": [new_guide],
                                        "Creator Email": [st.session_state["user_email"]]})
                # Concatenate the new row to the DataFrame
                df_tutors = pd.concat([df_tutors, new_row], ignore_index=True)
                write_csv(st.session_state["ai_tutors_data_fn"], df_tutors)

                # Display button to load
                (st.session_state["instructions"], 
                st.session_state["guidelines"], 
                st.session_state["introduction"]) = select_instructions(df_tutors, 
                                                                        tool_name=new_name)
                st.session_state["tool name"] = new_name
                st.session_state["banner"] = 'success'
                
        else:
            st.session_state["banner"] = 'missing info'
        st.rerun()

if st.session_state["banner"] is not None:
    if st.session_state["banner"] == 'success':
        st.success("Your AI Tutor is built!")
        if st.button("Load Tutor"):
            st.session_state.model_loaded = False
            # Switch to the selected page
            st.switch_page('pages/tutor_main.py')
    elif st.session_state["banner"] == 'missing info':
        st.error("Please provide all of the info below.")
    elif st.session_state["banner"] == 'name exists':
        st.error("This tool name already exists, please choose another one")