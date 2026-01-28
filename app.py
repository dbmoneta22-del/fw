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
                return "Nessun file ricevuto", 400

            img = Image.open(file.stream).convert("RGB")

            # 🔥 RIDIMENSIONA IMMAGINE (SALVA RAM)
            max_size = 2000
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size))

            testo = pytesseract.image_to_string(
                img,
                lang="ita",
                config="--psm 6"
            )

            doc = Document()
            doc.add_heading("Testo estratto dall'immagine", level=1)
            doc.add_paragraph(testo if testo.strip() else "[Nessun testo rilevato]")

            out = f"/tmp/{uuid.uuid4()}.docx"
            doc.save(out)

            return send_file(out, as_attachment=True)

        except Exception:
            err = traceback.format_exc()
            print(err, file=sys.stderr)
            return Response(f"<pre>{err}</pre>", status=500)

    return """
    <html>
    <body style="font-family:system-ui">
        <h2>Foto → Word OCR</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="image" accept="image/*" required>
            <button type="submit">Trascrivi</button>
        </form>
    </body>
    </html>
    """
