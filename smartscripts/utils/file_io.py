# smartscripts/utils/file_io.py

import uuid
import json
from pathlib import Path
from flask import current_app
from werkzeug.utils import secure_filename
import shutil
from typing import List, Union

# Allowed extensions for uploaded files
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}

def allowed_file(filename: str) -> bool:
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_folder_exists(folder_path: Union[Path, str]) -> None:
    """Create the folder if it doesn't exist."""
    Path(folder_path).mkdir(parents=True, exist_ok=True)

def save_file(
    file_storage,
    subfolder: str,
    test_id: Union[str, int],
    student_id: Union[str, int, None] = None
) -> str:
    """
    Save uploaded file with a unique filename inside structured folders.

    Directory structure:
    <UPLOAD_FOLDER>/<subfolder>/<test_id>/<student_id_optional>/<uuid_filename>

    Returns the relative file path from UPLOAD_FOLDER.
    """
    upload_root = Path(current_app.config.get('UPLOAD_FOLDER'))
    if not upload_root:
        raise RuntimeError("UPLOAD_FOLDER not configured in app config")

    if not file_storage:
        raise ValueError("No file provided")

    filename = file_storage.filename
    if not allowed_file(filename):
        raise ValueError(f"File type not allowed: {filename}")

    unique_filename = f"{uuid.uuid4().hex}_{secure_filename(filename)}"

    dir_path = upload_root / subfolder / str(test_id)
    if student_id is not None:
        dir_path = dir_path / str(student_id)

    ensure_folder_exists(dir_path)

    file_path = dir_path / unique_filename
    file_storage.save(str(file_path))

    relative_path = file_path.relative_to(upload_root)
    return str(relative_path)

def create_test_directories(test_id: Union[str, int]) -> None:
    """
    Create required test-related folders for a given test_id based on app config.
    Folders created for 'answers', 'rubrics', 'guides', and 'submissions'.
    """
    base_folders = {
        'answers': current_app.config.get('UPLOAD_FOLDER_ANSWERS'),
        'rubrics': current_app.config.get('UPLOAD_FOLDER_RUBRICS'),
        'guides': current_app.config.get('UPLOAD_FOLDER_GUIDES'),
        'submissions': current_app.config.get('UPLOAD_FOLDER_SUBMISSIONS'),
    }

    for subfolder, base_path_str in base_folders.items():
        if not base_path_str:
            current_app.logger.error(f"Upload folder for '{subfolder}' not configured!")
            continue
        base_path = Path(base_path_str)
        path = base_path / str(test_id)
        try:
            ensure_folder_exists(path)
            current_app.logger.info(f"Created directory: {path}")
        except Exception as e:
            current_app.logger.error(f"Failed to create directory {path}: {e}")

def is_released(test_id: Union[str, int]) -> bool:
    """
    Check if the test is marked as released by reading metadata.json file.
    """
    metadata_path = Path(current_app.config.get('UPLOAD_FOLDER')) / "tests" / str(test_id) / "metadata.json"
    if not metadata_path.exists():
        return False
    try:
        with metadata_path.open('r') as f:
            metadata = json.load(f)
        return metadata.get('released', False)
    except Exception as e:
        current_app.logger.error(f"Failed to read metadata file {metadata_path}: {e}")
        return False

def delete_file_if_exists(filepath: Union[Path, str]) -> bool:
    """Delete a file if it exists."""
    try:
        path = Path(filepath)
        if path.exists():
            path.unlink()
            return True
    except Exception as e:
        current_app.logger.error(f"Could not delete file {filepath}: {e}")
    return False

def delete_files(file_paths: List[Union[Path, str]]) -> List[str]:
    """Delete multiple files and return a list of successfully deleted file paths."""
    deleted = []
    for path in file_paths:
        if delete_file_if_exists(path):
            deleted.append(str(path))
    return deleted

def move_files(file_paths: List[Union[Path, str]], target_folder: Union[Path, str]) -> List[str]:
    """Move files to a target folder, creating the folder if needed."""
    ensure_folder_exists(target_folder)
    moved = []
    for path in file_paths:
        try:
            src = Path(path)
            if src.exists():
                dest = Path(target_folder) / src.name
                shutil.move(str(src), str(dest))
                moved.append(str(dest))
        except Exception as e:
            current_app.logger.error(f"Could not move {path}: {e}")
    return moved
