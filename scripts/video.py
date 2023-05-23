from moviepy.editor import (concatenate_videoclips, TextClip, CompositeVideoClip,
                            AudioFileClip, ImageClip)
from av import AVError
from scripts.custom_google_search import CustomGoogleSearchAPIWrapper
import streamlit as st
from scripts.utils import *
from moviepy.video.fx.all import margin, resize, crop


def create_title_card_variant0(title_text, duration=5, bg_video=None):
    canvas_clip = TextClip(f" ", fontsize=45, font="Arial-Bold",
                           color='White', size=(540, 960), stroke_color='black', stroke_width=2, transparent=True)
    canvas_clip = canvas_clip.set_duration(duration)
    title_clip = TextClip(title_text, fontsize=45, font="Arial-Bold",
                          color='YellowGreen', size=(540, 960), method='caption', align='center', stroke_color='black', stroke_width=2)
    title_clip = title_clip.set_position(
        ('center')).set_duration(duration)
    # title_clip = title_clip.margin(left=50, right=50, bottom=20, top=20)

    if bg_video is not None:
        # Fit the video to the height of the canvas
        bg_video = bg_video.fx(resize, height=960)
        # If the video is now wider than the canvas, crop it to the width of the canvas
        if bg_video.w > 540:
            bg_video = bg_video.fx(crop, width=540)

        bg_video = bg_video.set_duration(duration)
        title_card = CompositeVideoClip([canvas_clip, bg_video, title_clip])
    else:
        title_card = CompositeVideoClip([canvas_clip, title_clip])

    return title_card

# def create_title_card_variant1(title_text, duration=4, bg_video=None):
#     title_clip = TextClip(title_text, fontsize=70, font="Amiri-Bold",
#                           color='Red', size=(540, 960), method='caption', align='center',
#                           stroke_color='black', stroke_width=3)
#     title_clip = title_clip.set_duration(duration)
#     title_clip = title_clip.margin(left=20, right=20, top=20, bottom=20)

#     if bg_video is not None:
#         bg_video = bg_video.resize(height=960, width=540)
#         bg_video = bg_video.set_duration(duration)
#         title_card = CompositeVideoClip([bg_video, title_clip.set_pos('center')])
#     else:
#         title_card = title_clip

#     return title_card

# def create_title_card_variant2(title_text, duration=4, bg_video=None):
#     title_clip = TextClip(title_text, fontsize=60, font="Courier-Bold",
#                           color='white', size=(540, 960), method='caption', align='west',
#                           stroke_color='black', stroke_width=3)
#     title_clip = title_clip.set_duration(duration)
#     title_clip = title_clip.margin(left=50, right=50, bottom=20, top=200)

#     if bg_video is not None:
#         bg_video = bg_video.resize(height=960, width=540)
#         bg_video = bg_video.set_duration(duration)
#         title_card = CompositeVideoClip([bg_video, title_clip.set_pos(('center', 'bottom'))])
#     else:
#         title_card = title_clip

#     return title_card


