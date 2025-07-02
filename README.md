# 🧠 SmartScripts - AI-Powered Marking System

SmartScripts is a Flask + React-based web platform that enables teachers to **automatically grade handwritten or typed student answer sheets** using cutting-edge AI technologies such as OCR, NLP, and computer vision.

---

## 🚀 Features

- 📝 Upload student answer sheets (handwritten or typed)
- 🎯 Intelligent grading using:
  - OCR (TrOCR and Tesseract)
  - GPT-based semantic similarity and keyword matching
  - Rubric-based weighted scoring for detailed feedback
- ✅ Visual feedback with tick/cross annotations over answers
- 📊 Teacher dashboard with student scores, manual overrides, and summaries
- 📂 Support for multi-question structured grading guides (rubrics)
- 🖼️ Per-question detailed feedback and annotated result views
- 🔐 Authentication system for students and teachers
- 📄 Export reports (PDF export coming soon)
- 🧪 Extensive testing coverage for OCR, grading logic, question alignment, and overlays

---

## 💻 Technologies Used

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **Frontend**: React, Tailwind CSS (optional)
- **AI/ML**: 
  - TrOCR (handwritten OCR via Hugging Face)
  - Tesseract OCR (fallback/alternative)
  - OpenAI GPT (semantic similarity, grading pipeline)
  - spaCy (NLP utilities)
- **DevOps**: Docker, Render / Railway (cloud deployment)

---

## 📁 Project Structure

