import os
import magic
from flask_login import current_user
from flask import abort, current_app
from werkzeug.utils import secure_filename

# Base upload directory
BASE_UPLOAD_FOLDER = 'static/uploads'


# ========== Access Control Utilities ==========

def check_role_access(required_role: str):
    """
    Aborts with 403 if the current user is not authenticated or lacks the required role.
    """
    if not current_user.is_authenticated or current_user.role != required_role:
        abort(403)


def check_teacher_access():
    check_role_access('teacher')


def check_student_access():
    check_role_access('student')


# ========== File Type Utilities ==========

def is_pdf(file) -> bool:
    """
    Checks if the uploaded file is a PDF based on MIME type.
    """
    file.seek(0)
    mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)
    return mime == 'application/pdf'


# ========== File Handling Utilities ==========

def allowed_file(filename: str) -> bool:
    """
    Checks if the uploaded file has an allowed extension.
    Uses app config if available, otherwise falls back to default set.
    """
    allowed_exts = current_app.config.get('ALLOWED_EXTENSIONS', {'jpg', 'jpeg', 'png', 'pdf'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts


def safe_remove(filepath: str):
    """
    Safely removes a file if it exists. Logs a warning on failure.
    """
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        current_app.logger.warning(f"Failed to delete file {filepath}: {e}")


def save_file(file, subfolder: str, test_id: int = None, student_id: int = None) -> str:
    """
    Saves an uploaded file under the correct subfolder path based on type and IDs.
    Returns a path relative to BASE_UPLOAD_FOLDER.
    """
    # Determine folder structure
    if subfolder == 'guides':
        folder_path = os.path.join(BASE_UPLOAD_FOLDER, 'guides')

    elif subfolder == 'rubrics':
        folder_path = os.path.join(BASE_UPLOAD_FOLDER, 'rubrics')

    elif subfolder == 'scripts' and test_id:
        folder_path = os.path.join(BASE_UPLOAD_FOLDER, 'scripts', f'test_id_{test_id}')

    elif subfolder == 'submissions' and test_id and student_id:
        folder_path = os.path.join(BASE_UPLOAD_FOLDER, 'submissions', f'test_id_{test_id}', f'student_id_{student_id}')

    elif subfolder == 'ocr_images' and test_id and student_id:
        folder_path = os.path.join(BASE_UPLOAD_FOLDER, 'submissions', f'test_id_{test_id}', f'student_id_{student_id}')

    elif subfolder == 'marked' and test_id and student_id:
        folder_path = os.path.join(BASE_UPLOAD_FOLDER, 'marked', f'test_id_{test_id}', f'student_id_{student_id}')

    elif subfolder == 'audit_logs' and test_id and student_id:
        folder_path = os.path.join(BASE_UPLOAD_FOLDER, 'audit_logs', f'test_id_{test_id}', f'student_id_{student_id}')

    elif subfolder == 'exports' and test_id:
        folder_path = os.path.join(BASE_UPLOAD_FOLDER, 'final_exports', f'test_id_{test_id}')

    else:
        raise ValueError(f"Invalid upload path parameters: subfolder={subfolder}, test_id={test_id}, student_id={student_id}")

    # Ensure directory exists
    os.makedirs(folder_path, exist_ok=True)

    # Save file safely
    filename = secure_filename(file.filename)
    full_path = os.path.join(folder_path, filename)
    file.save(full_path)

    # Return path relative to BASE_UPLOAD_FOLDER
    return os.path.relpath(full_path, BASE_UPLOAD_FOLDER)
