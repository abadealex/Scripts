from flask import (
    Blueprint, render_template, abort, redirect, url_for, flash,
    send_file, request, current_app
)
from flask_login import login_required, current_user
from werkzeug.exceptions import Forbidden
import os

from ..models import MarkingGuide, StudentSubmission
from smartscripts.app import db

main_bp = Blueprint('main', __name__)

# --- Helper functions ---

def check_teacher_access(guide_or_submission):
    if current_user.role != 'teacher':
        raise Forbidden("Access denied: Teacher role required.")

    if isinstance(guide_or_submission, MarkingGuide):
        owner_id = guide_or_submission.teacher_id
    elif isinstance(guide_or_submission, StudentSubmission):
        owner_id = guide_or_submission.guide.teacher_id if guide_or_submission.guide else None
    else:
        owner_id = None

    if owner_id != current_user.id:
        raise Forbidden("You do not have permission to access this resource.")

def check_student_access(submission):
    if current_user.role != 'student':
        raise Forbidden("Access denied: Student role required.")
    if submission.student_id != current_user.id:
        raise Forbidden("You do not have permission to access this submission.")

def paginate_query(query, page, per_page=10):
    return query.paginate(page=page, per_page=per_page, error_out=False)

# --- Routes ---

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')  # ✅

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'teacher':
        return redirect(url_for('main.teacher_dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('main.student_dashboard'))
    else:
        abort(403)

@main_bp.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        abort(403)

    page = request.args.get('page', 1, type=int)
    guides_query = MarkingGuide.query.filter_by(teacher_id=current_user.id).order_by(MarkingGuide.created_at.desc())
    guides_pagination = paginate_query(guides_query, page)

    guides_with_submissions = []
    for guide in guides_pagination.items:
        submissions = StudentSubmission.query.filter_by(guide_id=guide.id).order_by(StudentSubmission.timestamp.desc()).all()
        guides_with_submissions.append({
            'guide': guide,
            'submissions': submissions
        })

    return render_template(
        'teacher/dashboard.html',  # ✅ moved to teacher/
        guides_with_submissions=guides_with_submissions,
        pagination=guides_pagination
    )

@main_bp.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        abort(403)

    page = request.args.get('page', 1, type=int)
    submissions_query = StudentSubmission.query.filter_by(student_id=current_user.id).order_by(StudentSubmission.timestamp.desc())
    submissions_pagination = paginate_query(submissions_query, page)

    return render_template(
        'student/dashboard.html',  # ✅ moved to student/
        submissions=submissions_pagination.items,
        pagination=submissions_pagination
    )

@main_bp.route('/submission/<int:submission_id>')
@login_required
def view_submission(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)

    if current_user.role == 'student':
        check_student_access(submission)
    elif current_user.role == 'teacher':
        check_teacher_access(submission)
    else:
        abort(403)

    return render_template('main/view_result.html', submission=submission)  # ✅ renamed from view_submission

@main_bp.route('/submission/<int:submission_id>/download/pdf')
@login_required
def download_pdf(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)

    if current_user.role == 'student':
        check_student_access(submission)
    elif current_user.role == 'teacher':
        check_teacher_access(submission)
    else:
        abort(403)

    pdf_path = None
    if submission.report_filename:
        pdf_path = os.path.join(
            current_app.config.get('REPORT_FOLDER', 'uploads/reports'),
            submission.report_filename
        )

    if not pdf_path or not os.path.isfile(pdf_path):
        flash("PDF report not found.", "warning")
        return redirect(url_for('main.view_submission', submission_id=submission_id))

    base_name = os.path.splitext(submission.answer_filename or 'submission')[0]
    download_name = f"{base_name}_report.pdf"

    return send_file(pdf_path, as_attachment=True, download_name=download_name)

@main_bp.route('/submission/<int:submission_id>/download/annotated')
@login_required
def download_annotated(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)

    if current_user.role == 'student':
        check_student_access(submission)
    elif current_user.role == 'teacher':
        check_teacher_access(submission)
    else:
        abort(403)

    annotated_path = None
    if submission.graded_image:
        annotated_path = os.path.join(
            current_app.config.get('ANNOTATED_FOLDER', 'uploads/annotated'),
            submission.graded_image
        )

    if not annotated_path or not os.path.isfile(annotated_path):
        flash("Annotated file not found.", "warning")
        return redirect(url_for('main.view_submission', submission_id=submission_id))

    base_name = os.path.splitext(submission.answer_filename or 'submission')[0]
    download_name = f"{base_name}_annotated.jpg"

    return send_file(annotated_path, as_attachment=True, download_name=download_name)

@main_bp.route('/upload/guide', methods=['GET', 'POST'])
@login_required
def upload_guide():
    if current_user.role != 'teacher':
        abort(403)
    return render_template('teacher/upload.html')  # ✅ moved to teacher/

@main_bp.route('/upload/submission', methods=['GET', 'POST'])
@login_required
def upload_submission():
    if current_user.role != 'student':
        abort(403)
    return render_template('student/upload.html')  # ✅ moved to student/

@main_bp.route('/init-db')
def init_db():
    db.create_all()
    return "✅ Database tables created successfully!"

# --- Error Handlers ---

@main_bp.app_errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

@main_bp.route('/test-error')
def test_error():
    return render_template("errors/500.html")
