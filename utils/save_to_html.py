import tempfile
import os
import re
from typing import List, Dict
import markdown
from pygments.formatters import HtmlFormatter
import streamlit as st
import random
from datetime import datetime
from utils.emailing import send_email_chat

def escape_markdown(text: str) -> str:
    """
    Escapes markdown special characters in text to prevent markdown formatting.
    
    Args:
        text (str): The text to escape
        
    Returns:
        str: Text with markdown special characters escaped
    """
    # List of markdown special characters that need escaping
    markdown_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', 
                     '-', '.', '!', '|', '>', '~', '^']
    
    escaped_text = text
    for char in markdown_chars:
        escaped_text = escaped_text.replace(char, '\\' + char)
    return escaped_text

def convert_messages_to_markdown(messages: List[Dict[str, str]], code_block_indent='                 ') -> str:
    """
    Converts a list of message dictionaries to a markdown-formatted string.

    Each message is formatted with the sender's role as a header and the message content as a blockquote.
    Code blocks within the message content are detected and indented accordingly.

    Args:
        messages (List[Dict[str, str]]): A list of message dictionaries, where each dictionary contains
                                         'role' and 'content' keys.
        code_block_indent (str): The string used to indent lines within code blocks.

    Returns:
        A markdown-formatted string representing the messages.
    """
    markdown_lines = []
    for message in messages:
        role = message['role']
        if role == 'assistant':
            role = 'tutor'
            content = message['content']
        else:
            # Escape markdown special characters in user messages
            content = escape_markdown(message['content'])
        indented_content = _indent_content(content, code_block_indent)
        markdown_lines.append(f"###*{role.capitalize()}*:\n{indented_content}\n")
    return '\n\n'.join(markdown_lines)


def _indent_content(content: str, code_block_indent: str) -> str:
    """
    Helper function to indent the content for markdown formatting.

    Args:
        content (str): The content of the message to be indented.
        code_block_indent (str): The string used to indent lines within code blocks.

    Returns:
        The indented content as a string.
    """
    if content is not None:
        lines = content.split('\n')
        indented_lines = []
        in_code_block = False  # Flag to track whether we're inside a code block

        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                indented_lines.append(line)
            elif not in_code_block:
                line = f"> {line}"
                indented_lines.append(line)
            else:
                indented_line = code_block_indent + line  # Apply indentation
                indented_lines.append(indented_line)

        return '\n'.join(indented_lines)
    
    else:
        return ""

def markdown_to_html(md_content: str, tool_name: str) -> str:
    """
    Converts markdown content to HTML with syntax highlighting and custom styling.

    This function takes a string containing markdown-formatted text and converts it to HTML.
    It adds the tool name and current date at the top of the content.

    Args:
        md_content (str): A string containing markdown-formatted text.
        tool_name (str): The name of the tool to be displayed at the top of the file.

    Returns:
        A string containing the HTML representation of the markdown text, including a style tag
        with CSS for syntax highlighting and custom styles for the <code> and <em> elements.
    """

    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Add tool name and date at the top of the markdown content
    header = f"# {tool_name}\n**Date:** {current_date}\n\n"
    md_content = header + md_content

    # Convert markdown to HTML with syntax highlighting
    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'codehilite'])

    html_content = re.sub(
        r'<code>',
        '<code style="background-color: #f7f7f7; color: green;">',
        html_content
    )

    html_content = re.sub(
        r'<h3>',
        '<h3 style="color: blue;">',
        html_content
    )

    # Get CSS for syntax highlighting from Pygments
    css = HtmlFormatter(style='tango').get_style_defs('.codehilite')

    # Insert MathJax
    html_content = process_html_with_mathjax(f"<style>{css}</style>{html_content}")

    return html_content

def preprocess_math(html_content: str) -> str:
    """
    Preprocess the HTML content to ensure that inline and display math expressions 
    are correctly formatted for MathJax to process.

    Args:
        html_content (str): The original HTML content.

    Returns:
        The HTML content with correctly preprocessed math expressions.
    """
    # Process display math (e.g., $$...$$) first to avoid interference from inline math
    display_math_pattern = re.compile(r'(?<!\\)\$\$(.+?)\$\$', re.DOTALL)
    html_content = re.sub(display_math_pattern, r'\\[\1\\]', html_content)

    # Process inline math (e.g., $...$) with stricter negative lookahead
    inline_math_pattern = re.compile(r'(?<!\\)\$(.+?)\$(?!\$)', re.DOTALL)
    html_content = re.sub(inline_math_pattern, r'\\(\1\\)', html_content)

    return html_content


def preprocess_math(html_content: str) -> str:
    """
    Preprocess the HTML content to ensure that inline and display math expressions 
    are correctly formatted for MathJax to process.

    Args:
        html_content (str): The original HTML content.

    Returns:
        The HTML content with correctly preprocessed math expressions.
    """
    # Ensure display math is processed first (e.g., $$...$$)
    display_math_pattern = re.compile(r'(?<!\\)\$\$(.+?)\$\$', re.DOTALL)
    html_content = re.sub(display_math_pattern, r'\\[\1\\]', html_content)

    # Now process inline math (e.g., $...$) with stricter boundaries
    inline_math_pattern = re.compile(r'(?<!\\)\$(.+?)\$(?!\$)', re.DOTALL)
    html_content = re.sub(inline_math_pattern, r'\\(\1\\)', html_content)

    return html_content


