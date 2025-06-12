 student_name = "John Doe"
guide_name = "Business Ethics"
question_scores = {
    "Q1": {"score": 80, "feedback": "Good explanation, missed one point."},
    "Q2": {"score": 90, "feedback": "Well done."},
    "Q3": {"score": 70, "feedback": "Need more clarity."}
}
total_score = 80.0

create_pdf_report(
    student_name,
    guide_name,
    question_scores,
    total_score,
    output_path="results/john_doe_report.pdf",
    annotated_img_path="annotated/john_doe_q1.png"
)

