import requests
from PIL import Image
import os
import json
import tempfile

def download_image(url: str, file_path: str) -> bool:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type")
            if content_type and "image" in content_type and len(response.content) > 1024:  # Check if content type is an image and its size is more than 1KB
                with open(file_path, "wb") as file:
                    file.write(response.content)
                return True
            else:
                return False
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return False
    
def is_image_readable(file_path: str) -> bool:
    try:
        with Image.open(file_path) as img:
            img.verify()  # This will raise an exception if the image is not readable
        return True
    except Exception as e:
        print(f"Error reading image: {e}")
        return False


def delete_media_files(num_files: int) -> None:
    for i in range(num_files):
        file_path = f"media_{i}.jpg"
        if os.path.exists(file_path):
            os.remove(file_path)

def remove_non_printable_chars(s):
    lines = s.splitlines()
    cleaned_lines = [line for line in lines if line.strip() != "."]
    return '\n'.join(cleaned_lines)

def save_uploaded_file(uploaded_file):
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.getvalue())
    return tfile.name
    
def convert_openai_response(response):
    try:
        print(f"Raw response: {response}")  # Print the raw response for debugging
        response = remove_non_printable_chars(response)  # Remove non-printable characters
        response = response.strip()
        print(f"Response: {response}")  # Print the response for debugging

        if not response:
            raise ValueError("Empty response received")

        ranking_list = json.loads(response)
        return ranking_list
    except json.JSONDecodeError as e:
        print(f"Error: {e}")  # Print the error for debugging
        return "Error: Response is not in valid JSON format."
    except ValueError as e:
        print(f"Error: {e}")
        return "Error: Empty response received."