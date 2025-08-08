import os
import csv
import re
import zipfile
from difflib import SequenceMatcher
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app, flash

from smartscripts.extensions import db
from smartscripts.models import Test, TestSubmission, AttendanceRecord
from smartscripts.ai.marking_pipeline import mark_submission_async, mark_all_for_test
from smartscripts.utils.file_helpers import (
    get_answer_dir, get_marking_guide_dir, get_rubric_dir,
    get_submission_dir, get_class_list_dir, get_combined_pdf_dir,
)
from smartscripts.ai.ocr_engine import extract_name_id_from_image
from smartscripts.utils.pdf_helpers import convert_pdf_to_images, split_pdf_by_page_ranges
from smartscripts.analytics.layout_detection import detect_front_pages_via_ocr
from smartscripts.ai.text_matching import fuzzy_match_id, match_ocr_ids_to_class


# -------------------- Directory Setup --------------------

def ensure_test_dirs_exist(test_id: str):
    for path_func in [get_answer_dir, get_marking_guide_dir, get_rubric_dir, get_submission_dir]:
        os.makedirs(path_func(test_id), exist_ok=True)


# -------------------- File Routing --------------------

def determine_destination(filename: str, test_id: str) -> str:
    lower_fn = filename.lower()
    if "rubric" in lower_fn:
        return get_rubric_dir(test_id)
    elif "guide" in lower_fn:
        return get_marking_guide_dir(test_id)
    elif re.match(r"student_", lower_fn):
        match = re.match(r"student_([\w\-]+)_", filename)
        if not match:
            raise ValueError(f"Invalid student submission filename format: {filename}")
        student_id = match.group(1)
        return os.path.join(get_submission_dir(test_id), f"student_{student_id}")
    else:
        return get_answer_dir(test_id)


# -------------------- Validation --------------------

def all_required_components_exist(test_id: str) -> bool:
    guide_files = os.listdir(get_marking_guide_dir(test_id)) if os.path.exists(get_marking_guide_dir(test_id)) else []
    rubric_files = os.listdir(get_rubric_dir(test_id)) if os.path.exists(get_rubric_dir(test_id)) else []
    has_guide = any("guide" in f.lower() and f.lower().endswith(".pdf") for f in guide_files)
    has_rubric = any("rubric" in f.lower() and f.lower().endswith(".pdf") for f in rubric_files)
    has_submissions = TestSubmission.query.filter_by(test_id=test_id).first() is not None
    return has_guide and has_rubric and has_submissions


# -------------------- Submission Handling --------------------

def save_submission(file_storage, test_id: str):
    filename = secure_filename(file_storage.filename)
    destination_dir = determine_destination(filename, test_id)
    os.makedirs(destination_dir, exist_ok=True)
    filepath = os.path.join(destination_dir, filename)
    file_storage.save(filepath)
    print(f"?? Saved file: {filepath}")

    if destination_dir.startswith(get_submission_dir(test_id)):
        match = re.match(r"student_([\w\-]+)_", filename, re.IGNORECASE)
        if not match:
            print(f"?? Could not parse student_id from: {filename}")
            return
        student_id = match.group(1)
        submission = TestSubmission(test_id=test_id, student_id=student_id, file_path=filepath, marked=False)
        db.session.add(submission)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Database error: {e}')
            flash('A database error occurred.', 'danger')
            return
        print(f"? Submission record saved for student {student_id}")
        mark_submission_async.delay(submission.id)


# -------------------- Bulk ZIP Upload --------------------

