
from pathlib import Path
from tempfile import NamedTemporaryFile
import math
import codecs

from streamlit.runtime.scriptrunner import get_script_run_ctx
import streamlit as st
import faster_whisper

from converters import srt2docx, srt2pdf, srt2txt

# set the details of the page
st.set_page_config(
    page_title="Offline Transcription",
    layout="centered",
    initial_sidebar_state="auto"
)

# create transcript session state
if 'transcript' not in st.session_state:
    st.session_state['transcript'] = None

if 'export' not in st.session_state:
    st.session_state['export'] = 'srt'
    st.session_state['disabled'] = True

# create dummy transcript file if doesn't exist.
if 'transcript_file' not in st.session_state:
    Path('./audio').mkdir(parents=True, exist_ok=True)
    transcript_file_path = Path('./audio/transcript.srt')
    with open(transcript_file_path, 'w+') as tt:
        tt.write(" ")

    st.session_state['transcript_file'] = transcript_file_path
    st.session_state['transcript_output'] = st.session_state['transcript_file']

def get_remote_ip() -> str:
    """Get remote ip."""

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
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = math.floor((seconds % 1) * 1000)
    output = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

    return output

# convert segment to a srt like format
def convert_seg(segment: faster_whisper.transcribe.Segment) -> str:
    return (f"{convert_to_hms(segment.start)} --> {convert_to_hms(segment.end)}\n"
            f"{segment.text.lstrip()}\n\n")

# transcribe the audio
#@st.cache_resource(show_spinner="Transcribing...")
def transcription(audio_file_name, model):

    fw_model = faster_whisper.WhisperModel(model, device="cpu", compute_type="int8")

    if st.session_state['eo'] == 'yes':
        segments, _ = fw_model.transcribe(audio_file_name, language='en', beam_size=5, vad_filter=False)
    else:
        segments, _ = fw_model.transcribe(audio_file_name, beam_size=5, vad_filter=False)

    tr_file_path = Path(audio_file_name + '.srt')
    with open(transcript_file_path, 'w', encoding='utf-8') as tr:
        for i, segment in enumerate(segments, start=1):
            tr.write(f"{i}\n{convert_seg(segment)}")

    tr.close()

    st.session_state['transcript_file'] = tr_file_path

    with codecs.open(st.session_state['transcript_file'], encoding='utf-8') as file:
        data = file.read()

    st.session_state['transcript'] = data
    st.session_state['transcript_output'] = st.session_state['transcript_file']

    return True

# Convert the transcript to various forms
def convert_transcript():
    export = st.session_state['export']
    transcript_file = st.session_state['transcript_file']
    if export == 'pdf':
        st.session_state['transcript_output'] = srt2pdf.convert(transcript_file, 
                                                                st.session_state['transcript'])
    elif export == 'docx':
        st.session_state['transcript_output'] = srt2docx.convert(transcript_file, 
                                                                 st.session_state['transcript'])
    else:
        st.session_state['transcript_output'] = srt2txt.convert(transcript_file, 
                                                                st.session_state['transcript'], export)

    return True

if __name__ == "__main__":
    # ------------------- Sidebar Information -------------------------
    st.title('Offline Transcription Service')

    # UC banner
    if Path('./UCWhite.png').is_file():
        st.sidebar.image('UCWhite.png')
    else:
        pass
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
    
    # Model and audio file in a form
    with st.form("setup-form", clear_on_submit=True):
        model_select = st.radio('Select a model', 
                        ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'],
                        key='model',
                        index=3,
                        horizontal=True)
        eo = st.radio('English Only', 
                        ['yes', 'no'],
                        key='eo',
                        index=1,
                        horizontal=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload file you want to transcribe",
            accept_multiple_files=False,
        )

        transcribe_btn = st.form_submit_button("Transcribe")

    if transcribe_btn: 
        if uploaded_file is not None:
            # write to temporary file and get name           
            with NamedTemporaryFile() as temp:
                temp.write(uploaded_file.getvalue())
                temp.seek(0)
                audio_file = temp.name

                # Transcribe the audio file
                if st.session_state['eo'] == 'yes':
                    model = st.session_state['model'] + '.en'
                else:
                    model = st.session_state['model']

                with st.spinner("Transcribing!..."):
                    RETURN_CODE = transcription(audio_file, model)

                if RETURN_CODE:
                    st.success('Transcription complete!')
                    st.session_state['disabled'] = False              
                else:
                    st.warning("Something went wrong. Please contact the eResearch Team. Or try refreshing the app.")

                with st.expander(label='Preview the transcript'):
                    st.write(st.session_state['transcript'])

    # Output widgets
    col1, col2 = st.columns(2)

    with col1:
        export_select = st.selectbox('Select your file export format',
                            ['srt', 'txt', 'docx', 'pdf', 'vtt', 'lrc', 'tsv'],
                            key='export',
                            index=0,
                            on_change=convert_transcript,
                            disabled=st.session_state['disabled'],
                            )

        if st.session_state['export'] == 'docx':
            MIME = 'docx'
        elif st.session_state['export'] == 'json':
            MIME = 'application/json'
        elif st.session_state['export'] == 'pdf':
            MIME = 'application/octet-stream'
        else:
            MIME = 'text/plain'

    with col2:
        st.write(" ")
        st.write(" ")
        with open(st.session_state['transcript_output'], 'rb') as f:
            download = st.download_button(
                        label='Download Transcript',
                        data = f,
                        file_name=st.session_state['transcript_output'].name,
                        MIME = MIME,
                        disabled=st.session_state['disabled'],
                        )

            # if download:
            #     os.remove(st.session_state['transcript_output'])

    st.write(st.session_state)
