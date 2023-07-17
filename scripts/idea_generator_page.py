import streamlit as st
from scripts.youtube import *
import random
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from scripts.templates import idea_template

def page3():
    llm = OpenAI(model_name='text-davinci-003', temperature=1) #gpt-4

    idea_chain = LLMChain(llm=llm, prompt=idea_template, verbose=True)

    if 'ideas' not in st.session_state:
        st.session_state.ideas = ['Click Get Video List for ideas related to your channel!']
    
    colors = ["black","grey"] #"red", "blue", "green", "purple", "orange",

    # Pick Youtube Channel
    channel_choice = st.selectbox(
        "Pick YT channel to get ideas for", ('🟡top10countryrankings', '🔴Top10AnythingAndMore', '🟢HistoryTop10s', '🟣EverythinNature'))
    authenticate_button = st.button("Get Video List")
    if authenticate_button:
        # Get the channel ID by authenticating as the chosen channel
        youtube = authenticate_youtube(channel_choice)
        channel_id = youtube.channels().list(mine=True, part='id').execute()['items'][0]['id']
        list_of_shorts = list_uploaded_shorts(channel_id)
        sample_size = min(25, len(list_of_shorts))  # Adjust sample size if list is smaller
        random_sample = random.sample(list_of_shorts, sample_size)
        result = idea_chain.run({"list":  random_sample})
        ideas = result.strip().split('\n')  # replace ',' with your separator
        st.write("Suggested Ideas:")
        # Store new ideas in session state
        st.session_state.ideas = ideas

    # Display previously generated ideas on page load
    for index, idea in enumerate(st.session_state.ideas):
        color = colors[index % len(colors)]  # cycle through colors
        st.markdown(f"<div style='background-color:{color}; border:1px solid black; padding:10px; margin:5px;'>{idea}</div>", unsafe_allow_html=True)
