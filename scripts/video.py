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




fadein_time = 0.2  # duration of the fade-in in seconds
transparent_image = np.zeros((1920, 1080, 4), dtype=np.uint8)
#transparent_image[:, :] = [255, 0, 0, 255] # Set all pixels to red


def create_title_card_variant0(title_element, title_topic, duration=3.90, thread_id=None, bg_video=None, title_media_file_paths=None, title_flag_paths = None, title_ball_file_names = None, voice_over = 'No', custom_thumbnail = 'No'):
    # Convert the NumPy array to an ImageClip
    canvas_clip = ImageClip(transparent_image)
    canvas_clip = canvas_clip.set_duration(duration)
    # element_clip = TextClip(wrap_text(title_element, 10), fontsize=font_size(290, len(title_element.split())+2), font="Calibri-Bold",
    #                         color='Firebrick', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=2)
    # element_clip_shadow = TextClip(wrap_text(title_element, 10), fontsize=font_size(290, len(title_element.split())+2), font="Calibri-Bold",
    #                         color='Black', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=2)
    shadow_clip = TextClip(wrap_text(f'{title_topic}', 16), fontsize=font_size(240, len(title_topic.split()) + 3), font="Calibri-Bold",
                          color='Black', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=3)
    topic_clip = TextClip(wrap_text(f'{title_topic}', 16), fontsize=font_size(240, len(title_topic.split()) + 3), font="Calibri-Bold",
                          color='White', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=3)

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
    #shadow_clip = shadow_clip.set_position(lambda t: (10+amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-300 + amplitude_topic_ver * np.sin(2 * np.pi * frequency_topic_ver * t)))).set_duration(duration) #Offset of 2 for Drop Shadow
    shadow_clip = shadow_clip.set_position(lambda t: (10+amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-300))).set_duration(duration) #Offset of 2 for Drop Shadow
    #topic_clip = topic_clip.set_position(lambda t: (amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-310 + amplitude_topic_ver * np.sin(2 * np.pi * frequency_topic_ver * t)))).set_duration(duration)
    topic_clip = topic_clip.set_position(lambda t: (amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-310))).set_duration(duration)
    # element_clip = element_clip.set_position(lambda t: (amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-800))).set_duration(duration)
    # element_clip_shadow = element_clip_shadow.set_position(lambda t: (5+amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-795))).set_duration(duration)
    # shadow_clip = shadow_clip.crossfadein(fadein_time)
    # topic_clip = topic_clip.crossfadein(fadein_time)
    # element_clip = element_clip.crossfadein(fadein_time) 
    # element_clip_shadow = element_clip_shadow.crossfadein(fadein_time)




     # Create a list to hold all the ImageClips
    flag_clips = []
    #title_flag_paths = title_flag_paths[::-1] #Reverse list 
    #chosen_flag = random.sample(title_flag_paths,10)
    #each_shuffle_duration = duration/10
    each_shuffle_duration = [0.05, 0.40, 0.65, 0.55, 0.30, 0.15, 0.15, 0.5, 0.45, 0.50, 0.30, 0.45, 0.40, 0.35]
    for i in range(4):
        title_flag_paths.append(title_flag_paths[i])
    index = 0
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
                flag_clip = flag_clip.set_position('center', 'center').set_duration(each_shuffle_duration[index])
                time_left -= each_shuffle_duration[index] #subtracting each flags duration until we have neough for the whole clip
                index+=1
                #set position and duration of each clip
                #flag_clip = flag_clip.set_position(lambda t: (amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (-300 + amplitude_topic_ver * np.sin(2 * np.pi * frequency_topic_ver * t)))).set_duration(each_shuffle_duration)
                # Add the flag clip to the list of flag clips
                flag_clips.append(flag_clip)

        # Create a single clip that contains all the flag clips in sequence
        flags_clip = concatenate_videoclips(flag_clips, method="compose")
        #flags_clip = flags_clip.set_position(lambda t: (540 - flag_clip.w/2 + amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (440 + amplitude_topic_ver * np.sin(2 * np.pi * frequency_topic_ver * t)))).set_duration(duration)
        flags_clip = flags_clip.set_position(lambda t: (540 - flag_clip.w/2 + amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t), (440))).set_duration(duration)
        #flags_clip = flags_clip.crossfadein(fadein_time)

    # Set margins
    #topic_clip = topic_clip.margin(left=100, right=100, bottom=0, top=0)
    #element_clip = element_clip.margin(left=100, right=100, bottom=0, top=0)
    #bg_video = None #Remove Later if no map
    if bg_video is not None:
        bg_video = VideoFileClip(bg_video)
        bg_video = bg_video.resize(height=1920)
        # If the video is now wider than the canvas, crop it to the width of the canvas
        if bg_video.w > 540:
            bg_video = bg_video.crop(width=1080)
        bg_video = bg_video.set_duration(duration)
        # grey_filter = ColorClip(bg_video.size, col=(128, 128, 128), duration=bg_video.duration)
        # # Set the opacity of the grey filter to be 0.2 (you can adjust this value)
        # grey_filter = grey_filter.set_opacity(0.6)

        # bg_video = CompositeVideoClip([bg_video, grey_filter])
    amplitude_media_hor = -50#-W/15  # maximum distance to the left or right of center
    frequency_media_hor = 0.4  # number of full oscillations per second
    amplitude_media_ver = -20#-H/80  # maximum distance to the up or down of center
    frequency_media_ver = 0.3  # number of full oscillations per second
    # title_media_file_path = None

    #Country Ball
    ball_clips = []
    #title_ball_file_names = random.sample(title_ball_file_names,10)
    for i in range(4):
        title_ball_file_names.append(title_ball_file_names[i])
    time_left = duration
    index = 0
    if title_ball_file_names is not None:
        while time_left > 0:
            for country in title_ball_file_names:
                countryball_path = f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\src\\img\\countryballs\\{country}.png'
                # Open the image using PIL
                img = Image.open(countryball_path)
                # Resize the image, ignoring original aspect ratio
                img_resized = img.resize((650, 650))
                # Convert the image back to a MoviePy clip
                ball_clip = ImageClip(np.array(img_resized))
                ball_clip = ball_clip.set_position('center', 'center').set_duration(each_shuffle_duration[index])
                time_left -= each_shuffle_duration[index] #subtracting each balls duration until we have neough for the whole clip
                index+=1
                # Add the ball clip to the list of ball clips
                ball_clips.append(ball_clip)

        # Create a single clip that contains all the flag clips in sequence
        balls_clip = concatenate_videoclips(ball_clips, method="compose")
        speed = 100
        balls_clip = balls_clip.set_position(
            lambda t: (t * speed + 350 - flag_clip.w/2 + amplitude_topic_hor * np.sin(2 * np.pi * frequency_topic_hor * t),740 + amplitude_topic_ver * np.sin(2 * np.pi * frequency_topic_ver * t))).set_duration(duration)
    
    # if len(title_media_file_paths) == 1:
    #     # Open the image using PIL
    #     img = Image.open(title_media_file_paths)
    #     # Resize the image, ignoring original aspect ratio
    #     img_resized = img.resize((1500, 880))
    #     # Convert the image back to a MoviePy clip
    #     media_clip = ImageClip(np.array(img_resized)).set_duration(duration)
    #     media_clip = media_clip.margin(left=10, right=10, bottom=10, top=10)

    #     # Position the media clip on the frame
    #     if media_clip is None:
    #         print(
    #             f"Failed to resize the media file: {title_media_file_paths}")
    #     else:
    #         if media_clip.w is not None:
    #             #media_clip = media_clip.set_position(lambda t: ((280 - media_clip.w/2)  + amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (1500 - media_clip.size[1]/2 + amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)
    #             media_clip = media_clip.set_position(((280 - media_clip.w/2), (1600 - media_clip.size[1]/2))).set_duration(duration)  
    #             #media_clip = media_clip.crossfadein(fadein_time)
    # else:
    #     chosen_media = random.sample(title_media_file_paths,3)
    #     media_clips = []
    #     each_shuffle_duration = duration/3
    #     time_left = duration
    #     while time_left > 0:
    #         for title_media_path in chosen_media:
    #             # Open the image using PIL
    #             img = Image.open(title_media_path)
    #             # Resize the image, ignoring original aspect ratio
    #             img_resized = img.resize((1500, 980))
    #             # Convert the image back to a MoviePy clip
    #             media_clip = ImageClip(np.array(img_resized))
    #             media_clip = media_clip.margin(left=10, right=10, bottom=10, top=10)
    #             media_clip = media_clip.set_position('center', 'center').set_duration(each_shuffle_duration)
    #             time_left -= each_shuffle_duration #subtracting each flags duration until we have neough for the whole clip
    #             # Add the flag clip to the list of media clips
    #             media_clips.append(media_clip)
            

    #     # Create a single clip that contains all the medias clips in sequence
    #     final_media_clip = concatenate_videoclips(media_clips, method="compose")
    #     #final_media_clip = final_media_clip.set_position(lambda t: ((540 - media_clip.w/2)  + amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (1100 + amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)
    #     final_media_clip = final_media_clip.set_position(lambda t: ((540 - media_clip.w/2), (1100))).set_duration(duration)  
    #     #final_media_clip = final_media_clip.crossfadein(fadein_time)

    if bg_video is not None:
        if flags_clip is not None:
            title_card = CompositeVideoClip(
                [canvas_clip, bg_video,  flags_clip, balls_clip, shadow_clip, topic_clip]) #final_media_clip, element_clip_shadow, element_clip
        else:
            title_card = CompositeVideoClip(
                [canvas_clip, bg_video, shadow_clip, topic_clip])#final_media_clip, element_clip_shadow, element_clip
    else:
        if flags_clip is not None:
            title_card = CompositeVideoClip(
                [canvas_clip, flags_clip, balls_clip, shadow_clip, topic_clip])#final_media_clip, element_clip_shadow, element_clip
        else:
            title_card = CompositeVideoClip(
                [canvas_clip, shadow_clip, topic_clip])#final_media_clip, element_clip_shadow, element_clip
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
     
    #whoosh sound
    whoosh_sound_path = get_whoosh()
    whoosh_audio = AudioFileClip(whoosh_sound_path).volumex(1.0 * 0.2)
    # Text-To-Speech
    audio_file_path = f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp_audio\\title_topic_{title_topic}_{thread_id}.mp3'
    if voice_over == "Yes":
        text_str = f'Can you guess Top 10 {title_topic}' #Can you guess ?
        azure_speak_text(text_str, duration, audio_file_path)
        if os.path.exists(audio_file_path):
            tts_audio = AudioFileClip(audio_file_path).volumex(1.0)
            final_audio = CompositeAudioClip([tts_audio, whoosh_audio])
            title_card = title_card.set_audio(final_audio)
        else:
            print("Debug: File path does not exist:", audio_file_path)
    else:
        title_card = title_card.set_audio(whoosh_audio)
    #os.remove(audio_file_path)
    return title_card




