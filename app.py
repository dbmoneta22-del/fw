from flask import Flask, request, send_file
from docx import Document
from PIL import Image
import pytesseract
import uuid
import os

# === PATH TESSERACT (OBBLIGATORIO SU RENDER) ===
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Prende il file caricato
        file = request.files.get("image")
        if not file:
            return "Nessun file caricato", 400

        # Salva immagine temporanea
        img_path = f"/tmp/{uuid.uuid4()}.png"
        file.save(img_path)

        # OCR in italiano
        testo = pytesseract.image_to_string(
            Image.open(img_path),
            lang="ita"
        )

        # Crea Word
        doc = Document()
        doc.add_heading("Testo estratto dall'immagine", level=1)
        doc.add_paragraph(testo)

        out_path = f"/tmp/{uuid.uuid4()}.docx"
        doc.save(out_path)

        return send_file(out_path, as_attachment=True)

    # HTML INLINE (ZERO TEMPLATE, ZERO ERRORI)
    return """
    <!doctype html>
    <html lang="it">
    <head>
        <meta charset="utf-8">
        <title>Foto → Word OCR</title>
    </head>
    <body style="
        font-family:system-ui;
        background:#0f172a;
        color:white;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
    ">
        <form method="POST" enctype="multipart/form-data">
            <h2>Foto → Word OCR</h2>
            <input type="file" name="image" required>
            <br><br>
            <button type="submit">Trascrivi e scarica Word</button>
        </form>
    </body>
    </html>
    """
