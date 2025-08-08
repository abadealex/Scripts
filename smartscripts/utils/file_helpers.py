import os
import csv
import json
import uuid
import shutil
import zipfile
import datetime
import logging
from typing import Optional, List, Dict
from pathlib import Path
from flask import current_app
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt', 'csv'}


def get_upload_root() -> Path:
    """Return absolute path to static/uploads directory."""
    return Path(current_app.root_path) / 'static' / 'uploads'


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename: str) -> str:
    filename = secure_filename(filename)
    return f"{uuid.uuid4().hex}_{filename}"


def save_file(file_storage, subfolder: str, test_id: int, student_id: Optional[str] = None) -> str:
    upload_root = get_upload_root()

    if not file_storage:
        raise ValueError("No file provided")

    filename = file_storage.filename
    if not allowed_file(filename):
        raise ValueError(f"File type not allowed: {filename}")

    unique_filename = generate_unique_filename(filename)

    dir_path = upload_root / subfolder / str(test_id)
    if student_id:
        dir_path = dir_path / str(student_id)

    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / unique_filename

    file_storage.save(str(file_path))
    relative_path = file_path.relative_to(upload_root)
    logger.info(f"File saved: {file_path} (relative path: {relative_path})")

    return str(relative_path)


def create_test_directory_structure(test_id: int) -> Dict[str, str]:
    base = get_upload_root() / str(test_id)
    folders = [
        "answered_scripts", "audit_logs", "combined_scripts", "extracted",
        "feedback", "manifests", "marked", "marking_guides", "question_papers",
        "rubrics", "student_lists", "student_scripts", "submissions",
        "tmp", "exports",
    ]

    paths = {}
    for folder in folders:
        path = base / folder
        path.mkdir(parents=True, exist_ok=True)
        paths[folder] = str(path.resolve())

    return paths


# === Path getters ===

def get_answered_scripts_dir(test_id: int) -> str:
    return str(get_upload_root() / 'answered_scripts' / str(test_id))

def get_audit_logs_dir(test_id: int) -> str:
    return str(get_upload_root() / 'audit_logs' / str(test_id))

def get_combined_scripts_dir(test_id: int) -> str:
    return str(get_upload_root() / 'combined_scripts' / str(test_id))

def get_extracted_dir(test_id: int, student_id: Optional[str] = None) -> str:
    base = get_upload_root() / 'extracted' / str(test_id)
    return str(base / str(student_id)) if student_id else str(base)

def get_feedback_dir(test_id: int) -> str:
    return str(get_upload_root() / 'feedback' / str(test_id))

def get_manifests_dir(test_id: int) -> str:
    return str(get_upload_root() / 'manifests' / str(test_id))

def get_marked_dir(test_id: int, student_id: Optional[str] = None) -> str:
    base = get_upload_root() / 'marked' / str(test_id)
    return str(base / str(student_id)) if student_id else str(base)

def get_marking_guides_dir(test_id: int) -> str:
    return str(get_upload_root() / 'marking_guides' / str(test_id))

def get_question_papers_dir(test_id: int) -> str:
    return str(get_upload_root() / 'question_papers' / str(test_id))

def get_rubrics_dir(test_id: int) -> str:
    return str(get_upload_root() / 'rubrics' / str(test_id))

def get_student_lists_dir(test_id: int) -> str:
    return str(get_upload_root() / 'student_lists' / str(test_id))

def get_student_scripts_dir(test_id: int) -> str:
    return str(get_upload_root() / 'student_scripts' / str(test_id))

def get_submissions_dir(test_id: int, student_id: Optional[str] = None) -> str:
    base = get_upload_root() / 'submissions' / str(test_id)
    return str(base / str(student_id)) if student_id else str(base)

def get_tmp_dir(teacher_id: int) -> str:
    return str(get_upload_root() / 'tmp' / str(teacher_id) / 'working_files')

def get_exports_dir(test_id: int) -> str:
    return str(get_upload_root() / 'exports' / str(test_id))


# === Utility functions ===

def delete_test_folder(subfolder: str, test_id: int) -> None:
    test_path = get_upload_root() / subfolder / str(test_id)
    if test_path.exists() and test_path.is_dir():
        shutil.rmtree(test_path)
        logger.info(f"Deleted folder: {test_path}")


def load_student_list(path: str) -> List[Dict[str, str]]:
    students = []
    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            students.append({
                "student_id": row.get("student_id", "").strip(),
                "name": row.get("name", "").strip(),
                "email": row.get("email", "").strip()
            })
    return students


def generate_presence_csv(matched: List[Dict[str, str]], unmatched: List[Dict[str, str]], test_id: int) -> str:
    output_dir = get_upload_root() / 'presence_reports' / str(test_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "presence.csv"
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["student_id", "name", "email", "status"])
        for student in matched:
            writer.writerow([student["student_id"], student["name"], student["email"], "Present"])
        for student in unmatched:
            writer.writerow([student["student_id"], student["name"], student["email"], "Absent"])

    return str(csv_path.relative_to(get_upload_root()))


def save_manual_override(test_id: int, page_num: int, decision: str) -> None:
    override_file = get_upload_root() / f"test_{test_id}_overrides.json"
    overrides = {}

    if override_file.exists():
        with open(override_file, "r", encoding='utf-8') as f:
            overrides = json.load(f)

    overrides[str(page_num)] = decision
    with open(override_file, "w", encoding='utf-8') as f:
        json.dump(overrides, f, indent=2)


def get_image_path_for_page(test_id: int, page_num: int) -> Optional[str]:
    base_dir = get_upload_root() / 'split_pages' / str(test_id)
    image_path = base_dir / f"page_{page_num}.png"
    return str(image_path) if image_path.exists() else None


def generate_extracted_filename(student_name: str, student_id: str, index: int = 1) -> str:
    safe_name = student_name.replace(" ", "_").lower()
    safe_id = student_id.replace("/", "_")
    return f"{safe_name}_{safe_id}_script_{index}.pdf"


def zip_test_directory(test_id: int) -> str:
    test_dir = get_upload_root() / str(test_id)
    if not test_dir.exists():
        raise FileNotFoundError(f"Test folder not found: {test_dir}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = get_upload_root() / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    zip_path = backup_dir / f"test_{test_id}_{timestamp}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(test_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, test_dir)
                zipf.write(abs_path, arcname=rel_path)

    logger.info(f"Backup ZIP created: {zip_path}")
    return str(zip_path.resolve())


def cleanup_old_tests(days_old: int = 30) -> List[str]:
    deleted = []
    now = datetime.datetime.now()

    for folder in get_upload_root().glob("*"):
        if folder.is_dir() and folder.name.isdigit():
            mtime = datetime.datetime.fromtimestamp(folder.stat().st_mtime)
            if (now - mtime).days >= days_old:
                try:
                    shutil.rmtree(folder)
                    deleted.append(str(folder.resolve()))
                    logger.info(f"Deleted old test folder: {folder}")
                except Exception as e:
                    logger.error(f"Error deleting {folder}: {e}")

    return deleted


def get_file_path(filename: str) -> Path:
    path = Path(filename)
    return path if path.is_absolute() else get_upload_root() / path
