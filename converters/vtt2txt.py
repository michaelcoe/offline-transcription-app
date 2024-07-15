from pathlib import Path

def convert(transcript_file, transcript, extension):
    new_transcript = Path(str(transcript_file.parent.joinpath(transcript_file.stem)) + '.' + extension)
    
    with open(new_transcript, 'w') as tr:
        tr.write(transcript)
    
    return new_transcript