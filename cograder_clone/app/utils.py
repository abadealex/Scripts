import os
import uuid
import cv2
import pytesseract
from fpdf import FPDF
from flask import current_app
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer, util
import openai

from .models import MarkingGuide

# Load the model once globally
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define common grading keywords
KEYWORDS = [
    'density', 'mass', 'volume', 'weighing scale', 'measuring cylinder',
    'displacement', 'water level', 'submerge', 'gold', 'compare', 'investigation'
]

# ----------- File Validation -----------
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# ----------- OCR with Preprocessing -----------
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    text = pytesseract.image_to_string(thresh, lang='eng').strip()
    return text

# ----------- Keyword Scoring -----------
def score_keywords(text, keywords):
    hits = [kw for kw in keywords if kw.lower() in text.lower()]
    return len(hits) / len(keywords), hits

# ----------- Semantic Matching using GPT or Fallback -----------
def semantic_match(expected, actual):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a strict teacher grading answers."},
                {"role": "user", "content": f"Compare:\nExpected: {expected}\nStudent: {actual}\nReply with 'Correct' or 'Incorrect'."}
            ],
            temperature=0
        )
        reply = response.choices[0].message.content.strip().lower()
        return 1.0 if 'correct' in reply else 0.0
    except Exception as e:
        print("OpenAI error, falling back to string similarity:", e)
        return SequenceMatcher(None, expected, actual).ratio()

# ----------- Optional: SentenceTransformer similarity -----------
def semantic_similarity(student_text, guide_text):
    emb_student = model.encode(student_text, convert_to_tensor=True)
    emb_guide = model.encode(guide_text, convert_to_tensor=True)
    return util.pytorch_cos_sim(emb_student, emb_guide).item()

# ----------- Placeholder Answer Extraction -----------
def extract_answer_for_question(full_text, question):
    return full_text  # To improve with question-based chunking later

# ----------- Grading Pipeline -----------
def grade_submission(image_path, guide: MarkingGuide, student_name, output_dir='uploads/marked'):
    student_text = extract_text_from_image(image_path)
    guide_answers = guide.get_answers_list()

    all_scores = []
    question_scores = {}

    for idx, q in enumerate(guide_answers, start=1):
        question = q.get("question", f"Question {idx}")
        ideal = q.get("ideal_answer", "")
        student_answer = extract_answer_for_question(student_text, question)

        kw_score, kw_hits = score_keywords(student_answer, KEYWORDS)
        sim_score = semantic_match(ideal, student_answer)
        final_score = round((0.5 * kw_score + 0.5 * sim_score) * 100, 2)

        all_scores.append(final_score)

        feedback = f"Keywords matched: {', '.join(kw_hits) if kw_hits else 'None'}. "
        feedback += f"Semantic score: {sim_score*100:.1f}%."

        question_scores[f"Question {idx}"] = {
            "answer": student_answer,
            "score": final_score,
            "feedback": feedback,
            "matched_keywords": kw_hits,
            "keyword_score": round(kw_score * 100, 2),
            "semantic_score": round(sim_score * 100, 2)
        }

    overall_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0.0

    os.makedirs(output_dir, exist_ok=True)
    annotated_path = os.path.join(output_dir, f"{uuid.uuid4().hex}_annotated.jpg")
    pdf_path = os.path.join(output_dir, f"{uuid.uuid4().hex}_report.pdf")

    try:
        annotate_image(image_path, guide_answers, question_scores, annotated_path)
    except Exception as e:
        print("Annotation failed:", e)
        annotated_path = None

    create_pdf_report(student_name, guide.title, question_scores, overall_score, pdf_path, annotated_path)

    return {
        "total_score": overall_score,
        "question_scores": question_scores,
        "annotated_file": annotated_path,
        "pdf_report": pdf_path
    }

# ----------- Image Annotation (Tick/Cross) -----------
def annotate_image(image_path, guide_answers, question_scores, output_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot load image from {image_path}")

    boxes = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    for i in range(len(boxes['text'])):
        word = boxes['text'][i].strip()
        x, y = boxes['left'][i], boxes['top'][i]

        for q_data in question_scores.values():
            if word and word.lower() in q_data["answer"].lower():
                mark = "✅" if q_data["score"] >= 60 else "❌"
                color = (0, 255, 0) if q_data["score"] >= 60 else (0, 0, 255)
                cv2.putText(img, mark, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
                break

    cv2.imwrite(output_path, img)

# ----------- PDF Report Generator -----------
class FeedbackPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Graded Report", ln=True, align="C")
        self.ln(10)

    def student_info(self, student_name, guide_name):
        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"Student: {student_name}", ln=True)
        self.cell(0, 10, f"Marking Guide: {guide_name}", ln=True)
        self.ln(5)

    def add_scores(self, question_scores):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Question-wise Breakdown", ln=True)
        self.set_font("Arial", "", 12)
        for question, data in question_scores.items():
            score = data.get("score", "N/A")
            feedback = data.get("feedback", "")
            answer = data.get("answer", "")
            self.cell(0, 10, f"{question}: {score}/100", ln=True)
            self.set_font("Arial", "I", 10)
            self.multi_cell(0, 8, f"Your Answer: {answer}\nFeedback: {feedback}")
            self.set_font("Arial", "", 12)
        self.ln(5)

    def final_score(self, total):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, f"Total Score: {total:.2f}%", ln=True)

    def add_image(self, image_path):
        if os.path.exists(image_path):
            self.image(image_path, x=10, y=self.get_y(), w=180)
            self.ln(90)

def create_pdf_report(student_name, guide_name, question_scores, total_score, output_path, annotated_img_path=None):
    pdf = FeedbackPDF()
    pdf.add_page()
    pdf.student_info(student_name, guide_name)
    pdf.add_scores(question_scores)
    pdf.final_score(total_score)
    if annotated_img_path:
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Annotated Answer Sheet:", ln=True)
        pdf.add_image(annotated_img_path)
    pdf.output(output_path)
