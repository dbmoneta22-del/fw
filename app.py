from flask import Flask, request, send_file, Response
from docx import Document
from PIL import Image
import pytesseract
import uuid
import traceback
import sys
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            subject_name = request.form.get("subject_name", "")
            subject_type = request.form.get("subject_type", "")
            analyst_notes = request.form.get("analyst_notes", "")

            testo = ""

            file = request.files.get("image")
            if file and file.filename:
                img = Image.open(file.stream).convert("RGB")
                max_size = 2000
                if max(img.size) > max_size:
                    img.thumbnail((max_size, max_size))
                testo = pytesseract.image_to_string(img, lang="ita", config="--psm 6")

            doc = Document()
            doc.add_heading("OSINT INVESTIGATION REPORT", level=0)

            doc.add_paragraph(f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
            doc.add_paragraph(f"Target: {subject_name}")
            doc.add_paragraph(f"Target Type: {subject_type}")
            doc.add_paragraph("Classification: Open Source Intelligence (OSINT)")

            doc.add_heading("1. Scope of Analysis", level=1)
            doc.add_paragraph(
                "This OSINT report was generated based on user-provided data and optional document analysis."
            )

            doc.add_heading("2. User Provided Information", level=1)
            doc.add_paragraph(analyst_notes if analyst_notes else "No additional information provided.")

            doc.add_heading("3. Extracted Text (OCR)", level=1)
            doc.add_paragraph(testo if testo.strip() else "[No OCR data available]")

            doc.add_heading("4. Analyst Observations", level=1)
            doc.add_paragraph(
                "All extracted and provided data should be cross-verified using independent open sources."
            )

            doc.add_heading("5. Disclaimer", level=1)
            doc.add_paragraph(
                "This report is automatically generated and does not constitute legal or investigative advice."
            )

            out = f"/tmp/{uuid.uuid4()}.docx"
            doc.save(out)

            return send_file(out, as_attachment=True)

        except Exception:
            err = traceback.format_exc()
            print(err, file=sys.stderr)
            return Response(f"<pre>{err}</pre>", status=500)

    return """
    <!doctype html>
    <html lang='it'>
    <head>
        <meta charset='utf-8'>
        <title>OSINT Report Generator</title>
        <style>
            body{
                margin:0;
                font-family:system-ui;
                background:#0b1020;
                color:#e5e7eb;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
            }
            .box{
                background:#020617;
                padding:40px;
                border-radius:14px;
                width:460px;
                box-shadow:0 0 40px rgba(0,0,0,.6);
            }
            h1{font-size:20px;margin-bottom:10px}
            label{font-size:12px;color:#94a3b8}
            input, textarea{
                width:100%;
                margin:8px 0 16px 0;
                padding:8px;
                border-radius:6px;
                border:none;
            }
            textarea{resize:vertical}
            button{
                width:100%;
                padding:12px;
                background:#22c55e;
                border:none;
                border-radius:8px;
                font-weight:600;
            }
            footer{
                margin-top:15px;
                font-size:11px;
                text-align:center;
                color:#64748b;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>OSINT REPORT GENERATOR</h1>
            <form method="POST" enctype="multipart/form-data">
                <label>Target Name / Entity</label>
                <input type="text" name="subject_name" placeholder="Nome persona / azienda">

                <label>Target Type</label>
                <input type="text" name="subject_type" placeholder="Persona, Azienda, Dominio, Email">

                <label>Analyst Notes / Known Data</label>
                <textarea name="analyst_notes" rows="4" placeholder="Inserisci informazioni note..."></textarea>

                <label>Optional Document (OCR)</label>
                <input type="file" name="image" accept="image/*">

                <button type="submit">Generate OSINT Report</button>
            </form>
            <footer>OSINT • Intelligence • Analysis</footer>
        </div>
    </body>
    </html>
    """
