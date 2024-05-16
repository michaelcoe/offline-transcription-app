import streamlit as st
import os
import tempfile
from pathlib import Path
import subprocess
from docx import Document

@st.cache_resource
def transcription(audio_file, model, output):
    cmd = f'./Whisper-Faster-XXL/whisper-faster-xxl ./{str(audio_file)} --language English --model {model} --output_format {output} --output_dir source'.split()
            
    # try the transcription or throw an error
    #return_code = subprocess.run(cmd, shell=False)
    return_code = subprocess.run(cmd, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return return_code.check_returncode()

@st.cache_resource
def convert_transcript(audio_file, output_select):
    if output_select == 'docx':
        transcript_file = str(audio_file.parent.joinpath(audio_file.stem)) + '.txt'
        document = Document()
        with open(transcript_file) as f:
            for line in f:
                document.add_paragraph(line)
        download_doc = str(audio_file.parent.joinpath(audio_file.stem)) + '.docx'
        document.save(download_doc)

        mime='docx'

        os.remove(transcript_file)
        return download_doc, mime
    else:
        transcript_file = str(audio_file.parent.joinpath(audio_file.stem)) + '.' + output_select

        mime = 'text/plain'

        return transcript_file, mime

def delete_transcription(file):
    # remove the transcript file
    os.remove(file)

    return

# ------------------- Sidebar Information -------------------------
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

# ------------------------ Audio File form ---------------------------
st.write(st.session_state)

# Model and audio file in a form
with st.form("setup-form", clear_on_submit=True):
    model_select = st.radio('Select a model', 
                    ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'],
                    index=3,
                    horizontal=True)
    english_only = st.radio('English Only', 
                    ['yes', 'no'],
                    index=1,
                    horizontal=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload file you want to transcribe",
        accept_multiple_files=False,
    )

    output_select = st.radio('Select an output format',
                             ['srt', 'txt', 'docx'],
                             key='output',
                             index=2,
                             horizontal=True)
    
    transcribe_btn = st.form_submit_button("Transcribe")
    
if uploaded_file is not None:
    # write the audio file to a folder
    audio_file=Path('./audio').joinpath(uploaded_file.name)
    with open(audio_file, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
        # Transcribe the audio file
        if english_only == 'yes':
            model = model_select + '.en'
        else:
            model = model_select
        
        if output_select == 'docx':
            return_code = transcription(audio_file, model, 'txt')
        else:
            return_code = transcription(audio_file, model, output_select)

        if return_code == None:
            st.success('Transcription complete!')
            os.remove(audio_file)
        else:
            st.warning("Something went wrong. Please contact the eResearch Team. Or try refreshing the app.")

    # load the transcript
    transcript_file, mime = convert_transcript(audio_file, output_select)
    
    # Download the transcript
    with open(transcript_file, 'rb') as file:
        st.download_button(
                    label='Download Transcript',
                    data = file,
                    file_name=transcript_file,
                    mime=mime,
                    on_click=delete_transcription,
                    args=(transcript_file,)
                )