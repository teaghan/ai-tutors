import streamlit as st
import datetime

def update_cookies(keys=['authentication_status', 'user_email', 'role', 'username', 'email']):
    for key in keys:
        value = str(st.session_state.get(key, 'None'))
        st.write(f'Setting cookie {key} to {value}')  # Debugging
        st.session_state['cookie_manager'].set(key, value)

def update_tutor_cookies(keys=['tool name', 'introduction', 'instructions', 'guidelines', 'api_key', 'tutor_test_mode']):
    update_cookies(keys=keys)


def cookies_to_session(keys=['authentication_status', 'user_email', 'role', 'username', 'email']):
    #cookie_keys = st.session_state['cookie_manager'].cookies.keys()
    for key in keys:
        #if key not in cookie_keys:
        #    st.write(f'{key} not in cookies')
        #    continue
        value = str(st.session_state['cookie_manager'].get(key))
        st.write(f'Setting session state "{key}" to "{value}"')
        if value=='None':
            st.session_state[key] = None
        elif value.lower()=='false':
            st.session_state[key] = False
        elif value.lower()=='true':
            st.session_state[key] = True
        else:
            st.session_state[key] = value
    return

def clear_cookies(keys=['authentication_status', 'user_email', 'role', 'username', 'email', 'tool name', 
                        'introduction', 'instructions', 'guidelines', 'api_key', 'tutor_test_mode']):
    cookie_keys = st.session_state['cookie_manager'].cookies.keys()
    for key in keys:
        if key in cookie_keys:
            st.session_state['cookie_manager'].remove(key)

