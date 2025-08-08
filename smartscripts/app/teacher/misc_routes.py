from flask import (
    Blueprint, render_template, flash, redirect, url_for,
    current_app, abort, jsonify, send_file
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
import os
import csv

from smartscripts.models import Test, SubmissionManifest
from smartscripts.utils.utils import check_teacher_access
from smartscripts.utils.permissions import teacher_required

# 🔧 Blueprint
misc_bp = Blueprint('misc_bp', __name__)

# -------------------- ROUTES --------------------

@misc_bp.route('/misc')
def misc_something():
    return "Misc endpoint working!"

@misc_bp.route('/analytics')
@login_required
def analytics():
    return render_template('teacher/analytics.html')

@misc_bp.route('/rubric')
@login_required
def rubric():
    return render_template('teacher/rubric.html')

@misc_bp.route('/process_test_scripts/<int:test_id>', methods=['POST'])
@login_required
def process_test_scripts(test_id):
    test = Test.query.get_or_404(test_id)
    if not check_teacher_access(test.teacher_id):
        abort(403)
    flash(f"Test scripts for Test ID {test_id} processed.", "success")
    return redirect(url_for('misc_bp.analytics'))

@misc_bp.route('/submission_manifest/<int:test_id>')
@login_required
@teacher_required
def view_submission_manifest(test_id):
    manifests = SubmissionManifest.query.filter_by(test_id=test_id).all()
    data = [{
        "student_id": m.student_id,
        "pages_uploaded": m.pages_uploaded,
        "last_updated": m.updated_at.isoformat()
    } for m in manifests]
    return jsonify(data)

@misc_bp.route('/generate_dummy_student_list/<int:test_id>')  # 🔄 renamed endpoint
@login_required
@teacher_required
def generate_dummy_student_list(test_id):
    dir_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'student_lists', str(test_id))  # ✅ updated folder
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, 'student_list.csv')  # ✅ updated file name
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['student_id'])
        for i in range(1001, 1021):
            writer.writerow([i])
    return send_file(file_path, as_attachment=True)
