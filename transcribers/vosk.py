from pathlib import Path
import math
import subprocess
import json
import textwrap

from webvtt import WebVTT, Caption
from vosk import Model, KaldiRecognizer, SetLogLevel

# convert seconds to hms
def convert_to_hms(seconds: float) -> str:
    """Converts segment timestamp to hours:minuts:seconds:milliseconds"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = math.floor((seconds % 1) * 1000)
    output = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{milliseconds:03}"

    return output

def transcribe(audio_file_path, model, eo):
    """Uses vosk-api to transcribe audio file and writes the segments"""
    # set sample rate for model (16000) is desired
    SAMPLE_RATE = 16000

    # set LogLevel to -1 so that output isn't printed to terminal
    SetLogLevel(-1)
    
    # initialize the model and set the transcription to word level
    v_model = Model(lang="en-us")
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

        # create a webvtt using webvtt-py
        vtt = WebVTT()
        for _, res in enumerate(results):
            words = json.loads(res).get("result")
            if not words:
                continue

            start = convert_to_hms(words[0]["start"])
            end = convert_to_hms(words[-1]["end"])
            content = " ".join([w["word"] for w in words])

            caption = Caption(start, end, textwrap.fill(content))
            vtt.captions.append(caption)

        # Save transcription to appropriate file path
        tr_file_path = Path(audio_file_path + '.vtt')
        vtt.save(tr_file_path)

    return tr_file_path