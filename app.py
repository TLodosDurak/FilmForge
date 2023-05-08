from moviepy.editor import (concatenate_videoclips, TextClip, CompositeVideoClip,
                            AudioFileClip, VideoFileClip)
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.utilities.wikipedia import WikipediaAPIWrapper
import os
import json
from dotenv import load_dotenv
import streamlit as st
from moviepy.config import change_settings

change_settings(
    {"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})


def create_ranking_frame(rank, text, duration=2, bg_video=None):
    txt_clip = TextClip(f"Rank {rank}: {text}", fontsize=24,
                        color='white', size=(540, 960))  # Updated size for 9:16 aspect ratio
    txt_clip = txt_clip.set_duration(duration)

    if bg_video is not None:
        # Resize the background video to fit 9:16 aspect ratio
        bg_video = bg_video.resize(height=960, width=540)
        bg_video = bg_video.set_duration(duration)
        clip = CompositeVideoClip([bg_video, txt_clip])
    else:
        clip = txt_clip

    return clip


def create_video(ranking_list, bg_videos=None, bg_music=None):
    clips = []
    j = 0
    for i in range(len(ranking_list), 0, -1):
        bg_video = None if bg_videos is None else bg_videos[j % len(bg_videos)]
        clips.append(create_ranking_frame(
            i, ranking_list[j], bg_video=bg_video))  # Rank and Country
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
            template='Based on the topic "{topic}" and its Wikipedia summary "{wiki_summary}", generate a list of 10 countries ranked from last place to first place.\
                    Your response should be in an array format, like this:\
                    ["Country 10th place", "Country 9th place", "Country 8th place", "Country 7th place",\
                    "Country 6th place", "Country 5th place", "Country 4th place", "Country 3rd place", "Country 2nd place", "Country 1st place"]. Reflect on your answer.'
        )

        llm = OpenAI(temperature=0.8)
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
                response), bg_videos, bg_music)

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
