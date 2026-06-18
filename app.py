from flask import Flask, request, render_template_string
from summarizer import summarize
import os

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Text Summarizer</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #0f172a; color: #e2e8f0; min-height: 100vh; display: flex;
    justify-content: center; padding: 2rem 1rem;
  }
  .container { max-width: 720px; width: 100%; }
  h1 { font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; color: #38bdf8; }
  p.sub { color: #94a3b8; margin-bottom: 1.5rem; }
  textarea {
    width: 100%; min-height: 220px; padding: 1rem; border-radius: 10px;
    border: 1px solid #334155; background: #1e293b; color: #e2e8f0;
    font-size: 0.95rem; resize: vertical; font-family: inherit;
  }
  textarea:focus { outline: none; border-color: #38bdf8; }
  button {
    margin-top: 1rem; padding: 0.75rem 2rem; background: #38bdf8;
    color: #0f172a; border: none; border-radius: 8px; font-size: 1rem;
    font-weight: 600; cursor: pointer; transition: background 0.2s;
  }
  button:hover { background: #7dd3fc; }
  button:disabled { opacity: 0.6; cursor: not-allowed; }
  .spinner { display: none; }
  button.loading .spinner { display: inline-block; }
  button.loading .label { display: none; }
  .result {
    margin-top: 1.5rem; padding: 1.25rem; border-radius: 10px;
    background: #1e293b; border: 1px solid #334155; white-space: pre-wrap;
    line-height: 1.6;
  }
  .result h2 { font-size: 1.1rem; color: #38bdf8; margin-bottom: 0.5rem; }
  .error { color: #f87171; }
  .footer { margin-top: 2rem; text-align: center; font-size: 0.8rem; color: #475569; }
  @media (max-width: 480px) {
    body { padding: 1rem; }
    h1 { font-size: 1.5rem; }
  }
</style>
</head>
<body>
<div class="container">
  <h1>&#9889; Text Summarizer</h1>
  <p class="sub">Paste any text and get a concise summary powered by Groq AI</p>
  <form id="form">
    <textarea id="input" placeholder="Paste your text here..."></textarea>
    <button type="submit" id="btn">
      <span class="label">Summarize</span>
      <span class="spinner">Summarizing...</span>
    </button>
  </form>
  <div id="result" class="result" style="display:none"></div>
</div>
<script>
  const form = document.getElementById("form");
  const input = document.getElementById("input");
  const btn = document.getElementById("btn");
  const result = document.getElementById("result");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    btn.classList.add("loading");
    btn.disabled = true;
    result.style.display = "none";

    try {
      const res = await fetch("/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (res.ok) {
        result.innerHTML = "<h2>Summary</h2>" + data.summary;
        result.className = "result";
      } else {
        result.innerHTML = "<h2>Error</h2><p class='error'>" + (data.error || "Something went wrong") + "</p>";
        result.className = "result error";
      }
    } catch (err) {
      result.innerHTML = "<h2>Error</h2><p class='error'>Network error. Is the server running?</p>";
      result.className = "result error";
    }
    result.style.display = "block";
    btn.classList.remove("loading");
    btn.disabled = false;
  });
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/summarize", methods=["POST"])
def handle_summarize():
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return {"error": "No text provided"}, 400
    try:
        summary = summarize(text)
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
