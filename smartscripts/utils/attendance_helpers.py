import random
from fpdf import FPDF
import os

def generate_mock_score_distribution(num_students=50):
    return [random.gauss(65, 15) for _ in range(num_students)]

def get_common_mistakes():
    return {
        "Q1": ["Forgot formula", "Calculation error"],
        "Q2": ["Misinterpreted graph", "Unit mismatch"],
        "Q4": ["No working shown"]
    }

def rubric_difficulty_scores():
    return {
        "Understanding Concepts": 0.7,
        "Problem Solving": 0.6,
        "Communication": 0.8,
        "Accuracy": 0.5
    }

def generate_pdf_report(output_path="generated_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="AI Grading Analytics Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Summary:", ln=True)
    pdf.multi_cell(0, 10, txt="This report summarizes student performance, common mistakes, and rubric item difficulty.")
    pdf.output(output_path)
    return os.path.abspath(output_path)


