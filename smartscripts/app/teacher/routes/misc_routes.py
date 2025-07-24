from flask import render_template, flash, redirect, url_for, current_app, abort, jsonify
from flask_login import login_required, current_user
from smartscripts.models import Test
from smartscripts.utils.utils import check_teacher_access
from . import teacher_bp
from smartscripts.models import SubmissionManifest
import csv
import os
from flask import send_file
from smartscripts.utils.permissions import teacher_required




@teacher_bp.route('/analytics')
@login_required
def analytics():
    # TODO: Implement analytics view logic
    return render_template('teacher/analytics.html')


@teacher_bp.route('/rubric')
@login_required
def rubric():
    # TODO: Implement rubric view logic
    return render_template('teacher/rubric.html')


@teacher_bp.route('/process_test_scripts/<int:test_id>', methods=['POST'])
@login_required
def process_test_scripts(test_id):
    # TODO: Implement logic to process test scripts
    # For now, just simulate redirection or feedback
    test = Test.query.get_or_404(test_id)
    if not check_teacher_access(test.teacher_id):
        abort(403)
    
    flash(f"Test scripts for Test ID {test_id} processed.", "success")
    return redirect(url_for('teacher_bp.analytics'))

@teacher_bp.route('/submission_manifest/<int:test_id>', methods=['GET'])
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

@teacher_bp.route('/generate_dummy_class_list/<int:test_id>', methods=['GET'])
@login_required
@teacher_required
def generate_dummy_class_list(test_id):
    dir_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'class_lists', str(test_id))
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, 'class_list.csv')

    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['student_id'])
        for i in range(1001, 1021):
            writer.writerow([i])

    return send_file(file_path, as_attachment=True)
