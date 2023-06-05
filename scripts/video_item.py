from moviepy.editor import (concatenate_videoclips, TextClip, CompositeVideoClip,
                            AudioFileClip, ImageClip)
from av import AVError
from scripts.custom_google_search import CustomGoogleSearchAPIWrapper
import streamlit as st
from scripts.utils import *
from moviepy.video.fx.all import margin, resize, crop
import cv2
import numpy as np


def convert_frame_to_rgb(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)



def create_title_card_variant0(title_element, title_topic, duration=3.90, bg_video=None, title_media_file_path=None):
    # canvas_clip = TextClip(f" ", fontsize=90, font="Calibri-Bold",
    #                        color='White', size=(1080, 1920), stroke_color='black', stroke_width=4, transparent=True)
    #canvas_clip = canvas_clip.set_duration(duration)
    element_clip = TextClip(title_element, fontsize=220, font="Calibri-Bold",
                            color='Firebrick', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=2)
    element_clip = element_clip.set_position(
        ('center', -700)).set_duration(duration)
    topic_clip = TextClip(title_topic, fontsize=180, font="Calibri-Bold",
                          color='YellowGreen', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=2)
    topic_clip = topic_clip.set_position(
        ('center', -300)).set_duration(duration)
    # Add Fade-in Effect
    # element_clip = fadein_clip(element_clip, 0.25) # 1 second fade-in
    # topic_clip = fadein_clip(topic_clip, 0.25)

    # Set margins
    topic_clip = topic_clip.margin(left=40, right=40, bottom=0, top=0)
    if bg_video is not None:
        bg_video = VideoFileClip(bg_video).set_duration(duration)

        # bg_video = apply_shake_for_duration(bg_video, 1)

    # title_media_file_path = None
    if title_media_file_path is not None:
        media_clip = ImageClip(title_media_file_path).set_duration(duration)
        # Resize the media clip as needed
        media_clip = media_clip.resize(height=600)
        # Convert the image to RGB
        # media_clip = media_clip.fl_image(convert_frame_to_rgb)
        media_clip = media_clip.margin(left=10, right=10, bottom=10, top=10)

        # Position the media clip on the frame
        if media_clip is None:
            print(
                f"Failed to resize the media file: {title_media_file_path}")
        else:
            if media_clip.h is not None:
                media_clip = media_clip.set_position(("center", 950))
                # Add fade in for media
                # media_clip =fadein_clip(media_clip, 0.25)
        if bg_video is not None:
            title_card = CompositeVideoClip(
                [bg_video, media_clip, element_clip, topic_clip]) #canvas_clip, 
        else:
            title_card = CompositeVideoClip(
                [media_clip, element_clip, topic_clip])
    else:
        if bg_video is not None:
            title_card = CompositeVideoClip(
                [bg_video, element_clip, topic_clip])
        else:
            title_card = CompositeVideoClip(
                [element_clip, topic_clip])
    return title_card





