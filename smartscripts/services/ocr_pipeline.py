import os
import csv
import fitz  # PyMuPDF
from uuid import uuid4
from pdf2image import convert_from_path
from werkzeug.utils import secure_filename
from difflib import SequenceMatcher

from flask import current_app, flash
from sqlalchemy.exc import SQLAlchemyError

from smartscripts.extensions import db
from smartscripts.models import ExtractedStudentScript
from smartscripts.ai.ocr_engine import extract_name_id_from_image
from smartscripts.ai.text_matching import fuzzy_match_id  # ? ID matching

UPLOAD_DIR = os.path.join('smartscripts', 'app', 'static', 'uploads', 'extracted')
os.makedirs(UPLOAD_DIR, exist_ok=True)


def process_combined_student_scripts(test_id, class_list_path, scripts_pdf_path):
    """
    Processes a merged PDF of student scripts with a provided class list,
    extracts individual scripts, performs OCR, and matches to students.
    """
    class_list = load_class_list(class_list_path)
    class_ids = [s['id'] for s in class_list]
    class_names = [s['name'] for s in class_list]

    images = convert_from_path(scripts_pdf_path, dpi=300)

    current_script = None
    extracted_scripts = []
    attendance = {"present": [], "absent": []}

    for i, image in enumerate(images):
        name, student_id, confidence = extract_name_id_from_image(image)
        matched = None

        # Match by student ID
        if student_id:
            match_id, score = fuzzy_match_id(student_id, class_ids, threshold=0.85)
            if match_id:
                matched = next((s for s in class_list if s["id"] == match_id), None)

        # Fallback match by name
        if not matched and name:
            match_name, score = fuzzy_match_name(name, class_names, threshold=0.8)
            if match_name:
                matched = next((s for s in class_list if s["name"] == match_name), None)

        if matched:
            attendance["present"].append(matched)

            if current_script:
                script = split_pdf(
                    scripts_pdf_path, test_id,
                    current_script['start'], i - 1,
                    current_script['matched']['name'], current_script['matched']['id']
                )
                extracted_scripts.append(script)

            current_script = {
                'start': i,
                'matched': matched
            }
        else:
            attendance["absent"].append({"name": name, "id": student_id})

    # Final script at end of file
    if current_script:
        script = split_pdf(
            scripts_pdf_path, test_id,
            current_script['start'], len(images) - 1,
            current_script['matched']['name'], current_script['matched']['id']
        )
        extracted_scripts.append(script)

    # Save to DB
    for s in extracted_scripts:
        db.session.add(s)

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Database error: {e}')
        flash('A database error occurred.', 'danger')

    export_attendance_csv(attendance, UPLOAD_DIR)


def fuzzy_match_name(name: str, class_names: list, threshold: float = 0.8):
    """
    Performs fuzzy matching of a name against a list of names.
    """
    best_score = 0.0
    best_match = ""

    for cname in class_names:
        score = SequenceMatcher(None, name.lower(), cname.lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = cname

    return (best_match, best_score) if best_score >= threshold else ("", 0.0)


def load_class_list(path):
    """
    Loads a class list CSV or TXT. Expects either:
    - CSV with headers: name, id
    - Plain rows: Name, ID
    """
    students = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f) if path.endswith('.csv') else csv.reader(f)
        for row in reader:
            if isinstance(row, dict):
                students.append({
                    'name': row.get('name') or row.get('Name'),
                    'id': row.get('id') or row.get('ID')
                })
            else:
                if len(row) >= 2:
                    students.append({'name': row[0], 'id': row[1]})
    return students


def split_pdf(pdf_path, test_id, start_page, end_page, name, student_id):
    """
    Extracts a range of pages from the PDF into a separate file.
    """
    pdf = fitz.open(pdf_path)
    student_pdf = fitz.open()

    for page_num in range(start_page, end_page + 1):
        student_pdf.insert_pdf(pdf, from_page=page_num, to_page=page_num)

    filename = f"{uuid4().hex}_{secure_filename(name)}_{student_id}_{start_page + 1}-{end_page + 1}.pdf"
    output_path = os.path.join(UPLOAD_DIR, filename)
    student_pdf.save(output_path)

    return ExtractedStudentScript(
        test_id=test_id,
        student_name=name,
        student_id=student_id,
        page_range=f"{start_page + 1}-{end_page + 1}",
        script_path=output_path,
        confirmed=False
    )


def export_attendance_csv(attendance, output_dir):
    """
    Saves a CSV report of present and absent students.
    """
    csv_path = os.path.join(output_dir, "attendance.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Status", "Name", "ID"])
        for s in attendance["present"]:
            writer.writerow(["Present", s["name"], s["id"]])
        for s in attendance["absent"]:
            writer.writerow(["Absent", s.get("name", ""), s.get("id", "")])
    return csv_path
