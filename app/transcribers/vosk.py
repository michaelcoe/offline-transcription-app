from pathlib import Path
import os
import math
import subprocess
import json
import urllib
import zipfile

from vosk import Model, KaldiRecognizer, SetLogLevel

# convert seconds to hms
def convert_to_hms(seconds: float) -> str:
    """Converts segment timestamp to hours:minuts:seconds:milliseconds"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = math.floor((seconds % 1) * 1000)
    output = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{milliseconds:03}"

    return output

def transcribe(audio_file_path, model, eo, ts):
    """Uses vosk-api to transcribe audio file and writes the segments"""
    # set sample rate for model (16000) is desired
    SAMPLE_RATE = 16000

    # set LogLevel to -1 so that output isn't printed to terminal
    SetLogLevel(-1)
    
    # initialize the model and set the transcription to word level
    cwd = Path(os.getcwd())
    if model == 'vosk-large' or model == 'vosk-large.en':
        path_to_model = cwd.joinpath("models/vosk/vosk-model-en-us-0.22")
        url = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
    else:
        path_to_model = cwd.joinpath("models/vosk/vosk-model-small-en-us-0.15")
        url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    
    # check if model exists, and download if it doesnt
    if path_to_model.is_dir():
        v_model = Model(str(path_to_model))
    else:
        path_to_model.parent.mkdir(parents=True, exist_ok=True)
        zip_file, _ = urllib.request.urlretrieve(url)
        with zipfile.ZipFile(zip_file, 'r') as zf:
            zf.extractall(path_to_model.parent)
        v_model = Model(str(path_to_model))        
    
    rec = KaldiRecognizer(v_model, SAMPLE_RATE)
    rec.SetWords(True)
    
    # converts audio/video with ffmpeg
    command = ["ffmpeg", "-nostdin", "-loglevel", "quiet", "-i", audio_file_path,
               "-ar", str(SAMPLE_RATE), "-ac", "1", "-f", "s16le", "-"]
    with subprocess.Popen(command, stdout=subprocess.PIPE) as process:

        # send the data through the model
        results = []
        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                results.append(rec.Result())
        results.append(rec.FinalResult())

    tr_file_path = Path(audio_file_path + '.vtt')
    with open(tr_file_path, 'w', encoding='utf-8') as tr:         
        i = 1 # counter for each segment
        for _, res in enumerate(results):
            words = json.loads(res).get("result")
            if not words:
                continue
            
            start = convert_to_hms(words[0]["start"])
            end = convert_to_hms(words[-1]["end"])
            content = " ".join([w["word"] for w in words])
            
            if ts == 'yes':
                tr.write(f"{i}\n" f"{start} --> {end}\n"
                            f"{content}\n\n")
                i += 1
            else:
                tr.write(f"{content}\n\n")
                
    return tr_file_path