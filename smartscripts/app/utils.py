import uuid
import json
from pathlib import Path
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

# ✅ Import shared utility functions
from smartscripts.utils.file_io import allowed_file, ensure_folder_exists, delete_file_if_exists

# -------------------- Core Upload Utilities --------------------

def generate_unique_filename(filename):
    """Generate a unique filename with a UUID prefix to avoid collisions."""
    filename = secure_filename(filename)
    unique_prefix = uuid.uuid4().hex
    return f"{unique_prefix}_{filename}"


def save_file(file_storage, subfolder, test_id, student_id=None):
    """
    Save uploaded file with unique filename, creating subdirectories as needed.
    Directory structure: <UPLOAD_FOLDER>/<subfolder>/<test_id>/<student_id>/ (student_id optional)
    Returns relative path to saved file from UPLOAD_FOLDER.
    """
    upload_root = Path(current_app.config.get('UPLOAD_FOLDER'))
    if not upload_root:
        raise RuntimeError("UPLOAD_FOLDER not configured in app config")

    if not file_storage:
        raise ValueError("No file provided")

    filename = file_storage.filename
    if not allowed_file(filename):
        raise ValueError("File type not allowed")

    unique_filename = generate_unique_filename(filename)

    dir_path = upload_root / subfolder / str(test_id)
    if student_id:
        dir_path = dir_path / str(student_id)

    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = dir_path / unique_filename
    file_storage.save(str(file_path))

    relative_path = file_path.relative_to(upload_root)
    return str(relative_path)


def create_test_directories(test_id):
    """
    Creates the required directories for a given test_id
    under answers/, rubrics/, guides/, submissions/ base folders.
    """
    base_folders = {
        'answers': current_app.config.get('UPLOAD_FOLDER_ANSWERS'),
        'rubrics': current_app.config.get('UPLOAD_FOLDER_RUBRICS'),
        'guides': current_app.config.get('UPLOAD_FOLDER_GUIDES'),
        'submissions': current_app.config.get('UPLOAD_FOLDER_SUBMISSIONS'),
    }

    for subfolder, base_path_str in base_folders.items():
        if not base_path_str:
            current_app.logger.error(f"Upload folder for {subfolder} not configured!")
            continue
        base_path = Path(base_path_str)
        path = base_path / str(test_id)
        try:
                    path.mkdir(parents=True, exist_ok=True)
            current_app.logger.info(f"Created directory: {path}")
        except Exception as e:
            current_app.logger.error(f"Failed to create directory {path}: {e}")


# -------------------- Reusable Path Helpers --------------------

def get_uploads_root() -> Path:
    """Returns the root upload path from config or 'uploads' as default."""
    return Path(current_app.config.get('UPLOAD_FOLDER', 'uploads'))


def get_submission_path(test_id: str, student_id: str) -> Path:
    return get_uploads_root() / "submissions" / test_id / student_id


def get_submission_file_path(test_id: str, student_id: str, filename: str) -> Path:
    return get_submission_path(test_id, student_id) / filename


def get_marked_script_path(test_id: str, student_id: str, page_no: int) -> Path:
    return get_uploads_root() / "marked" / test_id / student_id / f"page_{page_no}_marked.png"


def get_test_assets_path(test_id: str) -> Path:
    return get_uploads_root() / "tests" / test_id / "assets"


def get_test_definition_path(test_id: str) -> Path:
    return get_uploads_root() / "tests" / test_id / "test_definition.json"


def get_feedback_path(test_id: str, student_id: str) -> Path:
    return get_uploads_root() / "feedback" / test_id / f"{student_id}.json"


def get_grading_metadata_path(test_id: str, student_id: str) -> Path:
    return get_uploads_root() / "grading" / test_id / f"{student_id}_grading.json"


# -------------------- Added Helper Function --------------------

def is_released(test_id: str) -> bool:
    """
    Check if the test is released by reading metadata.json inside the test folder.
    Expects metadata.json at: <UPLOAD_FOLDER>/tests/<test_id>/metadata.json
    """
    metadata_path = get_uploads_root() / "tests" / str(test_id) / "metadata.json"
    if not metadata_path.exists():
        return False
    try:
                with metadata_path.open('r') as f:
            metadata = json.load(f)
        return metadata.get('released', False)
    except Exception as e:
        current_app.logger.error(f"Failed to read metadata file {metadata_path}: {e}")
        return False