def create_item_ranking_frame(rank, country, why, what, duration=2.80, bg_video=None, media_file_paths=None):
    canvas_clip = TextClip(f" ", fontsize=130, font="Calibri-Bold",
                           color='White', size=(1080, 1920), stroke_color='black', stroke_width=4, transparent=True)
    txt_clip = TextClip(f"#{rank}: {country}", fontsize=75, font="Calibri-Bold",
                        color='YellowGreen', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    why_clip = TextClip(f"{why}", fontsize=130, font="Calibri-Bold",
                        color='white', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    what_clip = TextClip(f"{what}", fontsize=130, font="Calibri-Bold",
                         color='Orange', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)

    canvas_clip = canvas_clip.set_duration(duration)
    txt_clip = txt_clip.set_position(('center', -600)).set_duration(duration)
    why_clip = why_clip.set_position(('center', 550)).set_duration(duration)
    what_clip = what_clip.set_position(('center', 655)).set_duration(duration)

    # Add Fade-in Effect
    # txt_clip = fadein_clip(txt_clip, 0.25) # 1 second fade-in
    # why_clip = fadein_clip(why_clip, 0.25)
    # what_clip = fadein_clip(what_clip, 0.25)

    if bg_video is not None:
        bg_video = bg_video.set_duration(duration)
        # Apply Shake
        # bg_video = apply_shake_for_duration(bg_video, 1)

    if media_file_paths is not None:
        media_clips = []
        for media_file_path in media_file_paths:
            try:
                media_clip = ImageClip(media_file_path).set_duration(duration)
                # Resize the media clip as needed
                # Convert the image to RGB
                # media_clip = media_clip.fl_image(convert_frame_to_rgb)
                media_clip = media_clip.resize(height=600)

                media_clip = media_clip.margin(
                    left=10, right=10, bottom=10, top=10)

                # Position the media clip on the frame
                if media_clip is None:
                    print(
                        f"Failed to resize the media file: {media_file_path}")
                else:
                    # Add Fade-in for media
                    # media_clip =fadein_clip(media_clip, 0.25)
                    # This is the first image
                    if media_clip.h is not None:
                        media_clip = media_clip.set_position(
                            ("center", 850))
                    else:
                        media_clip = media_clip.set_position("center")

                media_clips.append(media_clip)

            except AVError:
                print(f"Error processing the media file: {media_file_path}")
                media_clips.append(None)

        if bg_video is not None:
            clip = CompositeVideoClip(
                [canvas_clip, bg_video] + media_clips + [txt_clip, why_clip, what_clip])
        else:
            clip = CompositeVideoClip(
                [canvas_clip] + media_clips + [txt_clip, why_clip, what_clip])
    else:
        if bg_video is not None:
            clip = CompositeVideoClip(
                [canvas_clip, bg_video, txt_clip, why_clip, what_clip])
        else:
            clip = CompositeVideoClip(
                [canvas_clip, txt_clip, why_clip, what_clip])

    return clip


def create_item_video(ranking_list, topic, bg_videos=None, bg_music=None, title_media_query='usa flag'):
    clips = []
    j = 0
    # Title card
    title_element = f""
    title_topic = f"{topic}"
    if bg_videos is not None:
        bg_video = bg_videos[j % len(bg_videos)] if bg_videos else None
    else:
        bg_video = None

    google_search = CustomGoogleSearchAPIWrapper()
    # Title Card
    title_media_query = [title_media_query]
    try:
        title_media_results = google_search.search_media(
            title_media_query, num_results=3)
    except Exception as e:
        print(f"Error occurred while using Google Search API: {e}")
        raise e

    # pic from top 3 results
    title_media_file_path = f"media_title.jpg"
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
            print(
                f"Error occurred while downloading or reading the image: {e}")
            raise e
    if not image_downloaded:
        title_media_file_path = None  # Skip using the image if the download fails

    try:
        title_card = create_title_card_variant0(
            title_element, title_topic, bg_video=bg_video, title_media_file_path=title_media_file_path)
        if title_card is not None:
            clips.append(title_card)
    except Exception as e:
        print(f"Error occurred while creating the title card: {e}")
        raise e

    # Rest
    with st.expander("Click to expand google image search queries"):
        j = 0
        for i in range(min(10, len(ranking_list)), 0, -1):
            try:
                media_queries = [f"{ranking_list[j][0][0]} high quality image"]
                media_file_paths = []
                for media_query in media_queries:
                    st.write(media_query)
                    media_results = google_search.search_media(
                        media_query, num_results=3)
                    # pic from top 3 results
                    media_file_path = f"media_{j}.jpg"
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
                    media_file_paths.append(media_file_path)
            except Exception as e:
                print(
                    f"Error occurred while processing the media queries: {e}")
                raise e

            try:
                if bg_videos is None:
                    bg_video = None
                else:
                    bg_video = bg_videos[(j %
                                          len(bg_videos))+1] if bg_videos else None
                ranking_frame = create_item_ranking_frame(
                    i, ranking_list[j][0][0], ranking_list[j][1][0], ranking_list[j][2][0],
                    bg_video=bg_video, media_file_paths=media_file_paths)

                if ranking_frame is not None:
                    ranking_frame = ranking_frame.set_duration(
                        ranking_frame.duration).set_fps(24)  # set fps to 24
                clips.append(ranking_frame)
                j += 1
            except Exception as e:
                print(f"Error occurred while creating ranking frames: {e}")
                raise e

    try:
        final_video = concatenate_videoclips(clips)
    except Exception as e:
        print(f"Error occurred while concatenating video clips: {e}")
        raise e

    try:
        if bg_music is not None:
            audio = AudioFileClip(bg_music)
            audio = audio.volumex(0.6)  # Set audio volume
            audio = audio.set_duration(final_video.duration)
            final_video = final_video.set_audio(audio)
            final_video.write_videofile(
                "ranking_video.mp4", fps=24, codec='libx264')
            audio.close()  # Close the AudioFileClip before deleting the temporary file
        else:
            final_video.write_videofile(
                "ranking_video.mp4", fps=24, codec='libx264')
    except Exception as e:
        print(
            f"Error occurred while processing the final video or writing it to a file: {e}")
        raise e

    try:
        delete_media_files(len(ranking_list), len(media_queries))
    except Exception as e:
        print(f"Error occurred while deleting media files: {e}")
        raise e
