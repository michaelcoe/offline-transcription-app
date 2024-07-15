import numpy as np

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate

from pathlib import Path

def convert(transcript_file, transcript):
    new_transcript = Path(str(transcript_file.parent.joinpath(transcript_file.stem)) + '.pdf')
    
    text_width=A4[0] / 2
    text_height=A4[1] / 2

    # creating a pdf object 
    pdf = SimpleDocTemplate(str(new_transcript))
    styles = getSampleStyleSheet()

    lines = transcript.split('\n')
    # need to add carrage return for proper formatting
    for i, line in enumerate(lines):
        lines[i] = lines[i] + '\n'
    
    paragraphs = []

    for i in np.arange(0, len(lines), 3):
        line = ''.join(lines[i:i+3]).replace('\n','<br/>\n')
        # line = line.replace('\n','<br/>\n')

        p = Paragraph(line, styles["Normal"])   
        p.wrapOn(pdf, text_width, text_height)
        paragraphs.append(p)

    pdf.build(paragraphs)

    return new_transcript