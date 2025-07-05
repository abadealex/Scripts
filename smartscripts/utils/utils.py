from flask_login import current_user
from flask import abort, current_app


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


def allowed_file(filename: str) -> bool:
    """
    Checks if the uploaded file has an allowed extension.
    Uses app config if available, otherwise falls back to default set.
    """
    allowed_exts = current_app.config.get('ALLOWED_EXTENSIONS', {'jpg', 'jpeg', 'png', 'pdf'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts
