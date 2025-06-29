import os
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app, abort, send_from_directory
)
from flask_login import login_required, current_user

from smartscripts.app import db
from smartscripts.app.models import MarkingGuide, StudentSubmission
from smartscripts.utils.utils import check_teacher_access, check_student_access  # ✅ Correct import

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'teacher':
        return redirect(url_for('teacher_bp.dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('student_bp.dashboard'))
    else:
        abort(403)


@main_bp.route('/upload/guide')
@login_required
def upload_guide_redirect():
    check_teacher_access()
    return redirect(url_for('teacher_bp.upload_guide'))


@main_bp.route('/upload/submission')
@login_required
def upload_submission_redirect():
    check_student_access()
    return redirect(url_for('student_bp.student_upload'))


@main_bp.route('/submissions')
@login_required
def list_submissions():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    if current_user.role == 'teacher':
        submissions = StudentSubmission.query.order_by(
            StudentSubmission.timestamp.desc()
        ).paginate(page, per_page, error_out=False)
    elif current_user.role == 'student':
        submissions = StudentSubmission.query.filter_by(
            student_id=current_user.id
        ).order_by(StudentSubmission.timestamp.desc()).paginate(page, per_page, error_out=False)
    else:
        abort(403)

    return render_template('main/submissions.html', submissions=submissions)


@main_bp.route('/submission/<int:submission_id>')
@login_required
def view_submission(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)

    if submission.student_id != current_user.id and current_user.role != 'teacher':
        abort(403)

    return render_template('main/view_submission.html', submission=submission)


@main_bp.route('/download/report/<int:submission_id>')
@login_required
def download_report(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)

    if submission.student_id != current_user.id and current_user.role != 'teacher':
        abort(403)

    if not submission.report_filename:
        flash('No report available for download.', 'warning')
        return redirect(url_for('main_bp.view_submission', submission_id=submission_id))

    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    try:
        return send_from_directory(directory=upload_dir, filename=submission.report_filename, as_attachment=True)
    except FileNotFoundError:
        flash('Report file not found.', 'danger')
        return redirect(url_for('main_bp.view_submission', submission_id=submission_id))


@main_bp.route('/download/annotated/<int:submission_id>')
@login_required
def download_annotated(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)

    if submission.student_id != current_user.id and current_user.role != 'teacher':
        abort(403)

    if not submission.graded_image:
        flash('No annotated image available for download.', 'warning')
        return redirect(url_for('main_bp.view_submission', submission_id=submission_id))

    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    try:
        return send_from_directory(directory=upload_dir, filename=submission.graded_image, as_attachment=True)
    except FileNotFoundError:
        flash('Annotated file not found.', 'danger')
        return redirect(url_for('main_bp.view_submission', submission_id=submission_id))


# Error Handlers
@main_bp.app_errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@main_bp.app_errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


# Test Route
@main_bp.route('/test')
def test():
    return "Main blueprint is working!"


# DB Init Route (DEV ONLY)
@main_bp.route('/init-db')
def init_db():
    db.drop_all()
    db.create_all()
    return "Database initialized."
