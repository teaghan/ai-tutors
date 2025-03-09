import os
import tempfile
import chardet
import streamlit as st
from striprtf.striprtf import rtf_to_text
import zipfile

from utils.mathpix import mathpix_extract

def extract_json_from_csv(csv_file) -> str:
    """
    Converts an uploaded CSV file to a JSON string.

    Args:
        csv_file: An UploadedFile object representing the uploaded CSV file.

    Returns:
        str: The JSON string representation of the CSV data.
    """
    
    # Decode the file content with the detected encoding, handling errors
    raw_data = csv_file.getvalue()
    encoding = chardet.detect(raw_data)['encoding']
    file_content = raw_data.decode(encoding, errors='replace')
    
    # Strip the BOM if present
    if file_content.startswith('\ufeff'):
        file_content = file_content[1:]

    return file_content

def extract_text_from_different_file_types(file) -> str:
    """
    Extract text from a file of various types including PDF, TXT, RTF, and ZIP.
    A file with another extension is treated as a .txt file.
    Args:
        file (file-like object): The file from which to extract text.

    Returns:
        str: The extracted text.
    """
    type = file.name.split('.')[-1].lower()
    if type == 'zip':
        text = extract_text_from_zip(file)
    elif type == 'pdf' or type == 'docx' or type == 'png' or type == 'jpg' or type == 'jpeg':
        text = mathpix_extract(file)
    elif type in ['txt', 'rtf']:
        raw_text = file.read().decode("utf-8")
        text = rtf_to_text(raw_text) if type == 'rtf' else raw_text
    elif type == 'csv':
        text = extract_json_from_csv(file) # in fact in json format
    else:  # Treat other file type as .txt file
        text = file.read().decode("utf-8")  # Treat all other types as text files

    return text

def extract_text_from_zip(zip_file) -> str:
    """
    Unzip a .zip file and extract content from all files within it.

    Args:
        zip_file: The uploaded zip file.
    Returns:
        str: The combined extracted text from all files.
    """
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Open the ZIP file in read mode
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # Extract all files to the temporary directory
            zip_ref.extractall(temp_dir)
            # Get the list of all files before closing zip_ref
            file_list = [f for f in zip_ref.namelist() if not f.startswith('__MACOSX')]

        # Initialize an empty list to store the extracted texts
        extracted_texts = []

        # Loop through each file
        for filename in file_list:
            full_path = os.path.join(temp_dir, filename)
            if not os.path.isdir(full_path):
                try:
                    # Create a file-like object that mimics Streamlit's UploadedFile
                    class FileWrapper:
                        def __init__(self, path, name):
                            self.path = path
                            self.name = name
                        
                        def read(self):
                            with open(self.path, 'rb') as f:
                                return f.read()
                        
                        def getvalue(self):
                            return self.read()

                    # Create a wrapper for the file
                    file_wrapper = FileWrapper(full_path, filename)
                    
                    # Use the existing function to extract text based on file type
                    text = extract_text_from_different_file_types(file_wrapper)
                    extracted_texts.append(f"File: {filename}\n{text}\n")
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

    # Combine all extracted texts with separators
    return "\n---\n".join(extracted_texts)
