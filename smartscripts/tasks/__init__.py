import os
import re
import tempfile
from uuid import uuid4

import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app, flash
from werkzeug.utils import secure_filename

from smartscripts.extensions import celery, db
from smartscripts.models import Test, ExtractedStudentScript
from smartscripts.services.ocr_pipeline import process_combined_student_scripts

# Directory for saving extracted scripts
UPLOAD_DIR = os.path.join('smartscripts', 'app', 'static', 'uploads', 'extracted')
os.makedirs(UPLOAD_DIR, exist_ok=True)


@celery.task(bind=True)
def run_ocr_on_test(self, test_id):
    test = Test.query.get(test_id)
    if not test or not test.answered_script_filename:
        return f"No test or answered script found for test ID: {test_id}"

    pdf_path = os.path.join('static', 'uploads', test.answered_script_filename)
    return _process_pdf_with_ocr(self, test_id, pdf_path)


@celery.task(bind=True)
def run_ocr_on_merged_pdf(self, test_id, file_path):
    """
    OCR task for a user-uploaded merged PDF.
    """
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    return _process_pdf_with_ocr(self, test_id, file_path)


@celery.task
def run_student_script_ocr_pipeline(test_id, class_list_path, scripts_pdf_path):
    """
    ? New OCR pipeline task for class list + merged student scripts.
    """
    process_combined_student_scripts(test_id, class_list_path, scripts_pdf_path)


def _process_pdf_with_ocr(task_self, test_id, pdf_path):
    try:
        images = convert_from_path(pdf_path, dpi=300)
    except Exception as e:
        return f"Error converting PDF to images: {str(e)}"

    total_pages = len(images)
    extracted_scripts = []
    current_script = {'start': 0, 'name': None, 'id': None}

    with tempfile.TemporaryDirectory() as temp_dir:
        for i, image in enumerate(images):
            image_path = os.path.join(temp_dir, f"page_{i}.png")
            image.save(image_path)

            text = pytesseract.image_to_string(Image.open(image_path))

            name_match = re.search(r'Name\s*[:\-]?\s*([\w\s]{2,})', text, re.IGNORECASE)
            id_match = re.search(r'(ID|Student ID)\s*[:\-]?\s*(\d{4,})', text, re.IGNORECASE)

            if name_match and id_match:
                name = name_match.group(1).strip()
                student_id = id_match.group(2).strip()

                # If we already started another student's script, save it
                if current_script['name'] and i != current_script['start']:
                    script = split_pdf_and_create_script(
                        pdf_path, test_id,
                        current_script['start'], i - 1,
                        current_script['name'], current_script['id']
                    )
                    extracted_scripts.append(script)

                current_script = {'start': i, 'name': name, 'id': student_id}

            # Progress update
            progress = int((i + 1) / total_pages * 100)
            task_self.update_state(
                state='PROGRESS',
                meta={'current': i + 1, 'total': total_pages, 'progress': progress}
            )

        # Save the last student script
        if current_script['name']:
            script = split_pdf_and_create_script(
                pdf_path, test_id,
                current_script['start'], total_pages - 1,
                current_script['name'], current_script['id']
            )
            extracted_scripts.append(script)

    # Save to database
    for s in extracted_scripts:
        db.session.add(s)

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Database error: {e}')
        flash('A database error occurred.', 'danger')
        return {
            'state': 'FAILURE',
            'message': f'Database error: {str(e)}'
        }

    return {
        'state': 'SUCCESS',
        'message': f"OCR complete: {len(extracted_scripts)} student scripts extracted."
    }


def split_pdf_and_create_script(pdf_path, test_id, start_page, end_page, name, student_id):
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

