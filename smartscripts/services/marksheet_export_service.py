import os
import csv
import json
from pathlib import Path
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

LOGO_PATH = Path("static/overlays/logo.png")  # example logo to put in PDF header


class MarksheetExportService:
    def __init__(self, base_export_dir: Path = Path("uploads/final_exports")):
        self.base_export_dir = base_export_dir
        self.base_export_dir.mkdir(parents=True, exist_ok=True)

    def export_marksheet(
        self,
        test_id: str,
        student_id: str,
        marks_data: Dict[str, Any],
        feedback_data: Dict[str, Any],
        annotations: List[Dict[str, Any]] = None,
    ) -> None:
        """
        Generate and save export files for a single student's test.

        Args:
            test_id: Test identifier (e.g., "test_id_X").
            student_id: Student identifier (e.g., "student_id_Y").
            marks_data: Dictionary of marks per question or section.
            feedback_data: Dictionary or list of feedback comments.
            annotations: Optional list of annotations (e.g., for overlayed PDFs).
        """
        student_export_dir = self.base_export_dir / test_id / student_id
        student_export_dir.mkdir(parents=True, exist_ok=True)

        # 1) Export CSV marksheet
        csv_path = student_export_dir / "final_marksheet.csv"
        self._export_csv(csv_path, marks_data)

        # 2) Export JSON feedback + marks summary
        feedback_path = student_export_dir / "final_feedback.json"
        self._export_json(feedback_path, {
            "marks": marks_data,
            "feedback": feedback_data,
            "annotations": annotations or []
        })

        # 3) Optional: export a simple PDF summary report
        pdf_path = student_export_dir / "final_marked.pdf"
        self._export_pdf(pdf_path, test_id, student_id, marks_data, feedback_data)

        print(f"Export completed for {test_id} / {student_id}")

    def _export_csv(self, csv_path: Path, marks_data: Dict[str, Any]) -> None:
        """Save marks dictionary as CSV with 'Question,Mark' columns."""
        with csv_path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Question", "Mark"])
            for question, mark in marks_data.items():
                writer.writerow([question, mark])

    def _export_json(self, json_path: Path, data: Dict[str, Any]) -> None:
        """Save data dict as pretty JSON."""
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def _export_pdf(
        self,
        pdf_path: Path,
        test_id: str,
        student_id: str,
        marks_data: Dict[str, Any],
        feedback_data: Dict[str, Any],
    ) -> None:
        """Generate a simple PDF summary report with marks and feedback."""

        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        width, height = letter

        # Draw logo if exists
        if LOGO_PATH.exists():
            c.drawImage(str(LOGO_PATH), x=50, y=height - 80, width=100, height=30)

        c.setFont("Helvetica-Bold", 16)
        # Adjust title y-position if logo exists to avoid overlap
        title_y = height - 50 if not LOGO_PATH.exists() else height - 90
        c.drawString(50, title_y, "Marksheet Summary")

        c.setFont("Helvetica", 12)
        c.drawString(50, title_y - 20, f"Test ID: {test_id}")
        c.drawString(50, title_y - 40, f"Student ID: {student_id}")

        y = title_y - 80
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Marks Obtained:")
        y -= 20

        c.setFont("Helvetica", 12)
        for question, mark in marks_data.items():
            c.drawString(60, y, f"{question}: {mark}")
            y -= 20
            if y < 80:
                c.showPage()
                y = height - 50

        y -= 10
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Feedback:")
        y -= 20

        c.setFont("Helvetica", 12)
        # If feedback is a dict or list, handle both:
        if isinstance(feedback_data, dict):
            feedback_texts = []
            for key, val in feedback_data.items():
                if isinstance(val, list):
                    feedback_texts.extend(val)
                else:
                    feedback_texts.append(str(val))
        elif isinstance(feedback_data, list):
            feedback_texts = feedback_data
        else:
            feedback_texts = [str(feedback_data)]

        for line in feedback_texts:
            if y < 80:
                c.showPage()
                y = height - 50
            c.drawString(60, y, f"- {line}")
            y -= 18

        c.save()
