# 🧠 SmartScripts - AI-Powered Marking System

SmartScripts is a Flask + React-based web platform that allows teachers to **automatically grade handwritten or typed student answer sheets** using AI technologies like OCR, NLP, and computer vision.

---

## 🚀 Features

- 📝 Upload student answer sheets (handwritten or typed)
- 🎯 Intelligent grading using:
  - OCR (Tesseract)
  - GPT-based semantic similarity
  - Keyword-based scoring
- ✅ Visual feedback with tick/cross annotations on answers
- 📊 Teacher dashboard with student scores and summaries
- 📂 Multi-question structured grading
- 🖼️ Per-question feedback and result view
- 🔐 Authentication system for students and teachers
- 📄 Export reports (PDF - coming soon)

---

## 💻 Technologies Used

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **Frontend**: React, Tailwind CSS (optional)
- **AI/ML**: Tesseract OCR, GPT (OpenAI API), spaCy
- **DevOps**: Docker, Render / Railway (deployment)

---

## 🛠️ Local Setup

```bash
git clone https://github.com/amooti365/SmartScripts.git
cd SmartScripts
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
flask db upgrade
flask run
