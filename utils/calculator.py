import streamlit as st
import emoji

def equation_creator():
    # Initialize session state for the equation if it doesn't exist
    if 'input_equation' not in st.session_state:
        st.session_state.input_equation = ""
    if 'latex_equation' not in st.session_state:
        st.session_state.latex_equation = ""

    st.markdown("Use the buttons and edit the equation directly.")
    # Creating a container for input and outputto be placed side by side

    st.markdown("**Copy** this text into your message:")
    input_display = st.empty()
    with input_display:
        text = st.text_input("Copy this text:", 
                             key='input_equation', 
                             label_visibility="collapsed")

    #if st.session_state.input_equation != "":
    st.columns((1,20))[1].markdown("to show the AI Tutor this equation:")
    latex_display = st.empty()
    if st.session_state.input_equation == "":
        latex_display.markdown("...")
    else:
        latex_display.markdown(f"${st.session_state.input_equation}$")

    # Function to update display
    def update_equation(value):
        st.session_state["input_equation"] = st.session_state["input_equation"] + value
        # Wrap the equation in $ signs for LaTeX rendering
        latex_display.markdown(f"${st.session_state.input_equation}$")

    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns((1.5,1.5,1.5,0.1,1,1,1,1))
        
    with c1:
        st.button("(", on_click=update_equation, args=("( ",), use_container_width=True)
        st.button("$\sin()$", on_click=update_equation, args=("\sin{ () }",), use_container_width=True)
        st.button(r"$a^b$", on_click=update_equation, args=("a^{ b }",), use_container_width=True)
        st.button("$\log()$", on_click=update_equation, args=("\log{ () }",), use_container_width=True)

    with c2:
        st.button(")", on_click=update_equation, args=(") ",), use_container_width=True)
        st.button("$\cos()$", on_click=update_equation, args=("\cos{ () }",), use_container_width=True)
        st.button(r"$\sqrt{\ \ }$", on_click=update_equation, args=("\sqrt{  }",), use_container_width=True)
        st.button("$\ln()$", on_click=update_equation, args=("\ln{ () }",), use_container_width=True)

    with c3:
        st.button("$\pi$", on_click=update_equation, args=("\pi ",), use_container_width=True)
        st.button("$\\tan()$", on_click=update_equation, args=("\\tan{ () }",), use_container_width=True)
        st.button(r"$^n\sqrt{\ \ }$", on_click=update_equation, args=("\sqrt[n]{ }",), use_container_width=True)
        st.button(r"$\frac{\ x \ }{\ y \ }$", on_click=update_equation, args=("\\frac{ x }{ y }",), use_container_width=True)  # Added fraction button

    with c5:
        st.button("7", on_click=update_equation, args=("7",), use_container_width=True)
        st.button("4", on_click=update_equation, args=("4",), use_container_width=True)
        st.button("1", on_click=update_equation, args=("1",), use_container_width=True)
        st.button("0", on_click=update_equation, args=("0",), use_container_width=True)

    with c6:
        st.button("8", on_click=update_equation, args=("8",), use_container_width=True)
        st.button("5", on_click=update_equation, args=("5",), use_container_width=True)
        st.button("2", on_click=update_equation, args=("2",), use_container_width=True)
        st.button(".", on_click=update_equation, args=(".",), use_container_width=True)

    with c7:
        st.button("9", on_click=update_equation, args=("9",), use_container_width=True)
        st.button("6", on_click=update_equation, args=("6",), use_container_width=True)
        st.button("3", on_click=update_equation, args=("3",), use_container_width=True)
        st.button(emoji.emojize(":heavy_equals_sign:"), on_click=update_equation, args=("= ",), use_container_width=True)

    with c8:
        st.button(emoji.emojize(":heavy_plus_sign:"), on_click=update_equation, args=("+",), use_container_width=True)
        st.button(emoji.emojize(":heavy_minus_sign:"), on_click=update_equation, args=("-",), use_container_width=True)
        st.button(emoji.emojize(":heavy_multiplication_x:"), on_click=update_equation, args=("\\times ",), use_container_width=True)
        st.button(emoji.emojize(":heavy_division_sign:"), on_click=update_equation, args=("/",), use_container_width=True)

    return text

if __name__ == "__main__":
    equation_creator()