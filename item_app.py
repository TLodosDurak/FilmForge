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
from scripts.utils import convert_openai_response, save_uploaded_file, pick_default_audio_path, get_hashtags_list, generate_columns_layout
from scripts.video_item import create_item_video, download_image, is_image_readable
from scripts.templates import *
from scripts.youtube import *
from moviepy.config import change_settings
from scripts.custom_google_search import CustomGoogleSearchAPIWrapper

from src.audio import *
from src.videos import *
from src.videos.default_pexel_bg import get_title_bg_nature, get_ranking_frame_videos

# Necessary if using Windows
change_settings(
    {"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})


google_search = CustomGoogleSearchAPIWrapper()

def main():

    load_dotenv()  # Loading env vars
    os.environ['CLIENT_SECRET_FILE0'] = 'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\client_secret_0.json'
    os.environ['CLIENT_SECRET_FILE1'] = 'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\client_secret_1.json'
    st.set_page_config(page_title="ItemForge")  # Setting up Streamlit
    st.header("ItemForge")
    # Asking for user input

    user_input = st.text_input(
        "Enter the topic of your Top 10 short video", 'Biggest Animals')
    # Pick Youtube Channel
    channel_choice = st.selectbox(
        "Pick YT channel", ('🟡top10countryrankings', '🔴Top10AnythingAndMore'))
    authenticate_button = st.button("Authenticate YouTube")

    if 'channel_category' not in st.session_state:
        st.session_state.channel_category = ' #nature'

    # For testing the code without making openai calls $$$
    if 'ranking_list' not in st.session_state:
        st.session_state.ranking_list =  [[["Giant Anteater"], ["Longest Mammal"], ["2.3 Meters"]],
        [["Komodo Dragon"], ["Largest Lizard"], ["3 Meters"]],
        [["Giant Squid"], ["Longest Mollusk"], ["13 Meters"]],
        [["Hippopotamus"], ["Heaviest Land Mammal"], ["3.5 Tonnes"]],
        [["Gorilla"], ["Heaviest Primate"], ["220 Kilograms"]],
        [["Ostrich"], ["Tallest Bird"], ["2.7 Meters"]],
        [["Saltwater Crocodile"], ["Longest Reptile"], ["6 Meters"]],
        [["Giraffe"], ["Tallest Animal"], ["5.5 Meters"]],
        [["African Elephant"], ["Heaviest Animal"], ["6 Tonnes"]],
        [["Blue Whale"], ["Largest Animal"], ["30 Meters"]]]
    if 'title' not in st.session_state:
        st.session_state.title = 'Top 10: ' + user_input + \
            st.session_state.channel_category + ' #shorts #fyp '
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

    video_chain = LLMChain(llm=llm, prompt=item_template1, verbose=True)
    fact_check_chain = LLMChain(
        llm=llm, prompt=item_fact_check_template, verbose=True)
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
        user_entered_response = st.text_area(
            "Enter your own response", st.session_state.ranking_list)
        submit_button = st.button("Submit Response")
        if submit_button:
            st.session_state.media_file_paths.clear()  # Clear existing paths
            st.session_state.queries.clear()  # Clear existing queries
            st.session_state.ranking_list = convert_openai_response(
                user_entered_response)
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
                            media_query, num_results=3)
                        # pic from top 3 results
                        media_file_path = f"media_{j}_{media_queries.index(media_query)}.jpg"
                        image_downloaded = False
                        for media in media_results[:3]:
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
        # OpenAI Call Bypass Radio Button
        openai_bypass = st.radio('Bypass OpenAI Call?', ('No', 'Yes'))
        user_entered_response = st.text_area(
            "Enter your own response", st.session_state.ranking_list)
        submit_button = st.button("Submit Response")
        if submit_button:
            st.session_state.ranking_list = convert_openai_response(
                user_entered_response)
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
                    response = video_chain.run({"topic": user_input})
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
        title_media_query = st.text_input(
            'Input Thumbnail Search Query', user_input)

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
                            create_item_video(st.session_state.ranking_list,
                                         user_input, bg_videos=bg_videos, bg_music=bg_music, title_media_query=title_media_query)
                        except Exception as e:
                            st.error(
                                f'Error occurred while generating video: {e}')

                    if uploaded_bg_music is not None:
                        os.remove(bg_music)
        else:
            st.error(
                'Error: No JSON object to make a video out of. Click "Make OpenAICall" before this button.\
                    \nOr by pass it in advanced settings')

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
        st.session_state.title = user_input + \
            st.session_state.channel_category + ' #shorts #fyp '
        # st.session_state.description = 'Top 10: ' + user_input + '\n Music: 6th String by Dedpled \n' + \
        #     '#fashion #italy #france #uk #usa #nyc #london #milan #paris #india #mumbai #shangai #sydney #berlin #japan #tokyo #spain #madrid'

    with st.expander('Advanced Youtube Settings') as adv_yt:
        st.session_state.title = st.text_input(
            'Title:', st.session_state.title)
        st.session_state.description = st.text_area(
            'Description:', st.session_state.description)
    
    if os.path.exists("ranking_video.mp4"):
        st.video("ranking_video.mp4")

    if st.button("Upload to YT"):
        if 'youtube' not in st.session_state:
            st.error("You must authenticate YouTube before uploading.")
        else:
            st.write(f'Uploading video with title: "{st.session_state.title}"')
            response = upload_video(
                st.session_state.youtube, "ranking_video.mp4", st.session_state.title, st.session_state.description, tags)
            st.write("Video uploaded, video id is: ", response['id'])


if __name__ == "__main__":
    main()
