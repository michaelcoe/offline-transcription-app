"""Streamlit Webapp to handle offline transcriptions"""
from pathlib import Path
from tempfile import NamedTemporaryFile

import codecs
import zipfile
import os
import uuid

from streamlit.runtime.scriptrunner import get_script_run_ctx
import streamlit as st

from converters import vtt2docx, vtt2pdf, vtt2txt
from transcribers import whisper, vosk

st.set_page_config(
    page_title="Offline Batch Transcriptions",
    layout="centered",
    initial_sidebar_state="auto"
)

# create transcript session state
if 'transcript' not in st.session_state:
    st.session_state['transcript'] = None

if 'export' not in st.session_state:
    st.session_state['export'] = 'vtt'

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = ''
    
# get IP of remote client
def get_remote_ip() -> str:
    """Returns the remote ip for this each session."""
    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None

        session_info = st.runtime.get_instance().get_client(ctx.session_id)
        st.session_state['session_id'] = str(uuid.uuid4())
        if session_info is None:
            return None
    except Exception as e:
        return None

    return session_info.request.remote_ip

# create ip address session state
if 'ip_address' not in st.session_state:
    st.session_state['ip_address'] = get_remote_ip()
    with open('connections.txt', 'a', encoding='utf-8') as cn:
        cn.write(st.session_state['ip_address'] + '\n')

# transcribe the audio
#@st.cache_resource(show_spinner="Transcribing...")
def transcription(audio_file_name, model):
    """Uses different packages to transcribe audio file and writes the segments"""
    if model[0:4] == 'vosk':
        st.session_state['transcript_file'] = vosk.transcribe(audio_file_name, model,
                                                             st.session_state['eo'],
                                                             st.session_state['ts'])
    else:
        st.session_state['transcript_file'] = whisper.transcribe(audio_file_name, model,
                                                                st.session_state['eo'],
                                                                st.session_state['ts'])

    with codecs.open(st.session_state['transcript_file'], encoding='utf-8') as file:
        data = file.read()

    st.session_state['transcript'] = data
    st.session_state['transcript_output'] = st.session_state['transcript_file']

    return True

# Convert the transcript to various forms
def convert_transcript(transcript_num):
    """If-else statement to send transcript to the proper converter script"""
    export = st.session_state['export']
    transcript_file = st.session_state['transcript_file']
    if export == 'pdf':
        st.session_state['transcript_output'] = vtt2pdf.convert(transcript_file,
                                                                st.session_state['transcript'])
    elif export == 'docx':
        st.session_state['transcript_output'] = vtt2docx.convert(transcript_file,
                                                                 st.session_state['transcript'])
    else:
        st.session_state['transcript_output'] = vtt2txt.convert(transcript_file,
                                                                st.session_state['transcript'],
                                                                export)

    return True

# Zip the files in a .zip file
def zipFiles(zip_file_path, transcript_file_paths):
    compression = zipfile.ZIP_DEFLATED
    zf = zipfile.ZipFile(zip_file_path, mode="w")
        
    # Zip the files
    for i, file_path in enumerate(transcript_file_paths):
        current_path = Path(file_path)
        new_path = current_path.rename(str(current_path.parent.joinpath('transcript_' + str(i+1) + current_path.suffix)))
        zf.write(new_path, compress_type=compression)
        os.remove(new_path)
    zf.close()

    return zip_file_path

if __name__ == "__main__":
    # ------------------- Sidebar Information -------------------------
    st.title('Offline Transcription Service')

    # UC banner
    st.sidebar.image('./img/UCWhite.png')

    # Add a description in the sidebar
    st.sidebar.title('About this app')
    st.sidebar.markdown("""This app uses the offline version of the openAI Whisper Automatic Speech
                        Recognition (ASR) package to transcribe uploaded audio or video files.
                        To transcribe an audio or video file, drag and drop the file, or you can use
                        the **Browse Files** button""")

    st.sidebar.subheader("Note")
    st.sidebar.markdown("""This Whisper ASR package has been trained using machine learning, but is
                        secure to use at UC. Your data will not be used to train future versions of
                        the app. All files are automatically deleted after closing the browser window.
                        Please ensure that you download the generated transcript file and save it in a
                        secure location. You should also save the original audio or video file in a
                        secure location.
                        """)

    st.sidebar.subheader("Support")
    st.sidebar.markdown("""Our eResearch consultants are on hand to support your use of this app and
                        for support with data storage. For support, please contact the eResearch team
                        using UC services [Offline Transcription Feedback and Issues](https://services.canterbury.ac.nz/uc?id=sc_cat_item&sys_id=728773f587d70a10a0840649dabb3597)""")

    # Model and audio file in a form
    with st.form("setup-form", clear_on_submit=True):
        model_select = st.radio('Select a model',
                        ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3',
                         'vosk-small', 'vosk-large'], key='model', index=5, horizontal=True,
                        help='Choose which model you want to use of transcription')
        
        eo = st.radio('English Only', ['yes', 'no'], key='eo', index=0, horizontal=True,
                      help='Choose only if the transcript is all in English')

        ts = st.radio('Include Time Stamps', ['yes', 'no'], key='ts', index=0, horizontal=True,
                      help='Should the transcription be labeled with timestamps')

        # File uploader
        uploaded_files = st.file_uploader(
            "Upload file you want to transcribe",
            accept_multiple_files=True,
        )

        output_select = st.radio('Select an output format',
                                ['vtt', 'txt', 'pdf', 'docx', 'json', 'lrc', 'tsv'],
                                key='output',
                                index=0,
                                horizontal=True)

        transcribe_btn = st.form_submit_button("Transcribe")
            

    if transcribe_btn:       
        # set the model
        if st.session_state['eo'] == 'yes':
            if st.session_state['model'].split('-')[0] == 'large':
                model = st.session_state['model']
            else:
                model = st.session_state['model'] + '.en'
        else:
            model = st.session_state['model']        
    
        # transcribe the audio for each file
        return_codes = []
        transcript_files = []
        with st.spinner("Transcribing!..."):
            # write the audio files into the temp folder
            for file_num, uploaded_file in enumerate(uploaded_files):
                if uploaded_file is not None:
                    # write to temporary file and get name    
                    with NamedTemporaryFile() as temp:
                        temp.write(uploaded_file.getvalue())
                        temp.seek(0)
                        audio_file = temp.name

                        return_code = transcription(audio_file, model)
                        return_codes.append(return_code)
                        convert_transcript(file_num)
                        transcript_files.append(st.session_state['transcript_output'])

        zip_file_path = zipFiles(st.session_state['session_id'] + '.zip', transcript_files)
        for i, return_code in enumerate(return_codes):
            if return_code:
                st.success('Transcript ' + str(i+1) + " was successful")
            else:
                st.warning("Something went wrong. Transcript " +
                           'Transcript ' + str(i+1) + ' failed. ' +
                           "Please contact the eResearch Team. Or try refreshing the app.")
        
        # Download the transcript
        with open(zip_file_path, 'rb') as f:
            download = st.download_button(
                    label='Download Transcript',
                    data = f,
                    file_name='transcripts.zip'
                    )
                   
            # remove the zipfile if it exists
            if zipfile.is_zipfile(zip_file_path):
                os.remove(zip_file_path)
            else:
                pass
    
    # st.write(st.session_state)
