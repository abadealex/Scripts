from typing import List
from werkzeug.utils import secure_filename
import os

from smartscripts.utils.file_io import allowed_file, ensure_folder_exists, move_files


def save_file(file_storage, upload_folder: str, prefix: str = "") -> str:
    """
    Save an uploaded file securely with an optional prefix.
    Returns the saved file path.
    """
    ensure_folder_exists(upload_folder)
    filename = secure_filename(file_storage.submission_file)
    if prefix:
        filename = f"{prefix}_{filename}"
    filepath = os.path.join(upload_folder, filename)
    file_storage.save(filepath)
    return filepath


def save_multiple_files(files: List, upload_folder: str, prefix: str = "") -> List[str]:
    """
    Save multiple uploaded files and return a list of saved paths.
    """
    saved_paths = []
    ensure_folder_exists(upload_folder)
    for index, file_storage in enumerate(files):
        if file_storage and allowed_file(file_storage.submission_file):
            indexed_prefix = f"{prefix}_{index}" if prefix else f"{index}"
            path = save_file(file_storage, upload_folder, indexed_prefix)
            saved_paths.append(path)
    return saved_paths


def organize_into_batch_folder(base_folder: str, batch_name: str, files: List[str]) -> List[str]:
    """
    Move files into a batch-specific subfolder inside base_folder.
    """
    batch_folder = os.path.join(base_folder, batch_name)
    return move_files(files, batch_folder)

