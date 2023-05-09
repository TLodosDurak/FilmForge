# FilmForge

This script creates a ranking video of top 10 countries for a given topic. It uses the OpenAI API, the GPT-3 language model, to generate the ranking list with LangChain. The video is created using the MoviePy library, and the script also includes an implementation using Streamlit as the front-end. The script has the following features:

User provides a topic for the top 10 ranking.
The script uses the OpenAI API with the GPT-3 language model to generate the ranking list of top 10 countries for the given topic.
It allows users to upload background video and background music files.
It creates a video consisting of a title card and ranking frames using MoviePy, with each frame displaying a rank, country, and a short description.
The video is then displayed in the Streamlit front-end.
Main functions in the script are:

download_image: Downloads an image from a URL and saves it to the specified file path.
delete_media_files: Deletes temporary media files generated during video creation.
create_title_card: Creates a title card for the video.
create_ranking_frame: Creates a ranking frame for each entry in the ranking list.
create_video: Generates the final video with the ranking frames and title card.
remove_non_printable_chars: Removes non-printable characters from a string.
convert_openai_response: Converts the OpenAI API response into a ranking list.
main: The main function that runs the Streamlit app.
How the script works:

The user provides a topic for the top 10 ranking and uploads background video and background music files.
The user clicks on the "Generate Video" button.
The script generates the ranking list of top 10 countries for the given topic using the OpenAI API with the GPT-3 language model.
It then creates a video with the ranking list, background video files, and background music file using MoviePy.
The generated video is displayed in the Streamlit app.
