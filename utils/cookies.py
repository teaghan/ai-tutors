import streamlit as st
import extra_streamlit_components as stx
import datetime
import time

def get_manager(key='ai_tutors_cookies'):
    return stx.CookieManager(key=key)

def update_cookies(keys=['authentication_status', 'user_email', 'role', 'username', 'email'], 
                   expiration_days=0.1, do_nothing_for_now=True):
    if do_nothing_for_now:
        return
    else:
        for key in keys:
            expires_at = datetime.datetime.now() + datetime.timedelta(days=expiration_days)
            if key in st.session_state.keys():
                value = str(st.session_state[key])
            else:
                value = 'None'
            #st.write(f'Setting cookie "{key}" to "{value}')
            st.session_state['cookie_manager'].set(key, value)#, expires_at=expires_at, key=key)
        #st.session_state['cookie_manager'].cookies.save()
        return

def update_tutor_cookies(keys=['tool name', 'introduction', 'instructions', 'guidelines', 'api_key', 'tutor_test_mode']):
    update_cookies(keys=keys)

def cookies_to_session(keys=['authentication_status', 'user_email', 'role', 'username', 'email'], 
                       do_nothing_for_now=True):
    if do_nothing_for_now:
        return
    else:
        for key in keys:
            value = str(st.session_state['cookie_manager'].get(key))
            #st.write(f'Setting session state "{key}" to "{value}')
            if value=='None':
                st.session_state[key] = None
            elif value.lower()=='false':
                st.session_state[key] = False
            elif value.lower()=='true':
                st.session_state[key] = True
            else:
                st.session_state[key] = value
        # Hard-coded matching for now
        st.session_state['username'] = st.session_state['user_email']
        return

def clear_cookies(keys=['authentication_status', 'user_email', 'role', 'username', 'email', 'tool name', 
                        'introduction', 'instructions', 'guidelines', 'api_key', 'tutor_test_mode']):
    #cookie_keys = st.session_state['cookie_manager'].getAll().keys()
    cookie_keys = st.session_state['cookie_manager'].cookies.keys()
    for key in keys:
        if key in cookie_keys:
            st.session_state['cookie_manager'].remove(key)#.delete(key, key=f'del_{key}')

    #for k, d in zip(keys, defaults):
    #    cookie_manager.set(k, d, key=f'set_{k}')



from streamlit_cookies_manager import CookieManager, EncryptedCookieManager

class NEW_CM:
    def __init__(self) -> None:
        self.cookies = CookieManager()#EncryptedCookieManager(prefix="ai_tutors_cookies", 
                                      #               password="password")#CookieManager()

        if not self.cookies.ready():
            st.stop()

    def set(self, cookie_name, content):
        self.cookies[cookie_name] = content

    def get(self, cookie_name):
        return self.cookies.get(cookie_name)

    def remove(self, cookie_name):
        if cookie_name in self.cookies:
            self.cookies[cookie_name] = 'None'
    
    def save(self, key="CookieManager.sync_cookies.save"):
        #if self.cookies._cookie_manager._queue:
        self.cookies._cookie_manager._run_component(save_only=True, key=key)