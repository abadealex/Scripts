import os

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app, abort,
    send_from_directory, jsonify
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from celery.result import AsyncResult

from smartscripts.utils.utils import check_teacher_access, check_student_access
from smartscripts.models.student_submission import StudentSubmission  
from smartscripts.extensions import db, celery     

from smartscripts.services.review_service import (
    get_review_history, process_teacher_review
)

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/', methods=['GET'])
def index():
    return render_template('main/index.html')


@main_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.role == 'teacher':
        return redirect(url_for('teacher_bp.dashboard_bp.dashboard'))
    else:
        abort(403)


@main_bp.route('/upload/guide', methods=['GET'])
@login_required
def upload_guide_redirect():
    check_teacher_access()
    return redirect(url_for('teacher_bp.export_upload_guide_page'))


@main_bp.route('/upload/submission', methods=['GET'])
@login_required
def upload_submission_redirect():
    check_student_access()
    return redirect(url_for('student_bp.student_upload'))


@main_bp.route('/submissions', methods=['GET'])
@login_required
def list_submissions():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    if current_user.role == 'teacher':
        submissions = StudentSubmission.query.order_by(
            StudentSubmission.timestamp.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
    elif current_user.role == 'student':
        submissions = StudentSubmission.query.filter_by(
            student_id=current_user.id
        ).order_by(StudentSubmission.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False)
    else:
        abort(403)

    return render_template('main/submissions.html', submissions=submissions)


@main_bp.route('/submission/<int:submission_id>', methods=['GET'])
@login_required
def view_submission(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.student_id != current_user.id and current_user.role != 'teacher':
        abort(403)

    return render_template('main/view_submission.html', submission=submission)


@main_bp.route('/download/report/<int:submission_id>', methods=['GET'])
@login_required
def download_report(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)

    if submission.student_id != current_user.id and current_user.role != 'teacher':
        abort(403)

    if not submission.report_filename:
        flash('No report available for download.', 'warning')
        return redirect(url_for('main_bp.view_submission', submission_id=submission_id))

    upload_dir = current_app.config.get('UPLOAD_FOLDER') or os.path.join(current_app.root_path, 'uploads')
    report_path = os.path.join(upload_dir, submission.report_filename)

    if not os.path.exists(report_path):
        flash('Report file not found.', 'danger')
        return redirect(url_for('main_bp.view_submission', submission_id=submission_id))

    return send_from_directory(directory=upload_dir, path=submission.report_filename, as_attachment=True)


@main_bp.route('/download/annotated/<int:submission_id>', methods=['GET'])
@login_required
def download_annotated(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)

    if submission.student_id != current_user.id and current_user.role != 'teacher':
        abort(403)

    if not submission.graded_image:
        flash('No annotated image available for download.', 'warning')
        return redirect(url_for('main_bp.view_submission', submission_id=submission_id))

    upload_dir = current_app.config.get('UPLOAD_FOLDER') or os.path.join(current_app.root_path, 'uploads')
    annotated_path = os.path.join(upload_dir, submission.graded_image)

    if not os.path.exists(annotated_path):
        flash('Annotated file not found.', 'danger')
        return redirect(url_for('main_bp.view_submission', submission_id=submission_id))

    return send_from_directory(directory=upload_dir, path=submission.graded_image, as_attachment=True)


@main_bp.route('/api/reviews/<int:submission_id>', methods=['GET'])
@login_required
def get_review(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if current_user.role != 'teacher' and submission.student_id != current_user.id:
        abort(403)

    review_data = {
        question_id: get_review_history(question_id)
        for question_id in submission.get_question_ids()
    }

    return jsonify({
        "submission_id": submission_id,
        "reviews": review_data,
    })


@main_bp.route('/api/reviews/<int:submission_id>/feedback', methods=['POST'])
@login_required
def post_feedback(submission_id):
    if current_user.role != 'teacher':
        abort(403)

    data = request.json or {}

    # Fallback to empty string for type safety
    question_id = str(data.get('question_id') or "")
    original_text = str(data.get('original_text') or "")
    corrected_text = str(data.get('corrected_text') or "")
    feedback = data.get('feedback')
    comment = data.get('comment')

    if not all([question_id.strip(), original_text.strip(), corrected_text.strip()]):
        return jsonify({"error": "Missing required fields"}), 400

    override = process_teacher_review(
        reviewer_id=current_user.id,
        question_id=question_id,
        original_text=original_text,
        corrected_text=corrected_text,
        feedback=feedback,
        comment=comment
    )

    return jsonify({
        "message": "Feedback recorded successfully",
        "override_id": override.id
    })


@main_bp.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = AsyncResult(task_id, app=celery)
    if not task:
        abort(404, description="Task not found")

    return jsonify({
        'task_id': task_id,
        'state': task.state,
        'status': task.info if isinstance(task.info, dict) else {'message': str(task.info)}
    })


@main_bp.app_errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403


@main_bp.app_errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


@main_bp.route('/test', methods=['GET'])
def test():
    return "Main blueprint is working!"


@main_bp.route('/init-db', methods=['GET'])
def init_db():
    db.drop_all()
    db.create_all()
    return "Database initialized."