def insert_mathjax(html_content: str) -> str:
    """
    Inserts the MathJax script and configuration into the HTML content.

    The MathJax script is placed before the closing </head> tag in the HTML content.

    Args:
        html_content (str): The original HTML content.

    Returns:
        The HTML content with the MathJax script and configuration inserted.
    """
    mathjax_script = """
    <!-- Load MathJax -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/latest.js?config=TeX-AMS_CHTML-full,Safe"></script>
    <!-- MathJax configuration -->
    <script type="text/x-mathjax-config">
      MathJax.Hub.Config({
        TeX: {
          equationNumbers: {
            autoNumber: "AMS",
            useLabelIds: true
          }
        },
        tex2jax: {
          inlineMath: [ ['\\\(','\\\)'], ['$','$'] ],
          displayMath: [ ['\\\[','\\\]'], ['$$','$$'] ],
          processEscapes: true,
          processEnvironments: true,
          ignoreClass: "no-mathjax",  <!-- Ignore specific classes -->
          processClass: "mathjax-process",  <!-- Process specific classes -->
        },
        displayAlign: 'center',
        CommonHTML: {
          linebreaks: {
            automatic: true
          }
        }
      });
      MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
    </script>
    """

    # Insert the MathJax script before the closing </head> tag
    if "</head>" in html_content:
        html_content = html_content.replace("</head>", f"{mathjax_script}</head>")
    else:
        # If there's no </head> tag, insert the MathJax script at the beginning
        html_content = f"{mathjax_script}\n{html_content}"
    
    return html_content


def process_html_with_mathjax(html_content: str) -> str:
    """
    Preprocess the HTML content for inline math expressions and insert the MathJax configuration.

    Args:
        html_content (str): The original HTML content.

    Returns:
        The final HTML content with preprocessed inline math and MathJax support.
    """
    # Step 1: Preprocess inline math
    preprocessed_content = preprocess_math(html_content)

    # Step 2: Insert MathJax configuration
    final_content = insert_mathjax(preprocessed_content)

    return final_content


def is_valid_file_name(file_name: str) -> bool:
    """
    Checks if the provided file name is valid based on certain criteria.

    This function checks the file name against a set of rules to ensure it does not contain
    illegal characters, is not one of the reserved words, and does not exceed 255 characters in length.

    Args:
        file_name (str): The file name to validate.

    Returns:
        bool: True if the file name is valid, False otherwise.
    """
    illegal_chars = r'[\\/:"*?<>|]'
    reserved_words = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                      'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 
                      'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']

    # Check for illegal characters, reserved words, and length constraint
    return not (re.search(illegal_chars, file_name) or
                file_name in reserved_words or
                len(file_name) > 255)

def download_chat_button(tool_name, container):
    session_md = convert_messages_to_markdown(st.session_state.messages)
    session_html = markdown_to_html(session_md, tool_name)
    file_name = f"ai_tutor_{''.join(str(random.randint(0, 9)) for _ in range(5))}.html"

    download_chat_session = container.download_button(
        label="⬇️ Download Chat",
        data=session_html,
        file_name=file_name,
        use_container_width=True,
        type='secondary',
        mime="text/markdown",
    )
    if download_chat_session:
        if is_valid_file_name(file_name):
            st.success("Data saved.")
        else:
            st.error(f"The file name '{file_name}' is not a valid file name. File not saved!", icon="🚨")

@st.dialog("Send to Teacher")
def send_to_teacher(session_html):
    st.markdown(f"Feel free to include some additional information for your teacher.")

    student_name = st.text_input("Your name/nickname (recommended):", 
                                placeholder='e.g. "MathNinja2024"')
    message = st.text_area("A message to your teacher (optional):", 
                          placeholder='e.g. "Can you please look over my chat and give me some feedback?"')
    
    send_button_spot = st.empty()
    if send_button_spot.button(f"Send", type='primary', use_container_width=True):
        filename = f"chat_history_{student_name or 'student'}.html"
        
        with st.spinner("Sending chat to teacher..."):
            # Send the HTML content directly
            send_email_chat(st.session_state.teacher_email, student_name, message, 
                        session_html, filename)
        send_button_spot.success(f"Your convo has been sent to your teacher!")

    if st.button(f"Close", use_container_width=True):
        st.rerun()

def send_chat_button(tool_name, container):
    session_md = convert_messages_to_markdown(st.session_state.messages)
    session_html = markdown_to_html(session_md, tool_name)

    
    if container.button("📨 Send to Teacher", type='primary', use_container_width=True, help="Send chat to your teacher"):
        send_to_teacher(session_html)