def create_title_card_variant2(title_element, title_topic, duration=3.90, thread_id=None, bg_video=None, title_media_file_paths=None, title_flag_paths = None, voice_over = 'No', custom_thumbnail = 'No'):
    display_str = f'{title_topic}'
    word_list = display_str.split(' ')
    word_list.append('Around')
    word_list.append('The World')

    # Convert the NumPy array to an ImageClip
    canvas_clip = ImageClip(transparent_image)
    canvas_clip = canvas_clip.set_duration(duration)

    W = 1080  # width
    H = 1920   # height
    amplitude_topic_hor = W/30  # maximum distance to the left or right of center
    frequency_topic_hor = 0.25  # number of full oscillations per second
    amplitude_topic_ver = H/70  # maximum distance to the up or down of center
    frequency_topic_ver = 0.20  # number of full oscillations per second

    y_position = -600
    start_time = 0
    fadein_duration = 0.25
    txt_clips = []

    def make_position_lambda(amplitude_hor, frequency_hor, y, amplitude_ver, frequency_ver):
        return lambda t: (amplitude_hor * np.sin(2 * np.pi * frequency_hor * t), y + amplitude_ver * np.sin(2 * np.pi * frequency_ver * t))
    
    for word in word_list:
        element_clip = TextClip(wrap_text(word, 16), fontsize=font_size(240, len(title_element.split())+2), font="Calibri-Bold",
                                color='SkyBlue', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=2)
        element_clip_shadow = TextClip(wrap_text(word, 16), fontsize=font_size(240, len(title_element.split())+2), font="Calibri-Bold",
                                color='Black', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=2)
        element_clip = element_clip.set_position(make_position_lambda(amplitude_topic_hor, frequency_topic_hor, y_position, amplitude_topic_ver, frequency_topic_ver)).set_duration(duration)
        element_clip_shadow = element_clip_shadow.set_position(make_position_lambda(amplitude_topic_hor, frequency_topic_hor, y_position + 5, amplitude_topic_ver, frequency_topic_ver)).set_duration(duration)# Fade in element and its shadow
        element_clip = element_clip.crossfadein(fadein_duration).set_start(start_time)
        element_clip_shadow = element_clip_shadow.crossfadein(fadein_duration).set_start(start_time)
        txt_clips.append(element_clip_shadow)
        txt_clips.append(element_clip)
        y_position += 175
        start_time += 0.3


    bg_video = None
    if bg_video is not None:
        title_card = CompositeVideoClip([canvas_clip, bg_video] + txt_clips)
    else:
        title_card = CompositeVideoClip([canvas_clip] + txt_clips)
            
     
    # Text-To-Speech
    audio_file_path = f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp_audio\\title_topic_{title_topic}_{thread_id}.mp3'
    if voice_over == "Yes":
        text_str = f'{title_topic} Around The World' #Can you guess ?
        azure_speak_text(text_str, duration, audio_file_path)
        if os.path.exists(audio_file_path):
            tts_audio = AudioFileClip(audio_file_path).volumex(1.0)
            title_card = title_card.set_audio(tts_audio)
        else:
            print("Debug: File path does not exist:", audio_file_path)
    #os.remove(audio_file_path)
    
    # Set the end of the final clip to the desired duration
    title_card = title_card.set_end(duration)
    return title_card


