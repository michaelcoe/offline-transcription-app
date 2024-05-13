import streamlit as st
import os
from os import walk
from pathlib import Path
import whisper
import io
from docx import Document
import pandas as pd

# Transcribe the audio
def transcribe_audio(audio_file, model):
    result = model.transcribe(audio_file, fp16=False)
    transcript = result["text"]
    
    return transcript

# Load the AI model
@st.cache_resource
def load_model(model_name):
    model = whisper.load_model(model_name)

    return model

st.title('Offline Transcription App')

# Add a description in the sidebar
st.sidebar.title('About this app')
st.sidebar.markdown("""This app uses the offline version of the openAI Whisper Automatic Speech Recognition (ASR) package to transcribe uploaded audio or video files. 
                 To transcribe an audio or video file, drag and drop the file, or you can use the **Browse Files** button""")

st.sidebar.subheader("Note")
st.sidebar.markdown("""This Whisper ASR package has been trained using machine learning, but is secure to use at UC. Your data will not be used to train future versions 
                    of the app. All files are automatically deleted after closing the browser window. Please ensure that you download the generated transcript file and
                    save it in a secure location. You should also save the original audio or video file in a secure location.
                    """)

st.sidebar.subheader("Support")
st.sidebar.markdown("""Our eResearch consultants are on hand to support your use of this app and for support with data storage. For support, please contact the eResearch
                    team using UC services [eResearch consultancy form](https://services.canterbury.ac.nz/uc?id=sc_cat_item&sys_id=8effe377db992510e447f561f396197c)""")

col1, col2 = st.columns(2)
transcript_keys = []

# Model and audio file in a form
with st.form("my-form", clear_on_submit=True):
    model_select = st.radio('Select a model', 
                    ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'],
                    key='model',
                    index=1,
                    horizontal=True)
    english_only = st.radio('Select a model', 
                    ['yes', 'no'],
                    key='eo',
                    index=0,
                    horizontal=True)
    
    if english_only == 'yes':
        model = load_model(model_select + '.en')
    else:
        model = load_model(model_select)

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload some files",
        accept_multiple_files=False,
    )


    transcribe_btn = st.form_submit_button("Transcribe")

# save the keys
transcript_keys = []

if uploaded_file is not None:
    # write the audio file to a folder
    uploaded_file_path =Path('./audio').joinpath(uploaded_file.name)
    with open(uploaded_file_path, 'wb') as f:
        f. write(uploaded_file.getbuffer())
    
        with st.spinner('Transcribing...'):
            # Transcribe the audio file
            transcript = transcribe_audio(str(uploaded_file_path), model)
            transcript_name = uploaded_file_path.stem
            transcript_keys.append(transcript_name)
            # Initialization
            if transcript_name not in st.session_state:
                st.session_state[transcript_name] = transcript

            st.success('Transcription complete!')
            # Remove the audio file
            for file in os.listdir("./audio"):
                os.remove(os.path.join('./audio', file))
            
            # Display the transcript and provide a download link
            with st.expander("See the Transcript"):
                st.write(transcript)


    document = Document()
    paragraph = document.add_paragraph()
    download_doc = document.save('transcript.docx')

    # Download the transcript
    with open('transcript.docx', 'rb') as file:

        st.download_button(
                    label='Download Transcript',
                    data = file,
                    file_name='transcript.docx',
                    mime='docx'
                )
        
        os.remove("transcript.docx")