def process_bulk_teacher_upload(zip_filepath: str, test_id: str):
    if not zipfile.is_zipfile(zip_filepath):
        raise ValueError(f"Invalid ZIP file: {zip_filepath}")

    extract_dir = os.path.splitext(zip_filepath)[0]
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"?? ZIP extracted ? {extract_dir}")

    ensure_test_dirs_exist(test_id)

    for root, _, files in os.walk(extract_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'rb') as f:
                    class FileWrapper:
                        def __init__(self, filename, fileobj):
                            self.filename = filename
                            self.file = fileobj
                        def save(self, dst):
                            with open(dst, 'wb') as out_f:
                                out_f.write(self.file.read())

                    wrapper = FileWrapper(fname, f)
                    save_submission(wrapper, test_id)
            except Exception as e:
                print(f"? Failed to process {fname}: {e}")

    if all_required_components_exist(test_id):
        print(f"?? All components present for test {test_id}. Triggering full batch marking...")
        mark_all_for_test(test_id)
    else:
        print(f"? Awaiting required files for test {test_id} before marking can begin.")


# -------------------- ZIP Output --------------------

def zip_extracted_data(output_zip_path: str, folders_to_include: list):
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder_path in folders_to_include:
            if not os.path.exists(folder_path):
                continue
            for root, _, files in os.walk(folder_path):
                for file in files:
                    abs_path = os.path.join(root, file)
                    arcname = os.path.relpath(abs_path, os.path.dirname(folder_path))
                    zipf.write(abs_path, arcname)
    print(f"?? Output ZIP created: {output_zip_path}")


def zip_outputs(pdf_paths: list, attendance_csv_path: str, output_zip_path: str):
    with zipfile.ZipFile(output_zip_path, 'w') as zipf:
        for pdf_path in pdf_paths:
            zipf.write(pdf_path, arcname=os.path.basename(pdf_path))
        zipf.write(attendance_csv_path, arcname='attendance.csv')
    print(f"?? Zipped {len(pdf_paths)} scripts + attendance CSV ? {output_zip_path}")


# -------------------- Combined Script OCR & Matching --------------------

def fuzzy_match_name(name: str, class_names: list, threshold: float = 0.8):
    best_score = 0.0
    best_match = ""
    for cname in class_names:
        score = SequenceMatcher(None, name.lower(), cname.lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = cname
    return (best_match, best_score) if best_score >= threshold else ("", 0.0)


def process_combined_student_scripts(pdf_path: str, class_list: list, output_dir: str = None):
    class_ids = [s['student_id'] for s in class_list]
    class_names = [s['name'] for s in class_list]

    temp_image_dir = os.path.join(output_dir, "temp_images")
    image_paths = convert_pdf_to_images(pdf_path, temp_image_dir)
    page_ranges = detect_front_pages_via_ocr(image_paths, extract_name_id_from_image)
    split_output_dir = os.path.join(output_dir, "student_scripts")
    split_paths = split_pdf_by_page_ranges(pdf_path, page_ranges, split_output_dir)

    presence_table = []
    matched_files = []
    unmatched_pages = []
    attendance = {"present": [], "absent": []}
    extracted_data = []

    for pdf_file in split_paths:
        page_images = convert_pdf_to_images(pdf_file, os.path.join(output_dir, "temp_single"))
        if not page_images:
            continue
        ocr_result = extract_name_id_from_image(page_images[0])
        extracted_data.append((pdf_file, ocr_result.get('id', ''), ocr_result.get('name', '')))

    extracted_ids = [e[1] for e in extracted_data]
    matched_ids, _ = match_ocr_ids_to_class(extracted_ids, class_list)

    for pdf_file, ocr_id, ocr_name in extracted_data:
        matched_student = None
        matched_by = ''
        confidence = 0.0

        if ocr_id in matched_ids:
            matched_student = next((s for s in class_list if s['student_id'] == ocr_id), None)
            matched_by = 'id'
            confidence = 1.0
        else:
            name_match, name_score = fuzzy_match_name(ocr_name, class_names)
            if name_match:
                matched_student = next((s for s in class_list if s['name'] == name_match), None)
                matched_by = 'name'
                confidence = name_score

        if matched_student:
            presence_table.append({
                'student_id': matched_student['student_id'],
                'student_name': matched_student['name'],
                'matched_by': matched_by,
                'confidence': confidence,
            })
            matched_student['script_path'] = pdf_file
            matched_files.append((matched_student, pdf_file))
            attendance["present"].append({
                "student_id": matched_student["student_id"],
                "student_name": matched_student["name"],
            })
        else:
            unmatched_pages.append(pdf_file)
            attendance["absent"].append({"name": ocr_name, "id": ocr_id})

    zip_path = None
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        attendance_csv = export_attendance_csv(attendance, output_dir)

        presence_csv_path = export_presence_csv(
            test_id=os.path.basename(pdf_path).split('.')[0],
            presence_table=presence_table,
            class_list=class_list,
            output_dir=output_dir
        )

        pdf_paths = [s['script_path'] for s, _ in matched_files if 'script_path' in s]
        zip_path = os.path.join(output_dir, "processed_output.zip")
        zip_outputs(pdf_paths, attendance_csv, zip_path)
        print(f"? Final ZIP saved ? {zip_path}")

        store_attendance_records(
            test_id=os.path.basename(pdf_path).split('.')[0],
            class_list=class_list,
            matched_ids=set(s['student_id'] for s in attendance["present"])
        )

        test = Test.query.get(os.path.basename(pdf_path).split('.')[0])
        if test:
            test.presence_csv_path = presence_csv_path
            try:
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                current_app.logger.error(f'Database error: {e}')
                flash('A database error occurred.', 'danger')

    return presence_table, matched_files, unmatched_pages, attendance, zip_path, presence_csv_path


# -------------------- CSV Helpers --------------------

def export_attendance_csv(attendance, output_dir):
    csv_path = os.path.join(output_dir, "attendance.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Status", "Name", "ID"])
        for s in attendance["present"]:
            writer.writerow(["Present", s["student_name"], s["student_id"]])
        for s in attendance["absent"]:
            writer.writerow(["Absent", s.get("name", ""), s.get("id", "")])
    return csv_path


