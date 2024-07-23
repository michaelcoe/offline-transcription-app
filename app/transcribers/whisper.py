from pathlib import Path
import math
import faster_whisper

# convert seconds to hms
def convert_to_hms(seconds: float) -> str:
    """Converts segment timestamp to hours:minuts:seconds:milliseconds"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = math.floor((seconds % 1) * 1000)
    output = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{milliseconds:03}"

    return output

# convert segment to a srt like format
def convert_seg(segment: faster_whisper.transcribe.Segment) -> str:
    """Converts the segment into a string to be output into file"""
    return (f"{convert_to_hms(segment.start)} --> {convert_to_hms(segment.end)}\n"
            f"{segment.text.lstrip()}\n\n")

def transcribe(audio_file_path, model, eo):
    """Uses faster_whisper to transcribe audio file and writes the segments"""
    # initialize the model and set the transcription to word level
    fw_model = faster_whisper.WhisperModel(model, device="cpu", compute_type="int8")

    # Check if english only model happens
    if eo == 'yes':
        segments, _ = fw_model.transcribe(audio_file_path, language='en', beam_size=5,
                                          vad_filter=False)
    else:
        segments, _ = fw_model.transcribe(audio_file_path, beam_size=5, vad_filter=False)

    # write the webvtt file
    tr_file_path = Path(audio_file_path + '.vtt')
    with open(tr_file_path, 'w', encoding='utf-8') as tr:
        for i, segment in enumerate(segments, start=1):
            tr.write(f"{i}\n{convert_seg(segment)}")

    return tr_file_path