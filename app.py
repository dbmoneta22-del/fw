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
            return "Nessun file", 400

        img = Image.open(file.stream).convert("RGB")

        testo = pytesseract.image_to_string(img, lang="ita")

        doc = Document()
        doc.add_heading("Testo estratto dall'immagine", level=1)
        doc.add_paragraph(testo)

        out = f"/tmp/{uuid.uuid4()}.docx"
        doc.save(out)

        return send_file(out, as_attachment=True)

    return """
    <html>
    <body style="font-family:system-ui">
        <h2>Foto → Word OCR</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="image" required>
            <button type="submit">Trascrivi</button>
        </form>
    </body>
    </html>
    """
