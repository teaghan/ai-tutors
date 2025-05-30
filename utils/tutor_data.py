import streamlit as st
import pandas as pd
import s3fs
import ast

@st.cache_data(show_spinner=False)
def read_csv(fn):
    # Create connection object and retrieve file contents.
    fs = s3fs.S3FileSystem(anon=False)
    with fs.open(fn, 'rb') as f:
        return pd.read_csv(f).fillna('')

def write_csv(fn, df):
    # Create connection object and write file contents.
    
    fs = s3fs.S3FileSystem(anon=False)
    with fs.open(fn, 'wt') as f:
        df.to_csv(f, index=False)
    # Reset cache so that new data gets loaded
    read_csv.clear()

def select_instructions(df, tool_name):
    # Select the row where the Name matches the given name
    selected_row = df[df["Name"] == tool_name]

    # Extract the Instructions and Guidelines for the selected row
    if not selected_row.empty:
        description = selected_row["Description"].values[0]
        introduction = selected_row["Introduction"].values[0]
        instructions = selected_row["Instructions"].values[0]
        guidelines = selected_row["Guidelines"].values[0]
        knowledge = selected_row["Knowledge Base"].values[0]
        availability = selected_row["Availability"].values[0]

        return description, introduction, instructions, guidelines, knowledge, availability
    else:
        print(f"No entry found for {tool_name}")

def get_creator_email(df, tool_name):
    # Select the row where the Name matches the given name
    selected_row = df[df["Name"] == tool_name]
    if not selected_row.empty:
        return selected_row["Creator Email"].values[0]
    else:
        return None  

def str_to_list(string):
    try:
        return ast.literal_eval(string)
    except:
        return []

def get_tags(df, tool_name):
    selected_row = df[df["Name"] == tool_name]
    grades = str_to_list(selected_row["Grades"].values[0])
    subjects = str_to_list(selected_row["Subjects"].values[0])
    return grades, subjects  

def available_tutors(df):
    # Return a list of tuples of all tools available (Name, Description, Creator Email)
    names = df["Name"].values
    descriptions = df["Description"].values
    creator_emails = df["Creator Email"].values
    grades = [str_to_list(gr) for gr in df["Grades"].values]
    subjects = [str_to_list(sub) for sub in df["Subjects"].values]
    
    availability = df["Availability"].values

    # Zip names, descriptions, and creator emails into a list of tuples
    return list(zip(names, descriptions, creator_emails, grades, subjects, availability))

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

def create_tutor(fn, new_name, new_descr, new_intro, 
                 new_instr, new_knowledge, new_guide, 
                 selected_grades, selected_subjects, 
                 availability, user_email, overwrite=False):
    # Read current csv
    df = read_csv(fn)

    # Create a new row as a DataFrame
    new_row = pd.DataFrame({
        "Name": [new_name], 
        "Description": [new_descr],
        "Introduction": [new_intro],
        "Instructions": [new_instr], 
        "Knowledge Base": [new_knowledge],
        "Guidelines": [new_guide],
        "Grades": [selected_grades],
        "Subjects": [selected_subjects],
        "Creator Email": [user_email],
        "Availability": [availability],
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

def delete_tutor(fn, tool_name):
    # Read current csv
    df = read_csv(fn)

    # Check if the tool_name exists in the DataFrame
    if tool_name in df['Name'].values:
        # Remove the row with the matching 'Name'
        df = df[df['Name'] != tool_name]
        # Write the updated DataFrame back to the CSV file
        write_csv(fn, df)
        st.success("Tutor removed successfully.")
        return df
    else:
        st.error(f"Failed to remove '{tool_name}'.")
        return df

# Dialog window to confirm and delete Tutor
@st.dialog("Delete Tutor")
def delete_tutor_confirm(tutor_name):
    st.markdown(f"Are you sure you want to delete the tutor '{tutor_name}'?")
    # Ask for confirmation
    if st.button(f"Delete", type='primary', use_container_width=True):
        # Remove the key from the user config
        st.session_state["df_tutors"] = delete_tutor(st.session_state["ai_tutors_data_fn"], tutor_name)
        st.rerun()
    if st.button(f"Cancel", use_container_width=True):
        st.rerun()