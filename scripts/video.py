from moviepy.editor import (concatenate_videoclips, TextClip, CompositeVideoClip,
                            AudioFileClip, ImageClip, CompositeAudioClip)
from av import AVError
from scripts.utils import *
import cv2
import os
import shutil
from pydub import AudioSegment
import soundfile as sf
import librosa
import numpy as np
from moviepy.audio.AudioClip import AudioArrayClip
import numpy as np






def create_title_card_variant0(title_element, title_topic, duration=3.90, bg_video=None, title_media_file_paths=None, title_flag_paths = None, voice_over = 'No'):
    canvas_clip = TextClip(f" ", fontsize=90, font="Calibri-Bold",
                           color='White', size=(1080, 1920), stroke_color='black', stroke_width=4, transparent=True)
    canvas_clip = canvas_clip.set_duration(duration)
    element_clip = TextClip(wrap_text(title_element, 18), fontsize=font_size(190, len(title_element.split())+2), font="Calibri-Bold",
                            color='Firebrick', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=2)
    element_clip = element_clip.set_position(
        ('center', -700)).set_duration(duration)
    shadow_clip = TextClip(wrap_text(f'{title_topic}', 16), fontsize=font_size(240, len(title_topic.split()) + 3), font="Calibri-Bold",
                          color='Black', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=3)
    topic_clip = TextClip(wrap_text(f'{title_topic}', 16), fontsize=font_size(240, len(title_topic.split()) + 3), font="Calibri-Bold",
                          color='YellowGreen', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=3)
    # topic_clip = topic_clip.set_position(
    #     ('center', -300)).set_duration(duration)
    W = 1080  # width
    H = 1920   # height
    amplitude_topic_hor = W/30  # maximum distance to the left or right of center
    frequency_topic_hor = 0.25  # number of full oscillations per second
    amplitude_topic_ver = H/70  # maximum distance to the up or down of center
    frequency_topic_ver = 0.20  # number of full oscillations per second

    # t: time in seconds
    # np.sin(2 * np.pi * frequency * t) oscillates between -1 and 1
    # amplitude * np.sin(2 * np.pi * frequency * t) oscillates between -amplitude and amplitude
    # adding W/2 (the center) moves the oscillation to the center of the screen
    shadow_clip = shadow_clip.set_position(lambda t: (5+amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-295 + amplitude_topic_ver * np.sin(2 * np.pi * frequency_topic_ver * t)))).set_duration(duration) #Offset of 2 for Drop Shadow
    topic_clip = topic_clip.set_position(lambda t: (amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-300 + amplitude_topic_ver * np.sin(2 * np.pi * frequency_topic_ver * t)))).set_duration(duration)
    #topic_clip = topic_clip.resize(lambda t : 1+(amplitude * np.sin(2 * np.pi * frequency * t))*t)  # Size increases as time goes on
    

     # Create a list to hold all the ImageClips
    flag_clips = []
    each_shuffle_duration = duration/30.0
    time_left = duration
    if title_flag_paths is not None:
        while time_left > 0:
            for flag_path in title_flag_paths:
                # Create an ImageClip for each flag
                flag_clip = ImageClip(flag_path)
                # Resize and position the flag clip as needed
                flag_clip = flag_clip.resize(width=820, height=450)
                flag_clip = flag_clip.margin(left=10, right=10, bottom=10, top=10)
                flag_clip = flag_clip.set_position('center', 'center').set_duration(each_shuffle_duration)
                time_left -= each_shuffle_duration #subtracting each flags duration until we have neough for the whole clip
                #set position and duration of each clip
                #flag_clip = flag_clip.set_position(lambda t: (amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-300 + amplitude_topic_ver * np.sin(2 * np.pi * frequency_topic_ver * t)))).set_duration(each_shuffle_duration)
                # Add the flag clip to the list of flag clips
                flag_clips.append(flag_clip)

        # Create a single clip that contains all the flag clips in sequence
        flags_clip = concatenate_videoclips(flag_clips, method="compose")
        flags_clip = flags_clip.set_position(lambda t: (515 - 860/2 + amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (450 + amplitude_topic_ver * np.sin(2 * np.pi * frequency_topic_ver * t)))).set_duration(duration)
    
    # Set margins
    #topic_clip = topic_clip.margin(left=100, right=100, bottom=0, top=0)
    #element_clip = element_clip.margin(left=100, right=100, bottom=0, top=0)
    if bg_video is not None:
        bg_video = VideoFileClip(bg_video)
        bg_video = bg_video.resize(height=1920)
        # If the video is now wider than the canvas, crop it to the width of the canvas
        if bg_video.w > 540:
            bg_video = bg_video.crop(width=1080)
        bg_video = bg_video.set_duration(duration)


    # title_media_file_path = None
    if len(title_media_file_paths) == 1:
        media_clip = ImageClip(title_media_file_paths).set_duration(duration)
        # Resize the media clip as needed
        media_clip = media_clip.resize(height=580, width=1000)
        media_clip = media_clip.margin(left=10, right=10, bottom=10, top=10)

        # Position the media clip on the frame
        if media_clip is None:
            print(
                f"Failed to resize the media file: {title_media_file_paths}")
        else:
            amplitude_media_hor = -50#-W/15  # maximum distance to the left or right of center
            frequency_media_hor = 0.4  # number of full oscillations per second
            amplitude_media_ver = -20#-H/80  # maximum distance to the up or down of center
            frequency_media_ver = 0.3  # number of full oscillations per second
            if media_clip.w is not None:
                media_clip = media_clip.set_position(lambda t: ((540 - media_clip.w/2)  + amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (1000 + amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)  
        
        if bg_video is not None:
            if flags_clip is not None:
                title_card = CompositeVideoClip(
                    [canvas_clip, bg_video, media_clip, element_clip,flags_clip, shadow_clip, topic_clip])
            else:
                title_card = CompositeVideoClip(
                    [canvas_clip, bg_video, media_clip, element_clip,shadow_clip, topic_clip])
        else:
            title_card = CompositeVideoClip(
                [canvas_clip, media_clip, element_clip, shadow_clip, topic_clip])
    else:
        if bg_video is not None:
            if flags_clip is not None:
                title_card = CompositeVideoClip(
                    [canvas_clip, bg_video, element_clip, flags_clip, shadow_clip, topic_clip])
            else:
                title_card = CompositeVideoClip(
                    [canvas_clip, bg_video, element_clip, shadow_clip, topic_clip])
        else:
            title_card = CompositeVideoClip(
                [canvas_clip, element_clip, shadow_clip, topic_clip])
    
            
    # Text-To-Speech
    if voice_over == "Yes":
        audio_file_path = f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\title_topic_{title_topic}.mp3'
        azure_speak_text(f'Can you guess Top 10 {title_topic}?', duration, audio_file_path)
        if os.path.exists(audio_file_path):
            #print("Debug: File path exists:", audio_file_path)
            final_audio = AudioFileClip(audio_file_path).volumex(1.0)
            title_card = title_card.set_audio(final_audio)
        else:
            print("Debug: File path does not exist:", audio_file_path)
        os.remove(audio_file_path)
    return title_card


def create_counrty_ranking_frame(rank, country, why, what,topic, duration=2.80, bg_video=None, media_file_paths=None, voice_over = 'No'):
    canvas_clip = TextClip(f" ", fontsize=130, font="Calibri-Bold",
                           color='White', size=(1080, 1920), stroke_color='black', stroke_width=9, transparent=True)
    topic_clip = TextClip(wrap_text(f"{topic}", 24), fontsize=60, font="Calibri-Bold",
                        color='White', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=0)
    txt_clip = TextClip(wrap_text(f"#{rank}: {country}", 16), fontsize=font_size(150, len(country.split())+1 ), font="Calibri-Bold",
                        color='YellowGreen', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    shadow_clip = TextClip(wrap_text(f"#{rank}: {country}", 16), fontsize=font_size(150, len(country.split())+1 ), font="Calibri-Bold",
                          color='Black', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    why_clip = TextClip(wrap_text(f"{why}", 16), fontsize=font_size(110, len(why.split())), font="Calibri-Bold",
                        color='white', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    what_clip = TextClip(wrap_text(f"{what}", 16), fontsize=font_size(110, len(what.split())), font="Calibri-Bold",
                         color='Orange', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    

    W = 1080  # width
    H = 1920   # height
    multiplier = 1
    if rank%2 == 0: #Alternating between each rank whether animation starts to left or right, up or down
        multiplier = -1
    amplitude_flag_hor = multiplier * -20  #-W/15  # maximum distance to the left or right of center
    frequency_flag_hor = 0.3  # number of full oscillations per second
    amplitude_flag_ver = multiplier * -10#-H/80  # maximum distance to the up or down of center
    frequency_flag_ver = 0.1  # number of full oscillations per second

    # t: time in seconds
    # np.sin(2 * np.pi * frequency * t) oscillates between -1 and 1
    # amplitude * np.sin(2 * np.pi * frequency * t) oscillates between -amplitude and amplitude
    # adding W/2 (the center) moves the oscillation to the center of the screen
    txt_clip = txt_clip.set_position(lambda t: (amplitude_flag_hor * np.sin(2 * np.pi * frequency_flag_hor * t), (-560 + amplitude_flag_ver * np.sin(2 * np.pi * frequency_flag_ver * t)))).set_duration(duration)
    shadow_clip = shadow_clip.set_position(lambda t: (5 + amplitude_flag_hor * np.sin(2 * np.pi * frequency_flag_hor * t), (-555 + amplitude_flag_ver * np.sin(2 * np.pi * frequency_flag_ver * t)))).set_duration(duration)




    canvas_clip = canvas_clip.set_duration(duration)
    topic_clip = topic_clip.set_position(('center', -825)).set_duration(duration)
    topic_clip = topic_clip.set_opacity(0.5)
    what_clip = what_clip.set_position(('center', 450)).set_duration(duration)
    why_clip = why_clip.set_position(('center',650)).set_duration(duration)




    if bg_video is not None:
        bg_video = VideoFileClip(bg_video)
        bg_video = bg_video.resize(height=1920)
        # If the video is now wider than the canvas, crop it to the width of the canvas
        if bg_video.w > 540:
            bg_video = bg_video.crop(width=1080)
        bg_video = bg_video.set_duration(duration)


    if media_file_paths is not None:
        media_clips = []
        for media_file_path in media_file_paths:
            if media_file_path is None:
                media_file_path = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\img\image_missing.png'
            try:
                media_clip = ImageClip(media_file_path).set_duration(duration)
                media_clip = media_clip.resize(width=720)

                media_clip = media_clip.margin(
                    left=10, right=10, bottom=10, top=10)

                # Position the media clip on the frame
                if media_clip is None:
                    print(
                        f"Failed to resize the media file: {media_file_path}")
                else:
                    W = 1080  # width
                    H = 1920   # height

                    amplitude_media_hor = multiplier * 20#W/15  # maximum distance to the left or right of center
                    frequency_media_hor = 0.2  # number of full oscillations per second
                    amplitude_media_ver = multiplier * 10#H/80  # maximum distance to the up or down of center
                    frequency_media_ver = 0.1  # number of full oscillations per second


                    if len(media_clips) == 0:
                        # This is the first image
                        if media_clip.h is not None:
                            media_clip = media_clip.set_position(lambda t: ((540 - media_clip.size[0] / 2)  + amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (850 + amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)
                            #media_clip = media_clip.set_position(("center", 850))
                        else:
                            media_clip = media_clip.set_position(lambda t: ((540 - media_clip.size[0] / 2)  + amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)
                            #media_clip = media_clip.set_position("center")
                    # For the flag image (second image)
                    else:
                        # media_clip = media_clip.set_position(
                        #     ("center", 1920 - media_clip.h - 1150))
                        media_clip = media_clip.set_position(lambda t: ((540 - media_clip.size[0] / 2)  + amplitude_flag_hor * np.sin(2 * np.pi * frequency_flag_hor * t), (640 - media_clip.h + amplitude_flag_ver * np.sin(2 * np.pi * frequency_flag_ver * t)))).set_duration(duration)


                media_clips.append(media_clip)

            except AVError:
                print(f"Error processing the media file: {media_file_path}")
                media_clips.append(None)

        if bg_video is not None:
            clip = CompositeVideoClip(
                [canvas_clip, bg_video] + media_clips + [topic_clip, shadow_clip, txt_clip, why_clip, what_clip])
        else:
            clip = CompositeVideoClip(
                [canvas_clip] + media_clips + [topic_clip, shadow_clip, txt_clip, why_clip, what_clip])
    else:
        if bg_video is not None:
            clip = CompositeVideoClip(
                [canvas_clip, bg_video, topic_clip, shadow_clip, txt_clip, why_clip, what_clip])
        else:
            clip = CompositeVideoClip(
                [canvas_clip, topic_clip, shadow_clip, txt_clip, why_clip, what_clip])
            
    # Text-To-Speech
    if voice_over == "Yes":
        audio_file_path = f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\rank_country_{topic}_{rank}.mp3'
        azure_speak_text(f"#{rank} {country}", duration, audio_file_path)
        if os.path.exists(audio_file_path):
            #print("Debug: File path exists:", audio_file_path)
            final_audio = AudioFileClip(audio_file_path).volumex(1.0)
            clip = clip.set_audio(final_audio)
        else:
            print("Debug: File path does not exist:", audio_file_path)
        os.remove(audio_file_path)
    return clip

def create_country_video(ranking_list, topic, include_flag, thread_id, title_duration, frame_duration, include_bg_videos=True, elements='Countries', 
                         bg_videos=None, bg_music=None, two_parts="No", voice_over="No"):
    clips = []
    title_media_file_path = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_title.jpg"
    new_title_media_file_path = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_title_{thread_id}.jpg"
    shutil.copy2(title_media_file_path, new_title_media_file_path)
    title_flag_paths = []

    # Rename all media files upfront
    for j in range(len(ranking_list)):
        try:
            if include_flag == 'Yes':
                media_file_path0 = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_{j}_0.jpg"
                media_file_path1 = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_{j}_1.jpg"

                # Copy the files with a new name so each thread can have their own
                new_media_file_path0 = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_{thread_id}_{j}_0.jpg"
                new_media_file_path1 = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_{thread_id}_{j}_1.jpg"
                
                shutil.copy2(media_file_path0, new_media_file_path0)
                shutil.copy2(media_file_path1, new_media_file_path1)
                title_flag_paths.append(new_media_file_path1) #Flags
            else:
                media_file_path0 = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_{j}_0.jpg"
                
                # Rename the media file using os.rename
                new_media_file_path0 = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_{thread_id}_{j}_0.jpg"
                shutil.copy(media_file_path0, new_media_file_path0)
        except Exception as e:
            print(f"Error occurred while renaming the media files: {e}")
            raise e
        
    if two_parts == "Yes":
        ranking_lists = [ranking_list[:5], ranking_list[5:10]]  # Split the list into two parts
    else:
        ranking_lists = [ranking_list[:10]]  # Keep the list as it is

    j = 0
    for part, ranking_list in enumerate(ranking_lists, start=1): 
        media_file_counter = 0
        clips = []
        # Title card
        title_element = f""
        title_topic = topic
        if two_parts == "Yes":
            title_topic = f"{topic} Part {part}"  # Add part number to title if two_parts
        if bg_videos:
            bg_video = bg_videos[j % len(bg_videos)]
        else:
            bg_video = None


        try:
            title_card = create_title_card_variant0(
                title_element, title_topic, duration=title_duration, bg_video=bg_video, title_media_file_paths=new_title_media_file_path, title_flag_paths=title_flag_paths, voice_over = voice_over)
            if title_card is not None:
                clips.append(title_card)
        except Exception as e:
            print(f"Error occurred while creating the title card: {e}")
            raise e

        # Rest
        for i in range(len(ranking_list), 0, -1):
            try:
                media_file_paths = []
                if include_flag == 'Yes':
                    # Get the new media file paths
                    new_media_file_path0 = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_{thread_id}_{j}_0.jpg"
                    new_media_file_path1 = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_{thread_id}_{j}_1.jpg"

                    media_file_paths.append(new_media_file_path0)
                    media_file_paths.append(new_media_file_path1)
                else:
                    # Get the new media file path
                    new_media_file_path0 = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_{thread_id}_{j}_0.jpg"

                    media_file_paths.append(new_media_file_path0)
            except Exception as e:
                print(f"Error occurred while processing the media queries: {e}")
                raise e

            try:
                if include_bg_videos and bg_videos:  # include_bg_videos flag added here
                    bg_video = bg_videos[(j + 1) % len(bg_videos)]
                else:
                    bg_video = None  # Set bg_video to None when include_bg_videos is False
                rank_offset = 0 #If only one part, offset is 0, other wise offset calculated differently for each part.
                if two_parts == "Yes":
                    rank_offset = (part-2) * 5
                ranking_frame = create_counrty_ranking_frame(
                    i - rank_offset, ranking_list[media_file_counter][0][0], ranking_list[media_file_counter][1][0], ranking_list[media_file_counter][2][0],
                    topic = topic,duration=frame_duration ,bg_video=bg_video, media_file_paths=media_file_paths, voice_over = voice_over)

                if ranking_frame is not None:
                    ranking_frame = ranking_frame.set_fps(24)  # set fps to 24
                clips.append(ranking_frame)
                j += 1
                media_file_counter += 1

            except Exception as e:
                print(f"Error occurred while creating ranking frames: {e}")
                raise e

        try:
            final_video = concatenate_videoclips(clips)
        except Exception as e:
            print(f"Error occurred while concatenating video clips: {e}")
            raise e

        # Save the video after each part
        try:
            output_dir = "C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\generated_videos\\"

            if bg_music is not None:
                bg_music_audio = AudioFileClip(bg_music).volumex(0.2 * 1.5).set_duration(final_video.duration)  # increased volume
                final_video_audio = final_video.audio.volumex(1.5)  # increased volume
                final_audio = CompositeAudioClip([final_video_audio, bg_music_audio])
                final_video = final_video.set_audio(final_audio)


            final_video.write_videofile(
                f"{output_dir}{'_'.join(topic.split())}_part{part}.mp4", fps=24, codec='libx264')

        except Exception as e:
            print(f"Error occurred while processing the final video or writing it to a file: {e}")
            raise e
    delete_media_files(min(10, len(ranking_list)), 2 if include_flag == 'Yes' else 1, thread_id)
    return None
    