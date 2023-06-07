import pickle
import json
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
from scripts.custom_google_search import CustomGoogleSearchAPIWrapper
from scripts.utils import convert_openai_response, save_uploaded_file, pick_default_audio_path, get_hashtags_list, switch_response, reverse_response, generate_columns_layout
from scripts.video import create_country_video, download_image, is_image_readable
from scripts.templates import *
from scripts.youtube import *
from moviepy.config import change_settings
from src.audio import *
from src.videos import *
from src.videos.default_pexel_bg import get_ranking_frame_videos
from PIL import Image
import queue
import threading
import time
import uuid





# Necessary if using Windows
change_settings(
    {"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

google_search = CustomGoogleSearchAPIWrapper()
video_queue = queue.Queue()


def worker(thread_id):
    while True:
        video_data = video_queue.get()
        if video_data is None:
            break
        create_country_video(
            video_data["ranking_list"],
            video_data["user_input"],
            video_data["include_flag"],
            bg_videos=video_data["bg_videos"],
            bg_music=video_data["bg_music"],
            thread_id=thread_id
        )
        video_queue.task_done()

threads = []
num_worker_threads = 4
for i in range(num_worker_threads):
    t = threading.Thread(target=worker, args=(str(uuid.uuid4()),))
    t.start()
    threads.append(t)


def main():

    load_dotenv()  # Loading env vars
    os.environ['CLIENT_SECRET_FILE0'] = 'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\client_secret_0.json'
    os.environ['CLIENT_SECRET_FILE1'] = 'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\client_secret_1.json'
    st.set_page_config(page_title="FilmForge")  # Setting up Streamlit
    st.header("FilmForge")
    # Asking for user input

    user_input = st.text_input(
        "Enter the topic of your Top 10 Countries short video", 'Countries in Fashion 2023')
    # Pick Youtube Channel
    channel_choice = st.selectbox(
        "Pick YT channel", ('🟡top10countryrankings', '🔴Top10AnythingAndMore'))
    authenticate_button = st.button("Authenticate YouTube")

    if 'channel_category' not in st.session_state:
        st.session_state.channel_category = ' #fashion'

    # For testing the code without making openai calls $$$
    if 'ranking_list' not in st.session_state:
        st.session_state.ranking_list = [[["India"], ["Fashion Hub"], ["Mumbai"], ["indian fashion"]], [["China"], ["Fashion Hub"], ["Shanghai"], ["chinese fashion"]],  [["Australia"], ["Fashion Destination"], ["Sydney"], ["australian fashion"]], [["Germany"], ["Fashion Pioneer"], ["Berlin"], ["german fashion"]], [["Spain"], ["Fashion Icon"], ["Madrid"], ["spanish fashion"]],   [
            ["United States"], ["Fashion Influencer"], ["New York"], ["american fashion"]], [["Japan"], ["Fashion Innovator"], ["Tokyo"], ["japanese fashion"]], [["United Kingdom"], ["Fashion Trendsetter"], ["London"], ["british fashion"]], [["Italy"], ["Fashion Leader"], ["Milan"], ["italian fashion"]],  [["France"], ["Fashion Capital"], ["Paris"], ["french fashion"]]]
    if 'title' not in st.session_state:
        st.session_state.title = user_input + st.session_state.channel_category + ' #shorts '
    if 'description' not in st.session_state:
        st.session_state.description = 'Top 10: ' + user_input + '\n Music: 6th String by Dedpled \n' + \
            '#italy #france #uk #usa #nyc #london #milan #paris #india #mumbai #shangai #sydney #berlin #japan #tokyo #spain #madrid'
    # Example Meta Data Input: 'India, Mumbai, China, Shanghai, Australia, Sydney, Germany, Berlin, Spain, Madrid, United States, New York, Japan, Tokyo, United Kingdom, London, Italy, Milan, France, Paris'
    # Background video upload
    # uploaded_bg_videos = st.file_uploader("Choose background video files", type=[
    #                                       'mp4', 'avi', 'mov', 'gif'], accept_multiple_files=True)

    # Background music upload
    uploaded_bg_music = st.file_uploader(
        "Choose a background music file", type=['mp3', 'wav'])

    # Creating chains
    llm = OpenAI(model_name='text-davinci-003', temperature=0.2)
    llm2 = OpenAI(model_name='text-davinci-002', temperature=0.2)

    video_chain4 = LLMChain(llm=llm, prompt=video_template4, verbose=True)
    fact_check_chain = LLMChain(
        llm=llm, prompt=fact_check_template, verbose=True)
    hashtage_chain = LLMChain(llm=llm2, prompt=hashtag_template, verbose=True)

    openai_button = st.button("Make OpenAI Call")  # OpenAI Call Button
    user_entered_response = ""
    if 'media_file_paths' not in st.session_state:
        st.session_state.media_file_paths = []
    if 'queries' not in st.session_state:
        st.session_state.queries = []


    with st.expander('Advanced OpenAI Settings'):
        # OpenAI Call Bypass Radio Button
        openai_bypass = st.radio('Bypass OpenAI Call?', ('No', 'Yes'))
        reverse_button = st.button("Reverse Response")
        switch_button = st.button("Switch Response")

        if reverse_button:
            reversed_response = reverse_response(st.session_state.ranking_list)
            st.session_state.ranking_list = reversed_response
        
        if switch_button:
            switched_response = switch_response(st.session_state.ranking_list)
            st.session_state.ranking_list = switched_response

        user_entered_response = st.text_area(
            "Enter your own response", st.session_state.ranking_list)
        if user_entered_response:
            st.session_state.ranking_list = convert_openai_response(user_entered_response)

        submit_button = st.button("Submit Response")
        if submit_button:
            st.session_state.media_file_paths.clear()  # Clear existing paths
            st.session_state.queries.clear()  # Clear existing queries
            st.session_state.ranking_list = convert_openai_response(st.session_state.ranking_list)
            print('Ranking_List:', st.session_state.ranking_list)
            j = 0
            for i in range(min(10, len(st.session_state.ranking_list)), 0, -1):
                try:
                    media_queries = [
                        f"{st.session_state.ranking_list[j][3][0]}"]
                    media_queries.append(
                        f"{st.session_state.ranking_list[j][0][0]} + 'flag'")
                    for media_query in media_queries:
                        st.session_state.queries.append(media_query)
                        media_results = google_search.search_media(
                            media_query, num_results=5)
                        # pic from top 3 results
                        media_file_path = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_{j}_{media_queries.index(media_query)}.jpg"
                        image_downloaded = False
                        for media in media_results[:5]:
                            media_url = media["link"]
                            try:
                                if not image_downloaded:
                                    image_downloaded = download_image(
                                        media_url, media_file_path)
                                    # Check if the image is readable
                                    if image_downloaded and is_image_readable(media_file_path):
                                        break
                            except Exception as e:
                                print(
                                    f"Error occurred while downloading or reading the image: {e}")
                                raise e
                        if not image_downloaded:
                            media_file_path = None  # Skip using the image if the download fails
                        st.session_state.media_file_paths.append(media_file_path)
                except Exception as e:
                    print(
                        f"Error occurred while processing the media queries: {e}")
                    raise e
                j += 1
        cols = generate_columns_layout(st.session_state.media_file_paths, st.session_state.queries)
    for row in cols:
        for column in row:
            column.write("")  # Add empty write statements to preserve the layout

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
                    print(get_hashtags_list(st.session_state.ranking_list))
                    hashtag_response = hashtage_chain.run(
                        {"list": get_hashtags_list(st.session_state.ranking_list)})
                    print(hashtag_response)
                    st.session_state.description = 'Top 10: ' + user_input + \
                        '\n Music: 6th String by Dedpled \n' + hashtag_response

                except Exception as e:
                    print(f'Error occurred while calling OpenAI API: {e}')
                with st.expander("Click to expand OpenAI response:"):
                    st.write("Fact Checked Response:", fact_checked_response)
                    st.write("Formatted Response:",
                             st.session_state.ranking_list)
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
        title_media_query = st.text_input('Input Thumbnail Search Query')

        # The user's input is now in title_media_query
        title_media_query = [title_media_query]

        # Perform Google search
        try:
            title_media_results = google_search.search_media(
                title_media_query, num_results=3)
        except Exception as e:
            st.write(f"Error occurred while using Google Search API: {e}")
            raise e

        # Download and check image from top 3 results
        title_media_file_path = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_title.jpg"
        image_downloaded = False
        for media in title_media_results[:3]:
            media_url = media["link"]
            try:
                if not image_downloaded:
                    image_downloaded = download_image(
                        media_url, title_media_file_path)
                    # Check if the image is readable
                    if image_downloaded and is_image_readable(title_media_file_path):
                        break
            except Exception as e:
                st.write(
                    f"Error occurred while downloading or reading the image: {e}")
                raise e

        # Display image to the user
        if image_downloaded:
            image = Image.open(title_media_file_path)
            st.image(image, caption=title_media_query)
        else:
            st.write("No valid image found.")

    if generate_video_button:
        if user_input.strip() == '':
            st.error('Error: Input field is empty. Please enter a topic.')
        elif (st.session_state.get('generate_video') and user_input) or openai_bypass == 'Yes':
            with st.spinner("Generating video...\n this might take a minute!"):
                st.session_state.generate_video = False
                if isinstance(st.session_state.ranking_list, list):
                    try:
                        bg_videos = get_ranking_frame_videos()
                    except Exception as e:
                        st.error(
                            f'Error occurred while creating video clips: {e}')
                    default_audio_file_path = pick_default_audio_path()
                    with open(default_audio_file_path, 'rb') as default_audio_file:
                        bg_music = default_audio_file.name if uploaded_bg_music is None else save_uploaded_file(
                            uploaded_bg_music)

                        # This line creates the video using the ranking list.
                        try:
                            # create_country_video(st.session_state.ranking_list,
                            #                      user_input, include_flag, bg_videos=bg_videos, bg_music=bg_music)
                            video_queue.put({
                                "ranking_list": st.session_state.ranking_list,
                                "user_input": user_input,
                                "include_flag": include_flag,
                                "bg_videos": bg_videos,
                                "bg_music": bg_music
                            })

                        except Exception as e:
                            st.error(
                                f'Error occurred while generating video: {e}')

                    # for video_clip in bg_videos:  # Close video clips before deleting the temporary files
                    #     video_clip.close()

                    # for video_path in ranking_frame_videos:  # Remove the video files
                    #     if os.path.exists(video_path):
                    #         os.remove(video_path)

                    if uploaded_bg_music is not None:
                        os.remove(bg_music)
        else:
            st.error(
                'Error: No JSON object to make a video out of. Click "Make OpenAICall" before this button.\
                    \nOr by pass it in advanced settings')  
        for row in cols:
            for column in row:
                column.write("")  # Add empty write statements to preserve the layout

    if authenticate_button:
        st.session_state.youtube = authenticate_youtube(channel_choice)
        st.session_state.channel_category = get_channel_category(
            channel_choice)
    tags = []
    if user_input.strip() == '':
        st.error(
            'Error: Video title cannot be empty. Please enter a topic for your video.')
    else:
        each_word = user_input.split()
        st.session_state.title = 'Top 10: ' + user_input + \
            st.session_state.channel_category + ' #shorts #fyp '
        # st.session_state.description = 'Top 10: ' + user_input + '\n Music: 6th String by Dedpled \n' + \
        #     '#fashion #italy #france #uk #usa #nyc #london #milan #paris #india #mumbai #shangai #sydney #berlin #japan #tokyo #spain #madrid'

    with st.expander('Advanced Youtube Settings') as adv_yt:
        st.session_state.title = st.text_input(
            'Title:', st.session_state.title)
        st.session_state.description = st.text_area(
            'Description:', st.session_state.description)
    # if upload_video_button:
    video_title = f"{'_'.join(user_input.split())}.mp4"
    if os.path.exists(video_title):
        st.video(video_title)

    if st.button("Upload to YouTube"):
        if 'youtube' not in st.session_state:
            st.error("You must authenticate YouTube before uploading.")
        else:
            st.write(f'Uploading video with title: "{st.session_state.title}"')
            csv_path = r'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\src\\files\\schedule.csv'
            last_upload_time = get_last_upload_time(csv_path)
            next_slot = get_next_available_slot(last_upload_time)
            print('Next available slot is:', next_slot)
            response = upload_video(
                st.session_state.youtube, video_title, st.session_state.title, st.session_state.description, tags, next_slot)
            write_schedule_to_csv(next_slot, st.session_state.title, csv_path)
            st.write("Video uploaded, video id is: ", response['id'])


if __name__ == "__main__":
    main()
