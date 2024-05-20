import streamlit as st
import zipfile
import os 
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from pathlib import Path
import subprocess
from docx import Document

st.set_page_config(
    page_title="Offline Transcription",
    layout="centered",
    initial_sidebar_state="auto"
)

if 'transcript' not in st.session_state:
    st.session_state['transcript'] = None
    st.session_state['transcript_success'] = False

@st.cache_resource(show_spinner="Transcribing...")
def transcription(audio_files, model, output, eo):
    transcript_files = []
    return_codes = []
    compression = zipfile.ZIP_DEFLATED
    zf = zipfile.ZipFile("transcripts.zip", mode="w")

    for i, audio_file in enumerate(audio_files):
    
        if output == 'pdf' or output == 'docx':
            temp_output = 'srt'
        else:
            temp_output = output

        if eo == 'yes':
            cmd = f'./Whisper-Faster-XXL/whisper-faster-xxl ./{str(audio_file)} --language English --model {model} --output_format {temp_output} --output_dir source'.split()
        else:
            cmd = f'./Whisper-Faster-XXL/whisper-faster-xxl ./{str(audio_file)} --model {model} --output_format {temp_output} --output_dir source'.split()      
        
        # try the transcription or throw an error
        #return_code = subprocess.run(cmd, shell=False)
        return_code = subprocess.run(cmd, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return_codes.append(return_code.check_returncode())

        transcript_file = Path(str(audio_file.parent.joinpath(audio_file.stem)) + '.' + temp_output)

        if output == 'pdf':
            text_width=A4[0] / 2
            text_height=A4[1] / 2
            x = A4[0]/4
            y = A4[1]/4

            # initializing variables with values 
            temp_transcript = str(audio_file.parent.joinpath(audio_file.stem)) + '.pdf'
            documentTitle = audio_file.stem

            # creating a pdf object 
            pdf = canvas.Canvas(temp_transcript, pagesize=A4) 

            # setting the title of the document 
            pdf.setTitle(documentTitle) 

            # creating a multiline text using  
            # textline and for loop
            styles = getSampleStyleSheet()
            text = pdf.beginText(40, 680) 
            text.setFont("Courier", 12) 
            text.setFillColor(colors.black) 
            with open(transcript_file, 'r') as f: 
                lines = f.readlines()
                
            for line in lines:
                p = Paragraph(line, styles["Normal"])
                p.wrapOn(pdf, text_width, text_height)
                p.drawOn(pdf, x, y)

            # saving the pdf 
            pdf.save()

        elif output == 'docx':
            temp_transcript = str(audio_file.parent.joinpath(audio_file.stem)) + '.docx'
            document = Document()
            with open(transcript_file, 'r') as f:
                lines = f.readlines()
                document.add_paragraph(lines)
            
            document.save(temp_transcript)

        # Zip the files
        if return_code.check_returncode() == None:
            zf.write(transcript_file, compress_type=compression)

        transcript_files.append(transcript_file)

        os.remove(audio_file)
        os.remove(transcript_file)

    zf.close()
        
    return return_codes, transcript_files

if __name__ == "__main__":
    # ------------------- Sidebar Information -------------------------
    st.title('Offline Transcription App')

    # UC banner
    st.sidebar.image('UCWhite.png')
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
    with st.form("setup-form", clear_on_submit=False):
        model_select = st.radio('Select a model', 
                        ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'],
                        index=3,
                        horizontal=True)
        eo = st.radio('English Only', 
                        ['yes', 'no'],
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
    for uploaded_file in uploaded_files: 
        if uploaded_file is not None:
            # write the audio file to a folder
            audio_file = Path('./audio').joinpath(uploaded_file.name)       
            with open(audio_file, 'wb') as f:
                f.write(uploaded_file.getbuffer())
                audio_files.append(audio_file)

    # Transcribe the audio files
    if eo == 'yes':
        model = model_select + '.en'
    else:
        model = model_select
    
    # Perform the transcription
    return_codes, transcript_files = transcription(audio_files, model, output_select, eo)

    for i, return_code in enumerate(return_codes):
        if return_code == None:
            st.success(transcript_files[i].name + " was successful") 
        else:
            st.warning("Something went wrong. Transcript" + transcript_files[i].name + 'failed' + "Please contact the eResearch Team. Or try refreshing the app.")

    # Download the transcript
    zip_file_path = Path('./transcripts.zip')
    if  not zip_file_path.is_file():
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
    # st.write(st.session_state)