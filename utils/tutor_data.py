import streamlit as st
import pandas as pd
from st_files_connection import FilesConnection

def read_csv(fn):
    # Create connection object and retrieve file contents.
    conn = st.connection('s3', type=FilesConnection, ttl=0)
    # Return pandas dataframe
    return conn.read(fn, input_format="csv", ttl=0) 
    #return pd.read_csv(fn)

def write_csv(fn, df):
    # Create connection object and write file contents.
    conn = st.connection('s3', type=FilesConnection, ttl=0)
    with conn.open(fn, "wt") as f:
        df.to_csv(fn, index=False)

def select_instructions(df, tool_name):
    # Select the row where the Name matches the given name
    selected_row = df[df["Name"] == tool_name]

    # Extract the Instructions and Guidelines for the selected row
    if not selected_row.empty:
        description = selected_row["Description"].values[0]
        introduction = selected_row["Introduction"].values[0]
        instructions = selected_row["Instructions"].values[0]
        guidelines = selected_row["Guidelines"].values[0]
        availability = selected_row["Availability"].values[0]
        api_key = selected_row["API Key"].values[0]

        return description, introduction, instructions, guidelines, availability, api_key
    else:
        print(f"No entry found for {tool_name}")

def available_tutors(df):
    # Return a list of tuples of all tools available (Name, Description, Creator Email)
    names = df["Name"].values
    descriptions = df["Description"].values
    creator_emails = df["Creator Email"].values

    # Zip names, descriptions, and creator emails into a list of tuples
    return list(zip(names, descriptions, creator_emails))

# Dialog window to ask for overwrite priveleges
@st.dialog("Overwrite")
def ask_for_overwrite():
    st.markdown(f"You already have an AI Tutor with this name.")
    # Ask for confirmation
    if st.button(f"Overwrite", type='primary', use_container_width=True):
        st.session_state["overwrite"] = True
        st.session_state["overwrite_dialog"] = False
        st.rerun()
    if st.button(f"Cancel", use_container_width=True):
        st.session_state["overwrite"] = False
        st.session_state["overwrite_dialog"] = False
        st.rerun()

def create_tutor(fn, df, new_name, new_descr, new_intro, 
                 new_instr, new_guide, api_key, 
                 availability, user_email, overwrite=False):
    # Create a new row as a DataFrame
    new_row = pd.DataFrame({
        "Name": [new_name], 
        "Description": [new_descr],
        "Introduction": [new_intro],
        "Instructions": [new_instr], 
        "Guidelines": [new_guide],
        "Creator Email": [user_email],
        "API Key": [api_key],
        "Availability": [availability]
    })
    
    if overwrite:
        # Find the index of the row with the matching "Name"
        name_match_index = df[df['Name'] == new_name].index[0]
        
        # Overwrite the row with the new data
        df.loc[name_match_index] = new_row.iloc[0]
    else:
        # Concatenate the new row to the DataFrame
        df = pd.concat([df, new_row], ignore_index=True)
    
    # Write the updated DataFrame to a CSV file
    write_csv(fn, df)
    
    return df

def delete_tutor(fn, df, tool_name):
    # Check if the tool_name exists in the DataFrame
    if tool_name in df['Name'].values:
        # Remove the row with the matching 'Name'
        df = df[df['Name'] != tool_name]
        # Write the updated DataFrame back to the CSV file
        write_csv(fn, df)
        st.success("Tutor removed successfully.")
        return df
    else:
        st.error(f"Failed to remove '{tutor_name}'.")
        return df

# Dialog window to confirm and delete API key
@st.dialog("Delete Tutor")
def delete_tutor_confirm(tutor_name):
    st.markdown(f"Are you sure you want to delete the tutor '{tutor_name}'?")
    # Ask for confirmation
    if st.button(f"Delete", type='primary', use_container_width=True):
        # Remove the key from the user config
        st.session_state["df_tutors"] = delete_tutor(st.session_state["ai_tutors_data_fn"], st.session_state["df_tutors"], tutor_name)
        st.rerun()
    if st.button(f"Cancel", use_container_width=True):
        st.rerun()

def reset_build():
    st.session_state["banner"] = None
    st.session_state["tool name"] = None
    st.session_state["description"] = None
    st.session_state["introduction"] = None
    st.session_state["instructions"] = None
    st.session_state["guidelines"] = None
    st.session_state["availability"] = None
    st.session_state["api_key"] = None
    st.session_state["overwrite_dialog"] = False
    st.session_state["overwrite"] = False