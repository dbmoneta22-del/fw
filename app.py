from flask import Flask, request, send_file
from docx import Document
from PIL import Image
import pytesseract
import uuid

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("image")
        if not file:
            return "Nessun file caricato", 400

        img = Image.open(file.stream).convert("RGB")
        testo = pytesseract.image_to_string(img, lang="ita")

        doc = Document()
        doc.add_heading("Testo estratto dall'immagine", level=1)
        doc.add_paragraph(testo)

        out_path = f"/tmp/{uuid.uuid4()}.docx"
        doc.save(out_path)

        return send_file(out_path, as_attachment=True)

    return """
    <!doctype html>
    <html lang='it'>
    <head><meta charset='utf-8'><title>Foto → Word OCR</title></head>
    <body style='font-family:system-ui'>
        <h2>Foto → Word OCR</h2>
        <form method='POST' enctype='multipart/form-data'>
            <input type='file' name='image' required>
            <button type='submit'>Trascrivi</button>
        </form>
    </body>
    </html>
    """
