# smartscripts/utils/file_io.py

import os
import json
import shutil
from pathlib import Path
from typing import List, Union
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}


def allowed_file(filename: str) -> bool:
    """Check if file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_folder_exists(folder_path: Union[Path, str]) -> None:
    """Create folder if it doesn't exist."""
    Path(folder_path).mkdir(parents=True, exist_ok=True)


def save_file(file_storage, subfolder: str, test_id: Union[str, int], student_id: Union[str, int, None] = None) -> str:
    """
    Save uploaded file to structured folder path based on test and (optionally) student ID.
    Returns relative path to UPLOAD_FOLDER root.
    """
    upload_root_str = current_app.config.get('UPLOAD_FOLDER')
    if not isinstance(upload_root_str, str):
        raise RuntimeError("UPLOAD_FOLDER not configured correctly in app config")
    upload_root = Path(upload_root_str)

    if file_storage is None:
        raise ValueError("No file provided")

    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename):
        raise ValueError(f"File type not allowed: {filename}")

    # Build target path
    dir_path = upload_root / subfolder / str(test_id)
    if student_id is not None:
        dir_path /= str(student_id)

    ensure_folder_exists(dir_path)

    file_path = dir_path / filename
    file_storage.save(str(file_path))

    return str(file_path.relative_to(upload_root))


def create_test_directories(test_id: Union[str, int]) -> None:
    """
    Create upload folders for a given test ID under answers, rubrics, guides, and submissions.
    """
    base_folders = {
        'answers': current_app.config.get('UPLOAD_FOLDER_ANSWERS'),
        'rubrics': current_app.config.get('UPLOAD_FOLDER_RUBRICS'),
        'guides': current_app.config.get('UPLOAD_FOLDER_GUIDES'),
        'submissions': current_app.config.get('UPLOAD_FOLDER_SUBMISSIONS'),
    }

    for subfolder, base_path_str in base_folders.items():
        if not isinstance(base_path_str, str):
            current_app.logger.error(f"Upload folder for '{subfolder}' not configured!")
            continue

        path = Path(base_path_str) / str(test_id)
        try:
            ensure_folder_exists(path)
            current_app.logger.info(f"? Created directory: {path}")
        except Exception as e:
            current_app.logger.error(f"? Failed to create directory {path}: {e}")


def is_released(test_id: Union[str, int]) -> bool:
    """
    Check metadata.json for a given test ID to determine if it's marked as released.
    """
    upload_root_str = current_app.config.get('UPLOAD_FOLDER')
    if not isinstance(upload_root_str, str):
        current_app.logger.error("UPLOAD_FOLDER not configured properly")
        return False
    metadata_path = Path(upload_root_str) / "tests" / str(test_id) / "metadata.json"
    if not metadata_path.exists():
        return False
    try:
        with metadata_path.open('r') as f:
            metadata = json.load(f)
        return metadata.get('released', False)
    except Exception as e:
        current_app.logger.error(f"Failed to read metadata {metadata_path}: {e}")
        return False


def delete_file_if_exists(filepath: Union[Path, str]) -> bool:
    """
    Delete file if it exists. Returns True if deleted, False otherwise.
    """
    try:
        path = Path(filepath)
        if path.exists():
            path.unlink()
            return True
    except Exception as e:
        current_app.logger.error(f"Could not delete file {filepath}: {e}")
    return False


def delete_files(file_paths: List[Union[Path, str]]) -> List[str]:
    """Delete multiple files and return list of successfully deleted paths."""
    return [str(p) for p in file_paths if delete_file_if_exists(p)]


def move_files(file_paths: List[Union[Path, str]], target_folder: Union[Path, str]) -> List[str]:
    """
    Move multiple files to a target folder.
    Returns a list of new paths for successfully moved files.
    """
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
            current_app.logger.error(f"Could not move {path} ? {target_folder}: {e}")
    return moved
