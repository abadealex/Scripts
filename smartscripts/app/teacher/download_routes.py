import os
from flask import (
    Blueprint, current_app, send_file, abort,
    flash, redirect, url_for
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from smartscripts.models import MarkingGuide, StudentSubmission, Test

# Define the blueprint correctly
download_bp = Blueprint('download_bp', __name__)

def secure_file_download(file_path):
    """Helper function to check file existence and return it."""
    if not os.path.isfile(file_path):
        abort(404)
    return send_file(file_path, as_attachment=True)

@download_bp.route('/download/guide/<int:guide_id>')
@login_required
def download_marking_guide(guide_id):
    guide = MarkingGuide.query.get_or_404(guide_id)
    if guide.teacher_id != current_user.id:
        abort(403)

    file_path = os.path.join(
        current_app.config['UPLOAD_FOLDER_GUIDES'],
        guide.filename
    )
    return secure_file_download(file_path)

@download_bp.route('/download/rubric/<int:guide_id>')
@login_required
def download_rubric(guide_id):
    guide = MarkingGuide.query.get_or_404(guide_id)
    if guide.teacher_id != current_user.id:
        abort(403)

    file_path = os.path.join(
        current_app.config['UPLOAD_FOLDER_RUBRICS'],
        guide.rubric_filename
    )
    return secure_file_download(file_path)

@download_bp.route('/download/answered_script/<int:test_id>')
@login_required
def download_answered_script(test_id):
    test = Test.query.get_or_404(test_id)
    if test.teacher_id != current_user.id:
        abort(403)

    file_path = os.path.join(
        current_app.config['UPLOAD_FOLDER_ANSWERS'],
        test.answered_script_filename
    )
    return secure_file_download(file_path)

@download_bp.route('/download/submission/<int:submission_id>')
@login_required
def download_student_submission(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.test.teacher_id != current_user.id:
        abort(403)

    file_path = os.path.join(
        current_app.config['UPLOAD_FOLDER_SUBMISSIONS'],
        submission.filename
    )
    return secure_file_download(file_path)

@download_bp.route('/download/marked_zip/<int:test_id>')
@login_required
def download_marked_zip(test_id):
    zip_path = os.path.join(
        current_app.config['EXPORT_FOLDER'],
        'marked_scripts',
        f"test_{test_id}_marked.zip"
    )
    if not os.path.exists(zip_path):
        flash("Marked scripts ZIP not available yet.", "warning")
        return redirect(url_for('teacher.dashboard'))
    return send_file(zip_path, as_attachment=True)

# Optional test route
@download_bp.route('/download/sample')
def download_sample():
    return send_file('path/to/sample.pdf')
