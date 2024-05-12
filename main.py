import streamlit as st
import os
from pathlib import Path
import whisper

def transcribe_audio(audio_file, model):
    result = model.transcribe(audio_file, fp16=False)
    transcript = result["text"]
    
    return transcript

@st.cache_resource
def load_model(model_name):
    model = whisper.load_model(model_name)

    return model

st.title('Offline Transcription App')

# Add a description in the sidebar
st.sidebar.title('About this app')
st.sidebar.write("""This app uses the offline Whisper ASR package to transcribe uploaded audio files. 
                 To Transcribe an audio file, you can drag and drop the file, or you can use the browse files button""")


st.sidebar.markdown("""For support, please contact the eResearch services using the 
                    [eResearch consultancy form](https://services.canterbury.ac.nz/uc?id=sc_cat_item&sys_id=8effe377db992510e447f561f396197c)""")


model_name = 'base'
model = load_model(model_name)

uploaded_file = st.file_uploader("Choose a transcription file")

if uploaded_file is not None:
    # write the audio file to a folder
    uploaded_file_path =Path('./audio').joinpath(uploaded_file.name)
    with open(uploaded_file_path, 'wb') as f:
        f. write(uploaded_file.getbuffer())
    
    with st.spinner('Transcribing...'):
        # Transcribe the audio file
        transcript = transcribe_audio(str(uploaded_file_path), model)
        st.success('Transcription complete!')


        # Display the transcript and provide a download link
        st.write(transcript)
    st.download_button(
        label="Download Transcript",
        data=transcript,
        file_name='transcript.txt',
        mime='text/plain',
    )