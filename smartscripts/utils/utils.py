from flask_login import current_user
from flask import abort

def check_teacher_access():
    """
    Checks if the current user is authenticated and has the 'teacher' role.
    If not, it aborts with a 403 Forbidden error.
    """
    if not current_user.is_authenticated or current_user.role != 'teacher':
        abort(403)

def check_student_access():
    """
    Checks if the current user is authenticated and has the 'student' role.
    If not, it aborts with a 403 Forbidden error.
    """
    if not current_user.is_authenticated or current_user.role != 'student':
        abort(403)

def allowed_file(filename):
    """
    Checks if the uploaded file has an allowed extension.
    """
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
