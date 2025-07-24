from flask import abort
from flask_login import current_user

def teacher_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous or current_user.role != 'teacher':
            abort(403, description="Only teachers can perform this action.")
        return f(*args, **kwargs)
    return decorated_function
