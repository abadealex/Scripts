from flask_login import current_user
from flask import abort

def check_teacher_access():
    if not current_user.is_authenticated or current_user.role != 'teacher':
        abort(403)

def check_student_access():
    if not current_user.is_authenticated or current_user.role != 'student':
        abort(403)
