import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import numpy as np
import random
import string

from utils.session import reset_chatbot
from utils.tutor_data import select_instructions, write_csv, read_csv
from utils.knowledge_files import get_file_paths
from utils.config import domain_url

def use_code(df_access, df_tutors, access_code):
    # Get the current date and time
    cur_datetime = datetime.now(tz=timezone.utc)

    # Select the row where the Code matches the given code (case insensitive)
    selected_row = df_access[df_access["Code"].str.upper() == access_code.upper()]

    # Extract the Instructions and Guidelines for the selected row
    if not selected_row.empty:
        tool_name = selected_row["Name"].values[0]
        st.session_state['teacher_email'] = selected_row["Email"].values[0]
        end_datetime_str = selected_row["End Date"].values[0]  # This includes date and time

        # Check if the end date is NaN
        if pd.isna(end_datetime_str) or end_datetime_str == '':
            end_datetime = None  # No expiration
        else:
            try:
                # Convert the end date and time string to a datetime object
                end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')
            except ValueError:
                not_valid(error_msg='has an invalid date/time format')
                return
    else:
        not_valid(error_msg='does not exist')
        return

    # Compare the current datetime with the end datetime (if it exists)
    if (end_datetime is not None) and (end_datetime < cur_datetime):
        not_valid(error_msg='has expired')
    else:
        # Extract and set instructions and other details in session state
        (st.session_state["description"],
         st.session_state["introduction"],
         st.session_state["instructions"],
         st.session_state["guidelines"],
         st.session_state["knowledge"],
         st.session_state["availability"]) = select_instructions(df_tutors, tool_name=tool_name)

        st.session_state["tool name"] = tool_name
        st.session_state["tutor_test_mode"] = False

        # Launch new chat
        reset_chatbot()
        st.switch_page('pages/tutor.py')

# Dialog window to ask for single-use access code
@st.dialog("Not Valid")
def not_valid(error_msg='does not exit'):
    st.markdown(f"The access code you provided {error_msg}.")
    if st.button(f"Close", use_container_width=True, type='primary'):
        st.rerun()

# Dialog window to generate access code
@st.dialog("Access Code")
def code_window(tool_name):

    # Select duration
    duration_options = ['30 min', '1 hr', '2 hr', '12 hr', '24 hr', '48 hr', 'Indefinite']
    duration_hrs = [0.5, 1, 2, 12, 24, 48, None]
    duration_str = st.selectbox('Access duration', duration_options)
    duration = duration_hrs[duration_options.index(duration_str)]

    # Calculate end date-time
    if duration is not None:
        end_date = datetime.now(tz=timezone.utc) + timedelta(hours=duration)
        end_date = end_date.strftime('%Y-%m-%d %H:%M')  # Format to save nicely in the CSV
    else:
        end_date = np.nan  # Save as NaN if there is no end date

    # Generate 6-digit code
    access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    if st.button(f"Share", use_container_width=True, type='primary'):
        st.session_state.df_access_codes = add_code(st.session_state.access_codes_data_fn,
                                                    access_code, tool_name, 
                                                    end_date, st.session_state.user_email)
        # Display success banner with the access code
        url = domain_url()
        st.success(f"Access code **{access_code}** created successfully!\n\n You can also share [this link]({url}?code={access_code}) with students.")
        #st.rerun()
    if st.button(f"Close", use_container_width=True):
        st.rerun()

def add_code(fn, access_code, tool_name, 
                end_date, creator_email):
    # Load up to date csv
    df = read_csv(fn)

    # Create a new row as a DataFrame
    new_row = pd.DataFrame({
        "Code": [access_code],
        "Name": [tool_name], 
        "Email": [creator_email],
        "End Date": [end_date]
    })
    
    # Concatenate the new row to the DataFrame
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Write the updated DataFrame to a CSV file
    write_csv(fn, df)
    
    return df

def create_code(tool_name):

    # Select duration (or None)
    code_window(tool_name)

# Dialog window to confirm and delete access code
@st.dialog("Delete Access Code")
def delete_code(username, code):
    st.markdown(f"Are you sure you want to delete the code '{code}'?")
    # Ask for confirmation
    if st.button(f"Delete", type='primary', use_container_width=True):
        # Remove the code from the user config
        success = delete_access_code(st.session_state.df_access_codes, username, code)
        
        if success:
            # Save the updated CSV file
            write_csv(st.session_state.access_codes_data_fn, st.session_state.df_access_codes)
            st.success("Access code removed successfully.")
            st.rerun()
        else:
            st.error(f"Failed to remove code '{code}' for user '{username}'.")
    if st.button(f"Cancel", use_container_width=True):
        st.rerun()