def export_presence_csv(test_id: int, presence_table: list, class_list: list, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"presence_table_test_{test_id}.csv")
    match_info = {entry['student_id']: entry for entry in presence_table}

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "name", "status", "matched_by", "confidence"])
        for student in class_list:
            sid = student.get("student_id", "")
            name = student.get("name", "")
            if sid in match_info:
                entry = match_info[sid]
                writer.writerow([sid, name, "Present", entry.get("matched_by", ""), round(entry.get("confidence", 0.0), 2)])
            else:
                writer.writerow([sid, name, "Absent", "", ""])
    return csv_path


def store_attendance_records(test_id: str, class_list: list, matched_ids: set):
    existing = AttendanceRecord.query.filter_by(test_id=test_id).all()
    if existing:
        print(f"?? Attendance records already exist for test {test_id}, skipping insertion.")
        return

    records = []
    for student in class_list:
        student_id = student.get("student_id", "").strip()
        name = student.get("name", "").strip()
        if not student_id:
            print(f"?? Skipping student with missing ID: {student}")
            continue
        records.append(AttendanceRecord(
            test_id=test_id,
            student_id=student_id,
            name=name,
            present=student_id in matched_ids
        ))

    db.session.bulk_save_objects(records)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Database error: {e}')
        flash('A database error occurred.', 'danger')
    print(f"? Stored {len(records)} attendance records for test {test_id}")


def export_absentees_csv(test_id: int, class_list: list, matched_ids: set, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"absentees_test_{test_id}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "name"])
        for student in class_list:
            if student.get("student_id") not in matched_ids:
                writer.writerow([student.get("student_id", ""), student.get("name", "")])
    return csv_path

def generate_attendance_table(class_list, detected_entries):
    """
    Stub function to generate attendance table.
    Replace with real logic to compare OCR results to class list.
    """
    return {
        "present": [],
        "absent": [],
        "unmatched": [],
    }
