
import os
import streamlit as st

def enforce_https():
    """Redirect HTTP requests to HTTPS."""
    # Check the `X-Forwarded-Proto` header set by Heroku
    forwarded_proto = os.environ.get("X_FORWARDED_PROTO", "http")
    if forwarded_proto != "https":
        st.write(
            f"""
            <meta http-equiv="refresh" content="0; url=https://{os.environ['HOST_NAME']}" />
            """,
            unsafe_allow_html=True,
        )