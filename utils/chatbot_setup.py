import streamlit as st

def reset_chatboat():
    # Require model loading
    st.session_state.model_loaded = False
    st.session_state["messages"] = []