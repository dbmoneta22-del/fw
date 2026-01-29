
from flask import Flask, request, send_file, render_template_string
from docx import Document
from docx.shared import Pt
from PIL import Image
import pytesseract, uuid, os
from datetime import datetime

app = Flask(__name__)

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    testo_ocr = ""
    data = {
        "nome":"", "cf":"", "nascita":"", "luogo":"", "residenza":"",
        "intervista":"", "lavoro":"", "telefoni":"", "immobili":"", "veicoli":""
    }
    auto = {}

    if request.method == "POST":
        for k in data:
            data[k] = request.form.get(k,"")

        file = request.files.get("image")
        if file and file.filename:
            img = Image.open(file.stream).convert("RGB")
            img.thumbnail((2000,2000))
            testo_ocr = pytesseract.image_to_string(img, lang="ita", config="--psm 6")

        for k in ["intervista","lavoro","telefoni","immobili","veicoli"]:
            if not data[k] and testo_ocr.strip():
                data[k] = testo_ocr
                auto[k] = True
            else:
                auto[k] = False

        if "preview" in request.form:
            return render_template_string(PREVIEW_HTML, data=data, auto=auto)

        doc = Document()
        style = doc.styles['Normal']
        style.font.name = 'Calibri'
        style.font.size = Pt(11)

        doc.add_heading("RAPPORTO INFORMATIVO OSINT", 0)
        doc.add_paragraph(f"Data generazione: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        def section(title, keys):
            doc.add_heading(title, level=1)
            table = doc.add_table(rows=1, cols=2)
            table.style = "Table Grid"
            for k in keys:
                row = table.add_row().cells
                row[0].text = k.replace('_',' ').upper()
                row[1].text = data[k] or "—"

        section("DATI ANAGRAFICI", ["nome","cf","nascita","luogo","residenza"])
        section("DATI INVESTIGATI OSINT", ["intervista","lavoro","telefoni","immobili","veicoli"])

        doc.add_heading("TESTO OCR ORIGINALE", level=1)
        doc.add_paragraph(testo_ocr or "—")

        filename = f"report_osint_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.docx"
        path = os.path.join(REPORTS_DIR, filename)
        doc.save(path)
        return send_file(path, as_attachment=True)

    return render_template_string(FORM_HTML)

FORM_HTML = """
<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>OSINT Report Professionale</title>
<style>
body{
    background:#0b1220;
    color:#e5e7eb;
    font-family:system-ui;
}
.wrapper{
    max-width:1000px;
    margin:40px auto;
    background:#020617;
    padding:40px;
    border-radius:18px;
    box-shadow:0 25px 60px rgba(0,0,0,.6)
}
h1{
    color:#38bdf8;
    margin-bottom:10px;
}
.section-title{
    margin-top:30px;
    margin-bottom:10px;
    font-size:14px;
    letter-spacing:.08em;
    color:#94a3b8;
}
.grid{
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:14px;
}
input, textarea{
    padding:12px;
    border-radius:10px;
    border:none;
    background:#020617;
    color:#e5e7eb;
    outline:1px solid #1e293b;
}
textarea{
    grid-column:1/3;
    min-height:90px;
}
.actions{
    display:flex;
    gap:16px;
    margin-top:30px;
}
button{
    flex:1;
    padding:16px;
    border-radius:12px;
    border:none;
    font-weight:700;
    cursor:pointer;
    font-size:15px;
}
.preview{
    background:#38bdf8;
    color:#020617;
}
.generate{
    background:#22c55e;
    color:#020617;
}
</style>
</head>
<body>
<div class="wrapper">
<h1>Generatore Rapporto OSINT</h1>
<form method="POST" enctype="multipart/form-data">

<div class="section-title">DATI ANAGRAFICI</div>
<div class="grid">
<input name="nome" placeholder="Nome e Cognome">
<input name="cf" placeholder="Codice Fiscale">
<input name="nascita" placeholder="Data di nascita">
<input name="luogo" placeholder="Luogo di nascita">
<input name="residenza" placeholder="Residenza">
</div>

<div class="section-title">DATI INVESTIGATI OSINT</div>
<div class="grid">
<textarea name="intervista" placeholder="Intervista Web"></textarea>
<textarea name="lavoro" placeholder="Rapporto lavorativo"></textarea>
<textarea name="telefoni" placeholder="Numeri di telefono"></textarea>
<textarea name="immobili" placeholder="Immobili intestati"></textarea>
<textarea name="veicoli" placeholder="Veicoli intestati"></textarea>
</div>

<div class="section-title">DOCUMENTO</div>
<input type="file" name="image" accept="image/*">

<div class="actions">
<button name="preview" class="preview">Anteprima</button>
<button type="submit" class="generate">Genera Report</button>
</div>

</form>
</div>
</body>
</html>
"""

PREVIEW_HTML = """
<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>Anteprima</title>
<style>
body{background:#0b1220;color:#e5e7eb;font-family:system-ui}
table{
    width:90%;
    margin:40px auto;
    border-collapse:collapse;
    background:#020617;
}
td{
    border:1px solid #1e293b;
    padding:12px;
}
.auto{background:#facc15;color:#020617}
.manual{background:#020617}
</style>
</head>
<body>
<h2 style="text-align:center">Anteprima Rapporto OSINT</h2>
<table>
{% for k,v in data.items() %}
<tr class="{{ 'auto' if auto.get(k) else 'manual' }}">
<td>{{k.replace('_',' ').upper()}}</td>
<td>{{v or '—'}}</td>
</tr>
{% endfor %}
</table>
<form method="POST" style="text-align:center">
{% for k,v in data.items() %}
<input type="hidden" name="{{k}}" value="{{v}}">
{% endfor %}
<button type="submit" class="generate">Conferma e genera report</button>
</form>
</body>
</html>
"""
