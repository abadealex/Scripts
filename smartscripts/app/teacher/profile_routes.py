# smartscripts/app/teacher/profile_routes.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user

teacher_profile_bp = Blueprint('teacher_profile_bp', __name__)

@teacher_profile_bp.route('/profile')
@login_required
def profile():
    return render_template('teacher/profile.html', user=current_user)

@teacher_profile_bp.route('/settings')
@login_required
def settings():
    return render_template('teacher/settings.html', user=current_user)
