import requests
from PIL import Image
import os
import json
import tempfile
import dotenv
from moviepy.video.fx.all import crop
from moviepy.editor import VideoFileClip
import random



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
dotenv.load_dotenv()
pexels_api_key = os.environ['PEXELS_API_KEY']
def get_video_from_pexels(query):
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
    headers = {
        'Authorization': pexels_api_key
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = json.loads(response.text)
        #random_index = random.randint(3)
        return data['videos'][0]['video_files'][0]['link']
    else:
        print('Failed to get video from Pexels', response.status_code)
        return None

def download_video(url, filename):
    """
    Download video from url, crop it, and save to filename.
    """
    temp_filename = "temp_" + filename
    response = requests.get(url)
    with open(temp_filename, 'wb') as f:
        f.write(response.content)
    
    # Crop the video
    crop_video(temp_filename, filename)

    # Delete the temporary video file
    if os.path.exists(temp_filename):
        os.remove(temp_filename)



def crop_video(file_path, output_file_path, new_resolution=(540, 960)):
    """
    Crop a video from the center.
    
    Parameters:
    - file_path: str: Path of the input video.
    - output_file_path: str: Path of the output video.
    - new_resolution: tuple: The new resolution (width, height) of the output video. Default is (540, 960).
    """
    clip = VideoFileClip(file_path)

    # calculate aspect ratio
    width, height = clip.size

    # new resolution
    new_width, new_height = new_resolution

    # calculate the crop dimensions
    crop_width = min(width, new_width)
    crop_height = min(height, new_height)

    cropped_clip = crop(clip, width=crop_width, height=crop_height, x_center=clip.w/2, y_center=clip.h/2)
    cropped_clip.write_videofile(output_file_path, codec='libx264')

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