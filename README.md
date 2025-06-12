# 🧠 AI-Powered Marking System

An intelligent web-based marking platform that automatically grades **handwritten student answers** using **AI**, **OCR**, and **image annotation**. Built for teachers and students, this tool simulates real-world marking by comparing student answers with a sample marking guide, applying visual ticks/crosses, and generating clean, exportable results.

---

## ✨ Features

- ✅ Web-based portal for **teachers and students**
- 📤 Upload **typed sample answers** as a marking guide
- 📸 Students upload **handwritten answer sheets** (image or PDF)
- 🧠 AI grades responses using **OCR** + **semantic matching**
- ✅ Tick/cross overlay on submitted answers (like real grading)
- 🧾 View/download **marked papers and grade summaries**
- 🖨️ Export marked papers as **PDF** (ready to print or send)

---

## 🏗️ Tech Stack

| Component          | Technology Used                          |
| ------------------ | ----------------------------------------- |
| Frontend           | React + Tailwind CSS (or plain HTML/CSS) |
| Backend API        | Python + Flask                           |
| Image Processing   | OpenCV + Tesseract OCR                   |
| AI Matching        | OpenAI GPT (or sentence similarity)      |
| File Storage       | Local filesystem (S3 optional)           |
| PDF Handling       | ReportLab / PyMuPDF                      |
| Database           | SQLite / PostgreSQL                      |
| Hosting            | Render / Heroku                          |

---

## 🚀 Getting Started

### 🔧 Prerequisites

- Python 3.9+
- Node.js & npm (if using React)
- Tesseract installed (`sudo apt install tesseract-ocr` or equivalent)

### 🛠️ Backend Setup (Flask)

```bash
git clone https://github.com/yourusername/ai-marking-system.git
cd ai-marking-system
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
