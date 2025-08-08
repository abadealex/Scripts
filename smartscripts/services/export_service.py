import io
import os
import csv
import json
import zipfile
from typing import List, Dict, Optional, Union
from fpdf import FPDF


class ExportService:
    """
    Service layer for exporting submissions as CSV, PDF, and optionally bundling artifacts like feedback.json or annotated files.
    """

    @staticmethod
    def export_submissions_to_csv(
        submissions: List[Union[Dict, object]],
        fieldnames: Optional[List[str]] = None
    ) -> str:
        if not submissions:
            raise ValueError("No submissions data provided for CSV export")

        data = [sub.to_dict() if hasattr(sub, "to_dict") else sub for sub in submissions]
        if not data:
            raise ValueError("No valid data to export")

        output = io.StringIO()
        if fieldnames is None:
            fieldnames = list(data[0].keys())

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def export_submissions_to_pdf(
        submissions: List[Union[Dict, object]],
        title: str = "Submissions Report"
    ) -> bytes:
        if not submissions:
            raise ValueError("No submissions data provided for PDF export")

        data = [sub.to_dict() if hasattr(sub, "to_dict") else sub for sub in submissions]
        if not data:
            raise ValueError("No valid data to export")

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(8)

        pdf.set_font("Arial", size=11)
        keys = list(data[0].keys())
        page_width = pdf.w - 2 * pdf.l_margin
        col_width = page_width / len(keys)

        pdf.set_fill_color(200, 220, 255)
        for key in keys:
            pdf.cell(col_width, 8, key, border=1, fill=True)
        pdf.ln()

        for row in data:
            for key in keys:
                val = str(row.get(key, ""))
                if len(val) > 30:
                    val = val[:27] + "..."
                pdf.cell(col_width, 8, val, border=1)
            pdf.ln()

        return pdf.output(dest='S').encode('latin1')

    @staticmethod
    def collect_artifacts(test_id: str, student_id: str) -> Dict[str, Optional[str]]:
        folder = os.path.join("uploads", "marked", str(test_id), str(student_id))
        artifacts = {
            "feedback_json": None,
            "annotated_image": None,
        }

        if os.path.isdir(folder):
            feedback_path = os.path.join(folder, "feedback.json")
            image_path = os.path.join(folder, "annotated.png")

            if os.path.isfile(feedback_path):
                artifacts["feedback_json"] = feedback_path
            if os.path.isfile(image_path):
                artifacts["annotated_image"] = image_path

        return artifacts

    @staticmethod
    def export_student_zip(test_id: str, student_id: str, destination_folder: str) -> Optional[str]:
        """
        Zip all feedback artifacts for a student and save it to destination folder.
        Returns path to zip file or None if no artifacts found.
        """
        artifacts = ExportService.collect_artifacts(test_id, student_id)
        files_to_include = [p for p in artifacts.values() if p]

        if not files_to_include:
            return None

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        zip_filename = f"student_{student_id}_test_{test_id}.zip"
        zip_path = os.path.join(destination_folder, zip_filename)

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for path in files_to_include:
                arcname = os.path.basename(path)
                zipf.write(path, arcname=arcname)

        return zip_path

    @staticmethod
    def save_export(file_bytes: bytes, filename: str, folder_path: str) -> str:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        full_path = os.path.join(folder_path, filename)
        with open(full_path, "wb") as f:
            f.write(file_bytes)

        return full_path


# Module-level aliases for compatibility with routes, scripts, or CLI

def export_submissions_to_csv(submissions: List[Union[Dict, object]], fieldnames: Optional[List[str]] = None) -> str:
    return ExportService.export_submissions_to_csv(submissions, fieldnames)

def export_submissions_to_pdf(submissions: List[Union[Dict, object]], title: str = "Submissions Report") -> bytes:
    return ExportService.export_submissions_to_pdf(submissions, title)

def export_student_zip(test_id: str, student_id: str, destination_folder: str) -> Optional[str]:
    return ExportService.export_student_zip(test_id, student_id, destination_folder)

def export_grading_results(test_id):
    from smartscripts.models import Test
    import csv

    test = Test.query.get(test_id)
    data = []

    for script in test.student_scripts:
        row = { 'Student ID': script.student_id }
        for score in script.scores:
            row[f'Q{score.question_id}'] = score.score
        data.append(row)

    return data  # Could write CSV or return JSON

import csv

def export_override_csv(overrides, output_path):
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['student_id', 'question_id', 'old_score', 'new_score', 'reason']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in overrides:
            writer.writerow(row)


