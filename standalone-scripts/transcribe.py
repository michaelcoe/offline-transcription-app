import faster_whisper
import subprocess
import math
from pathlib import Path
import time

def convert_to_hms(seconds: float) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = math.floor((seconds % 1) * 1000)
    output = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"
    return output

def convert_seg(segment: faster_whisper.transcribe.Segment) -> str:
    return f"{convert_to_hms(segment.start)} --> {convert_to_hms(segment.end)}\n{segment.text.lstrip()}\n\n"


model_size = "medium"

# Run on GPU with FP16
# model = WhisperModel(model_size, device="cuda", compute_type="float16")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
model = faster_whisper.WhisperModel(model_size, device="cpu", compute_type="int8")

start_time = time.time()

audio_file = Path('../audio').joinpath('test-recording.mkv')

segments, info = model.transcribe(str(audio_file), language='en', beam_size=2, vad_filter=False)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

with open(str(audio_file.stem) + '.srt', 'w') as t:
    for i, segment in enumerate(segments, start=1):
        t.write(f"{i}\n{convert_seg(segment)}")

t.close()

print(time.time() - start_time)
# return_code = subprocess.call(['./Whisper-Faster-XXL/whisper-faster-xxl', f'{str(audio_file)} --language English --model medium --output_dir source'], 
#                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# cmd = f'./Whisper-Faster-XXL/whisper-faster-xxl ./{str(audio_file)} --language English --model medium --output_format lrc --output_dir source'.split()
# return_code = subprocess.run(cmd, shell=False)
# return_code = subprocess.run(cmd, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# files = list(Path('./audio').rglob("*.srt"))
# for file in files:
#     print(file)