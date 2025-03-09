import os
import json

import streamlit as st
import s3fs

#from st_files_connection import FilesConnection
from tempfile import NamedTemporaryFile
from pathlib import Path

@st.cache_data(show_spinner=False)
def load_file_to_temp(fn):
    # Create a connection object to S3
    #conn = st.connection('s3', type=FilesConnection, ttl=0)
    fs = s3fs.S3FileSystem(anon=False)

    # Open the remote file in binary read mode
    with fs.open(fn, mode='rb') as remote_file:

        # Extract the file extension
        filename = Path(fn).name
        suffix = Path(filename).suffix

        # Create a temporary file with a custom name and appropriate suffix
        temp_file = NamedTemporaryFile(delete=False, suffix=suffix, prefix=filename.split('.')[0] + '_')

        # Write the content to the temporary file
        temp_file.write(remote_file.read())
        temp_file.flush()  # Ensure all data is written

    # Return the path to the temporary file
    return temp_file.name


def save_files(tool_name, knowledge_files):
    data_dir = f'ai-tutors/knowledge-files/{tool_name}'
    # Create connection object and write file contents.
    #conn = st.connection('s3', type=FilesConnection, ttl=0)
    fs = s3fs.S3FileSystem(anon=False)

    file_paths = []
    for knowledge_file in knowledge_files:
        file_path = os.path.join(data_dir,knowledge_file.name)
        with fs.open(file_path, "wb") as f:
            f.write(knowledge_file.getvalue())
            file_paths.append(file_path)

    return file_paths

def get_file_paths(df, tool_name):
    # Select the row where the Name matches the given name
    selected_row = df[df["Name"] == tool_name]
    if not selected_row.empty:
        try:
            return json.loads(selected_row["Knowledge Files"].values[0])
        except TypeError:
            return []
    else:
        return [] 

def drop_files(container, existing_file_paths=[]):
    dropped_files = container.file_uploader("Drop a file or multiple files (.txt, .rtf, .pdf, .csv, .docx)", 
                                     accept_multiple_files=True, key='upload')
    
    # Validate file extensions
    invalid_files = []
    if dropped_files:
        for uploaded_file in dropped_files:
            extension = uploaded_file.name.split(".")[-1].lower()
            if extension not in ['txt', 'rtf', 'pdf', 'csv', 'docx']:
                invalid_files.append(uploaded_file.name)
    # If invalid files are found, clear the uploaded files and show a warning
    if invalid_files:
        dropped_files = []  # Clear the uploaded files
        st.session_state.invalid_filetype = True
    else:
        st.session_state.invalid_filetype = False
    if st.session_state.invalid_filetype:
        st.warning(f"Invalid file(s): {', '.join(invalid_files)}. Please remove and upload an accepted file type.")

    if len(existing_file_paths)>0:
        existing_filenames  = [Path(fp).name for fp in existing_file_paths]
        existing_files_chosen = st.multiselect('**Existing Files:**', options=existing_filenames, default=existing_filenames, 
                    on_change=None, key='movies_choice')
        path_indices = [i for i, fn in enumerate(existing_filenames) if fn in existing_files_chosen]
        existing_file_paths_chosen = [existing_file_paths[i] for i in path_indices]
    else:
        existing_file_paths_chosen = []

    return dropped_files, existing_file_paths_chosen