def create_ranking_frame(rank, country, why, what, duration=2.5, bg_video=None, media_file_path=None):
    canvas_clip = TextClip(f" ", fontsize=45, font="Arial-Bold",
                           color='White', size=(540, 960), stroke_color='black', stroke_width=2, transparent=True)
    # canvas_clip = canvas_clip.margin(left=50, right=50, bottom=20, top=20)
    txt_clip = TextClip(f"Rank {rank}: {country}", fontsize=45, font="Arial-Bold",
                        color='YellowGreen', size=(540, 960), method='caption', align='center', stroke_color='black', stroke_width=2)
    why_clip = TextClip(f"{why}", fontsize=35, font="Arial-Bold",
                        color='white', size=(540, 960), method='caption', align='center', stroke_color='black', stroke_width=2)
    what_clip = TextClip(f"{what}", fontsize=35, font="Arial-Bold",
                         color='white', size=(540, 960), method='caption', align='center', stroke_color='black', stroke_width=2)

    canvas_clip = canvas_clip.set_duration(duration)
    txt_clip = txt_clip.set_position(('center', 50)).set_duration(duration)
    why_clip = why_clip.set_position(('center', 250)).set_duration(duration)
    what_clip = what_clip.set_position(('center', 300)).set_duration(duration)

    if bg_video is not None:
        # Fit the video to the height of the canvas
        bg_video = bg_video.fx(resize, height=960)
        # If the video is now wider than the canvas, crop it to the width of the canvas
        if bg_video.w > 540:
            bg_video = bg_video.fx(crop, width=540)

        bg_video = bg_video.set_duration(duration)

    if media_file_path is not None:
        try:
            media_clip = ImageClip(media_file_path).set_duration(duration)
            # Resize the media clip as needed
            media_clip = media_clip.resize(height=300)
            # Position the media clip on the frame
            if media_clip is None:
                print(f"Failed to resize the media file: {media_file_path}")
            else:
                if media_clip.h is not None:
                    media_clip = media_clip.set_position(
                        ("center", 960 - media_clip.h - 550))
                else:
                    media_clip = media_clip.set_position("center")

        except AVError:
            print(f"Error processing the media file: {media_file_path}")
            media_clip = None

        if bg_video is not None:
            clip = CompositeVideoClip(
                [canvas_clip, bg_video, media_clip, txt_clip, why_clip, what_clip])
        else:
            clip = CompositeVideoClip(
                [canvas_clip, media_clip, txt_clip, why_clip, what_clip])
    else:
        if bg_video is not None:
            clip = CompositeVideoClip(
                [canvas_clip, bg_video, txt_clip, why_clip, what_clip])
        else:
            clip = CompositeVideoClip(
                [canvas_clip, txt_clip, why_clip, what_clip])

    return clip


def create_video(ranking_list, topic, bg_videos=None, bg_music=None):
    try:
        clips = []
        j = 0
        # Title card
        title_text = f"Top 10 Countries: {topic}"
        if bg_videos is not None:
            bg_video = bg_videos[j % len(bg_videos)] if bg_videos else None
        else:
            bg_video = None

        title_card = create_title_card_variant0(title_text, bg_video=bg_video)
        if title_card is not None:
            clips.append(title_card)
        google_search = CustomGoogleSearchAPIWrapper()
        with st.expander("Click to expand google image search queries"):
            j = 0
            for i in range(len(ranking_list), 0, -1):
                media_query = f"{ranking_list[j][3][0]}"
                st.write(media_query)
                media_results = google_search.search_media(
                    media_query, num_results=3)
                # pic from top 3 results
                media_file_path = f"media_{j}.jpg"
                image_downloaded = False

                for media in media_results[:3]:
                    media_url = media["link"]
                    if not image_downloaded:
                        image_downloaded = download_image(
                            media_url, media_file_path)
                        # Check if the image is readable
                        if image_downloaded and is_image_readable(media_file_path):
                            break
                    else:
                        image_downloaded = False

                if not image_downloaded:
                    media_file_path = None  # Skip using the image if the download fails

                if bg_videos is None:
                    bg_video = None
                else:
                    bg_video = bg_videos[(j %
                                         len(bg_videos))+1] if bg_videos else None
                ranking_frame = create_ranking_frame(
                    i, ranking_list[j][0][0], ranking_list[j][1][0], ranking_list[j][2][0],
                    bg_video=bg_video, media_file_path=media_file_path)

                if ranking_frame is not None:
                    ranking_frame = ranking_frame.set_duration(
                        ranking_frame.duration).set_fps(24)  # set fps to 24
                clips.append(ranking_frame)
                j += 1
        final_video = concatenate_videoclips(clips)

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

        delete_media_files(len(ranking_list))
    except Exception as e:
        # Debug statement 3
        print(f"Debug: Error occurred while generating video: {e}")
        raise
