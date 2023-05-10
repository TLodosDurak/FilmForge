from moviepy.editor import ImageClip
import requests
from moviepy.editor import (concatenate_videoclips, TextClip, CompositeVideoClip,
                            AudioFileClip, VideoFileClip)
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
# from langchain.utilities.wikipedia import WikipediaAPIWrapper  Removed due to increased inaccuracies
from custom_google_search import CustomGoogleSearchAPIWrapper
import os
import json
import random
from dotenv import load_dotenv
import streamlit as st
from av import AVError
from moviepy.editor import ImageSequenceClip
from PIL import Image

from moviepy.config import change_settings

change_settings(
    {"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})


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


def create_title_card(title_text, duration=4, bg_video=None):
    title_clip = TextClip(title_text, fontsize=45, font="Arial-Bold",
                          color='YellowGreen', size=(540, 960), method='caption', align='center', stroke_color='black', stroke_width=2)
    title_clip = title_clip.set_duration(duration)

    if bg_video is not None:
        bg_video = bg_video.resize(height=960, width=540)
        bg_video = bg_video.set_duration(duration)
        title_card = CompositeVideoClip([bg_video, title_clip])
    else:
        title_card = title_clip

    return title_card


def create_ranking_frame(rank, country, why, what, duration=2, bg_video=None, media_file_path=None):
    canvas_clip = TextClip(f" ", fontsize=45, font="Arial-Bold",
                        color='White', size=(540, 960), stroke_color='black', stroke_width=2, transparent= True)
    txt_clip = TextClip(f"Rank {rank}: {country}", fontsize=45, font="Arial-Bold",
                        color='YellowGreen', size=(540, 960), method='caption', align='center', stroke_color='black', stroke_width=2)
    why_clip = TextClip(f"{why}", fontsize=35, font="Arial-Bold",
                        color='white', size=(540, 960), method='caption', align='center', stroke_color='black', stroke_width=2)
    what_clip = TextClip(f"{what}", fontsize=35, font="Arial-Bold",
                        color='white', size=(540, 960), method='caption', align='center', stroke_color='black', stroke_width=2)

    canvas_clip = canvas_clip.set_duration(duration)
    txt_clip = txt_clip.set_position(('center', 50)).set_duration(duration)
    why_clip = why_clip.set_position(('center', 250)).set_duration(duration)
    what_clip = what_clip.set_position(('center', 300)).set_duration(duration)
    if bg_video is not None:
        # Resize the background video to fit 9:16 aspect ratio
        bg_video = bg_video.resize(height=960, width=540)
        bg_video = bg_video.set_duration(duration)

    if media_file_path is not None:
        try:
            media_clip = ImageClip(media_file_path).set_duration(duration)
            # Resize the media clip as needed
            media_clip = media_clip.resize(height=300)
            # Position the media clip on the frame
            media_clip = media_clip.set_position(("center", 960 - media_clip.h - 550))
        except AVError:
            print(f"Error processing the media file: {media_file_path}")
            media_clip = None

        if bg_video is not None:
            clip = CompositeVideoClip([canvas_clip, bg_video, media_clip, txt_clip, why_clip, what_clip])
        else:
            clip = CompositeVideoClip([canvas_clip, media_clip, txt_clip, why_clip, what_clip])
    else:
        if bg_video is not None:
            clip = CompositeVideoClip([canvas_clip, bg_video, txt_clip, why_clip, what_clip])
        else:
            clip = CompositeVideoClip([txt_clip, why_clip, what_clip])

    return clip


def create_video(ranking_list, topic, bg_videos=None, bg_music=None):
    clips = []
    j = 0
    # Title card
    title_text = f"Top 10 Countries: {topic}"
    if bg_videos is not None:
        bg_video = bg_videos[j % len(bg_videos)] if bg_videos else None
    else:
        bg_video = None
    clips.append(create_title_card(title_text, bg_video=bg_video))

    google_search = CustomGoogleSearchAPIWrapper()
    with st.expander("Click to expand google image search queries"):
        j = 0
        for i in range(len(ranking_list), 0, -1):
            media_query = f"{ranking_list[j][3][0]}"
            st.write(media_query)
            media_results = google_search.search_media(media_query, num_results=3)
            # pic from top 3 results
            media_file_path = f"media_{j}.jpg"
            image_downloaded = False

            for media in media_results[:3]:
                media_url = media["link"]
                if not image_downloaded:
                    image_downloaded = download_image(media_url, media_file_path)
                    if image_downloaded and is_image_readable(media_file_path):  # Check if the image is readable
                        break
                else:
                    image_downloaded = False

            if not image_downloaded:
                media_file_path = None  # Skip using the image if the download fails

            if bg_videos is None:
                bg_video = None
            else:
                bg_video = bg_videos[j % len(bg_videos)] if bg_videos else None
            clips.append(create_ranking_frame(
                i, ranking_list[j][0][0],ranking_list[j][1][0],ranking_list[j][2][0], bg_video=bg_video, media_file_path=media_file_path))  # Rank and Country
            j += 1

    final_video = concatenate_videoclips(clips)

    if bg_music is not None:
        audio = AudioFileClip(bg_music)
        audio = audio.volumex(0.6)  # Set audio volume
        audio = audio.set_duration(final_video.duration)
        final_video = final_video.set_audio(audio)
        final_video.write_videofile("ranking_video.mp4", fps=24, codec='libx264')
        audio.close()  # Close the AudioFileClip before deleting the temporary file
    else:
        final_video.write_videofile("ranking_video.mp4", fps=24, codec='libx264')

    delete_media_files(len(ranking_list))

import string

def remove_non_printable_chars(s):
    lines = s.splitlines()
    cleaned_lines = [line for line in lines if line.strip() != "."]
    return '\n'.join(cleaned_lines)

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




is_generating_video = False


def main():
    global is_generating_video
    load_dotenv()
    st.set_page_config(page_title="FilmForge")
    st.header("FilmForge")
    user_input = st.text_input("Enter the topic of your Top 10 tiktok")
    # Add your background video files and background music file here
    uploaded_bg_videos = st.file_uploader("Choose background video files", type=[
                                          'mp4', 'avi', 'mov', 'gif'], accept_multiple_files=True)
    uploaded_bg_music = st.file_uploader(
        "Choose a background music file", type=['mp3', 'wav'])

    generate_video_button = st.button("Generate Video")

    if not is_generating_video and user_input and generate_video_button:
        is_generating_video = True
        # wiki = WikipediaAPIWrapper()
        # wiki_prompt = 'Top 10 Country' + user_input  # More detailed prompt for wiki
        # wiki_summary = wiki.run(wiki_prompt)
        video_template3 = PromptTemplate(
            input_variables=["topic"],
            template='Compute 1st country best in specifically related to "{topic}"\
                    Compute 2nd country best in specifically related to "{topic}"\
                    Compute 3rd country best in specifically related to "{topic}"\
                    Compute 4th country best in specifically related to "{topic}"\
                    Compute 5th country best in specifically related to "{topic}"\
                    Compute 6th country best in specifically related to "{topic}"\
                    Compute 7th country best in specifically related to "{topic}"\
                    Compute 8th country best in specifically related to "{topic}"\
                    Compute 9th country best in specifically related to "{topic}"\
                    Compute 10th country best in specifically related to "{topic}"\
                    Your response should be in an valid JSON 3D array format, like this starting from 10th place and ascending:\
                    [[["Country"], ["Why?"], ["What?"], ["google_image_search_query"]], [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]],\
                    [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]], [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]],\
                    [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]], [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]],\
                    [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]], [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]],\
                    [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]], [["Country"], ["Why?"], ["What?"], ["google_image_search_query"]]]\
                    Make Why? no more than 3 words, What? is a fact or name related to Why? and its also very concise no more than 3 words.\
                    google_image_search_query is a google image search query that fits the country/topic as well as the What? if its an easy search (avoid numbers unless a year) also no more than 3 words\
                    Make sure response is in the correct order! 10th place first and 1st place last!'
        )
        video_template4 = PromptTemplate(
            input_variables=['topic'],
            template= "Please provide a list of top 10 countries related to the topic '{topic}', starting from 10th place and including the following details for each country in a 3D array format made up of: [['Country'], ['Why?'], ['What?'], ['google_image_search_query']]. The 'Why?' field should not be more than 3 words and the 'What?' field should be a fact or name related to the 'Why?' field that is also no more than 3 words. The 'google_image_search_query' field should be a search query that accurately represents the country and the 'What?' field, and should avoid using numbers. Please ensure that your response is only the 3D array and nothing else."
        )
        llm = OpenAI(model_name='text-davinci-003', temperature=0)
        video_chain3 = LLMChain(llm=llm, prompt=video_template3, verbose=True)
        with st.spinner("Waiting for OpenAI response..."):
            response = video_chain3.run({"topic": user_input})
            ranking_list = convert_openai_response(response)
            # For testing the code without making openai calls $$$
            #response = '["North Korea", "France", "China", "United Kingdom", "India", "Pakistan", "Israel", "Russia", "United States", "Iran"]'
            with st.expander("Click to expand OpenAI response:"):
                st.write(response)
        #with st.expander("Click to expand st color options"):
        #    st.write(TextClip.list('color'))
        import tempfile

        def save_uploaded_file(uploaded_file):
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_file.getvalue())
            return tfile.name
        if isinstance(ranking_list, list):
            temp_bg_video_paths = [save_uploaded_file(
                video) for video in uploaded_bg_videos]
            bg_videos = [VideoFileClip(path) for path in temp_bg_video_paths]

            temp_bg_music_path = None if uploaded_bg_music is None else save_uploaded_file(
                uploaded_bg_music)
            bg_music = None if temp_bg_music_path is None else temp_bg_music_path

            with st.spinner("Generating video...\n this might take a minute!"):
                # This line creates the video using the ranking list.
                create_video(ranking_list, user_input, bg_videos, bg_music)

            is_generating_video = False

            if not is_generating_video and os.path.exists("ranking_video.mp4"):
                st.video("ranking_video.mp4")

            for video_clip in bg_videos:  # Close video clips before deleting the temporary files
                video_clip.close()
            for path in temp_bg_video_paths:
                os.remove(path)

            if temp_bg_music_path is not None:
                os.remove(temp_bg_music_path)


if __name__ == "__main__":
    main()
