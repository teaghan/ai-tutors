import streamlit as st

import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)

from st_files_connection import FilesConnection

def hash_passwords(config):
    # Pre-hashing all plain text passwords once
    stauth.Hasher.hash_passwords(config['credentials'])

@st.cache_data
def read_yaml(fn):
    # Create connection object and retrieve file contents.
    conn = st.connection('s3', type=FilesConnection, ttl=0)

    # Read the YAML file from S3 as a string
    yaml_content = conn.read(fn, input_format="text", ttl=0)

    # Return pandas dataframe
    return yaml.load(yaml_content, Loader=SafeLoader)

    #with open(fn) as file:
    #    config = yaml.load(file, Loader=SafeLoader)
    #return config

def read_users(fn):

    config = read_yaml(fn)
    #hash_passwords(config)
    authenticator = stauth.Authenticate(
        config['credentials'],
        cookie_name='ai_tutors_cookies',
        cookie_key='cookie_key',
        cookie_expiry_days=1,
        auto_hash=False
    )
    return config, authenticator


def get_email(config, username):
    # Navigate the dictionary to find the email for the given username
    return config['credentials']['usernames'][username]['email']

def get_api_keys(config, username):
    try:
        # Check if the user exists and if they have named API keys
        api_keys = config['credentials']['usernames'][username].get('api_keys', None)
        
        # If api_keys is None or empty, return None
        if not api_keys:
            return None
        
        # Convert the dictionary into a list of tuples (name, key)
        return [(name, key) for name, key in api_keys.items()]
    except KeyError:
        # Return None if the username is not found
        return None

def add_api_key(config, username, key_name, key_value):
    try:
        # Check if the user exists
        user_data = config['credentials']['usernames'][username]
        
        # Check if the user already has an api_keys field
        if 'api_keys' not in user_data:
            # If not, create an empty dictionary for api_keys
            user_data['api_keys'] = {}
        
        # Add or update the key for the given name
        user_data['api_keys'][key_name] = key_value
        
        return True  # Indicate success
    except KeyError:
        # Return False if the username is not found
        return False

def delete_api_key(config, username, key_name):
    try:
        # Check if the user exists and has an api_keys field
        user_data = config['credentials']['usernames'][username]
        
        if 'api_keys' in user_data and key_name in user_data['api_keys']:
            # Remove the key
            del user_data['api_keys'][key_name]
            
            return True  # Indicate success
        else:
            return False  # Key or api_keys field not found
    except KeyError:
        # Return False if the username is not found
        return False

def save_yaml(fn, config):
    # Saving config file
    #with open(fn, 'w', encoding='utf-8') as file:
    #    yaml.dump(config, file, default_flow_style=False)

    # Convert the config dictionary into a YAML string
    yaml_content = yaml.dump(config, default_flow_style=False)

    conn = st.connection('s3', type=FilesConnection, ttl=0)

    # Open the connection and write the YAML content to S3
    with conn.open(fn, "wt") as file:
        file.write(yaml_content)
    # Reset cache so that new data gets loaded
    read_yaml.clear()


def reset_password(authenticator):
    # Creating a password reset widget
    if st.session_state['authentication_status']:
        try:
            if authenticator.reset_password(st.session_state['username']):
                st.success('Password modified successfully')
        except (CredentialsError, ResetError) as e:
            st.error(e)

def forgot_password(authenticator):
    # Creating a forgot password widget
    try:
        (username_of_forgotten_password,
            email_of_forgotten_password,
            new_random_password) = authenticator.forgot_password()
        if username_of_forgotten_password:
            st.success('New password sent securely')
            # Random password to be transferred to the user securely
        elif not username_of_forgotten_password:
            st.error('Username not found')
    except ForgotError as e:
        st.error(e)

def forgot_username(authenticator):
    # Creating a forgot username widget
    try:
        (username_of_forgotten_username,
            email_of_forgotten_username) = authenticator.forgot_username()
        if username_of_forgotten_username:
            st.success('Username sent securely')
            # Username to be transferred to the user securely
        elif not username_of_forgotten_username:
            st.error('Email not found')
    except ForgotError as e:
        st.error(e)