# Function to delete the access code from the DataFrame
def delete_access_code(df, username, code):
    # Check if the access code exists for the given user
    selected_row = df[(df["Code"] == code) & (df["Email"] == username)]
    if not selected_row.empty:
        # Drop the row with the matching code
        df.drop(selected_row.index, inplace=True)
        return True
    else:
        return False

# Dialog window to extend access code
@st.dialog("Extend Access Code")
def extend_code(username, code):
    st.markdown(f"Extend the duration for code '{code}'.")

    # Provide duration options to extend the code
    duration_options = ['30 min', '1 hr', '2 hr', '12 hr', '24 hr', '48 hr', 'Indefinite']
    duration_hrs = [0.5, 1, 2, 12, 24, 48, None]
    duration_str = st.selectbox('Extension duration', duration_options)
    extension_duration = duration_hrs[duration_options.index(duration_str)]

    # Find the current end date in the DataFrame
    selected_row = st.session_state.df_access_codes[
        (st.session_state.df_access_codes["Code"] == code) & 
        (st.session_state.df_access_codes["Email"] == username)
    ]

    if selected_row.empty:
        st.error(f"Code '{code}' for user '{username}' not found.")
        return

    # Get current end date
    current_end_date_str = selected_row["End Date"].values[0]

    # If the current end date is NaN (no end date), set the current end date to now
    if pd.isna(current_end_date_str) or current_end_date_str == '':
        current_end_datetime = datetime.now(tz=timezone.utc)
    else:
        current_end_datetime = datetime.strptime(current_end_date_str, '%Y-%m-%d %H:%M')

    # Calculate the new end date based on the extension duration
    if extension_duration is not None:
        new_end_datetime = current_end_datetime + timedelta(hours=extension_duration)
        new_end_date = new_end_datetime.strftime('%Y-%m-%d %H:%M')  # Format as string for saving
    else:
        new_end_date = np.nan  # Indefinite (no end date)

    if st.button(f"Extend", type='primary', use_container_width=True):
        # Update the DataFrame with the new end date
        st.session_state.df_access_codes.loc[selected_row.index, 'End Date'] = new_end_date

        # Save the updated CSV file
        write_csv(st.session_state.access_codes_data_fn, st.session_state.df_access_codes)
        st.success(f"Access code '{code}' extended successfully.")
        st.rerun()

    if st.button(f"Cancel", use_container_width=True):
        st.rerun()

def extend_this_code(username, code):
    def inside_fn():
        extend_code(username, code)
    return inside_fn

def delete_this_code(username, code):
    def inside_fn():
        delete_code(username, code)
    return inside_fn

# Mock-up of get_access_codes function (this needs to return codes, tool names, and end dates)
def get_access_codes(df, user_email):
    filtered_df = df[df['Email'] == user_email]
    access_codes = filtered_df['Code'].tolist()
    tool_names = filtered_df['Name'].tolist()
    end_dates = filtered_df['End Date'].tolist()
    return access_codes, tool_names, end_dates

def display_codes():
    st.header('My Access Codes')
    # Load Access Codes for this user's email
    access_codes, tool_names, end_dates = get_access_codes(st.session_state.df_access_codes, 
                                                           st.session_state.user_email)

    # Display a table with columns: Code, Name, End Date, Extend button, and Delete button
    if access_codes is not None:
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
        with col1:
            st.subheader('Code')
        with col2:
            st.subheader('Name')
        with col3:
            st.subheader('Exp. Date (UTC)')
        with col4:
            st.subheader('')
            st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
        with col5:
            st.subheader('')
            st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)

        # Iterate through the access codes, tool names, and end dates
        for code, name, date in zip(access_codes, tool_names, end_dates):
            with col1:
                st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
                #st.markdown(f"<div style='font-size:16px;'>{code}</div>", unsafe_allow_html=True)
                st.markdown(f'[{code}]({domain_url()}?code={code})')
            with col2:
                st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
                st.markdown(name)
            with col3:
                # Check if date is NaN or None, display 'N/A' instead
                st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
                display_date = "N/A" if (pd.isna(date) or date == '') else date
                st.markdown(display_date)
            with col4:
                st.markdown("<div style='margin-bottom: 35px;'></div>", unsafe_allow_html=True)
                if st.button(f"Extend", key=f'{code}_extend', type="primary", use_container_width=True,
                             on_click=extend_this_code(st.session_state.user_email, code)):
                    pass
            with col5:
                st.markdown("<div style='margin-bottom: 35px;'></div>", unsafe_allow_html=True)
                if st.button(f"Delete", key=f'{code}_delete', type="secondary", use_container_width=True,
                              on_click=delete_this_code(st.session_state.user_email, code)):
                    pass