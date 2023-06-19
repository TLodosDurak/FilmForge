
import streamlit as st
import os
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from scripts.utils import convert_openai_response, save_uploaded_file, pick_default_audio_path, get_hashtags_list, switch_response, reverse_response, generate_columns_layout
from scripts.video import download_image, is_image_readable
from scripts.templates import *
from scripts.youtube import *
from src.videos.default_pexel_bg import get_ranking_frame_videos
from PIL import Image
from scripts.custom_google_search import CustomGoogleSearchAPIWrapper
import re



def page1(video_queue):
    # Asking for user input
    if 'user_input' not in st.session_state:
        st.session_state.user_input = 'Countries in Fashion 2023'

    st.session_state.user_input = st.text_input(
        "Enter the topic of your Top 10 Countries short video", 'Countries in Fashion 2023')
    
    if 'channel_category' not in st.session_state:
        st.session_state.channel_category = ' #fashion'

    # For testing the code without making openai calls $$$
    if 'ranking_list' not in st.session_state:
        st.session_state.ranking_list = [[["India"], ["Fashion Hub"], ["Mumbai"], ["indian fashion"]], [["China"], ["Fashion Hub"], ["Shanghai"], ["chinese fashion"]],  [["Australia"], ["Fashion Destination"], ["Sydney"], ["australian fashion"]], [["Germany"], ["Fashion Pioneer"], ["Berlin"], ["german fashion"]], [["Spain"], ["Fashion Icon"], ["Madrid"], ["spanish fashion"]],   [
            ["United States"], ["Fashion Influencer"], ["New York"], ["american fashion"]], [["Japan"], ["Fashion Innovator"], ["Tokyo"], ["japanese fashion"]], [["United Kingdom"], ["Fashion Trendsetter"], ["London"], ["british fashion"]], [["Italy"], ["Fashion Leader"], ["Milan"], ["italian fashion"]],  [["France"], ["Fashion Capital"], ["Paris"], ["french fashion"]]]
    if 'title' not in st.session_state:
        st.session_state.title =  st.session_state.user_input
    if 'description' not in st.session_state:
        st.session_state.description = 'Top 10: ' +  st.session_state.user_input + '\n\n' + \
            '#italy #france #uk #usa #nyc #london #milan #paris #india #mumbai #shangai #sydney #berlin #japan #tokyo #spain #madrid'

    # Creating chains
    llm = OpenAI(model_name='text-davinci-003', temperature=0.2)
    llm2 = OpenAI(model_name='text-davinci-002', temperature=0.2)

    video_chain4 = LLMChain(llm=llm, prompt=video_template4, verbose=True)
    fact_check_chain = LLMChain(
        llm=llm, prompt=fact_check_template, verbose=True)
    hashtage_chain = LLMChain(llm=llm2, prompt=hashtag_template, verbose=True)

    openai_button = st.button("Make OpenAI Call")  # OpenAI Call Button
    user_entered_response = ""
    if 'media_file_paths' not in st.session_state:
        st.session_state.media_file_paths = []
    if 'queries' not in st.session_state:
        st.session_state.queries = []

    google_search = CustomGoogleSearchAPIWrapper()

    #with st.expander('Advanced OpenAI Settings'):
    # OpenAI Call Bypass Radio Button
    openai_bypass = st.radio('Bypass OpenAI Call?', ('No', 'Yes'))
    reverse_button = st.button("Reverse Response")
    switch_button = st.button("Switch Response")

    if reverse_button:
        reversed_response = reverse_response(st.session_state.ranking_list)
        st.session_state.ranking_list = reversed_response
    
    if switch_button:
        switched_response = switch_response(st.session_state.ranking_list)
        st.session_state.ranking_list = switched_response

    user_entered_response = st.text_area(
        "Enter your own response", st.session_state.ranking_list)
    if user_entered_response:
        st.session_state.ranking_list, error = convert_openai_response(user_entered_response)
        if error is not None:
            st.error(error)

    submit_button = st.button("Submit Response")
    if submit_button:
        if "media_file_paths" not in st.session_state:
            st.session_state.media_file_paths = []  # Initialize media_file_paths as an empty list if not already initialized
        st.session_state.media_file_paths.clear()  # Clear existing paths
        st.session_state.queries.clear()  # Clear existing queries
        st.session_state.ranking_list, error = convert_openai_response(st.session_state.ranking_list)
        if error is not None:
            st.error(error)
        print('Ranking_List:', st.session_state.ranking_list)
        j = 0
        for i in range(min(10, len(st.session_state.ranking_list)), 0, -1):
            try:
                media_queries = [
                    f"{st.session_state.ranking_list[j][3][0]}"]
                media_queries.append(
                    f"{st.session_state.ranking_list[j][0][0]} flag bitmap")
                for media_query in media_queries:
                    st.session_state.queries.append(media_query)
                    media_results = google_search.search_media(
                        media_query, num_results=5)
                    # pic from top 3 results
                    media_file_path = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_{j}_{media_queries.index(media_query)}.jpg"
                    image_downloaded = False
                    for media in media_results[:5]:
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
                            continue
                    if not image_downloaded:
                        media_file_path = None  # Skip using the image if the download fails
                    st.session_state.media_file_paths.append(media_file_path)
            except Exception as e:
                print(
                    f"Error occurred while processing the media queries: {e}")
                raise e
            j += 1
    cols = generate_columns_layout(st.session_state.media_file_paths, st.session_state.queries)
    for row in cols:
        for column in row:
            column.write("")  # Add empty write statements to preserve the layout

    if openai_button:
        if  st.session_state.user_input.strip() == '':
            st.error('Error: Input field is empty. Please enter a topic.')
        elif openai_bypass == 'No':
            with st.spinner("Waiting for OpenAI response..."):
                try:
                    response = video_chain4.run({"topic":  st.session_state.user_input})
                    fact_checked_response = fact_check_chain.run(
                        {"topic":  st.session_state.user_input, "response": response})
                    st.session_state.ranking_list, error = convert_openai_response(
                        fact_checked_response)
                    if error is not None:
                        st.error(error)
                    # print(get_hashtags_list(st.session_state.ranking_list))
                    # hashtag_response = hashtage_chain.run(
                    #     {"list": get_hashtags_list(st.session_state.ranking_list)})
                    # print(hashtag_response)
                    hashtag_response = get_hashtags_list(st.session_state.ranking_list)
                    st.session_state.description = 'Top 10: ' +  st.session_state.user_input + \
                        '\n\n#shorts #countries #countryfacts ' + hashtag_response

                except Exception as e:
                    print(f'Error occurred while calling OpenAI API: {e}')
                with st.expander("Click to expand OpenAI response:"):
                    st.write("Fact Checked Response:", fact_checked_response)
                    st.write("Formatted Response:",
                             st.session_state.ranking_list)
                st.session_state.generate_video = True
        elif openai_bypass == 'Yes':
            st.error('Error: Bypass OpenAI is set to Yes')
            st.session_state.generate_video = True
            if user_entered_response.strip() == '':
                st.error(
                    'Error: Response field is empty. Please enter your own response.')
            else:
                try:
                    st.session_state.ranking_list, error = convert_openai_response(
                        user_entered_response)
                    if error is not None:
                        st.error(error)
                    st.session_state.generate_video = True
                except Exception as e:
                    st.error(
                        f'Error occurred while parsing user entered response: {e}')
        st.experimental_rerun()
    with st.expander("Advanced Generate Video Settings"):
        include_flag = st.radio('Include Country flag?', ('No', 'Yes'))
        two_parts = st.radio('Make it two parts?', ('No', 'Yes'))
        voice_over = st.radio('Have a voice over?', ('No', 'Yes'))

        title_media_query = st.text_input('Input Thumbnail Search Query')

        # The user's input is now in title_media_query
        title_media_query = [title_media_query]

        # Perform Google search
        try:
            title_media_results = google_search.search_media(
                title_media_query, num_results=3)
        except Exception as e:
            st.write(f"Error occurred while using Google Search API: {e}")
            raise e

        # Download and check image from top 3 results
        title_media_file_path = f"C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\temp\\media_title.jpg"
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
                st.write(
                    f"Error occurred while downloading or reading the image: {e}")
                raise e

        # Display image to the user
        if image_downloaded:
            image = Image.open(title_media_file_path)
            st.image(image, caption=title_media_query)
        else:
            if os.path.isfile(title_media_file_path):
                image = Image.open(title_media_file_path)
                st.image(image, caption=title_media_query)
            else:
                st.write("No valid image found.")
    
    tags = []
    if  st.session_state.user_input.strip() == '':
        st.error(
            'Error: Video title cannot be empty. Please enter a topic for your video.')
    else:
        each_word =  st.session_state.user_input.split()
        st.session_state.title = st.session_state.user_input
        # st.session_state.description = 'Top 10: ' + user_input + '\nMusic: 6th String by Dedpled \n' + \
        #     '#fashion #italy #france #uk #usa #nyc #london #milan #paris #india #mumbai #shangai #sydney #berlin #japan #tokyo #spain #madrid'

    with st.expander('Advanced Youtube Settings') as adv_yt:
        st.session_state.title = st.text_input(
            'Title:', st.session_state.title)
        st.session_state.description = st.text_area(
            'Description:', st.session_state.description)
        description_button = st.button("Redo Description")
    if description_button:
        # hashtag_response = hashtage_chain.run(
        #                 {"list": get_hashtags_list(st.session_state.ranking_list)})
        hashtag_response = get_hashtags_list(st.session_state.ranking_list)
        st.session_state.description = 'Top 10: ' +  st.session_state.user_input + \
                        '\n\n#shorts #countries #countryfacts ' + hashtag_response
        st.experimental_rerun()
        
        
    # Initialize the session state
    if 'generate_video' not in st.session_state:
        st.session_state.generate_video = False

    generate_video_button = st.button("Generate Video")

    if generate_video_button:
        st.write(f'Generating Video {st.session_state.user_input}...')
        st.write(f'This will take around 3 minutes, you can check its progress in Schedule Tab.')
        st.write(f'Feel free to keep generating new videos!')
        print('Generating Video', st.session_state.user_input)
        if  st.session_state.user_input.strip() == '':
            st.error('Error: Input field is empty. Please enter a topic.')
        elif (st.session_state.get('generate_video') and  st.session_state.user_input) or openai_bypass == 'Yes':
            with st.spinner("Generating video...\n this might take a minute!"):
                st.session_state.generate_video = False
                if isinstance(st.session_state.ranking_list, list):
                    try:
                        bg_videos = get_ranking_frame_videos()
                    except Exception as e:
                        st.error(
                            f'Error occurred while creating video clips: {e}')
                    audio_info = pick_default_audio_path()
                    default_audio_file_path = audio_info[0]
                    title_duration = audio_info[1]
                    frame_duration = audio_info[2]
                    with open(default_audio_file_path, 'rb') as default_audio_file:
                        bg_music = default_audio_file.name

                        # This line creates the video using the ranking list.
                        try:
                            # create_country_video(st.session_state.ranking_list,
                            #                      user_input, include_flag, bg_videos=bg_videos, bg_music=bg_music)
                            video_queue.put({
                                "ranking_list": st.session_state.ranking_list,
                                "user_input":  st.session_state.user_input,
                                "include_flag": include_flag,
                                "title_duration": title_duration,
                                "frame_duration": frame_duration,
                                "two_parts": two_parts,
                                "voice_over": voice_over,
                                "bg_videos": bg_videos,
                                "bg_music": bg_music
                            })
                            if two_parts == "Yes":
                                yt_desc_path1 = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\generated_videos'+ f"\\{'_'.join(st.session_state.user_input.split())}_part1.csv"
                                yt_desc_path2 = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\generated_videos'+ f"\\{'_'.join(st.session_state.user_input.split())}_part2.csv"
                                full_title = st.session_state.title
                                title_hahtags = re.findall(r'#\w+', full_title)
                                title_part1 = full_title + ' Part 1 '#full_title[:full_title.index(title_hahtags[0])] + 'Part 1 ' + full_title[full_title.index(title_hahtags[0]):]
                                title_part2 = full_title + ' Part 2 '#full_title[:full_title.index(title_hahtags[0])] + 'Part 2 ' + full_title[full_title.index(title_hahtags[0]):]
                                full_desc = st.session_state.description
                                desc_hashtags = re.findall(r'#\w+', full_desc)
                                if len(desc_hashtags) >= 10:
                                    tenth_hashtag_index = full_desc.index(desc_hashtags[9]) + len(desc_hashtags[9])
                                else:
                                    tenth_hashtag_index = len(full_desc)
                                desc_part1 = full_desc[:tenth_hashtag_index].strip()
                                desc_part2 = full_desc[:tenth_hashtag_index].strip()#[:full_desc.index(desc_hashtags[0])].strip() +"\n\n"+full_desc[tenth_hashtag_index:].strip()
                                with open(yt_desc_path1, 'w', newline='') as csvfile:
                                    fieldnames = ['title', 'description']
                                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                                    # Uncomment this line if you are creating the file for the first time
                                    writer.writeheader()
                                    
                                    writer.writerow({'title': title_part1, 'description': desc_part1})
 
                                with open(yt_desc_path2, 'w', newline='') as csvfile:
                                    fieldnames = ['title', 'description']
                                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                                    # Uncomment this line if you are creating the file for the first time
                                    writer.writeheader()
                                    
                                    writer.writerow({'title': title_part2, 'description': desc_part2})
                            else:
                                yt_desc_path = r'C:\Users\lodos\Desktop\FilmForge Python\FilmForge\generated_videos'+ f"\\{'_'.join(st.session_state.user_input.split())}_part1.csv"
                                with open(yt_desc_path, 'w', newline='') as csvfile:
                                    fieldnames = ['title', 'description']
                                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                                    # Uncomment this line if you are creating the file for the first time
                                    writer.writeheader()
                                    
                                    writer.writerow({'title': st.session_state.title, 'description': st.session_state.description})

                        except Exception as e:
                            st.error(
                                f'Error occurred while generating video: {e}')
        else:
            st.error(
                'Error: No JSON object to make a video out of. Click "Make OpenAICall" before this button.\
                    \nOr by pass it in advanced settings')  
        for row in cols:
            for column in row:
                column.write("")  # Add empty write statements to preserve the layout
