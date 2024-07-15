"""Streamlit Webapp to handle offline transcriptions"""
from pathlib import Path
from tempfile import NamedTemporaryFile

import math
import codecs
import zipfile
import os

from streamlit.runtime.scriptrunner import get_script_run_ctx
import streamlit as st
import faster_whisper

from converters import srt2docx, srt2pdf, srt2txt

st.set_page_config(
    page_title="Offline Batch Transcriptions",
    layout="centered",
    initial_sidebar_state="auto"
)

if 'transcript' not in st.session_state:
    st.session_state['transcript_success'] = False

if 'export' not in st.session_state:
    st.session_state['export'] = 'srt'

def get_remote_ip() -> str:
    """Returns the remote ip for this each session."""
    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None

        session_info = st.runtime.get_instance().get_client(ctx.session_id)
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

# convert seconds to hms
def convert_to_hms(seconds: float) -> str:
    """Converts segment timestamp to hours:minuts:seconds:milliseconds"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = math.floor((seconds % 1) * 1000)
    output = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

    return output

# convert segment to a srt like format
def convert_seg(segment: faster_whisper.transcribe.Segment) -> str:
    """Converts the segment into a string to be output into file"""
    return (f"{convert_to_hms(segment.start)} --> {convert_to_hms(segment.end)}\n"
            f"{segment.text.lstrip()}\n\n")

#@st.cache_resource(show_spinner="Transcribing...")
def transcription(audio_files, model):
    """Uses faster_whisper to transcribe multiple audio file and writes the segments"""
    transcript_files = []
    return_codes = []

    compression = zipfile.ZIP_DEFLATED
    zf = zipfile.ZipFile("transcripts.zip", mode="w")

    for i, audio_file in enumerate(audio_files):

        model = faster_whisper.WhisperModel(model, device="cpu", compute_type="int8")

        if st.session_state['eo'] == 'yes':
            segments, _ = model.transcribe(audio_file, language='en', beam_size=5, vad_filter=False)
        else:
            segments, _ = model.transcribe(audio_file, beam_size=5, vad_filter=False)

        transcript_file_path = Path(str(audio_file.stem) + '.srt')
        with open(transcript_file_path, 'w', encoding='utf-8') as t:
            for i, segment in enumerate(segments, start=1):
                t.write(f"{i}\n{convert_seg(segment)}")

        t.close()

        st.session_state['transcript_file'] = transcript_file_path

        with codecs.open(st.session_state['transcript_file'], encoding='utf-8') as file:
            data = file.read()

        st.session_state['transcript'] = data
        st.session_state['transcript_output'] = st.session_state['transcript_file']

        if st.session_state['export'] == 'pdf':
            st.session_state['transcript_output'] = srt2pdf.convert(transcript_file_path,
                                                                    st.session_state['transcript'])
        elif st.session_state['export'] == 'docx':
            st.session_state['transcript_output'] = srt2docx.convert(transcript_file_path,
                                                                    st.session_state['transcript'])
        else:
            st.session_state['transcript_output'] = srt2txt.convert(transcript_file_path,
                                                                    st.session_state['transcript'],
                                                                    st.session_state['export'])

        # Zip the files
        if return_code.check_returncode() is None:
            zf.write(transcript_file_path, compress_type=compression)

        transcript_files.append(transcript_file_path)
        return_codes.append(None)

        # Remove audio and transcript files
        os.remove(audio_file)
        os.remove(transcript_file_path)

    zf.close()

    return return_codes, transcript_files

if __name__ == "__main__":
    # ------------------- Sidebar Information -------------------------
    st.title('Offline Transcription App')

    # UC banner
    if Path('./UCWhite.png').is_file():
        st.sidebar.image('UCWhite.png')
    else:
        pass
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
                        using UC services [eResearch consultancy form](https://services.canterbury.ac.nz/uc?id=sc_cat_item&sys_id=8effe377db992510e447f561f396197c)""")

    # Model and audio file in a form
    with st.form("setup-form", clear_on_submit=False):
        model_select = st.radio('Select a model',
                        ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'],
                        index=3,
                        horizontal=True)
        eo = st.radio('English Only',
                        ['yes', 'no'],
                        key='eo',
                        index=1,
                        horizontal=True)

        # File uploader
        uploaded_files = st.file_uploader(
            "Upload file you want to transcribe",
            accept_multiple_files=True,
        )

        output_select = st.radio('Select an output format',
                                ['srt', 'txt', 'pdf', 'docx', 'json', 'vtt', 'lrc', 'tsv'],
                                key='output',
                                index=0,
                                horizontal=True)

        transcribe_btn = st.form_submit_button("Transcribe")

    audio_files = []
    if transcribe_btn:
        for uploaded_file in uploaded_files:
            if uploaded_file is not None:
                # write to temporary file and get name
                with NamedTemporaryFile() as temp:
                    temp.write(uploaded_file.getvalue())
                    temp.seek(0)
                    audio_files.append(temp.name)

                    # Transcribe the audio file
                    if st.session_state['eo'] == 'yes':
                        model = st.session_state['model'] + '.en'
                    else:
                        model = st.session_state['model']

        # Perform the transcription
        return_codes, transcript_files = transcription(audio_files, model)

        for i, return_code in enumerate(return_codes):
            if return_code is None:
                st.success(transcript_files[i].name + " was successful")
            else:
                st.warning("Something went wrong. Transcript" +
                           transcript_files[i].name + 'failed' +
                           "Please contact the eResearch Team. Or try refreshing the app.")

        # Download the transcript
        zip_file_path = Path('./transcripts.zip')
        if not zip_file_path.is_file():
            zf = zipfile.ZipFile(zip_file_path, mode="w")
            zf.close()
        else:
            pass

        with open(zip_file_path, 'rb') as f:
            st.download_button(
                    label='Download Transcript',
                    data = f,
                    file_name='transcripts.zip'
                    )

    # remove all files
    for transcript in transcript_files:
        if transcript.is_file():
            os.remove(transcript)

    for audio_file in audio_files:
        if audio_file.is_file():
            os.remove(audio_file)

    os.remove(zip_file_path)
    st.write(st.session_state)
