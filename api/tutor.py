import pandas as pd
from datetime import datetime, timezone
import logging
from fastapi import HTTPException

# Import local modules
from llms.tutor_llm import TutorChain
from utils.tutor_data import select_instructions, read_csv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_tutor(access_code: str) -> TutorChain:
    """
    Load a tutor instance based on the provided access code.
    
    Args:
        access_code: The access code to authenticate and load the appropriate tutor
        
    Returns:
        TutorChain: The initialized tutor chain
        
    Raises:
        HTTPException: If the access code is invalid, expired, or data files can't be accessed
    """
    try:
        ai_tutors_data_fn = 'ai-tutors/tutor_info.csv'
        df_tutors = read_csv(ai_tutors_data_fn)
        access_codes_data_fn = 'ai-tutors/access_codes.csv'
        df_access_codes = read_csv(access_codes_data_fn)
    except Exception as e:
        logger.error(f"Error reading CSV files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error accessing tutor data: {str(e)}")

    # Get the current date and time
    cur_datetime = datetime.now(tz=timezone.utc)

    # Select the row where the Code matches the given code (case insensitive)
    selected_row = df_access_codes[df_access_codes["Code"].str.upper() == access_code.upper()]

    # Extract the Instructions and Guidelines for the selected row
    if not selected_row.empty:
        try:
            tool_name = selected_row["Name"].values[0]
            teacher_email = selected_row["Email"].values[0]
            end_datetime_str = selected_row["End Date"].values[0]  # This includes date and time
        except Exception as e:
            logger.error(f"Error extracting data from access code row: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing access code data")

        # Check if the end date is NaN
        if pd.isna(end_datetime_str) or end_datetime_str == '':
            end_datetime = None  # No expiration
        else:
            try:
                # Convert the end date and time string to a datetime object
                end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')
                # Set timezone to UTC for comparison
                end_datetime = end_datetime.replace(tzinfo=timezone.utc)
            except ValueError:
                logger.error(f"Invalid date format in access code data: {end_datetime_str}")
                raise HTTPException(status_code=400, detail="Access code has an invalid date/time format")
    else:
        logger.warning(f"Access code not found: {access_code}")
        raise HTTPException(status_code=404, detail="Access code does not exist")

    # Compare the current datetime with the end datetime (if it exists)
    if (end_datetime is not None) and (end_datetime < cur_datetime):
        logger.warning(f"Expired access code used: {access_code}")
        raise HTTPException(status_code=403, detail="Access code has expired")
    
    try:
        # Extract and set instructions and other details
        (description,
         introduction,
         instructions,
         guidelines,
         knowledge,
         availability) = select_instructions(df_tutors, tool_name=tool_name)
        
        tutor_chain = TutorChain(instructions, 
                     guidelines,
                     introduction, 
                     knowledge)
        
        return tutor_chain
    except Exception as e:
        logger.error(f"Error initializing tutor chain: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initializing tutor: {str(e)}") 