import sys, os, io, tempfile
from flask import Flask, request, render_template_string, send_file
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF

client = Groq(api_key="your-groq api(free)")

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Text Summarizer</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh;display:flex;justify-content:center;padding:2rem 1rem}
.container{max-width:720px;width:100%}
h1{font-size:2rem;font-weight:700;margin-bottom:.5rem;color:#38bdf8}
p.sub{color:#94a3b8;margin-bottom:.25rem}
.tabs{display:flex;gap:.5rem;margin-bottom:1.5rem;border-bottom:1px solid #334155;padding-bottom:.75rem}
.tab{padding:.5rem 1.25rem;border-radius:6px;border:1px solid #334155;background:transparent;color:#94a3b8;cursor:pointer;font-size:.9rem;transition:all .2s}
.tab.active{background:#38bdf8;color:#0f172a;border-color:#38bdf8;font-weight:600}
.tab:hover:not(.active){border-color:#38bdf8;color:#e2e8f0}
.tab-content{display:none}
.tab-content.active{display:block}
textarea{width:100%;min-height:220px;padding:1rem;border-radius:10px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;font-size:.95rem;resize:vertical;font-family:inherit}
textarea:focus{outline:none;border-color:#38bdf8}
.upload-zone{width:100%;min-height:220px;border:2px dashed #334155;border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1rem;cursor:pointer;transition:all .2s;padding:2rem;text-align:center}
.upload-zone:hover,.upload-zone.dragover{border-color:#38bdf8;background:#1e293b}
.upload-zone.has-file{border-color:#22c55e;background:#1e293b}
.upload-zone input{display:none}
.upload-zone .icon{font-size:2.5rem;color:#38bdf8}
.upload-zone .hint{color:#94a3b8;font-size:.9rem}
.upload-zone .fname{color:#22c55e;font-size:.9rem;font-weight:500}
button{margin-top:1rem;padding:.75rem 2rem;background:#38bdf8;color:#0f172a;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;transition:background .2s}
button:hover{background:#7dd3fc}
button:disabled{opacity:.6;cursor:not-allowed}
.spinner{display:none}
button.loading .spinner{display:inline-block}
button.loading .label{display:none}
.result{margin-top:1.5rem;padding:1.25rem;border-radius:10px;background:#1e293b;border:1px solid #334155;line-height:1.6}
.result h2{font-size:1.1rem;color:#38bdf8;margin-bottom:.75rem}
.result ul{padding-left:1.5rem}
.result li{margin-bottom:.4rem}
.error{color:#f87171}
.dl-btn{display:inline-flex;align-items:center;gap:.5rem;margin-top:1rem;padding:.5rem 1.25rem;background:#22c55e;color:#0f172a;border:none;border-radius:6px;font-size:.9rem;font-weight:600;cursor:pointer;text-decoration:none;transition:background .2s}
.dl-btn:hover{background:#4ade80}
@media(max-width:480px){body{padding:1rem}h1{font-size:1.5rem}}
</style>
</head>
<body>
<div class="container">
<h1>&#9889; Text Summarizer</h1>
<p class="sub">Summarize text or PDF files with bullet points &mdash; powered by Groq AI</p>
<div class="tabs">
<div class="tab active" data-tab="text">Text</div>
<div class="tab" data-tab="pdf">PDF</div>
</div>

<div id="tab-text" class="tab-content active">
<form id="form-text">
<textarea id="input" placeholder="Paste your text here..."></textarea>
<button type="submit" id="btn-text"><span class="label">Summarize</span><span class="spinner">Summarizing...</span></button>
</form>
</div>

<div id="tab-pdf" class="tab-content">
<form id="form-pdf">
<div class="upload-zone" id="dropzone">
<div class="icon">&#128196;</div>
<div class="hint">Click or drop a PDF file here</div>
<div class="fname" id="fname" style="display:none"></div>
<input type="file" id="pdf-input" accept=".pdf">
</div>
<button type="submit" id="btn-pdf"><span class="label">Summarize PDF</span><span class="spinner">Summarizing...</span></button>
</form>
</div>

<div id="result" class="result" style="display:none"></div>
</div>

<script>
const tabs=document.querySelectorAll(".tab"),tabContents=document.querySelectorAll(".tab-content");
tabs.forEach(t=>{t.addEventListener("click",()=>{
tabs.forEach(x=>x.classList.remove("active"));tabContents.forEach(x=>x.classList.remove("active"));
t.classList.add("active");document.getElementById("tab-"+t.dataset.tab).classList.add("active");
document.getElementById("result").style.display="none"})});

const dz=document.getElementById("dropzone"),pdfInput=document.getElementById("pdf-input"),fname=document.getElementById("fname");
dz.addEventListener("click",()=>pdfInput.click());
dz.addEventListener("dragover",e=>{e.preventDefault();dz.classList.add("dragover")});
dz.addEventListener("dragleave",()=>dz.classList.remove("dragover"));
dz.addEventListener("drop",e=>{e.preventDefault();dz.classList.remove("dragover");
if(e.dataTransfer.files.length){pdfInput.files=e.dataTransfer.files;handleFile()}});
pdfInput.addEventListener("change",handleFile);
function handleFile(){const f=pdfInput.files[0];if(f&&f.type==="application/pdf"){
fname.textContent="&#10003; "+f.name;fname.style.display="block";dz.classList.add("has-file")
}else{fname.style.display="none";dz.classList.remove("has-file")}}

document.getElementById("form-text").addEventListener("submit",async e=>{
e.preventDefault();const text=document.getElementById("input").value.trim();if(!text)return;
const btn=document.getElementById("btn-text");btn.classList.add("loading");btn.disabled=true;
const res=document.getElementById("result");res.style.display="none";
try{
const r=await fetch("/summarize",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text})});
const data=await r.json();
if(r.ok){res.innerHTML=data.summary+'<br><a class="dl-btn" href="/download" target="_blank">&#128196; Download as PDF</a>';res.className="result"}
else{res.innerHTML="<h2>Error</h2><p class='error'>"+(data.error||"Something went wrong")+"</p>";res.className="result error"}}
catch(e){res.innerHTML="<h2>Error</h2><p class='error'>Network error: "+(e.message||"")+"</p>";res.className="result error"}
res.style.display="block";btn.classList.remove("loading");btn.disabled=false});

document.getElementById("form-pdf").addEventListener("submit",async e=>{
e.preventDefault();const f=pdfInput.files[0];if(!f)return;
const btn=document.getElementById("btn-pdf");btn.classList.add("loading");btn.disabled=true;
const res=document.getElementById("result");res.style.display="none";
try{
const fd=new FormData();fd.append("file",f);
const r=await fetch("/summarize",{method:"POST",body:fd});
const data=await r.json();
if(r.ok){res.innerHTML=data.summary+'<br><a class="dl-btn" href="/download" target="_blank">&#128196; Download as PDF</a>';res.className="result"}
else{res.innerHTML="<h2>Error</h2><p class='error'>"+(data.error||"Something went wrong")+"</p>";res.className="result error"}}
catch(e){res.innerHTML="<h2>Error</h2><p class='error'>Network error: "+(e.message||"")+"</p>";res.className="result error"}
res.style.display="block";btn.classList.remove("loading");btn.disabled=false});
</script>
</body>
</html>"""

app = Flask(__name__)
_last_summary = ""

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def summarize_text(text):
    prompt = f"Summarize the following text in bullet points (each point as a <li> item, wrapped in a single <ul>). Keep it concise and cover all key points:\n\n{text}"
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    content = completion.choices[0].message.content
    if not content.startswith("<ul>"):
        lines = [l.strip().strip("-*").strip() for l in content.split("\n") if l.strip()]
        content = "<ul>" + "".join(f"<li>{l}</li>" for l in lines if l) + "</ul>"
    return content

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/summarize", methods=["POST"])
def handle_summarize():
    global _last_summary
    if request.content_type and "multipart/form-data" in request.content_type:
        if "file" not in request.files:
            return {"error": "No file uploaded"}, 400
        f = request.files["file"]
        if f.filename == "" or not f.filename.lower().endswith(".pdf"):
            return {"error": "Please upload a PDF file"}, 400
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(f.read())
        tmp.close()
        try:
            text = extract_text_from_pdf(tmp.name)
        finally:
            os.unlink(tmp.name)
        if not text.strip():
            return {"error": "Could not extract text from PDF"}, 400
    else:
        data = request.get_json(force=True)
        text = data.get("text", "").strip()
        if not text:
            return {"error": "No text provided"}, 400
    try:
        summary = summarize_text(text)
        _last_summary = summary
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/download")
def download():
    global _last_summary
    if not _last_summary:
        return {"error": "No summary available"}, 400
    import re
    plain = re.sub(r"<[^>]+>", "", _last_summary).strip()
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", "", "C:/Windows/Fonts/arial.ttf")
    pdf.set_font("Arial", "", 16)
    pdf.cell(0, 10, "Summary", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 11)
    for line in plain.split("\n"):
        line = line.strip()
        if line:
            pdf.multi_cell(0, 7, line)
            pdf.ln(2)
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="summary.pdf")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        text = ""
        if len(sys.argv) > 2:
            path = sys.argv[2]
            if path.lower().endswith(".pdf") and os.path.isfile(path):
                text = extract_text_from_pdf(path)
            else:
                text = " ".join(sys.argv[2:])
        else:
            print("Paste text or drag PDF path (Ctrl+Z then Enter to finish):", file=sys.stderr)
            text = sys.stdin.read().strip()
        if not text:
            print("No text provided.", file=sys.stderr)
            sys.exit(1)
        summary = summarize_text(text)
        import re
        plain = re.sub(r"<[^>]+>", "", summary)
        print("\n--- Summary (Bullet Points) ---\n")
        print(plain)
    else:
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port, debug=True)
