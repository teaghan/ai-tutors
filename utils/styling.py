import streamlit as st
import streamlit.components.v1 as components
import time

def load_style():
    """Load and apply custom styling to the Streamlit app."""
    
    # Define the CSS
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@700&family=Montserrat:wght@400;500;600;700&display=swap');

     /* Base styles */
    body * {
        font-family: 'Montserrat', sans-serif !important;
    }

    /* Headers */
    h1, h2, h3 {
        font-family: 'Lexend', sans-serif !important;
        color: #0F1B2A !important;
    }

    /* h4 specific styling */
    h4, h5, h6 {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 400 !important;
        color: #666666 !important;
        -webkit-font-smoothing: antialiased;
    }

    /* Text formatting */
    strong {
        font-weight: 700 !important;
    }

    em {
        font-style: italic !important;
    }
    """
    
    # Inject CSS
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def stream_lines(text: str, pause_time: float = 0.02, initial_pause: float = 0.7, slow_write: bool = True, center: bool = True) -> None:
    """
    Stream text letter by letter.
    
    Args:
        text (str): Text to be displayed
        pause_time (float): Time to pause between each letter
        slow_write (bool): Whether to stream the text or display it immediately
        center (bool): Whether to center-align the text
    """
    def stream_text(text):
        sentence = ""
        for letter in text:
            sentence += letter
            yield sentence.replace("\n", "<br>")  # Use <br> for new lines
    
    style = "text-align: center; " if center else ""
    style += "color: grey;"
            
    if slow_write:
        time.sleep(initial_pause)
        with st.empty():
            for sentence in stream_text(text):
                st.markdown(f"<h5 style='{style}'>{sentence}</h5>", unsafe_allow_html=True)
                time.sleep(pause_time)
    else:
        st.markdown(f"<h5 style='{style}'>{text.replace('\n', '<br>')}</h5>", unsafe_allow_html=True)


def scroll_to(element_id):
    components.html(f'''
        <script>
            var element = window.parent.document.getElementById("{element_id}");
            element.scrollIntoView({{behavior: 'smooth'}});
        </script>
    '''.encode())

def button_style():
    pr_color = st.get_option('theme.primaryColor')
    bg_color = st.get_option('theme.backgroundColor')
    sbg_color = st.get_option('theme.secondaryBackgroundColor')
    st.markdown(
        f"""
        <style>
        .element-container:has(#button-after) + div button {{
            background-color: {bg_color};
            border: 0px solid {pr_color};
            color: {pr_color};
            padding: 0.5em 1em;
            border-radius: 4px;
            transition: background-color 0.2s ease;
        }}
        .element-container:has(#button-after) + div button:hover {{
            background-color: {sbg_color};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    def custom_button():
        st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)

    return custom_button

def columns_style():
    
    def custom_columns():        
        st.markdown(
        """
        <style>
        [data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            gap: 10px;  /* Space between buttons */
            padding-bottom: 10px;  /* Space for scrollbar */
            justify-content: flex-start !important;  /* Align items to start */
            max-width: 100% !important;
        }
        
        /* Lock column widths to a specific size */
        [data-testid="stHorizontalBlock"] > div {
            flex: 0 0 80px !important;  /* Fixed width for columns */
            min-width: 80px !important;
            width: 80px !important;
            margin-right: 0 !important;
        }
        
        /* Make buttons fill their container */
        [data-testid="stHorizontalBlock"] button {
            width: 100% !important;
            min-width: unset !important;
            padding: 0 8px !important;
        }
        
        /* Hide scrollbar (optional) */
        [data-testid="stHorizontalBlock"]::-webkit-scrollbar {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
        st.markdown('<span id="scrollable-columns-after"></span>', unsafe_allow_html=True)
    
    return custom_columns