import requests
import json
import os
import httpx
import asyncio

def extract_text_from_image(file_or_path):
    """Handle both file objects and file paths for image processing"""
    headers = {
        "app_id": os.getenv('MATHPIX_APP_ID'),
        "app_key": os.getenv('MATHPIX_APP_KEY')
    }
    data = {
        "options_json": json.dumps({
         "formats": ["text"],
         "math_inline_delimiters": ["$", "$"],
         "rm_spaces": True
        })
    }
    
    # Handle either file object or path
    if isinstance(file_or_path, str):
        with open(file_or_path, "rb") as f:
            files = {"file": f.read()}
    else:
        files = {"file": file_or_path.getvalue()}
    
    r = requests.post(
        "https://api.mathpix.com/v3/text",
        files=files,
        data=data,
        headers=headers
    ).json()
    
    return r.get('text', 'Failed to extract text from image')

async def upload_pdf_file(file_or_path):
    """Handle both file objects and file paths for PDF upload"""
    headers = {
        "app_key": os.getenv('MATHPIX_APP_KEY'),
        "app_id": os.getenv('MATHPIX_APP_ID')
    }
    options = {
        "conversion_formats": {"docx": True, "tex.zip": True},
        "formats": ["text"],
        "math_inline_delimiters": ["$", "$"],
        "rm_spaces": True
    }
    
    # Handle either file object or path
    if isinstance(file_or_path, str):
        with open(file_or_path, "rb") as f:
            file_content = f.read()
    else:
        file_content = file_or_path.getvalue()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.mathpix.com/v3/pdf",
            headers=headers,
            data={"options_json": json.dumps(options)},
            files={"file": file_content}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Upload successful: {data}")
            return data.get("pdf_id")
        else:
            print(f"Failed to upload PDF: {response.status_code}, {response.text}")
            return None

async def check_pdf_status(pdf_id):
    """
    Check the processing status of the PDF.
    """
    url = f"https://api.mathpix.com/v3/pdf/{pdf_id}"
    headers = {"app_key": os.getenv('MATHPIX_APP_KEY'),
               "app_id": os.getenv('MATHPIX_APP_ID')}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get status: {response.status_code}, {response.text}")
            return None

async def get_pdf_content(pdf_id):
    url = f"https://api.mathpix.com/v3/pdf/{pdf_id}.mmd"
    headers = {"app_key": os.getenv('MATHPIX_APP_KEY'),
               "app_id": os.getenv('MATHPIX_APP_ID')}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to get content: {response.status_code}, {response.text}")
            return None
        
async def extract_text_from_doc(file_or_path):
    pdf_id = await upload_pdf_file(file_or_path)
    if pdf_id:
        finished = False
        while not finished:
            status = await check_pdf_status(pdf_id)
            if status and status.get('status') == 'completed':
                content = await get_pdf_content(pdf_id)
                finished = True
            else:
                print("PDF is still processing. Current status:", status)
                await asyncio.sleep(2)
        return content
    else:
        return None

async def mathpix(file_or_path):
    """
    Process a file through Mathpix API. Accepts either a file object or a file path.
    
    Args:
        file_or_path: Either a file object or a string path to the file
    """
    if isinstance(file_or_path, str):
        file_name = file_or_path
    else:
        file_name = file_or_path.name
        
    if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
        return extract_text_from_image(file_or_path)
    elif file_name.lower().endswith(('.pdf', '.docx')):
        return await extract_text_from_doc(file_or_path)
    else:
        print("File is not a png, jpg, pdf, or docx")
        return None
    
def mathpix_extract(file_path):
    return asyncio.run(mathpix(file_path))