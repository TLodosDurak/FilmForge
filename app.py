from dotenv import load_dotenv
import streamlit as st
from moviepy.editor import VideoFileClip
import os
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from scripts.utils import convert_openai_response, save_uploaded_file
from scripts.video import create_video
from scripts.templates import *
from moviepy.config import change_settings
from src.audio import *
from src.videos import *

change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"}) #Necessary if using Windows


#is_generating_video = False

def main():
    #Making sure no video is being edited
    #global is_generating_video
    #Loading env vars
    load_dotenv() 
    #Setting up Streamlit
    st.set_page_config(page_title="FilmForge")
    st.header("FilmForge")
    #Asking for user input 
    user_input = st.text_input("Enter the topic of your Top 10 Countries short video")
    #Background video upload
    uploaded_bg_videos = st.file_uploader("Choose background video files", type=['mp4', 'avi', 'mov', 'gif'], accept_multiple_files=True)
    #Background music upload
    uploaded_bg_music = st.file_uploader("Choose a background music file", type=['mp3', 'wav'])
    #Creating chains
    llm = OpenAI(model_name='text-davinci-003', temperature=0.5)
    video_chain4 = LLMChain(llm=llm, prompt=video_template4, verbose=True)
    fact_check_chain = LLMChain(llm=llm,prompt=fact_check_template, verbose=True)
    #OpenAI Call Button
    openai_button = st.button("Make OpenAI Call")
    # Initialize the session state
    if 'generate_video' not in st.session_state:
        st.session_state.generate_video = False
    # For testing the code without making openai calls $$$
    if 'ranking_list' not in st.session_state:
        st.session_state.ranking_list = [[["India"], ["Fashion Hub"], ["Mumbai"], ["indian fashion"]],[["China"], ["Fashion Hub"], ["Shanghai"], ["chinese fashion"]],  [["Australia"], ["Fashion Destination"], ["Sydney"], ["australian fashion"]],[["Germany"], ["Fashion Pioneer"], ["Berlin"], ["german fashion"]],[["Spain"], ["Fashion Icon"], ["Madrid"], ["spanish fashion"]],   [["United States"], ["Fashion Influencer"], ["New York"], ["american fashion"]],[["Japan"], ["Fashion Innovator"], ["Tokyo"], ["japanese fashion"]],[["United Kingdom"], ["Fashion Trendsetter"], ["London"], ["british fashion"]],[["Italy"], ["Fashion Leader"], ["Milan"], ["italian fashion"]],  [["France"], ["Fashion Capital"], ["Paris"], ["french fashion"]]] 

    generate_video_button = st.button("Generate Video")

    if openai_button:
        with st.spinner("Waiting for OpenAI response..."):
            try:
                response = video_chain4.run({"topic": user_input})
                fact_checked_response = fact_check_chain.run({"topic":user_input, "response": response})
                st.session_state.ranking_list = convert_openai_response(fact_checked_response)
            except Exception as e:
                print(f'Error occurred while calling OpenAI API: {e}')
            with st.expander("Click to expand OpenAI response:"):
                st.write("Initial Response:", response)
                st.write("Fact Checked Response:", st.session_state.ranking_list)
            st.session_state.generate_video = True
            print(f'generate_video_button: {generate_video_button}\n')
    if generate_video_button and st.session_state.generate_video:
        print('Generate Video Button clicked')
        if user_input:
            print(f'generate_video_button: {generate_video_button}\n')
            print(f'user_input: {user_input}\n')
            print('Button Clicked')
            st.session_state.generate_video = False
            print(isinstance(st.session_state.ranking_list, list))
            if isinstance(st.session_state.ranking_list, list):
                temp_bg_video_paths = [save_uploaded_file(video) for video in uploaded_bg_videos]
                bg_videos = [VideoFileClip(path) for path in temp_bg_video_paths]

                default_audio_file_path = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\audio\default_audio.mp3'
                with open(default_audio_file_path, 'rb') as default_audio_file:
                    bg_music = default_audio_file.name if uploaded_bg_music is None else save_uploaded_file(uploaded_bg_music)

                    with st.spinner("Generating video...\n this might take a minute!"):
                        # This line creates the video using the ranking list.
                        try:
                            create_video(st.session_state.ranking_list, user_input, bg_videos, bg_music)
                        except Exception as e:
                            st.error(f'Error occurred while generating video: {e}')

                if os.path.exists("ranking_video.mp4"):
                    st.video("ranking_video.mp4")

                for video_clip in bg_videos:  # Close video clips before deleting the temporary files
                    video_clip.close()
                for path in temp_bg_video_paths:
                    os.remove(path)

                if uploaded_bg_music is not None:
                    os.remove(bg_music)
    else:
        st.error('Error: No JSON object to make a video out of. Click "Make OpenAICall" before this button.')

if __name__ == "__main__":
    main()
