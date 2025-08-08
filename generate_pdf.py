from fpdf import FPDF
import os

class FeedbackPDF(FPDF):
    def header(self):
        """Adds a header to each page."""
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Graded Report", ln=True, align="C")
        self.ln(10)

    def student_info(self, student_name, guide_name):
        """Adds student and guide info to the PDF."""
        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"Student: {student_name}", ln=True)
        self.cell(0, 10, f"Marking Guide: {guide_name}", ln=True)
        self.ln(5)

    def add_scores(self, question_scores):
        """Adds question-wise grading breakdown."""
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Question-wise Breakdown", ln=True)
        self.set_font("Arial", "", 12)
        for question, data in question_scores.items():
            score = data.get("score", "N/A")
            feedback = data.get("feedback", "")
            self.cell(0, 10, f"{question}: {score}/100", ln=True)
            if feedback:
                self.set_font("Arial", "I", 10)
                self.multi_cell(0, 8, f"Feedback: {feedback}")
                self.set_font("Arial", "", 12)
        self.ln(5)

    def final_score(self, total):
        """Displays final score."""
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, f"Total Score: {total:.2f}%", ln=True)

    def add_image(self, image_path):
        """Inserts annotated student image."""
        if os.path.exists(image_path):
            self.image(image_path, x=10, y=self.get_y(), w=180)
            self.ln(5)

def create_pdf_report(student_name, guide_name, question_scores, total_score, output_path, annotated_img_path=None):
    """
    Generates a PDF feedback report for a student's submission.

    Args:
        student_name (str): Name of the student.
        guide_name (str): Name of the marking guide used.
        question_scores (dict): Dict of question scores and feedback.
        total_score (float): Overall percentage score.
        output_path (str): File path to save the PDF.
        annotated_img_path (str, optional): Path to the marked image.
    """
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

    try:
                pdf.output(output_path)
        print(f"PDF successfully saved at: {output_path}")
    except Exception as e:
        print(f"Error saving PDF: {e}")

