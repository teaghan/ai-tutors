import re
from typing import List, Dict
import markdown
import streamlit as st
import random
from datetime import datetime
from utils.emailing import send_email_chat
import weasyprint
from weasyprint.text.fonts import FontConfiguration
from pygments.formatters import HtmlFormatter
import matplotlib.pyplot as plt
import io

def latex_to_svg(latex: str, is_inline: bool = True) -> str:
    """
    Convert LaTeX to SVG using matplotlib.
    """
    try:
        # Create figure with transparent background
        if is_inline:
            fig = plt.figure(figsize=(0.4, 0.5))  # Adjusted for inline equations
        else:
            fig = plt.figure(figsize=(6, 1))  # Adjusted for display equations
        fig.patch.set_alpha(0)
        
        print('latex: ', latex)
        # Add text with LaTeX
        if is_inline:
            plt.text(0, 0, f'${latex}$', fontsize=10)
        else:
            plt.text(0, 0, f'${latex}$', fontsize=14)
            
        # Remove axes and margins
        plt.axis('off')
        plt.margins(0)
        
        # Save to SVG string
        buf = io.BytesIO()
        plt.savefig(buf, format='svg', bbox_inches='tight', pad_inches=0, 
                   transparent=True, dpi=300)
        plt.close()
        
        # Get SVG content and clean it up
        svg_content = buf.getvalue().decode('utf-8')
        return svg_content
    except Exception as e:
        print(f"Error converting latex to svg: {e}")
        return latex
    
def convert_math_to_svg(html_content: str) -> str:
    """
    Converts LaTeX math expressions to SVG for PDF rendering.
    """
    # Convert display math ($$...$$)
    display_math_pattern = re.compile(r'(?<!\\)\$\$(.*?)\$\$', re.DOTALL)
    def replace_display_math(match):
        latex = match.group(1).strip()
        try:
            svg_content = latex_to_svg(latex, is_inline=False)
            return f'<div class="math-block">{svg_content}</div>'
        except:
            return match.group(0)
    
    # Convert inline math ($...$)
    inline_math_pattern = re.compile(r'(?<!\\)\$(.*?)\$(?!\$)', re.DOTALL)
    def replace_inline_math(match):
        latex = match.group(1).strip()
        try:
            svg_content = latex_to_svg(latex, is_inline=True)
            return f'<span class="math-inline">{svg_content}</span>'
        except:
            return match.group(0)
    
    # Process math expressions
    html_content = re.sub(display_math_pattern, replace_display_math, html_content)
    html_content = re.sub(inline_math_pattern, replace_inline_math, html_content)
    
    return html_content

