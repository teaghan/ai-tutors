import streamlit as st

def reset_chatbot():
    # Require model loading
    st.session_state.model_loaded = False
    st.session_state["messages"] = []