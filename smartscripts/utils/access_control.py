from flask_login import current_user
from flask import abort

def check_role_access(required_role: str):
    if not current_user.is_authenticated or current_user.role != required_role:
        abort(403)

def check_teacher_access():
    check_role_access('teacher')

def check_student_access():
    check_role_access('student')
