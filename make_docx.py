from pathlib import Path
# importing modules 
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate

import numpy as np

text_width=A4[0] / 2
text_height=A4[1] / 2
x = A4[0]/4
y = A4[1]/4


transcript_file = list(Path('./audio').glob('*.srt'))[0]

# initializing variables with values 
fileName = 'sample.pdf'
documentTitle = 'sample'

# creating a pdf object 
pdf = SimpleDocTemplate(fileName)
styles = getSampleStyleSheet()

with open(transcript_file, 'r') as file:
    lines = file.readlines()

paragraphs = []

for i in np.arange(0, len(lines), 3):
    line = ''.join(lines[i:i+3]).replace('\n','<br/>\n')
    # line = line.replace('\n','<br/>\n')

    p = Paragraph(line, styles["Normal"])   
    p.wrapOn(pdf, text_width, text_height)
    paragraphs.append(p)

pdf.build(paragraphs)