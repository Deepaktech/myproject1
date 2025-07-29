from flask import Flask, render_template, request, send_file
import os
from pdf2docx import Converter
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from docx import Document
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pdf-to-word', methods=['GET', 'POST'])
def pdf_to_word():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400

        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400

        if file and file.filename.lower().endswith('.pdf'):
            # Save uploaded PDF
            pdf_filename = f"{uuid.uuid4()}.pdf"
            pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
            file.save(pdf_path)

            # Convert to DOCX
            docx_filename = pdf_filename.replace('.pdf', '.docx')
            docx_path = os.path.join(CONVERTED_FOLDER, docx_filename)

            cv = Converter(pdf_path)
            cv.convert(docx_path, start=0, end=None)
            cv.close()

            return send_file(docx_path, as_attachment=True)

        return "Invalid file format", 400

    return render_template('pdf_to_word.html')






@app.route('/image-to-word', methods=['GET', 'POST'])
def image_to_word():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg']:
            return "Invalid image format", 400

        image_filename = f"{uuid.uuid4()}{ext}"
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        file.save(image_path)

        # OCR
        text = pytesseract.image_to_string(Image.open(image_path))

        # Save to Word
        docx_filename = image_filename.rsplit('.', 1)[0] + ".docx"
        docx_path = os.path.join(CONVERTED_FOLDER, docx_filename)

        document = Document()
        document.add_paragraph(text)
        document.save(docx_path)

        return send_file(docx_path, as_attachment=True)

    return render_template('image_to_word.html')


@app.route('/word-to-pdf')
def word_to_pdf():
    return render_template('word_to_pdf.html')

if __name__ == '__main__':
    app.run(debug=True)
