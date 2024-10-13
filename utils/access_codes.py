import streamlit as st
from utils.chatbot_setup import reset_chatbot
from utils.tutor_data import select_instructions, write_csv
from datetime import datetime
import numpy as np

def use_code(df_access, df_tutors, access_code):
    # Get the current date and time
    cur_datetime = datetime.now()

    # Select the row where the Name matches the given name
    selected_row = df_access[df_access["Code"] == access_code]

    # Extract the Instructions and Guidelines for the selected row
    if not selected_row.empty:
        tool_name = selected_row["Name"].values[0]
        api_key = selected_row["API Key"].values[0]
        creator_email = selected_row["Email"].values[0]
        end_datetime_str = selected_row["End Date"].values[0]  # This includes date and time

        st.write(tool_name, np.isnan(end_datetime_str))
        if ~np.isnan(end_datetime_str):
            # Convert the end date and time string to a datetime object
            try:
                end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')  # Assuming the format is YYYY-MM-DD HH:MM:SS
            except ValueError:
                not_valid(error_msg='has an invalid date/time format')
                return
        else:
            end_datetime = None
    else:
        not_valid(error_msg='does not exist')
        return

    # Compare the current datetime with the end datetime
    if (end_datetime is not None) and end_datetime < cur_datetime:
        not_valid(error_msg='has expired')
    else:
        (st.session_state["description"],
        st.session_state["introduction"], 
        st.session_state["instructions"], 
        st.session_state["guidelines"], 
        st.session_state["availability"], _) = select_instructions(df_tutors, tool_name=tool_name)
        st.session_state["tool name"] = tool_name
        st.session_state["api_key"] = api_key
        st.session_state["tutor_test_mode"] = False

        # Launch new chat
        reset_chatbot()
        st.switch_page('pages/tutor.py')


# Dialog window to ask for single-use API Key
@st.dialog("Not Valid")
def not_valid(error_msg='does not exit'):
    st.markdown(f"The access code you provided {error_msg}.")
    if st.button(f"Close", use_container_width=True, type='primary'):
        st.rerun()

def add_code(fn, df, access_code, tool_name, api_key, 
                end_date, creator_email):
    # Create a new row as a DataFrame
    new_row = pd.DataFrame({
        "Code": [access_code]
        "Name": [tool_name], 
        "API Key": [api_key],
        "Email": [creator_email],
        "End Date": [end_date]
    })
    
    # Concatenate the new row to the DataFrame
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Write the updated DataFrame to a CSV file
    write_csv(fn, df)
    
    return df

def create_code(name):
    # Select API Key

    # Select duration (or None)

    # Calculate end date-time

    # 


