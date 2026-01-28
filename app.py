from flask import Flask, request, send_file, Response
from docx import Document
from PIL import Image
import pytesseract
import uuid
import traceback
import sys

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            file = request.files.get("image")
            if not file:
                return "❌ Nessun file ricevuto", 400

            # Apertura immagine sicura
            img = Image.open(file.stream)
            img = img.convert("RGB")

            # OCR
            testo = pytesseract.image_to_string(img, lang="ita")

            # Word
            doc = Document()
            doc.add_heading("Testo estratto dall'immagine", level=1)
            doc.add_paragraph(testo if testo.strip() else "[Nessun testo rilevato]")

            out = f"/tmp/{uuid.uuid4()}.docx"
            doc.save(out)

            return send_file(out, as_attachment=True)

        except Exception as e:
            # ERRORE VISIBILE IN PAGINA + LOG
            err = traceback.format_exc()
            print("🔥 ERRORE OCR 🔥", file=sys.stderr)
            print(err, file=sys.stderr)
            return Response(
                f"<pre>ERRORE:\n{err}</pre>",
                status=500,
                mimetype="text/html"
            )

    return """
    <!doctype html>
    <html lang="it">
    <head>
        <meta charset="utf-8">
        <title>Foto → Word OCR</title>
    </head>
    <body style="font-family:system-ui">
        <h2>Foto → Word OCR</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="image" accept="image/*" required>
            <button type="submit">Trascrivi</button>
        </form>
    </body>
    </html>
    """
