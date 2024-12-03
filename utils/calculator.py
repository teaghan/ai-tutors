import streamlit as st
import emoji

def equation_creator():
    # Initialize session state for the equation if it doesn't exist
    if 'input_equation' not in st.session_state:
        st.session_state.input_equation = ""
    if 'latex_equation' not in st.session_state:
        st.session_state.latex_equation = ""

    # Creating a container for input and outputto be placed side by side
    #st.write("Use the buttons and edit the equation in the box below:")
    input_display = st.empty()
    with input_display:
        text = st.text_input("Use the buttons and edit the equation in the box below:", max_chars=1000, key='input_equation', label_visibility="visible")

    st.info("💡 Tip: Copy the content from the text box above and paste it into your chat with the AI Tutor to discuss the equation.")

    if st.session_state.input_equation != "":
        st.write("This is what the equation looks like to the AI Tutor:")
    latex_display = st.empty()
    with latex_display:
        latex_display.markdown(f"${st.session_state.input_equation}$")

    # Function to update display
    def update_equation(value):
        st.session_state["input_equation"] = st.session_state["input_equation"] + value
        # Wrap the equation in $ signs for LaTeX rendering
        latex_display.markdown(f"${st.session_state.input_equation}$")

    # Function to clear input
    def clear_input():
        st.session_state.input_equation = ""

    button_style = """
        <style>
        .stButton>button {
            font-size: 30px;
            padding: 10px;
            width: 100%;
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            color: #333;
        }
        .stButton>button:hover {
            background-color: #ddd;
            border: 1px solid #bbb;
        }
        </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

    # Advanced Operators
    #with c1:
    #col1, col2, col3 = st.columns(3)
        
    with c1:
        st.button("(", on_click=update_equation, args=("( ",))
        st.button("$\sin()$", on_click=update_equation, args=("\sin{ () }",))
        st.button(r"$a^b$", on_click=update_equation, args=("a^{ b }",))
        st.button("$\log()$", on_click=update_equation, args=("\log{ () }",))
        st.button("{", on_click=update_equation, args=("{ ",))

    with c2:
        st.button(")", on_click=update_equation, args=(") ",))
        st.button("$\cos()$", on_click=update_equation, args=("\cos{ () }",))
        st.button(r"$\sqrt{\ \ }$", on_click=update_equation, args=("\sqrt{  }",))
        st.button("$\ln()$", on_click=update_equation, args=("\ln{ () }",))
        st.button("}", on_click=update_equation, args=("} ",))

    with c3:
        st.button("$\pi$", on_click=update_equation, args=("\pi ",))
        st.button("$\\tan()$", on_click=update_equation, args=("\\tan{ () }",))
        st.button(r"$^n\sqrt{\ \ }$", on_click=update_equation, args=("\sqrt[n]{ }",))
        st.button("e", on_click=update_equation, args=("e ",))
        st.button(r"$\frac{\ x \ }{\ y \ }$", on_click=update_equation, args=("\\frac{ x }{ y }",))  # Added fraction button


    # Numbers and Basic Operators
    #with c2:
    #    col1, col2, col3, col4 = st.columns(4)

    with c5:
        st.button("7", on_click=update_equation, args=("7",))
        st.button("4", on_click=update_equation, args=("4",))
        st.button("1", on_click=update_equation, args=("1",))
        st.button("0", on_click=update_equation, args=("0",))

    with c6:
        st.button("8", on_click=update_equation, args=("8",))
        st.button("5", on_click=update_equation, args=("5",))
        st.button("2", on_click=update_equation, args=("2",))
        st.button(".", on_click=update_equation, args=(".",))

    with c7:
        st.button("9", on_click=update_equation, args=("9",))
        st.button("6", on_click=update_equation, args=("6",))
        st.button("3", on_click=update_equation, args=("3",))
        st.button(emoji.emojize(":heavy_equals_sign:"), on_click=update_equation, args=("= ",))

    with c8:
        st.button(emoji.emojize(":heavy_plus_sign:"), on_click=update_equation, args=("+",))
        st.button(emoji.emojize(":heavy_minus_sign:"), on_click=update_equation, args=("-",))
        st.button(emoji.emojize(":heavy_multiplication_x:"), on_click=update_equation, args=("\\times ",))
        st.button(emoji.emojize(":heavy_division_sign:"), on_click=update_equation, args=("/",))
        st.button("C", on_click=clear_input)

if __name__ == "__main__":
    equation_creator()