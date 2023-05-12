from dotenv import load_dotenv
import streamlit as st
from moviepy.editor import VideoFileClip
import os
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from scripts.utils import convert_openai_response, save_uploaded_file
from scripts.video import create_video
from moviepy.config import change_settings
from src.audio import *
from src.videos import *

change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"}) #Necessary if using Windows


is_generating_video = False

def main():
    global is_generating_video
    load_dotenv()
    st.set_page_config(page_title="FilmForge")
    st.header("FilmForge")
    user_input = st.text_input("Enter the topic of your Top 10 Countries tiktok")
    uploaded_bg_videos = st.file_uploader("Choose background video files", type=['mp4', 'avi', 'mov', 'gif'], accept_multiple_files=True)
    uploaded_bg_music = st.file_uploader("Choose a background music file", type=['mp3', 'wav'])
    generate_video_button = st.button("Generate Video")

    if not is_generating_video and user_input and generate_video_button:
        is_generating_video = True
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
        fact_check_template = PromptTemplate(
            input_variables=['topic', 'response'],
            template='Please fix the following ranking list, which needs to be represented in a 3D array.\
                  The ranking list contains countries ranked specifically related to "{topic}".\
                The list needs to be sorted from 10th place to 1st place.\
                The current ranking list is: {response}\
                Your task is to:\
                1) Inspect the ranking list to see if it is in the correct order. If the list is not in the order of 10th place to 1st place, you will need to reverse it.\
                2) Fact-check the list to ensure that the ranking is correct. If any of the rankings are incorrect, you will need to make the necessary changes to the list.\
                3)Print only the new list with the corrected rankings, sorted from 10th place to 1st place.\
                4)Make sure to complete the list if ranking list is incomplete, there might be missing brackets make sure they are added.\
                Final Array should look like this with its contents,its a an array holding arrays which each contain 4 arrays: [[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]],[[...],[...],[...],[...]]]\
                Note: The first element of each sub-array represents the name of the country, the second element represents the reason for ranking, the third element represents\
                the category or topic being ranked, and the fourth element represents the Google image search query for the country.'
            
        )
        llm = OpenAI(model_name='text-davinci-003', temperature=0)
        video_chain3 = LLMChain(llm=llm, prompt=video_template3, verbose=True)
        fact_check_chain = LLMChain(llm=llm,prompt=fact_check_template, verbose=True)
        with st.spinner("Waiting for OpenAI response..."):
            response = video_chain3.run({"topic": user_input})
            fact_checked_response = fact_check_chain.run({"topic":user_input, "response": response})
            ranking_list = convert_openai_response(fact_checked_response)
            # For testing the code without making openai calls $$$
            #response = ''
            with st.expander("Click to expand OpenAI response:"):
                st.write("Initial Response:", response)
                st.write("Fact Checked Response:", ranking_list)

        if isinstance(ranking_list, list):
            temp_bg_video_paths = [save_uploaded_file(video) for video in uploaded_bg_videos]
            bg_videos = [VideoFileClip(path) for path in temp_bg_video_paths]

            default_audio_file_path = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\audio\default_audio.mp3'
            with open(default_audio_file_path, 'rb') as default_audio_file:
                bg_music = default_audio_file.name if uploaded_bg_music is None else save_uploaded_file(uploaded_bg_music)

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

            if uploaded_bg_music is not None:
                os.remove(bg_music)


if __name__ == "__main__":
    main()
