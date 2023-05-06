from moviepy.editor import concatenate_videoclips, TextClip, CompositeVideoClip
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import os
import json
from dotenv import load_dotenv
import streamlit as st
from moviepy.config import change_settings
change_settings(
    {"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})


def create_ranking_frame(rank, text, duration=2):
    clip = TextClip(f"Rank {rank}: {text}", fontsize=24,
                    color='white', size=(640, 480))
    clip = clip.set_duration(duration)
    return clip


def create_video(ranking_list):
    clips = []
    j = 0
    for i in range(10, 0, -1):
        clips.append(create_ranking_frame(
            i, ranking_list[j]))  # Rank and Country
        j += 1

    final_video = concatenate_videoclips(clips)
    final_video.write_videofile("ranking_video.mp4", fps=24)


def convert_openai_response(response):
    # Turn array wrapped by string to a normal array
    ranking_list = json.loads(response)
    return ranking_list


def main():
    load_dotenv()
    st.set_page_config(page_title="FilmForge")
    st.header("FilmForge")
    user_input = st.text_input("Enter the topic of your Top 10 tiktok")

    video_template = PromptTemplate(
        input_variables=["topic"],
        template='Generate a Top 10 list of countries related to {topic} and write it in an array format,\
                    starting from the tenth place. Your response should look like this: e.g.["Country 10th place", "Country 9th place",\
                    "Country 8th place", "Country 7th place", "Country 6th place", "Country 5th place", "Country 4th place", "Country 3rd place", "Country 2nd place", "Country 1st place"]'
    )

    llm = OpenAI(temperature=0.9)
    video_chain = LLMChain(llm=llm, prompt=video_template)

    if user_input:
        response = video_chain.run(user_input)
        st.write(response)

        # This line creates the video using the ranking list.
        create_video(convert_openai_response(response))


if __name__ == "__main__":
    main()
