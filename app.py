from flask import Flask, request, send_file
from docx import Document
from PIL import Image
import pytesseract
import uuid
import os
import traceback
import shutil

# === TROVA TESSERACT AUTOMATICAMENTE ===
tesseract_path = shutil.which("tesseract")
if not tesseract_path:
    raise RuntimeError("❌ Tesseract non trovato nel sistema")

pytesseract.pytesseract.tesseract_cmd = tesseract_path

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            file = request.files.get("image")
            if not file:
                return "❌ Nessun file ricevuto", 400

            # Salvataggio temporaneo
            img_path = f"/tmp/{uuid.uuid4()}"
            file.save(img_path)

            # Apertura e normalizzazione immagine
            img = Image.open(img_path)
            img = img.convert("RGB")

            # OCR
            testo = pytesseract.image_to_string(img, lang="ita")

            # Word
            doc = Document()
            doc.add_heading("Testo estratto dall'immagine", level=1)
            doc.add_paragraph(testo if testo.strip() else "[Nessun testo rilevato]")

            out_path = f"/tmp/{uuid.uuid4()}.docx"
            doc.save(out_path)

            return send_file(out_path, as_attachment=True)

        except Exception:
            print("🔥 ERRORE OCR 🔥")
            print(traceback.format_exc())
            return "Errore interno durante la trascrizione. Controlla i log.", 500

    # HTML INLINE
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
            <input type="file" name="image" accept="image/*" required>
            <br><br>
            <button type="submit">Trascrivi e scarica Word</button>
        </form>
    </body>
    </html>
    """
