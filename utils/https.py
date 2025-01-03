
from streamlit.components.v1 import html

def enforce_https():
    """Redirect HTTP requests to HTTPS using JavaScript."""
    html(
        """
        <script>
        if (window.location.protocol !== 'https:') {
            window.location.href = window.location.href.replace('http://', 'https://');
        }
        </script>
        """,
        unsafe_allow_html=True,
    )