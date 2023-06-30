import streamlit as st
from scripts.templates import *
from scripts.youtube import *
import pandas as pd
import os
import shutil

video_dir = 'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\generated_videos'
history_dir = 'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\history'

def page2():
    video_files_per_row = 3
    video_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]

    st.write(f"Displaying videos from: {video_dir}")
    st.write(f"Total number of videos found: {len(video_files)}")
    
    # Iterate over the video files
    for i in range(0, len(video_files), video_files_per_row):
        row_files = video_files[i:i+video_files_per_row]
        cols = st.columns(video_files_per_row)
        for j in range(video_files_per_row):
            with cols[j]:
                if j < len(row_files):
                    video_file = row_files[j]
                    video_path = os.path.join(video_dir, video_file)
                    cols[j].video(video_path, format='mp4')
                    
                    # Generate the corresponding CSV file path to be manipulated
                    csv_file_name = os.path.splitext(video_path)[0]
                    # We first split by the backslash to isolate the file name
                    path_parts = csv_file_name.split('\\')

                    # Then, we split the file name by the underscore to isolate the unique identifier
                    file_name_parts = path_parts[-1].split('_')

                    # We want to remove the last part of the file name (the unique identifier)
                    new_file_name = '_'.join(file_name_parts[:-1])

                    # We replace the old file name with the new one in the path parts
                    path_parts[-1] = new_file_name

                    # Finally, we join the path parts back together
                    csv_file_path = '\\'.join(path_parts) +'.csv'


                    with st.expander('Expand Meta Data'):
                        # Read the CSV file and extract the title and description
                        try:
                            df = pd.read_csv(csv_file_path)
                            title, description = df.iloc[0]['title'], df.iloc[0]['description']
                            st.write(f'Title: {title}')  
                            st.write(f'Description: {description}') 
                        except FileNotFoundError:
                            st.write('No corresponding CSV file found.')
                        except ValueError:
                            st.write('Unable to extract title and description from CSV file.')
                        except pd.errors.EmptyDataError:
                            st.write('CSV file is empty.')
                    
                    # Pick Youtube Channel
                    channel_choice = cols[j].selectbox(
                        "Pick YT channel", ('🟡top10countryrankings', '🔴Top10AnythingAndMore', '🟢HistoryTop10s', '🟣EverythinNature'), key=f"{video_file}_channel")
                    
                    authenticate_button = cols[j].button("Authenticate YouTube", key=f"{video_file}_auth")

                    if authenticate_button:
                        st.session_state[f"{video_file}_youtube"] = authenticate_youtube(channel_choice)
                        st.session_state[f"{video_file}_channel_category"] = get_channel_category(
                            channel_choice)

                    if cols[j].button("Upload to YouTube", key=f"{video_file}_upload"):
                        if f"{video_file}_youtube" not in st.session_state:
                            cols[j].error("You must authenticate YouTube before uploading.")
                        else:
                            cols[j].write(f'Uploading video with title: "{title}"')
                            csv_path = get_schedule_path(channel_choice)
                            last_upload_time = get_last_upload_time(csv_path)
                            next_slot = get_next_available_slot(last_upload_time)
                            print('Next available slot is:', next_slot)
                            response = upload_video(
                                st.session_state[f"{video_file}_youtube"], video_path, title, description, [], next_slot)
                            write_schedule_to_csv(next_slot, title, csv_path)
                            cols[j].write(f"Video uploaded, video id is: {response['id']}")

                             # If upload was successful, move video and CSV to history folder.
                            try:
                                shutil.move(video_path, history_dir)
                                shutil.move(csv_file_path, history_dir)
                                st.experimental_rerun()
                            except Exception as e:
                                cols[j].error(f"Failed to move files to history folder: {e}")
