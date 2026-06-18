# ADVANCED-COGNITIVE-TEXT-SUMMARIZATION-ENGINE
# Enterprise Text Summarizer (Groq AI)

An enterprise-grade, high-throughput text and document summarization platform powered by **Groq Language Processing Unit (LPU)** inference engines. This project decouples core LLM orchestration from user interfaces, providing three distinct execution paradigms to fit any workflow: a synchronous web portal, an interactive analytical lab, and a scriptable terminal tool.

 Core Features:
Multi-Interface Runtime:Flask Web App (`app.py`): Production-ready UI and REST API for text and file ingestion.
Streamlit Dashboard (`pr.py`): Interactive parameter lab to swap models and fine-tune output styles.
CLI Interface (`cli.py`)POSIX-compliant terminal tool supporting inline arguments and standard input (`stdin`) piping.
Advanced Document Ingestion:Built-in PDF parsing pipeline that maps and extracts clean unicode strings from binary file streams.
Dynamic Style Formatting: Strictly guided system prompts supporting three output formats: HTML Bullet Points (TL;DR), Executive Narrative Paragraphs, and Imperative Action Items.
Automated Document Export: Integrated downstream report compiler using coordinate vector graphics to generate clean, downloadable PDF summaries.
Hardware-Accelerated Inference:*Leverages the ultra-low latency of Groq-hosted models (`llama3-8b`, `llama3-70b`, `mixtral-8x7b`) for sub-second text processing.

🛠️ Tech Stack
Core AI: Groq SDK, Llama 3, Mixtral
Web & UI frameworks: Flask, Streamlit
Document Processing: PyPDF (extraction), FPDF2 (generation)
Environment Management: Python, Python-Dotenv

🏃 How to Run
1. Launch the Flask Web Application
To spin up the web interface and API routing gateway, execute the following command in your terminal:
summarizer.py
Once the server initializes, open your preferred web browser and navigate to:
👉 http://localhost:5000/
