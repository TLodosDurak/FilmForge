import requests
from PIL import Image
import os
import json
import tempfile
import dotenv
from moviepy.video.fx.all import crop
from moviepy.editor import VideoFileClip
import random
from src.videos.default_pexel_bg import get_default_bg
from moviepy.video.fx import fadein
from moviepy.editor import concatenate_videoclips
import numpy as np
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from src.audio import *


def shake(clip, amplitude=10):
    """ Returns a clip with a shaking effect """

    def shaking(t):
        h, w = clip.size
        tx = amplitude * (np.random.random() - 0.5)
        ty = amplitude * (np.random.random() - 0.5)
        return "center" + int(max(h, w)*tx), "center" + int(max(h, w)*ty)

    return clip.set_position(shaking)


def apply_shake_for_duration(clip, duration, amplitude=10):
    shaking_part = shake(clip.subclip(0, duration), amplitude)
    remaining_part = clip.subclip(duration)
    return concatenate_videoclips([shaking_part, remaining_part])


def fadein_clip(clip, duration):
    return clip.fx(fadein, duration)

def get_hashtags_list(ranking_list):
    hashtags_unformatted_list = []
    for rank in ranking_list:
        hashtags_unformatted_list.append(f'{rank[0][0]}, {rank[2][0]}')
    hashtags_formatted_string = ', '.join(hashtags_unformatted_list)
    return hashtags_formatted_string

def download_image(url: str, file_path: str) -> bool:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type")
            # Check if content type is an image and its size is more than 1KB
            if content_type and "image" in content_type and len(response.content) > 1024:
                with open(file_path, "wb") as file:
                    file.write(response.content)

                # Open the image file
                with Image.open(file_path) as img:
                    # If the image mode is not 'RGB', convert it
                    if img.mode != 'RGB':
                        img = img.convert('RGB')

                    # Check original image dimensions
                    width, height = img.size
                    # If either dimension is too large, resize the image
                    if width > 500 or height > 300:
                        # Compute the new dimensions while maintaining aspect ratio
                        aspect_ratio = width / height
                        if width > 500:
                            width = 500
                            height = int(width / aspect_ratio)
                        if height > 300:
                            height = 300
                            width = int(height * aspect_ratio)
                        # Resize the image and save it
                        img = img.resize((width, height), Image.ANTIALIAS)
                        img.save(file_path)

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
        if len(data['videos']) > 0 and len(data['videos'][0]['video_files']) > 0:
            # Sort the video files by quality, width and height in descending order
            sorted_files = sorted(data['videos'][0]['video_files'],
                                  key=lambda x: (
                                      x['quality'], x['width'], x['height']),
                                  reverse=True)
            # Return the link of the highest quality video
            return sorted_files[0]['link']
        else:
            print('No video found on Pexels for the query:', query)
            return get_default_bg()
    else:
        print('Failed to get video from Pexels', response.status_code)
        return get_default_bg()


def download_video(url, filename):
    """
    Download video from url, crop it, and save to filename.
    """
    temp_filename = "temp_" + filename
    response = requests.get(url)
    with open(temp_filename, 'wb') as f:
        f.write(response.content)

    # Crop the video
    set_duration_crop_video(temp_filename, filename)

    # Delete the temporary video file
    # Delete the temporary video file
    if os.path.exists(temp_filename):
        try:
            os.remove(temp_filename)
        except PermissionError:
            print(
                f"Warning: Could not delete temporary file '{temp_filename}' due to a permission error.")


def set_duration_crop_video(file_path, output_file_path, duration=5, new_resolution=(540, 960), shake_duration=1, shake_amplitude=10):
    """
    Set video duration, apply shaking effect and crop it from the center.

    Parameters:
    - file_path: str: Path of the input video.
    - output_file_path: str: Path of the output video.
    - duration: float: Duration of the video shaking effect.
    - new_resolution: tuple: The new resolution (width, height) of the output video. Default is (540, 960).
    - shake_amplitude: int: The amplitude of the shaking effect. Default is 10.
    """
    clip = VideoFileClip(file_path)

    # Set the duration of the video to 5 seconds; less if video shorter
    if clip.duration < duration:
        duration = clip.duration

    clip = clip.subclip(0, duration)

    # Resize the video to fit the new resolution
    resized_clip = clip.resize(newsize=new_resolution)

    resized_clip.write_videofile(output_file_path, codec='libx264')

    # Close the clips after writing the video file to release the resources
    clip.close()
    resized_clip.close()


def delete_media_files(num_i, num_j) -> None:
    for i in range(num_i):
        for j in range(num_j):
            file_path = f"media_{i}_{j}.jpg"
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
        # Print the raw response for debugging
        # print(f"Raw response: {response}")
        response = remove_non_printable_chars(
            response)  # Remove non-printable characters
        response = response.strip()
        # Repalce single quotes with double for json loader
        response = response.replace("'", '"')

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


def pick_default_audio_path():
    # audio file paths
    blast = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\audio\01_blast.mp3'
    passion = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\audio\02_passion.mp3'
    mazaphonk = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\audio\03_mazaphonk.mp3'
    phonkhouse = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\audio\04_phonkhouse.mp3'
    string6th = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\audio\05_6thstring.mp3'
    perfect = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\audio\06_perfect.mp3'
    isolation = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\audio\07_isolate.mp3'
    audio_list = [blast, passion, mazaphonk,
                  phonkhouse, string6th, perfect, isolation]
    # return random.choice(audio_list)
    return string6th
