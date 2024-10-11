import streamlit as st
import pandas as pd
from st_files_connection import FilesConnection

def read_csv(fn):
    # Create connection object and retrieve file contents.
    #conn = st.connection('s3', type=FilesConnection, ttl=0)
    # Return pandas dataframe
    #return conn.read(fn, input_format="csv", ttl=0) 
    return pd.read_csv(fn)

def write_csv(fn, df):
    # Create connection object and write file contents.
    #conn = st.connection('s3', type=FilesConnection, ttl=0)
    #with conn.open(fn, "wt") as f:
    df.to_csv(f, index=False)

def select_instructions(df, tool_name):
    # Select the row where the Name matches the given name
    selected_row = df[df["Name"] == tool_name]

    # Extract the Instructions and Guidelines for the selected row
    if not selected_row.empty:
        instructions = selected_row["Instructions"].values[0]
        guidelines = selected_row["Guidelines"].values[0]
        introduction = selected_row["Introduction"].values[0]
        return instructions, guidelines, introduction
    else:
        print(f"No entry found for {tool_name}")

def available_tutors(df):
    # Return a list of tuples of all tools available (Name, Description, Creator Email)
    names = df["Name"].values
    descriptions = df["Description"].values
    creator_emails = df["Creator Email"].values

    # Zip names, descriptions, and creator emails into a list of tuples
    return list(zip(names, descriptions, creator_emails))
