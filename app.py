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
            file = request.files.get("image")
            if not file:
                return "Nessun file ricevuto", 400

            img = Image.open(file.stream).convert("RGB")

            max_size = 2000
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size))

            testo = pytesseract.image_to_string(
                img,
                lang="ita",
                config="--psm 6"
            )

            doc = Document()
            doc.add_heading("OSINT DOCUMENT ANALYSIS REPORT", level=0)

            doc.add_paragraph(f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
            doc.add_paragraph("Source: Image OCR Analysis")
            doc.add_paragraph("Classification: Open Source Intelligence (OSINT)")

            doc.add_paragraph("")

            doc.add_heading("1. Executive Summary", level=1)
            doc.add_paragraph(
                "This report contains text automatically extracted from a submitted image "
                "using Optical Character Recognition (OCR). The content reflects the source material."
            )

            doc.add_heading("2. Extracted Text", level=1)
            doc.add_paragraph(testo if testo.strip() else "[No readable text detected]")

            doc.add_heading("3. OSINT Analyst Notes", level=1)
            doc.add_paragraph(
                "• Cross-verify extracted data with additional sources.\n"
                "• OCR accuracy depends on image quality.\n"
                "• Handwritten or degraded text may reduce reliability."
            )

            doc.add_heading("4. Disclaimer", level=1)
            doc.add_paragraph(
                "This document was generated automatically and requires human validation."
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
        <title>OSINT OCR Engine</title>
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
                width:420px;
                box-shadow:0 0 40px rgba(0,0,0,.6);
            }
            h1{font-size:20px;margin-bottom:10px}
            p{font-size:13px;color:#94a3b8}
            input{width:100%;margin:20px 0}
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
            <h1>OSINT OCR ENGINE</h1>
            <p>Upload an image to generate a structured OSINT report.</p>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="image" accept="image/*" required>
                <button type="submit">Generate OSINT Report</button>
            </form>
            <footer>OSINT • Document Intelligence</footer>
        </div>
    </body>
    </html>
    """
