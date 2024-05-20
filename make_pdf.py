import lorem
# importing modules 
from reportlab.pdfgen import canvas 
from reportlab.lib import colors

s1 = lorem.sentence()
s2 = lorem.sentence()
s3 = lorem.sentence()

textLines = [s1, s2, s3]

# initializing variables with values 
fileName = 'sample.pdf'
documentTitle = 'sample'

# creating a pdf object 
pdf = canvas.Canvas(fileName) 

# setting the title of the document 
pdf.setTitle(documentTitle) 

# creating a multiline text using  
# textline and for loop 
text = pdf.beginText(40, 680) 
text.setFont("Courier", 12) 
text.setFillColor(colors.black) 
for line in textLines: 
    text.textLine(line) 
pdf.drawText(text) 

# saving the pdf 
pdf.save()