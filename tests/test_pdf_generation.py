import os
from smartscripts.utils.file_helpers import create_pdf_report  # adjust if needed

def test_create_pdf_report(tmp_path):
    student_name = "John Doe"
    guide_name = "Business Ethics"
    question_scores = {
        "Q1": {"score": 80, "feedback": "Good explanation, missed one point."},
        "Q2": {"score": 90, "feedback": "Well done."},
        "Q3": {"score": 70, "feedback": "Need more clarity."}
    }
    total_score = 80.0

    output_path = tmp_path / "john_doe_report.pdf"
    annotated_img = "tests/sample_data/john_doe_q1.png"  # make sure this exists

    create_pdf_report(
        student_name,
        guide_name,
        question_scores,
        total_score,
        output_path=str(output_path),
        annotated_img_path=annotated_img
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0
