from dotenv import load_dotenv
import streamlit as st
import os
from scripts.custom_google_search import CustomGoogleSearchAPIWrapper
from scripts.video import create_country_video
from moviepy.config import change_settings
from scripts.main_page import page1
from scripts.upload_page import page2
import queue
import threading
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
            ranking_list = video_data["ranking_list"],
            topic = video_data["user_input"],
            include_flag = video_data["include_flag"],
            title_duration = video_data["title_duration"],
            frame_duration = video_data["frame_duration"],
            two_parts = video_data["two_parts"],
            voice_over = video_data["voice_over"],
            bg_videos = video_data["bg_videos"],
            bg_music = video_data["bg_music"],
            thread_id = thread_id
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
    os.environ['CLIENT_SECRET_FILE2'] = 'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\client_secret_2.json'
    os.environ['CLIENT_SECRET_FILE3'] = 'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\client_secret_3.json'
    st.set_page_config(page_title="FilmForge")  # Setting up Streamlit
    st.header("FilmForge")

    pages = {
        "Video Creation": page1,
        "Schedule and Uploads": page2,
    }

    page = st.sidebar.selectbox("Select your page:", tuple(pages.keys()))

    # Run the appropriate function to draw the selected page.
    pages[page](video_queue)

if __name__ == "__main__":
    main()
