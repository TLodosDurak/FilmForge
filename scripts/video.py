from moviepy.editor import (concatenate_videoclips, TextClip, CompositeVideoClip,
                            AudioFileClip, ImageClip, CompositeAudioClip, ColorClip)
from moviepy.audio.AudioClip import concatenate_audioclips
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
from around_world import generate_map
from src.videos.default_pexel_bg import get_bg, get_whoosh, get_shuffle, get_all_whoosh, get_all_audioclips
from PIL import Image




fadein_time = 0.5  # duration of the fade-in in seconds
transparent_image = np.zeros((1920, 1080, 4), dtype=np.uint8)

def create_title_card_variant0(title_element, title_topic, duration=3.90, thread_id=None, bg_video=None, title_media_file_paths=None, title_flag_paths = None, voice_over = 'No', custom_thumbnail = 'No'):
    # Convert the NumPy array to an ImageClip
    canvas_clip = ImageClip(transparent_image)
    canvas_clip = canvas_clip.set_duration(duration)
    element_clip = TextClip(wrap_text(title_element, 10), fontsize=font_size(290, len(title_element.split())+2), font="Calibri-Bold",
                            color='Firebrick', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=2)
    element_clip_shadow = TextClip(wrap_text(title_element, 10), fontsize=font_size(290, len(title_element.split())+2), font="Calibri-Bold",
                            color='Black', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=2)
    shadow_clip = TextClip(wrap_text(f'{title_topic}', 16), fontsize=font_size(240, len(title_topic.split()) + 3), font="Calibri-Bold",
                          color='Black', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=3)
    topic_clip = TextClip(wrap_text(f'{title_topic}', 16), fontsize=font_size(240, len(title_topic.split()) + 3), font="Calibri-Bold",
                          color='YellowGreen', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=3)



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
    shadow_clip = shadow_clip.set_position(lambda t: (5+amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-405 + amplitude_topic_ver * np.sin(2 * np.pi * frequency_topic_ver * t)))).set_duration(duration) #Offset of 2 for Drop Shadow
    topic_clip = topic_clip.set_position(lambda t: (amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-410 + amplitude_topic_ver * np.sin(2 * np.pi * frequency_topic_ver * t)))).set_duration(duration)
    element_clip = element_clip.set_position(lambda t: (amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-800))).set_duration(duration)
    element_clip_shadow = element_clip_shadow.set_position(lambda t: (5+amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-795))).set_duration(duration)
    # shadow_clip = shadow_clip.crossfadein(fadein_time)
    # topic_clip = topic_clip.crossfadein(fadein_time)
    # element_clip = element_clip.crossfadein(fadein_time) 
    # element_clip_shadow = element_clip_shadow.crossfadein(fadein_time)




     # Create a list to hold all the ImageClips
    flag_clips = []
    each_shuffle_duration = duration/30.0
    time_left = duration
    if title_flag_paths is not None:
        while time_left > 0:
            for flag_path in title_flag_paths:
                # Open the image using PIL
                img = Image.open(flag_path)
                # Resize the image, ignoring original aspect ratio
                img_resized = img.resize((820, 450))
                # Convert the image back to a MoviePy clip
                flag_clip = ImageClip(np.array(img_resized))
                flag_clip = flag_clip.margin(left=10, right=10, bottom=10, top=10)
                flag_clip = flag_clip.set_position('center', 'center').set_duration(each_shuffle_duration)
                time_left -= each_shuffle_duration #subtracting each flags duration until we have neough for the whole clip
                #set position and duration of each clip
                #flag_clip = flag_clip.set_position(lambda t: (amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-300 + amplitude_topic_ver * np.sin(2 * np.pi * frequency_topic_ver * t)))).set_duration(each_shuffle_duration)
                # Add the flag clip to the list of flag clips
                flag_clips.append(flag_clip)

        # Create a single clip that contains all the flag clips in sequence
        flags_clip = concatenate_videoclips(flag_clips, method="compose")
        flags_clip = flags_clip.set_position(lambda t: (540 - flag_clip.w/2 + amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (340 + amplitude_topic_ver * np.sin(2 * np.pi * frequency_topic_ver * t)))).set_duration(duration)
        #flags_clip = flags_clip.crossfadein(fadein_time)

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
    bg_video = None #Remove Later
    amplitude_media_hor = -50#-W/15  # maximum distance to the left or right of center
    frequency_media_hor = 0.4  # number of full oscillations per second
    amplitude_media_ver = -20#-H/80  # maximum distance to the up or down of center
    frequency_media_ver = 0.3  # number of full oscillations per second
    # title_media_file_path = None

    if len(title_media_file_paths) == 1:
        # Open the image using PIL
        img = Image.open(title_media_file_paths)
        # Resize the image, ignoring original aspect ratio
        img_resized = img.resize((1000, 580))
        # Convert the image back to a MoviePy clip
        media_clip = ImageClip(np.array(img_resized)).set_duration(duration)
        media_clip = media_clip.margin(left=10, right=10, bottom=10, top=10)

        # Position the media clip on the frame
        if media_clip is None:
            print(
                f"Failed to resize the media file: {title_media_file_paths}")
        else:
            if media_clip.w is not None:
                media_clip = media_clip.set_position(lambda t: ((280 - media_clip.w/2)  + amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (1400 - media_clip.size[1]/2 + amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)  
                #media_clip = media_clip.crossfadein(fadein_time)
    else:
        media_clips = []
        each_shuffle_duration = duration/30.0
        time_left = duration
        while time_left > 0:
            for title_media_path in title_media_file_paths:
                # Open the image using PIL
                img = Image.open(title_media_path)
                # Resize the image, ignoring original aspect ratio
                img_resized = img.resize((1000, 580))
                # Convert the image back to a MoviePy clip
                media_clip = ImageClip(np.array(img_resized))
                media_clip = media_clip.margin(left=10, right=10, bottom=10, top=10)
                media_clip = media_clip.set_position('center', 'center').set_duration(each_shuffle_duration)
                time_left -= each_shuffle_duration #subtracting each flags duration until we have neough for the whole clip
                # Add the flag clip to the list of media clips
                media_clips.append(media_clip)
            

        # Create a single clip that contains all the medias clips in sequence
        final_media_clip = concatenate_videoclips(media_clips, method="compose")
        final_media_clip = final_media_clip.set_position(lambda t: ((540 - media_clip.w/2)  + amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (1000 + amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)  
        #final_media_clip = final_media_clip.crossfadein(fadein_time)

    if bg_video is not None:
        if flags_clip is not None:
            title_card = CompositeVideoClip(
                [canvas_clip, bg_video, final_media_clip, flags_clip, shadow_clip, topic_clip, element_clip_shadow, element_clip])
        else:
            title_card = CompositeVideoClip(
                [canvas_clip, bg_video, final_media_clip, shadow_clip, topic_clip, element_clip_shadow, element_clip,])
    else:
        if flags_clip is not None:
            title_card = CompositeVideoClip(
                [canvas_clip, final_media_clip, flags_clip, shadow_clip, topic_clip, element_clip_shadow, element_clip])
        else:
            title_card = CompositeVideoClip(
                [canvas_clip, final_media_clip, shadow_clip, topic_clip, element_clip_shadow, element_clip])
    # #whoosh sound
    # shuffle_sound_paths = get_all_whoosh()
    # shuffle_audio_clips = get_all_audioclips(shuffle_sound_paths)
    # shuffle_audio = concatenate_audioclips(shuffle_audio_clips).volumex(1.0 * 0.3)
    # Add these lines before you create the final clip
    # from math import ceil
    # # Calculate how many times we need to loop the sound to cover the video duration
    # loop_times = ceil(duration / shuffle_audio.duration)

    # # Create a list of the audio clip repeated necessary times
    # audio_clips_list = [shuffle_audio] * loop_times

    # # Create a single audio clip that loops the sound
    # looped_shuffle_sound = concatenate_audioclips(audio_clips_list)
     
    # Text-To-Speech
    audio_file_path = f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp_audio\\title_topic_{title_topic}_{thread_id}.mp3'
    if voice_over == "Yes":
        text_str = f'Top 10 {title_topic}' #Can you guess ?
        azure_speak_text(text_str, duration, audio_file_path)
        if os.path.exists(audio_file_path):
            tts_audio = AudioFileClip(audio_file_path).volumex(1.0)
            #final_audio = CompositeAudioClip([looped_shuffle_sound, tts_audio])
            title_card = title_card.set_audio(tts_audio)
        else:
            print("Debug: File path does not exist:", audio_file_path)
    #os.remove(audio_file_path)
    return title_card


def create_counrty_ranking_frame(rank, country, why, what,topic, thread_id=None, duration=2.80, bg_video=None, media_file_paths=None, voice_over = 'No'):
    canvas_clip = ImageClip(transparent_image)
    topic_clip = TextClip(wrap_text(f"{topic}", 24), fontsize=60, font="Calibri-Bold",
                        color='White', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=0)
    txt_clip = TextClip(wrap_text(f"#{rank}: {country}", 16), fontsize=font_size(150, len(country.split())+1 ), font="Calibri-Bold",
                        color='YellowGreen', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    shadow_clip = TextClip(wrap_text(f"#{rank}: {country}", 16), fontsize=font_size(150, len(country.split())+1 ), font="Calibri-Bold",
                          color='Black', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    # why_clip = TextClip(wrap_text(f"{why}", 16), fontsize=font_size(110, len(why.split())), font="Calibri-Bold",
    #                     color='white', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
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
    txt_clip = txt_clip.set_position(lambda t: (amplitude_flag_hor * np.sin(2 * np.pi * frequency_flag_hor * t), (-645 + amplitude_flag_ver * np.sin(2 * np.pi * frequency_flag_ver * t)))).set_duration(duration)
    shadow_clip = shadow_clip.set_position(lambda t: (5 + amplitude_flag_hor * np.sin(2 * np.pi * frequency_flag_hor * t), (-650 + amplitude_flag_ver * np.sin(2 * np.pi * frequency_flag_ver * t)))).set_duration(duration)
    txt_clip = txt_clip.crossfadein(fadein_time)
    shadow_clip = shadow_clip.crossfadein(fadein_time)




    canvas_clip = canvas_clip.set_duration(duration)
    topic_clip = topic_clip.set_position(('center', -825)).set_duration(duration)
    #topic_clip = topic_clip.set_opacity(0.5)
    #why_clip = why_clip.set_position(('center',650)).set_duration(duration)




    if bg_video is not None:
        bg_video = VideoFileClip(bg_video)
        bg_video = bg_video.resize(height=1920)
        # If the video is now wider than the canvas, crop it to the width of the canvas
        if bg_video.w > 540:
            bg_video = bg_video.crop(width=1080)
        bg_video = bg_video.set_duration(duration)
    bg_video = None #Remove Later if no map


    if media_file_paths is not None:
        media_clips = []
        for media_file_path in media_file_paths:
            if media_file_path is None:
                media_file_path = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\img\image_missing.png'
            try:
                W = 1080  # width
                H = 1920   # height

                amplitude_media_hor = multiplier * 20#W/15  # maximum distance to the left or right of center
                frequency_media_hor = 0.2  # number of full oscillations per second
                amplitude_media_ver = multiplier * 10#H/80  # maximum distance to the up or down of center
                frequency_media_ver = 0.1  # number of full oscillations per second
                what_clip = what_clip.set_position(lambda t: (amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (350 + amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)


                if len(media_clips) == 0:
                    # Open the image using PIL
                    img = Image.open(media_file_path)
                    # Resize the image, ignoring original aspect ratio
                    img_resized = img.resize((1000, 560))
                    # Convert the image back to a MoviePy clip
                    media_clip = ImageClip(np.array(img_resized)).set_duration(duration)
                    media_clip = media_clip.margin(
                        left=10, right=10, bottom=10, top=10)
                    # This is the first image
                    if media_clip.h is not None:
                        media_clip = media_clip.set_position(lambda t: ((540 - 1000 / 2)  + amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (1250 + amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)
                        #media_clip = media_clip.set_position(("center", 850))
                    else:
                        media_clip = media_clip.set_position(lambda t: ((540 - 1000 / 2)  + amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)
                        #media_clip = media_clip.set_position("center")
                # For the flag image (second image)
                else:
                    # media_clip = media_clip.set_position(
                    #     ("center", 1920 - media_clip.h - 1150))
                    W = 1080  # width
                    H = 1920   # height
                    amplitude_topic_hor = W/30  # maximum distance to the left or right of center
                    frequency_topic_hor = 0.25  # number of full oscillations per second
                    amplitude_topic_ver = H/70  # maximum distance to the up or down of center
                    frequency_topic_ver = 0.20  # number of full oscillations per second
                    #media_clip = media_clip.resize(width=820, height=450)
                    # Open the image using PIL
                    img = Image.open(media_file_path)
                    # Resize the image, ignoring original aspect ratio
                    img_resized = img.resize((720, 400))
                    # Convert the image back to a MoviePy clip
                    media_clip = ImageClip(np.array(img_resized)).set_duration(duration)
                    media_clip = media_clip.margin(
                        left=10, right=10, bottom=10, top=10)
                    media_clip = media_clip.set_position(lambda t: ((540 - media_clip.size[0] / 2) + amplitude_flag_hor * np.sin(2 * np.pi * frequency_flag_hor * t), (245 + amplitude_flag_ver * np.sin(2 * np.pi * frequency_flag_ver * t)))).set_duration(duration)

                media_clip = media_clip.crossfadein(fadein_time)
                media_clips.append(media_clip)

            except AVError:
                print(f"Error processing the media file: {media_file_path}")
                media_clips.append(None)

        if bg_video is not None:
            clip = CompositeVideoClip(
                [canvas_clip, bg_video] + media_clips + [topic_clip, shadow_clip, txt_clip, what_clip])
        else:
            clip = CompositeVideoClip(
                [canvas_clip] + media_clips + [topic_clip, shadow_clip, txt_clip, what_clip])
    else:
        if bg_video is not None:
            clip = CompositeVideoClip(
                [canvas_clip, bg_video, topic_clip, shadow_clip, txt_clip, what_clip])
        else:
            clip = CompositeVideoClip(
                [canvas_clip, topic_clip, shadow_clip, txt_clip, what_clip])
            
    #whoosh sound
    whoosh_sound_path = get_whoosh()
    whoosh_audio = AudioFileClip(whoosh_sound_path).volumex(1.0 * 0.1)

    # Text-To-Speech
    audio_file_path = f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp_audio\\rank_country_{topic}_{rank}_{thread_id}.mp3'
    if voice_over == "Yes" and False:
        text_str = f"#{rank}" #{country}
        if rank == 1:
            text_str = f"and #{rank}" #{country}
        azure_speak_text(text_str, duration, audio_file_path)
        if os.path.exists(audio_file_path):
            #print("Debug: File path exists:", audio_file_path)
            tts_audio = AudioFileClip(audio_file_path).volumex(1.0)
            final_audio = CompositeAudioClip([whoosh_audio, tts_audio]) 
            clip = clip.set_audio(final_audio)
        else:
            print("Debug: File path does not exist:", audio_file_path)
    else:
        clip = clip.set_audio(whoosh_audio)
    return clip

def outro_card(topic, duration=3, thread_id=None, title_flag_paths=None, voice_over='No'):
    # Define your initial empty clips
    clips = []

    # Create a canvas clip
    canvas_clip = ImageClip(transparent_image)
    canvas_clip = canvas_clip.set_duration(duration)
    clips.append(canvas_clip)

    # Define the topic clip
    topic_clip = TextClip(wrap_text(f"{topic}", 24), fontsize=60, font="Calibri-Bold",
                          color='White', size=(1080, 1920), method='caption', align='center', 
                          stroke_color='black', stroke_width=0)
    topic_clip = topic_clip.set_position(('center', -825)).set_duration(duration)
    clips.append(topic_clip)

    # Build a single string that includes all ranks, separated by line breaks
    rank_string = "#1 :\n#2 :\n#3 :\n#4 :\n#5 :\n#6 :\n#7 :\n#8 :\n#9 :\n#10:"

    # Create a single text clip for all ranks
    rank_text_clip = TextClip(rank_string, fontsize=120, font="Calibri-Bold",
                              color='YellowGreen', size=(1080, 1920),
                              method='caption', align='center',
                              stroke_color='black', stroke_width=4).set_position((-250, -100)).set_duration(duration)
    rank_text_clip = rank_text_clip.crossfadein(fadein_time)
    clips.append(rank_text_clip)

    y_index = 280
    # For each rank, create an image clip
    for rank in range(10):
        # Open, resize and convert the flag image to an ImageClip
        img_path = title_flag_paths[-1 * (rank+1)] # make sure your paths are ordered correctly
        img = Image.open(img_path).resize((100, 75))
        img_clip = ImageClip(np.array(img), duration=duration).set_position((400, y_index))
        y_index += 120
        img_clip = img_clip.crossfadein(fadein_time)

        # Append image clip to the clips list
        clips.append(img_clip)

    # Put everything into a single composite clip
    final_clip = CompositeVideoClip(clips, size=(1080, 1920)).set_duration(duration)

    # Define the audio for the clip
    whoosh_sound_path = get_whoosh()
    whoosh_audio = AudioFileClip(whoosh_sound_path).volumex(1.0 * 0.1)
    final_clip = final_clip.set_audio(whoosh_audio)

    return final_clip




def create_country_video(ranking_list, topic, include_flag, thread_id, title_duration, frame_duration, include_bg_videos=True, elements='Countries', 
                         bg_videos=None, bg_music=None, two_parts="No", voice_over="No", custom_thumbnail = "No"):
    frame_duration = frame_duration/1.5
    title_duration = title_duration/2
    outro_duration = 3
    clips = []    
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
    title_media_file_path = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_title.jpg"
    if custom_thumbnail == 'Yes':
        new_title_media_file_paths = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_title_{thread_id}.jpg"
        shutil.copy2(title_media_file_path, new_title_media_file_paths)
    else:
        new_title_media_file_paths = []
        for j in range(len(ranking_list)):
            new_title_media_file_paths.append(f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_{thread_id}_{j}_0.jpg")

    if two_parts == "Yes":
        ranking_lists = [ranking_list[:5], ranking_list[5:10]]  # Split the list into two parts
    else:
        ranking_lists = [ranking_list[:10]]  # Keep the list as it is

    j = 0
    for part, ranking_list in enumerate(ranking_lists, start=1): 
        media_file_counter = 0
        clips = []
        # Title card
        title_element = f"TOP 10"
        title_topic = topic
        if two_parts == "Yes":
            title_topic = f"{topic} Part {part}"  # Add part number to title if two_parts
        if bg_videos:
            bg_video = bg_videos[j % len(bg_videos)]
        else:
            bg_video = None


        try:
            title_card = create_title_card_variant0(
                title_element, title_topic, duration=title_duration, thread_id=thread_id,bg_video=bg_video, title_media_file_paths=new_title_media_file_paths, title_flag_paths=title_flag_paths, voice_over = voice_over, custom_thumbnail = custom_thumbnail)
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
                    topic = topic,duration=frame_duration ,thread_id=thread_id, bg_video=bg_video, media_file_paths=media_file_paths, voice_over = voice_over)

                if ranking_frame is not None:
                    ranking_frame = ranking_frame.set_fps(24)  # set fps to 24
                clips.append(ranking_frame)
                j += 1
                media_file_counter += 1
            except Exception as e:
                print(f"Error occurred while creating ranking frames: {e}")
                raise e
        try:
            outro_clip=outro_card(topic, duration=outro_duration, thread_id=thread_id, title_flag_paths = title_flag_paths, voice_over = 'No')
            if outro_clip is not None:
                outro_clip = outro_clip.set_fps(24)
            clips.append(outro_clip)
        except Exception as e:
            print(f"Error occurred while creating outro clip: {e}")
            raise e
        try:
            final_video = concatenate_videoclips(clips)
        except Exception as e:
            print(f"Error occurred while concatenating video clips: {e}")
            raise e

        try:
            country_list = []
            for rank in ranking_list:
                country_list.append(rank[0][0])
            generate_map(country_list, title_duration, frame_duration, outro_duration, thread_id)
            overlay_video_path = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\maps\\map_movie_{thread_id}.mp4"
            overlay_video = VideoFileClip(overlay_video_path)
            overlay_video = overlay_video.resize(height=1920)
            # If the video is now wider than the canvas, crop it to the width of the canvas
            if overlay_video.w > 540:
                overlay_video = overlay_video.crop(width=1080)            
            # W = 1080  # width
            # H = 1920   # height
            # amplitude_topic_hor = W/30  # maximum distance to the left or right of center
            # frequency_topic_hor = 0.25  # number of full oscillations per second
            # amplitude_topic_ver = H/70  # maximum distance to the up or down of center
            # frequency_topic_ver = 0.20  # number of full oscillations per second

            # Resize overlay video to desired size and then crop
            # overlay_video = overlay_video.resize(newsize=(overlay_video.w, overlay_video.h)).crop(
            #     x_center=overlay_video.w/2, y_center=overlay_video.h/2, width=1080, height=300)
            overlay_video = overlay_video.set_position('center', 'center')

            #overlay_video = overlay_video.set_duration(final_video.duration)
            # Create the clip
            c_clip = ColorClip((1080, 1920), col= (0,0,0))
            # Create a transparent image of size 1080x1920 using NumPy
            c_clip = c_clip.set_duration(overlay_video.duration)
            #bg_clip = VideoFileClip(get_bg())



            final_video = CompositeVideoClip([c_clip, overlay_video, final_video])

            output_dir = "C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\generated_videos\\"

            if bg_music is not None:
                if not os.path.exists(bg_music):
                    print(f"Background music file {bg_music} does not exist.")
                    raise FileNotFoundError(f"Background music file {bg_music} does not exist.")
                try:
                    bg_music_audio = AudioFileClip(bg_music)
                except Exception as e:
                    print(f"Could not open background music file {bg_music}. Error: {e}")
                    raise e
                bg_music_audio = bg_music_audio.volumex(0.2 * 1.5).set_duration(final_video.duration)
                final_video_audio = final_video.audio.volumex(1.5)
                final_audio = CompositeAudioClip([final_video_audio, bg_music_audio]).volumex(2.0)
                final_video = final_video.set_audio(final_audio)

            final_video.write_videofile(
                f"{output_dir}{'_'.join(topic.split())}_part{part}_{thread_id}.mp4", fps=24, codec='libx264')
        except Exception as e:
            print(f"Error occurred while processing the final video or writing it to a file: {e}")
            raise e

            
    #delete_media_files(min(10, len(ranking_list)), 2 if include_flag == 'Yes' else 1, thread_id)
    return None
    