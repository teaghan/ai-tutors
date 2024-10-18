import streamlit as st
import extra_streamlit_components as stx
import datetime
import time

cookie_manager = stx.CookieManager(key='ai_tutors_cookies')

def update_cookies(keys=['authentication_status', 'user_email', 'role', 'username', 'email'], expiration_days=1):
    for key in keys:
        expires_at = datetime.datetime.now() + datetime.timedelta(days=expiration_days)
        if key in st.session_state.keys():
            cookie_manager.set(key, str(st.session_state[key]), expires_at=expires_at, key=key)
        else:
            cookie_manager.set(key, 'None', expires_at=expires_at, key=key)
    return

def update_tutor_cookies(keys=['tool name', 'introduction', 'instructions', 'guidelines', 'api_key', 'tutor_test_mode']):
    update_cookies(keys=keys)

def cookies_to_session(keys=['authentication_status', 'user_email', 'role', 'username', 'email']):
    for key in keys:
        value = str(cookie_manager.get(cookie=key))
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
    cookie_keys = cookie_manager.cookies.keys()
    for key in keys:
        if key in cookie_keys:
            cookie_manager.delete(key, key=f'del_{key}')

    #for k, d in zip(keys, defaults):
    #    cookie_manager.set(k, d, key=f'set_{k}')