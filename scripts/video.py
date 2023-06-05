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
        bg_video = VideoFileClip(bg_video)
        bg_video = bg_video.resize(height=1920)
        # If the video is now wider than the canvas, crop it to the width of the canvas
        if bg_video.w > 540:
            bg_video = bg_video.crop(width=1080)
        bg_video = bg_video.set_duration(duration)

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


def create_counrty_ranking_frame(rank, country, why, what, duration=2.80, bg_video=None, media_file_paths=None):
    canvas_clip = TextClip(f" ", fontsize=130, font="Calibri-Bold",
                           color='White', size=(1080, 1920), stroke_color='black', stroke_width=9, transparent=True)
    txt_clip = TextClip(f"#{rank}: {country}", fontsize=150, font="Calibri-Bold",
                        color='YellowGreen', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    why_clip = TextClip(f"{why}", fontsize=130, font="Calibri-Bold",
                        color='white', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    what_clip = TextClip(f"{what}", fontsize=130, font="Calibri-Bold",
                         color='Orange', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)

    canvas_clip = canvas_clip.set_duration(duration)
    txt_clip = txt_clip.set_position(('center', -600)).set_duration(duration)
    why_clip = why_clip.set_position(('center', 450)).set_duration(duration)
    what_clip = what_clip.set_position(('center',650)).set_duration(duration)

    # Add Fade-in Effect
    # txt_clip = fadein_clip(txt_clip, 0.25) # 1 second fade-in
    # why_clip = fadein_clip(why_clip, 0.25)
    # what_clip = fadein_clip(what_clip, 0.25)

    if bg_video is not None:
        bg_video = VideoFileClip(bg_video)
        bg_video = bg_video.resize(height=1920)
        # If the video is now wider than the canvas, crop it to the width of the canvas
        if bg_video.w > 540:
            bg_video = bg_video.crop(width=1080)
        bg_video = bg_video.set_duration(duration)
        # Apply Shake
        # bg_video = apply_shake_for_duration(bg_video, 1)

    if media_file_paths is not None:
        media_clips = []
        for media_file_path in media_file_paths:
            if media_file_path is None:
                media_file_path = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\img\image_missing.png'
            try:
                media_clip = ImageClip(media_file_path).set_duration(duration)
                # Resize the media clip as needed
                # Convert the image to RGB
                # media_clip = media_clip.fl_image(convert_frame_to_rgb)
                media_clip = media_clip.resize(height=500)

                media_clip = media_clip.margin(
                    left=10, right=10, bottom=10, top=10)

                # Position the media clip on the frame
                if media_clip is None:
                    print(
                        f"Failed to resize the media file: {media_file_path}")
                else:
                    # Add Fade-in for media
                    # media_clip =fadein_clip(media_clip, 0.25)
                    # For the first image, place it in the center bottom
                    if len(media_clips) == 0:
                        # This is the first image
                        if media_clip.h is not None:
                            media_clip = media_clip.set_position(
                                ("center", 850))
                        else:
                            media_clip = media_clip.set_position("center")
                    # For the flag image (second image)
                    else:
                        media_clip = media_clip.set_position(
                            ("center", 1920 - media_clip.h - 1200))

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


def create_country_video(ranking_list, topic, include_flag, include_bg_videos=True, elements='Countries', bg_videos=None, bg_music=None, title_media_query='usa flag'):
    clips = []
    j = 0
    # Title card
    title_element = f""
    title_topic = f"{topic}"
    if bg_videos:
        bg_video = bg_videos[j % len(bg_videos)]
    else:
        bg_video = None

    title_media_file_path = f"media_title.jpg"

    try:
        title_card = create_title_card_variant0(
            title_element, title_topic, bg_video=bg_video, title_media_file_path=title_media_file_path)
        if title_card is not None:
            clips.append(title_card)
    except Exception as e:
        print(f"Error occurred while creating the title card: {e}")
        raise e

    # Rest
    j = 0
    for i in range(min(10, len(ranking_list)), 0, -1):
        try:
            media_file_paths = []
            if include_flag == 'Yes':
                media_file_path0 = f"media_{j}_0.jpg"
                media_file_path1 = f"media_{j}_1.jpg"
                media_file_paths.append(media_file_path0)
                media_file_paths.append(media_file_path1)
            else:
                media_file_path0 = f"media_{j}_0.jpg"
                media_file_paths.append(media_file_path0)
        except Exception as e:
            print(
                f"Error occurred while processing the media queries: {e}")
            raise e

        try:
            if include_bg_videos and bg_videos:  # include_bg_videos flag added here
                bg_video = bg_videos[(j + 1) % len(bg_videos)]
            else:
                bg_video = None  # Set bg_video to None when include_bg_videos is False
            ranking_frame = create_counrty_ranking_frame(
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
