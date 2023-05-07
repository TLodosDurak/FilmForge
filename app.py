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
    for i in range(len(ranking_list), 0, -1):
        clips.append(create_ranking_frame(
            i, ranking_list[j]))  # Rank and Country
        j += 1

    final_video = concatenate_videoclips(clips)
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

    if not is_generating_video and user_input:
        is_generating_video = True
        video_template = PromptTemplate(
            input_variables=["topic"],
            template='Generate a Top N list of countries related to {topic} where N is size for example top 10 or top 8,\
                        something that fits, and write it in an array format, starting from the last place. Your response should\
                        look like this: e.g.["Country 10th place", "Country 9th place", "Country 8th place", "Country 7th place",\
                        "Country 6th place", "Country 5th place", "Country 4th place", "Country 3rd place", "Country 2nd place", "Country 1st place"]'
        )

        llm = OpenAI(temperature=0.9)
        video_chain = LLMChain(llm=llm, prompt=video_template)

        response = video_chain.run(user_input)
        # response = '["North Korea", "France", "China", "United Kingdom", "India", "Pakistan", "Israel", "Russia", "United States", "Iran"]'
        st.write(response)

        # This line creates the video using the ranking list.
        create_video(convert_openai_response(response))

        is_generating_video = False


if __name__ == "__main__":
    main()
