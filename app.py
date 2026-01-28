
from flask import Flask, render_template, request, send_file
import pytesseract
from PIL import Image
from docx import Document
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]
        if file:
            filename = f"{uuid.uuid4()}.png"
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(image_path)

            text = pytesseract.image_to_string(Image.open(image_path), lang="ita")

            doc_name = f"{uuid.uuid4()}.docx"
            doc_path = os.path.join(OUTPUT_FOLDER, doc_name)

            doc = Document()
            doc.add_heading("Testo estratto dall'immagine", level=1)
            doc.add_paragraph(text)
            doc.save(doc_path)

            return send_file(doc_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