def generate_pdf(html_content: str) -> bytes:
    """
    Generate PDF from HTML content with proper font configuration.
    """
    font_config = FontConfiguration()
    html = weasyprint.HTML(string=html_content, url_fetcher=lambda url: {'string': '', 'mime_type': 'text/css'})
    return html.write_pdf(
        stylesheets=[],
        font_config=font_config
    )

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
    """
    if content is not None:
        lines = content.split('\n')
        indented_lines = []
        in_code_block = False  # Flag to track whether we're inside a code block
        in_display_math = False  # Flag to track whether we're inside display math

        for line in lines:
            # Check for display math
            if line.strip().startswith('$$'):
                in_display_math = not in_display_math
                indented_lines.append(line)
                continue
            
            # Check for code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                indented_lines.append(line)
            elif in_code_block:
                indented_line = code_block_indent + line  # Apply indentation
                indented_lines.append(indented_line)
            elif in_display_math:
                # Don't add blockquote for display math content
                indented_lines.append(line)
            else:
                line = f"> {line}"
                indented_lines.append(line)

        return '\n'.join(indented_lines)
    else:
        return ""

def markdown_to_html(md_content: str, tool_name: str, student_name: str = None, student_message: str = None) -> str:
    """
    Converts markdown content to HTML with syntax highlighting and custom styling.
    
    Args:
        md_content (str): The markdown content to convert
        tool_name (str): Name of the tool
        student_name (str, optional): Student's name to include in header
        student_message (str, optional): Student's message to include in header
    """
    # Get the current date and theme color
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    theme_color = st.get_option('theme.primaryColor')

    # Add tool name and date at the top of the markdown content
    header = f"# {tool_name}\n**Date:** {current_date}\n\n"
    
    # Add student info if provided
    if student_name or student_message:
        header += "#### Student Information\n"
        if student_name:
            header += f"**Student Name:** {student_name}\n\n"
        if student_message:
            header += f"**Message to teacher:** {student_message}\n\n"
        header += "---\n\n"  # Add a horizontal line to separate student info from chat

    md_content = header + md_content

    # Pre-process display math blocks to protect them
    display_math_blocks = []
    def save_display_math(match):
        math = match.group(1).strip()
        display_math_blocks.append(math)
        return f"DISPLAY_MATH_PLACEHOLDER_{len(display_math_blocks)-1}"
    
    # Save display math blocks and replace with placeholders
    display_math_pattern = re.compile(r'(?<!\\)\$\$(.*?)\$\$', re.DOTALL)
    md_content = re.sub(display_math_pattern, save_display_math, md_content)

    # Convert markdown to HTML with syntax highlighting
    extensions = [
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
    ]
    
    html_content = markdown.markdown(md_content, extensions=extensions)

    # Restore display math blocks
    for i, math in enumerate(display_math_blocks):
        placeholder = f"DISPLAY_MATH_PLACEHOLDER_{i}"
        html_content = html_content.replace(placeholder, f"$${math}$$")

    # Get CSS for syntax highlighting from Pygments
    css = HtmlFormatter(style='tango').get_style_defs('.codehilite')

    # Convert math expressions to SVG
    html_content = convert_math_to_svg(html_content)

    html_content = f"""
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Color+Emoji&display=swap" rel="stylesheet">
        <style>
            {css}
            body {{ 
                font-family: Arial, sans-serif;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }}
            *[class*="emoji"], 
            *[class*=""] {{
                font-family: 'Noto Color Emoji', Arial, sans-serif !important;
            }}
            h1, h2 {{ 
                color: {theme_color};
                margin-bottom: 0.5em;
            }}
            h3 {{ 
                color: {theme_color};
                opacity: 0.8;
                margin-bottom: 0.3em;
            }}
            code {{ 
                background-color: #f7f7f7; 
                color: green; 
                padding: 2px 4px; 
            }}
            blockquote {{ 
                border-left: 3px solid {theme_color}; 
                margin-left: 20px;
                padding-left: 10px;
                margin-top: 0.5em;
            }}
            .math-block {{
                text-align: center;
                margin: 1em 0;
            }}
            .math-inline {{
                vertical-align: middle;
                display: inline-block;
            }}
            svg {{
                vertical-align: middle;
            }}
            hr {{
                border: none;
                border-top: 2px solid {theme_color};
                opacity: 0.3;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    return html_content

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

def download_chat_button(tool_name, container, include_text=True):
    session_md = convert_messages_to_markdown(st.session_state.messages)
    session_html = markdown_to_html(session_md, tool_name)
    file_name = f"ai_tutor_{''.join(str(random.randint(0, 9)) for _ in range(5))}.pdf"

    if include_text:
        button_text = "💾 Download Chat"
        use_container_width = True
    else:
        button_text = "💾"
        use_container_width = False

    pdf_content = generate_pdf(session_html)

    download_chat_session = container.download_button(
        label=button_text,
        data=pdf_content,
        file_name=file_name,
        use_container_width=use_container_width,
        type='secondary',
        mime="application/pdf",
        help="Save chat"
    )
    if download_chat_session:
        if is_valid_file_name(file_name):
            st.success("Data saved.")
        else:
            st.error(f"The file name '{file_name}' is not a valid file name. File not saved!", icon="🚨")

@st.dialog("Send to Teacher")
def send_to_teacher(tool_name):
    st.markdown(f"Feel free to include some additional information for your teacher.")

    student_name = st.text_input("Your name/nickname (recommended):", 
                                placeholder='e.g. "MathNinja2024"')
    message = st.text_area("A message to your teacher (optional):", 
                          placeholder='e.g. "Can you please look over my chat and give me some feedback?"')
    
    send_button_spot = st.empty()
    email_sent = st.session_state.get('email_sent', False)
    if not email_sent:
        if send_button_spot.button(f"Send", type='primary', use_container_width=True):
            st.session_state['email_sent'] = True
            filename = f"chat_history_{student_name or 'student'}.pdf"
            
            with st.spinner("Sending chat to teacher..."):
                # Do all the conversion work inside the spinner
                session_md = convert_messages_to_markdown(st.session_state.messages)
                session_html = markdown_to_html(session_md, tool_name, 
                                             student_name=student_name, 
                                             student_message=message)
                pdf_content = generate_pdf(session_html)
                send_email_chat(st.session_state.teacher_email, student_name, message, 
                            pdf_content, filename)
            send_button_spot.success(f"Your convo has been sent to your teacher!")
    else:
        send_button_spot.success(f"Your convo has been sent to your teacher!")
    if st.button(f"Close", use_container_width=True):
        st.rerun()

def send_chat_button(tool_name, container, include_text=True):
    if include_text:
        button_text = "📨 Send to Teacher"
        use_container_width = True
    else:
        button_text = "✉️"
        use_container_width = False
    if container.button(button_text, type='primary', 
                    use_container_width=use_container_width, 
                    help="Send chat to your teacher"):
        send_to_teacher(tool_name)