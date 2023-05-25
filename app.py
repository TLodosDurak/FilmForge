import pickle
from dotenv import load_dotenv
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import VideoFileClip
import os
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from scripts.utils import convert_openai_response, save_uploaded_file
from scripts.video import create_video, get_video_from_pexels, download_video
from scripts.templates import *
from scripts.youtube import *
from moviepy.config import change_settings
from src.audio import *
from src.videos import *

# Necessary if using Windows
change_settings(
    {"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})


def main():

    load_dotenv()  # Loading env vars
    os.environ['CLIENT_SECRET_FILE0'] = 'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\client_secret_0.json'
    os.environ['CLIENT_SECRET_FILE1'] = 'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\client_secret_1.json'
    st.set_page_config(page_title="FilmForge")  # Setting up Streamlit
    st.header("FilmForge")
    # Asking for user input

    user_input = st.text_input(
        "Enter the topic of your Top 10 Countries short video")
    # Pick Youtube Channel
    channel_choice = st.selectbox(
        "Pick YT channel", ('🟡top10countryrankings', '🔴Top10AnythingAndMore'))
    authenticate_button = st.button("Authenticate YouTube")

    # For testing the code without making openai calls $$$
    if 'ranking_list' not in st.session_state:
        st.session_state.ranking_list = [[["India"], ["Fashion Hub"], ["Mumbai"], ["indian fashion"]], [["China"], ["Fashion Hub"], ["Shanghai"], ["chinese fashion"]],  [["Australia"], ["Fashion Destination"], ["Sydney"], ["australian fashion"]], [["Germany"], ["Fashion Pioneer"], ["Berlin"], ["german fashion"]], [["Spain"], ["Fashion Icon"], ["Madrid"], ["spanish fashion"]],   [
            ["United States"], ["Fashion Influencer"], ["New York"], ["american fashion"]], [["Japan"], ["Fashion Innovator"], ["Tokyo"], ["japanese fashion"]], [["United Kingdom"], ["Fashion Trendsetter"], ["London"], ["british fashion"]], [["Italy"], ["Fashion Leader"], ["Milan"], ["italian fashion"]],  [["France"], ["Fashion Capital"], ["Paris"], ["french fashion"]]]

    # Background video upload
    # uploaded_bg_videos = st.file_uploader("Choose background video files", type=[
    #                                       'mp4', 'avi', 'mov', 'gif'], accept_multiple_files=True)

    # Background music upload
    uploaded_bg_music = st.file_uploader(
        "Choose a background music file", type=['mp3', 'wav'])

    # Creating chains
    llm = OpenAI(model_name='text-davinci-003', temperature=0.2)
    video_chain4 = LLMChain(llm=llm, prompt=video_template4, verbose=True)
    fact_check_chain = LLMChain(
        llm=llm, prompt=fact_check_template, verbose=True)

    openai_button = st.button("Make OpenAI Call")  # OpenAI Call Button
    user_entered_response = ""
    with st.expander('Advanced OpenAI Settings'):
        # OpenAI Call Bypass Radio Button
        openai_bypass = st.radio('Bypass OpenAI Call?', ('No', 'Yes'))
        user_entered_response = st.text_area("Enter your own response", st.session_state.ranking_list)
        submit_button = st.button("Submit Response")
        if submit_button:
            st.session_state.ranking_list = convert_openai_response(user_entered_response)
            print('Ranking_List:', st.session_state.ranking_list)
    # Initialize the session state
    if 'generate_video' not in st.session_state:
        st.session_state.generate_video = False

    generate_video_button = st.button("Generate Video")

    if openai_button:
        if user_input.strip() == '':
            st.error('Error: Input field is empty. Please enter a topic.')
        elif openai_bypass == 'No':
            with st.spinner("Waiting for OpenAI response..."):
                try:
                    response = video_chain4.run({"topic": user_input})
                    fact_checked_response = fact_check_chain.run(
                        {"topic": user_input, "response": response})
                    st.session_state.ranking_list = convert_openai_response(
                        fact_checked_response)
                except Exception as e:
                    print(f'Error occurred while calling OpenAI API: {e}')
                with st.expander("Click to expand OpenAI response:"):
                    st.write("Fact Checked Response:", fact_checked_response)
                    st.write("Formatted Response:",st.session_state.ranking_list)
                st.session_state.generate_video = True
        elif openai_bypass == 'Yes':
            st.error('Error: Bypass OpenAI is set to Yes')
            st.session_state.generate_video = True
            if user_entered_response.strip() == '':
                st.error(
                    'Error: Response field is empty. Please enter your own response.')
            else:
                try:
                    st.session_state.ranking_list = convert_openai_response(
                        user_entered_response)
                    st.session_state.generate_video = True
                except Exception as e:
                    st.error(
                        f'Error occurred while parsing user entered response: {e}')
        st.experimental_rerun()

    with st.expander("Advanced Generate Video Settings"):
            include_flag = st.radio('Include Country flag?', ('No', 'Yes'))
    if generate_video_button:
        if user_input.strip() == '':
            st.error('Error: Input field is empty. Please enter a topic.')
        elif (st.session_state.get('generate_video') and user_input) or openai_bypass == 'Yes':
            with st.spinner("Generating video...\n this might take a minute!"):

                st.session_state.generate_video = False

                ranking_frame_videos = []
                title_bg = (get_video_from_pexels(user_input))
        
                if title_bg is not None:
                    download_video(title_bg, f'ranking_frame_0.mp4')
                    ranking_frame_videos.append(f'ranking_frame_0.mp4')
                for j in range(len(st.session_state.ranking_list)):
                    element_name = st.session_state.ranking_list[j][0][0]
                    video = get_video_from_pexels(element_name)
                    if video is not None:
                        download_video(video, f'ranking_frame_{j+1}.mp4')
                        ranking_frame_videos.append(f'ranking_frame_{j+1}.mp4')

                if isinstance(st.session_state.ranking_list, list):
                    try:
                        bg_videos = [VideoFileClip(path)
                                    for path in ranking_frame_videos]
                    except Exception as e:
                        st.error(f'Error occurred while creating video clips: {e}')
                    default_audio_file_path = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\audio\default_audio.mp3'
                    with open(default_audio_file_path, 'rb') as default_audio_file:
                        bg_music = default_audio_file.name if uploaded_bg_music is None else save_uploaded_file(
                            uploaded_bg_music)

                        # This line creates the video using the ranking list.
                        try:
                            create_video(st.session_state.ranking_list,
                                        user_input, include_flag, bg_videos=bg_videos, bg_music=bg_music)
                        except Exception as e:
                            st.error(
                                f'Error occurred while generating video: {e}')

                    for video_clip in bg_videos:  # Close video clips before deleting the temporary files
                        video_clip.close()

                    for video_path in ranking_frame_videos:  # Remove the video files
                        if os.path.exists(video_path):
                            os.remove(video_path)

                    if uploaded_bg_music is not None:
                        os.remove(bg_music)
        else:
            st.error(
                'Error: No JSON object to make a video out of. Click "Make OpenAICall" before this button.\
                    \nOr by pass it in advanced settings')

    if authenticate_button:
        st.session_state.youtube = authenticate_youtube(channel_choice)

    upload_video_button = st.button("Upload to YouTube")
    title = ''
    description=''
    if user_input.strip() == '':
        st.error(
            'Error: Video title cannot be empty. Please enter a topic for your video.')
    else:
        each_word = user_input.split()
        title = 'The Top 10 ' + user_input
    description = user_input + \
        ' Top10 Countries.\n What do you want to see next?'  # Video description
    tags = []#[user_input, st.session_state.ranking_list[9][0][0], st.session_state.ranking_list[8][0][0], st.session_state.ranking_list[7][0][0]]  # List of tags
    with st.expander('Advanced Youtube Settings') as adv_yt:
        title = st.text_input('Title:',title)
        description = st.text_area('Description:',description)
    #if upload_video_button:
    if os.path.exists("ranking_video.mp4"):
        st.video("ranking_video.mp4")

    if st.button("Confirm Upload"):
        if 'youtube' not in st.session_state:
            st.error("You must authenticate YouTube before uploading.")
        else:
            st.write(f'Uploading video with title: "{title}"')
            response = upload_video(
                st.session_state.youtube, "ranking_video.mp4", title, description, tags)
            st.write("Video uploaded, video id is: ", response['id'])


if __name__ == "__main__":
    main()
