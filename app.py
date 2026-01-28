from flask import Flask, request, send_file, Response
from docx import Document
from docx.shared import Pt
from PIL import Image
import pytesseract
import uuid
import traceback
import sys
from datetime import datetime

app = Flask(__name__)

def add_row(table, label, value):
    row = table.add_row().cells
    row[0].text = label
    row[1].text = value if value else "—"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Dati anagrafici
            nome = request.form.get("nome", "")
            cf = request.form.get("cf", "")
            nascita = request.form.get("nascita", "")
            luogo = request.form.get("luogo", "")
            residenza = request.form.get("residenza", "")

            # Dati OSINT
            note_osint = request.form.get("note_osint", "")
            fonti = request.form.get("fonti", "")

            testo_ocr = ""
            file = request.files.get("image")
            if file and file.filename:
                img = Image.open(file.stream).convert("RGB")
                if max(img.size) > 2000:
                    img.thumbnail((2000, 2000))
                testo_ocr = pytesseract.image_to_string(img, lang="ita", config="--psm 6")

            doc = Document()

            doc.add_heading("RAPPORTO INFORMATIVO OSINT", level=0)
            doc.add_paragraph(f"Data generazione: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

            doc.add_heading("DATI ANAGRAFICI", level=1)
            tab_ana = doc.add_table(rows=1, cols=2)
            tab_ana.style = "Table Grid"
            add_row(tab_ana, "Nome e Cognome", nome)
            add_row(tab_ana, "Codice Fiscale", cf)
            add_row(tab_ana, "Data di nascita", nascita)
            add_row(tab_ana, "Luogo di nascita", luogo)
            add_row(tab_ana, "Residenza", residenza)

            doc.add_heading("DATI INVESTIGATI OSINT", level=1)
            tab_osint = doc.add_table(rows=1, cols=2)
            tab_osint.style = "Table Grid"
            add_row(tab_osint, "Informazioni rilevate", note_osint)
            add_row(tab_osint, "Fonti", fonti)

            doc.add_heading("TESTO ESTRATTO DA DOCUMENTI (OCR)", level=1)
            doc.add_paragraph(testo_ocr if testo_ocr.strip() else "Nessun testo rilevato.")

            doc.add_heading("NOTE FINALI", level=1)
            doc.add_paragraph(
                "Il presente rapporto è redatto esclusivamente sulla base di fonti aperte (OSINT). "
                "Le informazioni riportate devono essere verificate e non costituiscono prova legale."
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
        <title>Rapporto OSINT</title>
        <style>
            body{background:#0b1020;color:#e5e7eb;font-family:system-ui}
            .box{max-width:600px;margin:40px auto;background:#020617;padding:30px;border-radius:12px}
            h2{margin-top:20px;color:#38bdf8}
            label{font-size:13px}
            input, textarea{width:100%;margin-bottom:12px;padding:8px;border-radius:6px;border:none}
            button{width:100%;padding:12px;background:#22c55e;border:none;border-radius:8px;font-weight:600}
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Generatore Rapporto OSINT</h1>
            <form method="POST" enctype="multipart/form-data">
                <h2>Dati Anagrafici</h2>
                <label>Nome e Cognome</label><input name="nome">
                <label>Codice Fiscale</label><input name="cf">
                <label>Data di nascita</label><input name="nascita">
                <label>Luogo di nascita</label><input name="luogo">
                <label>Residenza</label><input name="residenza">

                <h2>Dati Investigati OSINT</h2>
                <label>Informazioni rilevate</label><textarea name="note_osint"></textarea>
                <label>Fonti</label><textarea name="fonti"></textarea>

                <h2>Documento (OCR opzionale)</h2>
                <input type="file" name="image" accept="image/*">

                <button type="submit">Genera Rapporto</button>
            </form>
        </div>
    </body>
    </html>
    """
