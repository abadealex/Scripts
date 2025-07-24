import os
from flask import (
    current_app, send_file, abort
)
from flask_login import login_required, current_user

from smartscripts.models import MarkingGuide, StudentSubmission, Test
from . import teacher_bp


@teacher_bp.route('/download/guide/<int:guide_id>')
@login_required
def download_marking_guide(guide_id):
    guide = MarkingGuide.query.get_or_404(guide_id)
    if guide.teacher_id != current_user.id:
        abort(403)

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER_GUIDES'], guide.filename)
    if not os.path.isfile(file_path):
        abort(404)

    return send_file(file_path, as_attachment=True)


@teacher_bp.route('/download/rubric/<int:guide_id>')
@login_required
def download_rubric(guide_id):
    guide = MarkingGuide.query.get_or_404(guide_id)
    if guide.teacher_id != current_user.id:
        abort(403)

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER_RUBRICS'], guide.rubric_filename)
    if not os.path.isfile(file_path):
        abort(404)

    return send_file(file_path, as_attachment=True)


@teacher_bp.route('/download/answered_script/<int:test_id>')
@login_required
def download_answered_script(test_id):
    test = Test.query.get_or_404(test_id)
    if test.teacher_id != current_user.id:
        abort(403)

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER_ANSWERS'], test.answered_script_filename)
    if not os.path.isfile(file_path):
        abort(404)

    return send_file(file_path, as_attachment=True)


@teacher_bp.route('/download/submission/<int:submission_id>')
@login_required
def download_student_submission(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.test.teacher_id != current_user.id:
        abort(403)

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER_SUBMISSIONS'], submission.filename)
    if not os.path.isfile(file_path):
        abort(404)

    return send_file(file_path, as_attachment=True)