def create_counrty_ranking_frame(rank, country, what,topic, why, color_txt, thread_id=None, duration=2.80, bg_video=None, media_file_paths=None, voice_over = 'No'):
    canvas_clip = ImageClip(transparent_image)
    # topic_clip = TextClip(wrap_text(f"{topic}", 24), fontsize=60, font="Calibri-Bold",
    #                     color='White', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=0)
    txt_clip = TextClip(wrap_text(f"#{rank}: {country}", 16), fontsize=font_size(150, len(country.split())+1 ), font="Calibri-Bold", #f"#{rank}: {country}"
                        color= color_txt, size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4) #'#db1620'
    shadow_clip = TextClip(wrap_text(f"#{rank}: {country}", 16), fontsize=font_size(150, len(country.split())+1 ), font="Calibri-Bold",
                          color='Black', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    if why is None:
        why = ''

    why_clip = TextClip(wrap_text(f"{why}", 22), fontsize=font_size(110, len(why.split())), font="Calibri-Bold",
                        color='white', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    what_clip = TextClip(wrap_text(f"{what}", 16), fontsize=font_size(110, len(what.split())), font="Calibri-Bold",
                         color='white', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    what_shadow_clip = TextClip(wrap_text(f"{what}", 16), fontsize=font_size(110, len(what.split())), font="Calibri-Bold",
                         color='Black', size=(1080, 1920), method='caption', align='center', stroke_color='black', stroke_width=4)
    

    W = 1080  # width
    H = 1920   # height
    multiplier = 1
    if rank%2 == 0: #Alternating between each rank whether animation starts to left or right, up or down
        multiplier = -1
    amplitude_flag_hor = multiplier * -15  #-W/15  # maximum distance to the left or right of center
    frequency_flag_hor = 1/duration  # number of full oscillations per second
    amplitude_flag_ver = multiplier * -5#-H/80  # maximum distance to the up or down of center
    frequency_flag_ver = 0.1  # number of full oscillations per second

    # t: time in seconds
    # np.sin(2 * np.pi * frequency * t) oscillates between -1 and 1
    # amplitude * np.sin(2 * np.pi * frequency * t) oscillates between -amplitude and amplitude
    # adding W/2 (the center) moves the oscillation to the center of the screen
    #txt_clip = txt_clip.set_position(lambda t: (180 + amplitude_flag_hor * np.sin(2 * np.pi * frequency_flag_hor * t), (275 + amplitude_flag_ver * np.sin(2 * np.pi * frequency_flag_ver * t)))).set_duration(duration)
    #shadow_clip = shadow_clip.set_position(lambda t: (190 + amplitude_flag_hor * np.sin(2 * np.pi * frequency_flag_hor * t), (285 + amplitude_flag_ver * np.sin(2 * np.pi * frequency_flag_ver * t)))).set_duration(duration)
    txt_clip = txt_clip.set_position((180, 275)).set_duration(duration)
    shadow_clip = shadow_clip.set_position((190, 285)).set_duration(duration)
    # txt_clip = txt_clip.crossfadein(fadein_time)
    # shadow_clip = shadow_clip.crossfadein(fadein_time)




    canvas_clip = canvas_clip.set_duration(duration)
    #topic_clip = topic_clip.set_position(('center', -825)).set_duration(duration)
    #topic_clip = topic_clip.set_opacity(0.5)
    #why_clip = why_clip.set_position(('center',650)).set_duration(duration)



    bg_video = None #Remove Later if no map
    if bg_video is not None:
        bg_video = VideoFileClip(bg_video)
        bg_video = bg_video.resize(height=1920)
        # If the video is now wider than the canvas, crop it to the width of the canvas
        if bg_video.w > 540:
            bg_video = bg_video.crop(width=1080)
        bg_video = bg_video.set_duration(duration)

    #Countryballs
    countryballs_dir = 'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\src\\img\\countryballs'
    country_list = [f.split('.')[0] for f in os.listdir(countryballs_dir) if os.path.isfile(os.path.join(countryballs_dir, f))]

    # Find the nearest matching country from the country_list
    country = find_nearest_country(country, country_list)

    countryball_path = f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\src\\img\\countryballs\\{country}.png'
    if os.path.exists(countryball_path):
        # Open the image using PIL
        img = Image.open(countryball_path)
        # Resize the image, ignoring original aspect ratio
        img_resized = img.resize((650, 650))
        # Convert the image back to a MoviePy clip
        ball_clip = ImageClip(np.array(img_resized)).set_duration(duration)
        # media_clip = media_clip.margin(
        #     left=10, right=10, bottom=10, top=10)
        distance_from_wall = 150
        ball_position_1 = (distance_from_wall - ball_clip.size[0] / 2) #Position 1
        ball_position_2 = (1080 - distance_from_wall - ball_clip.size[0] / 2) #Position 2

        # Alternate positions based on rank
        if rank%2 == 0:
            ball_position_first_half, ball_position_second_half = ball_position_1, ball_position_2
        else:
            ball_position_first_half, ball_position_second_half = ball_position_2, ball_position_1

        ball_clip = ball_clip.set_position(lambda t: ((ball_position_first_half if t < duration/2 else ball_position_second_half) + 2*amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (975 - ball_clip.size[1] / 2 + 2*amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)#ball_clip = ball_clip.crossfadein(fadein_time) #1600 y
        #ball_clip = ball_clip.crossfadein(fadein_time)
    if media_file_paths is not None:
        media_clips = []
        flag_clips = []
        for media_file_path in media_file_paths:
            if media_file_path is None:
                media_file_path = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\src\img\image_missing.png'
            try:
                W = 1080  # width
                H = 1920   # height

                amplitude_media_hor = multiplier * 10#W/15  # maximum distance to the left or right of center
                frequency_media_hor = 0.2  # number of full oscillations per second
                amplitude_media_ver = multiplier * 10#H/80  # maximum distance to the up or down of center
                frequency_media_ver = 0.1  # number of full oscillations per second
                #what_clip = what_clip.set_position(lambda t: (amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (-100 + amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)
                what_clip = what_clip.set_position(((0), (-100))).set_duration(duration)
                #what_shadow_clip = what_shadow_clip.set_position(lambda t: (10+amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (-90 + amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)
                what_shadow_clip = what_shadow_clip.set_position(((10), (-90))).set_duration(duration)
                #why_clip = why_clip.set_position(lambda t: (amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (-200 + amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)
                why_clip = why_clip.set_position(('center', -300)).set_duration(duration)

                if len(media_clips) == 0:
                    # Open the image using PIL
                    img = Image.open(media_file_path)
                    # Resize the image, ignoring original aspect ratio
                    img_resized = img.resize((1180, 1240))
                    # Convert the image back to a MoviePy clip
                    media_clip = ImageClip(np.array(img_resized)).set_duration(duration)
                    # media_clip = media_clip.margin(
                    #     left=10, right=10, bottom=10, top=10)
                    # This is the first image
                    if media_clip.h is not None:
                        #media_clip = media_clip.set_position(lambda t: ((540 - 1180 / 2)  + amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (0 + amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)
                        media_clip = media_clip.set_position(lambda t: ((540 - 1180 / 2)  + amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (0))).set_duration(duration)
                        #media_clip = media_clip.set_position(((540 - media_clip.size[0] / 2), (0))).set_duration(duration)
                        #media_clip = media_clip.set_position(("center", 'center'))
                    else:
                        media_clip = media_clip.set_position(lambda t: ((540 - 1180 / 2)  + amplitude_media_hor * np.sin(2 * np.pi * frequency_media_hor * t), (amplitude_media_ver * np.sin(2 * np.pi * frequency_media_ver * t)))).set_duration(duration)
                        #media_clip = media_clip.set_position(("center", 'center'))
                    media_clips.append(media_clip)
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
                    img_resized = img.resize((335, 200))
                    # Convert the image back to a MoviePy clip
                    media_clip = ImageClip(np.array(img_resized)).set_duration(duration)
                    media_clip = media_clip.margin(
                        left=5, right=5, bottom=5, top=5)
                    #media_clip = media_clip.set_position(lambda t: ((35) + amplitude_flag_hor * np.sin(2 * np.pi * frequency_flag_hor * t), (1125 + amplitude_flag_ver * np.sin(2 * np.pi * frequency_flag_ver * t)))).set_duration(duration)
                    media_clip = media_clip.set_position((35, 1125)).set_duration(duration)
                    #media_clip = media_clip.crossfadein(fadein_time)
                    flag_clips.append(media_clip)

                    grey_box = ImageClip(np.array(img.resize((1080, 240)))).set_duration(duration)

            except AVError:
                print(f"Error processing the media file: {media_file_path}")
                media_clips.append(None)

        #grey_box = ColorClip((1080,240), col=(255,255,255), duration=txt_clip.duration) #col=(99, 96, 97) 
        grey_box = grey_box.set_position((0, 1105))
        grey_box = grey_box.margin(left=5, right=5, bottom=5, top=5)
        if bg_video is not None:
            clip = CompositeVideoClip(
                [canvas_clip] + media_clips + [grey_box] + flag_clips + [ball_clip, shadow_clip, txt_clip, what_shadow_clip, what_clip, why_clip]) #, bg_video, topic_clip,
        else:
            clip = CompositeVideoClip(
                [canvas_clip] + media_clips + [grey_box] + flag_clips + [ball_clip, shadow_clip, txt_clip, what_shadow_clip, what_clip, why_clip]) #topic_clip,
    else:
        if bg_video is not None:
            clip = CompositeVideoClip(
                [canvas_clip, bg_video, grey_box, ball_clip, shadow_clip, txt_clip, what_shadow_clip, what_clip, why_clip]) #topic_clip,
        else:
            clip = CompositeVideoClip(
                [canvas_clip, grey_box, ball_clip, shadow_clip, txt_clip, what_shadow_clip, what_clip, why_clip]) #topic_clip,
            
    #whoosh sound
    whoosh_sound_path = get_whoosh()
    whoosh_audio = AudioFileClip(whoosh_sound_path).volumex(1.0 * 0.2)

    # Text-To-Speech
    audio_file_path = f'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp_audio\\rank_country_{topic}_{rank}_{thread_id}.mp3'
    if voice_over == "Yes":# and False:
        text_str = f"{country}" #{rank} {country}
        if rank == 1:
            text_str = f"{country}" #{rank} {country}
        azure_speak_text(text_str, duration, audio_file_path)
        if os.path.exists(audio_file_path):
            #print("Debug: File path exists:", audio_file_path)
            tts_audio = AudioFileClip(audio_file_path).volumex(1.0)
            final_audio = CompositeAudioClip([whoosh_audio, tts_audio]) 
            clip = clip.set_audio(final_audio)
        else:
            print("Debug: File path does not exist:", audio_file_path)
    else:
        #clip = clip.set_audio(whoosh_audio)
        pass

    return clip

def outro_card(topic, duration=3, thread_id=None, title_flag_paths=None, title_media_file_paths = None ,voice_over='No'):
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
    rank_string_1 = "#1 :\n#2 :\n#3 :\n#4 :\n#5 :\n#6 :\n#7 :\n#8 :\n#9 :\n#10:"
    #rank_string_2 = "#11:\n#12:\n#13:\n#14:\n#15:\n#16:\n#17:\n#18:\n#19:\n#20:"

    # Create a single text clip for all ranks
    rank_text_clip1 = TextClip(rank_string_1, fontsize=120, font="Calibri-Bold",
                              color='YellowGreen', size=(1080, 1920),
                              method='caption', align='center',
                              stroke_color='black', stroke_width=4).set_position((-300, -100)).set_duration(duration)
    rank_text_clip1 = rank_text_clip1.crossfadein(fadein_time)
    clips.append(rank_text_clip1)

    # rank_text_clip2 = TextClip(rank_string_2, fontsize=120, font="Calibri-Bold",
    #                           color='YellowGreen', size=(1080, 1920),
    #                           method='caption', align='center',
    #                           stroke_color='black', stroke_width=4).set_position((80, -100)).set_duration(duration)
    # rank_text_clip2 = rank_text_clip2.crossfadein(fadein_time)
    # clips.append(rank_text_clip2)

    y_index = 280
    x_index = 350
    # For each rank, create an image clip
    bg_flag_path = title_flag_paths[-1]
    bg_flag = Image.open(bg_flag_path).resize((1080, 1920))
    bg_flag_clip = ImageClip(np.array(bg_flag), duration=duration).set_position(('center', 'center'))
    
    for rank in range(10):
        # Open, resize and convert the flag image to an ImageClip
        flag_path = title_flag_paths[-1 * (rank+1)] # make sure your paths are ordered correctly
        img_flag = Image.open(flag_path).resize((100, 75))
        flag_clip = ImageClip(np.array(img_flag), duration=duration).set_position((x_index, y_index))
        flag_clip = flag_clip.margin(
                        left=10, right=10, bottom=10, top=10)
        flag_clip = flag_clip.crossfadein(fadein_time)

        # Append flag clip to the clips list
        clips.append(flag_clip)

        # # Open, resize and convert the flag image to an ImageClip
        # media_path = title_media_file_paths[-1 * (rank+1)] # make sure your paths are ordered correctly
        # img_media = Image.open(media_path).resize((100, 75))
        # media_clip = ImageClip(np.array(img_media), duration=duration).set_position((550, y_index))
        # media_clip = media_clip.crossfadein(fadein_time)

        # # Append media clip to the clips list
        # clips.append(media_clip)
        y_index += 120
        if rank == 9:
            y_index = 280
            x_index= 750

    y_index += 120
    subscribe_text = "Subscribe for daily videos!"
    subscribe_text_clip = TextClip(wrap_text(subscribe_text, 16), fontsize=120, font="Calibri-Bold",
                                color='SkyBlue', size=(1080, 1920), method='caption', align='center',
                                stroke_color='black', stroke_width=4)
    subscribe_text_clip = subscribe_text_clip.set_position(('center', 625)).set_duration(duration)
    subscribe_text_clip = subscribe_text_clip.set_opacity(0.9)

    subscribe_text_clip = subscribe_text_clip.crossfadein(fadein_time)
    clips.append(subscribe_text_clip)
    # Put everything into a single composite clip
    final_clip = CompositeVideoClip([bg_flag_clip, *clips], size=(1080, 1920)).set_duration(duration)
    
    # Define the audio for the clip
    whoosh_sound_path = get_whoosh()
    whoosh_audio = AudioFileClip(whoosh_sound_path).volumex(1.0 * 0.2)
    final_clip = final_clip.set_audio(whoosh_audio)

    return final_clip




def create_country_video(lock, ranking_list, topic, include_flag, thread_id, title_duration, frame_duration, include_bg_videos=True, elements='Countries', 
                         bg_videos=None, bg_music=None, two_parts="No", voice_over="No", custom_thumbnail = "No"):
    #frame_duration = frame_duration/1.5
    #title_duration = title_duration/2
    outro_duration = 0
    clips = []
    country_list = []
    for rank in ranking_list:
        country_list.append(rank[0][0])
    #Countryballs
    countryballs_dir = 'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\src\\img\\countryballs'
    all_country_list = [f.split('.')[0] for f in os.listdir(countryballs_dir) if os.path.isfile(os.path.join(countryballs_dir, f))]
    ball_country_list = country_list.copy()
    # Find the nearest matching country from the country_list
    for i, country in enumerate(ball_country_list):
        ball_country_list[i] = find_nearest_country(country, all_country_list)
    
    highlight_colors = [
        '#FF0000', # red
        #'#0000FF', # blue
        '#008000', # green
        '#FFFF00', # yellow
        '#800080', # purple
        '#FFC0CB', # pink
        '#FFA500', # orange
        '#00FFFF', # cyan
        '#A52A2A', # brown
        '#FFD700', # gold
        '#C0C0C0', # silver
        '#808080', # gray
        '#00FF00', # lime
        '#FF00FF', # magenta
        '#008080', # teal
        '#808000', # olive
        '#800000', # maroon
        '#87CEEB', # sky blue
        '#E6E6FA', # lavender
        '#7FFFD4', # aquamarine
        '#D2B48C', # tan
        '#FA8072', # salmon
        '#F08080', # light coral
        '#20B2AA', # light sea green
        '#778899', # light slate gray
        '#B0C4DE', # light steel blue
        '#FFFFE0', # light yellow
        '#00FA9A', # medium spring green
        '#48D1CC', # medium turquoise
        '#FFE4E1'  # misty rose
    ]


    # Randomly sample 10 colors for highlighting countries
    highlight_colors_sampled = random.sample(highlight_colors, 10)
        
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
                title_element, title_topic, duration=title_duration, thread_id=thread_id,bg_video=bg_video, title_media_file_paths=new_title_media_file_paths, title_flag_paths=title_flag_paths, title_ball_file_names=ball_country_list, voice_over = voice_over, custom_thumbnail = custom_thumbnail)
            if title_card is not None:
                title_card = title_card.set_fps(24)
                clips.append(title_card)
        except Exception as e:
            print(f"Error occurred while creating the title card: {e}")
            raise e

        # Rest
        color_count = 0
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
                why_txt = ''
                if len(ranking_list[media_file_counter]) == 4:
                    why_txt = ranking_list[media_file_counter][3][0]
                ranking_frame = create_counrty_ranking_frame(
                    i - rank_offset, ranking_list[media_file_counter][0][0], ranking_list[media_file_counter][1][0], topic, why_txt, highlight_colors_sampled[color_count],
                    duration=frame_duration ,thread_id=thread_id, bg_video=bg_video, media_file_paths=media_file_paths, voice_over = voice_over)
                color_count+=1
                if ranking_frame is not None:
                    ranking_frame = ranking_frame.set_fps(24)  # set fps to 24
                clips.append(ranking_frame)
                j += 1
                media_file_counter += 1
            except Exception as e:
                print(f"Error occurred while creating ranking frames: {e}")
                raise e
        # try:
        #     outro_clip=outro_card(topic, duration=outro_duration, thread_id=thread_id, title_flag_paths = title_flag_paths, title_media_file_paths= new_title_media_file_paths, voice_over = 'No')
        #     if outro_clip is not None:
        #         outro_clip = outro_clip.set_fps(24)
        #     clips.append(outro_clip)
        # except Exception as e:
        #     print(f"Error occurred while creating outro clip: {e}")
        #     raise e
        try:
            final_video = concatenate_videoclips(clips)
        except Exception as e:
            print(f"Error occurred while concatenating video clips: {e}")
            raise e

        try:
            try:
                lock.acquire()
                generate_map(country_list, 0, frame_duration, outro_duration, thread_id, highlight_colors_sampled) #frame_duration, outro_duration
            finally:
                lock.release()
            overlay_video_path = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\maps\\map_movie_{thread_id}.mp4"
            overlay_video = VideoFileClip(overlay_video_path)
            overlay_video = overlay_video.resize(height=1600)
            # If the video is now wider than the canvas, crop it to the width of the canvas
            if overlay_video.w > 540:
                overlay_video = overlay_video.crop(width=3000)            
            # Create a black clip of 4 seconds
            black_clip = ColorClip((overlay_video.size[0], overlay_video.size[1]), col=(0,0,0)).set_duration(title_duration)

            # Concatenate the black clip at the beginning of your overlay video
            overlay_video = concatenate_videoclips([black_clip, overlay_video])
            overlay_video = overlay_video.set_position((540-overlay_video.size[0]/2, 1600 - overlay_video.size[1]/2))
            # # Create the clip
            c_clip = ColorClip((1080, 1920), col= (0,0,0))
            # Create a transparent image of size 1080x1920 using NumPy
            c_clip = c_clip.set_duration(final_video.duration)

            shake_period = frame_duration/2.0
            shake_duration = 0.2
            resize_rate = 1.1
            intensity = 30  # Change this to set how aggressive the shake should be

            shake_clip = CompositeVideoClip([c_clip, overlay_video, final_video])
            shake_clip = shake_clip.set_position('center')  # Center the clip
            # Apply the shake function to the clip after title_duration
            shake_clip = shake_clip.set_position(lambda t: ('center' if t < title_duration else shake(t - title_duration, shake_period, shake_duration, intensity)))

            grey_filter = ColorClip(c_clip.size, col=(128, 128, 128), duration=c_clip.duration)

            # Set the opacity of the grey filter to be 0.2 (you can adjust this value)
            grey_filter = grey_filter.set_opacity(0.2)

            final_video = CompositeVideoClip([c_clip, shake_clip, grey_filter])
            final_video = final_video.set_duration(c_clip.duration)
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
                bg_music_audio = bg_music_audio.volumex(1.0 * 0.2).set_duration(final_video.duration)
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
    