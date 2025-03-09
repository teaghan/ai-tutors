import stripe
import os
from utils.config import open_config
import streamlit as st

def nav_to(url):
    nav_script = """
        <meta http-equiv="refresh" content="0; url='%s'">
    """ % (url)
    st.write(nav_script, unsafe_allow_html=True)

def get_create_checkout_session_url():
    stripe.api_key = os.getenv('STRIPE_API_KEY')
    price_id = os.getenv('STRIPE_PRICE_ID')
    domain_url = open_config()['domain']['url']

    try:
        checkout_session = stripe.checkout.Session.create(success_url=domain_url,
                                       line_items=[{"price": price_id, "quantity": 1}],
                                       mode="payment")
    except Exception as e:
       print(e)
       return str(e)
    return checkout_session.url