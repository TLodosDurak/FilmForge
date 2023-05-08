from moviepy.editor import ImageClip
import requests
from moviepy.editor import (concatenate_videoclips, TextClip, CompositeVideoClip,
                            AudioFileClip, VideoFileClip)
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.utilities.wikipedia import WikipediaAPIWrapper
from custom_google_search import CustomGoogleSearchAPIWrapper
import os
import json
import random
from dotenv import load_dotenv
import streamlit as st
from moviepy.config import change_settings

change_settings(
    {"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})


def download_image(url: str, file_path: str) -> bool:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return False


def delete_media_files(num_files: int) -> None:
    for i in range(num_files):
        file_path = f"media_{i}.jpg"
        if os.path.exists(file_path):
            os.remove(file_path)


def create_ranking_frame(rank, text, duration=2, bg_video=None, media_file_path=None):
    txt_clip = TextClip(f"Rank {rank}: {text}", fontsize=24,
                        color='white', size=(540, 960))  # Updated size for 9:16 aspect ratio
    txt_clip = txt_clip.set_duration(duration)

    if bg_video is not None:
        # Resize the background video to fit 9:16 aspect ratio
        bg_video = bg_video.resize(height=960, width=540)
        bg_video = bg_video.set_duration(duration)

    if media_file_path is not None:
        media_clip = ImageClip(media_file_path).set_duration(duration)
        # Resize the media clip as needed
        media_clip = media_clip.resize(height=300)
        # Position the media clip on the frame
        media_clip = media_clip.set_position(("right", "bottom"))
        clip = CompositeVideoClip([bg_video, txt_clip, media_clip]
                                  ) if bg_video else CompositeVideoClip([txt_clip, media_clip])
    else:
        clip = bg_video.set_duration(duration).set_opacity(
            1) if bg_video else txt_clip

    return clip


def create_video(ranking_list, user_input, bg_videos=None, bg_music=None):
    clips = []
    j = 0

    google_search = CustomGoogleSearchAPIWrapper()

    for i in range(len(ranking_list), 0, -1):
        media_query = f"{ranking_list[j]} {user_input}"
        media_results = google_search.search_media(media_query)
        # Random pic from top 3 results
        media_url = random.choice(media_results[:3])["link"]
        media_file_path = f"media_{j}.jpg"
        image_downloaded = download_image(media_url, media_file_path)
        if not image_downloaded:
            media_file_path = None  # Skip using the image if the download fails
        if bg_videos is None:
            bg_video = None
        else:
            bg_video = bg_videos[j % len(bg_videos)] if bg_videos else None
        clips.append(create_ranking_frame(
            i, ranking_list[j], bg_video=bg_video, media_file_path=media_file_path))  # Rank and Country
        j += 1

    final_video = concatenate_videoclips(clips)

    if bg_music is not None:
        audio = AudioFileClip(bg_music)
        audio = audio.volumex(0.6)  # Set audio volume
        audio = audio.set_duration(final_video.duration)
        final_video = final_video.set_audio(audio)
        final_video.write_videofile("ranking_video.mp4", fps=24)
        audio.close()  # Close the AudioFileClip before deleting the temporary file
    else:
        final_video.write_videofile("ranking_video.mp4", fps=24)

    delete_media_files(len(ranking_list))


def convert_openai_response(response):
    try:
        ranking_list = json.loads(response)
        return ranking_list
    except json.JSONDecodeError:
        return "Error: Response is not in valid JSON format."


is_generating_video = False


def main():
    global is_generating_video
    load_dotenv()
    st.set_page_config(page_title="FilmForge")
    st.header("FilmForge")
    user_input = st.text_input("Enter the topic of your Top 10 tiktok")
    # Add your background video files and background music file here
    uploaded_bg_videos = st.file_uploader("Choose background video files", type=[
                                          'mp4', 'avi', 'mov'], accept_multiple_files=True)
    uploaded_bg_music = st.file_uploader(
        "Choose a background music file", type=['mp3', 'wav'])

    generate_video_button = st.button("Generate Video")

    if not is_generating_video and user_input and generate_video_button:
        is_generating_video = True
        wiki = WikipediaAPIWrapper()
        wiki_prompt = 'Top 10 Country' + user_input  # More detailed prompt for wiki
        wiki_summary = wiki.run(wiki_prompt)
        video_template = PromptTemplate(
            input_variables=["topic", "wiki_summary"],
            template='Given the topic "{topic}", generate a list of the overall top 10 countries specifically related to "{topic}" ranked from 10th place to 1st place.\
    Your response should be in an array format, like this:\
    ["Country 10th place", "Country 9th place", "Country 8th place", "Country 7th place",\
    "Country 6th place", "Country 5th place", "Country 4th place", "Country 3rd place", "Country 2nd place", "Country 1st place"]. Use the wiki_summary as a source of inspiration if needed: "{wiki_summary}"'
        )

        llm = OpenAI(temperature=0.5)
        video_chain = LLMChain(llm=llm, prompt=video_template, verbose=True)

        response = video_chain.run(
            {"topic": user_input, "wiki_summary": wiki_summary})
        # For testing the code without making openai calls $$$
        # response = '["North Korea", "France", "China", "United Kingdom", "India", "Pakistan", "Israel", "Russia", "United States", "Iran"]'
        st.write(response)
        import tempfile

        def save_uploaded_file(uploaded_file):
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_file.getvalue())
            return tfile.name

        temp_bg_video_paths = [save_uploaded_file(
            video) for video in uploaded_bg_videos]
        bg_videos = [VideoFileClip(path) for path in temp_bg_video_paths]

        temp_bg_music_path = None if uploaded_bg_music is None else save_uploaded_file(
            uploaded_bg_music)
        bg_music = None if temp_bg_music_path is None else temp_bg_music_path

        with st.spinner("Generating video...\n this might take a minute!"):
            # This line creates the video using the ranking list.
            create_video(convert_openai_response(
                response), user_input, bg_videos, bg_music)

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
