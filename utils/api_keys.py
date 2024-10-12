import datetime
import requests
import streamlit as st
import openai
from utils.user_data import add_api_key, delete_api_key, save_yaml

@st.dialog("Add a New API Key")
def add_key():
    key_name = st.text_input("Name")
    key_value = st.text_input("OpenAI API Key")
    if st.button("Add Key"):
        valid_key = check_openai_api_key(key_value)
        if valid_key:
            # Add key to user config
            success = add_api_key(st.session_state.users_config, 
                                st.session_state.user_email, 
                                key_name, key_value)
            
            # Update user data file
            if success:
                save_yaml(st.session_state.users_data_fn, st.session_state.users_config)
            st.rerun()
        else:
            st.error('Not a valid OpenAI API key.')

# Dialog window to confirm and delete API key
@st.dialog("Delete API Key")
def delete_key(username, key_name):
    st.markdown(f"Are you sure you want to delete the key '{key_name}'?")
    # Ask for confirmation
    if st.button(f"Delete", type='primary', use_container_width=True):
        # Remove the key from the user config
        success = delete_api_key(st.session_state.users_config, username, key_name)
        
        if success:
            # Save the updated YAML file
            save_yaml(st.session_state.users_data_fn, st.session_state.users_config)
            st.success("API key removed successfully.")
            st.rerun()
        else:
            st.error(f"Failed to remove key '{key_name}' for user '{username}'.")
    if st.button(f"Cancel", use_container_width=True):
        st.rerun()


def check_openai_api_key(api_key):
    client = openai.OpenAI(api_key=api_key)
    try:
        client.models.list()
    except openai.AuthenticationError:
        return False
    else:
        return True

def check_billing(api_key):
    now = datetime.datetime.now()
    start_date = (now - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
    end_date = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    sub_date = datetime.datetime(now.year, now.month, 1).strftime("%Y-%m-%d")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        response = requests.get(f"https://api.openai.com/v1/dashboard/billing/subscription", headers=headers)
        response.raise_for_status()
        total_amount = response.json()["hard_limit_usd"]
        st.write(total_amount)

        if total_amount > 20:
            start_date, url_usage = sub_date, f"https://api.openai.com/v1/dashboard/billing/usage?start_date={sub_date}&end_date={end_date}"
            response = requests.get(url_usage, headers=headers)
            response.raise_for_status()
            total_usage = response.json()["total_usage"] / 100
        else:
            total_usage = 0

        remaining = total_amount - total_usage

        url_models = "https://api.openai.com/v1/models"
        response = requests.get(url_models, headers=headers)
        response.raise_for_status()
        models = response.json()["data"]
        can_access = any(model["id"] == "gpt-4" for model in models)

        return [total_amount, total_usage, remaining, can_access]
    except Exception as e:
        st.write(f"Query failed: {e}")
        return [None, None, None, False]