import os
import uuid
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app, abort
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from smartscripts.app import db
from smartscripts.app.forms import StudentUploadForm
from smartscripts.app.models import MarkingGuide, StudentSubmission
from smartscripts.utils.utils import allowed_file
from smartscripts.utils.compress_image import compress_image
from smartscripts.utils import check_student_access
from smartscripts.ai.marking_pipeline import mark_submission

student_bp = Blueprint('student_bp', __name__, url_prefix='/student')


@student_bp.before_request
@login_required
def require_student_role():
    if current_user.role != 'student':
        abort(403)


@student_bp.route('/dashboard')
@login_required
def dashboard():
    check_student_access()
    submissions = StudentSubmission.query.filter_by(student_id=current_user.id).order_by(StudentSubmission.timestamp.desc()).all()
    return render_template('student/dashboard.html', submissions=submissions)


@student_bp.route('/upload', methods=['GET', 'POST'])
def student_upload():
    form = StudentUploadForm()

    form.guide_id.choices = [
        (g.id, f"{g.title} ({g.subject})") for g in MarkingGuide.query.order_by(MarkingGuide.created_at.desc()).all()
    ]

    if form.validate_on_submit():
        file = form.file.data

        if not file or not file.filename.strip():
            flash('No file selected.', 'danger')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Invalid file type. Only JPG, PNG, or PDF allowed.', 'danger')
            return redirect(request.url)

        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)

        max_mb = current_app.config.get('MAX_FILE_SIZE_MB', 10)
        if file_length > max_mb * 1024 * 1024:
            flash(f'File exceeds the {max_mb}MB limit.', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        uuid_token = uuid.uuid4().hex
        original_filename = f"{uuid_token}_original_{filename}"
        annotated_filename = f"{uuid_token}_annotated_{filename}"

        upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        original_path = os.path.join(upload_dir, original_filename)
        file.save(original_path)

        if original_path.lower().endswith(('.jpg', '.jpeg', '.png')) and os.path.getsize(original_path) > 4 * 1024 * 1024:
            compressed_path = os.path.join(upload_dir, f"compressed_{original_filename}")
            compress_image(original_path, compressed_path)
            os.remove(original_path)
            original_path = compressed_path

        current_app.logger.info(f"Student {current_user.email} uploaded file {filename}")

        guide = MarkingGuide.query.get_or_404(form.guide_id.data)

        try:
            result = mark_submission(
                file_path=original_path,
                marking_guide=guide,
                student_email=current_user.email,
                output_dir=upload_dir
            )
        except Exception as e:
            current_app.logger.error(f"Grading error: {str(e)}")
            flash("Grading failed. Please try again later.", "danger")
            return redirect(url_for('student_bp.student_upload'))

        annotated_file = result.get('annotated_file')
        pdf_report = result.get('pdf_report')
        ai_confidence = result.get('ai_confidence', None)
        feedback = result.get('feedback', '')
        grade = result.get('total_score', None)

        annotated_file = os.path.relpath(annotated_file, upload_dir) if annotated_file else None
        pdf_report = os.path.relpath(pdf_report, upload_dir) if pdf_report else None
        original_file_rel = os.path.relpath(original_path, upload_dir)

        submission = StudentSubmission(
            student_id=current_user.id,
            guide_id=guide.id,
            subject=guide.subject,
            grade_level=guide.grade_level,
            answer_filename=original_file_rel,
            graded_image=annotated_file,
            report_filename=pdf_report,
            grade=grade,
            feedback=feedback,
            ai_confidence=ai_confidence,
            timestamp=datetime.utcnow()
        )

        try:
            db.session.add(submission)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"DB Commit failed: {e}")
            flash("Failed to save submission. Please try again.", "danger")
            return redirect(request.url)

        flash('Submission graded successfully!', 'success')
        return redirect(url_for('student_bp.view_single_result', submission_id=submission.id))

    return render_template('student/upload.html', form=form)


@student_bp.route('/submission/<int:submission_id>')
@login_required
def view_single_result(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.student_id != current_user.id and current_user.role != 'teacher':
        abort(403)
    return render_template('student/view_result.html', submission=submission)


@student_bp.route('/retry/<int:submission_id>', methods=['POST'])
@login_required
def retry_submission(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.student_id != current_user.id:
        abort(403)

    guide = MarkingGuide.query.get_or_404(submission.guide_id)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], submission.answer_filename)

    try:
        result = mark_submission(
            file_path=file_path,
            marking_guide=guide,
            student_email=current_user.email,
            output_dir=current_app.config['UPLOAD_FOLDER']
        )
    except Exception as e:
        current_app.logger.error(f"Retry grading failed: {str(e)}")
        flash("Retry failed. Please try again later.", "danger")
        return redirect(url_for('student_bp.view_single_result', submission_id=submission_id))

    submission.graded_image = os.path.relpath(result.get('annotated_file'), current_app.config['UPLOAD_FOLDER'])
    submission.report_filename = os.path.relpath(result.get('pdf_report'), current_app.config['UPLOAD_FOLDER'])
    submission.grade = result.get('total_score')
    submission.feedback = result.get('feedback', '')
    submission.ai_confidence = result.get('ai_confidence')
    submission.timestamp = datetime.utcnow()

    try:
        db.session.commit()
        flash("Submission regraded successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Retry failed to save. Try again.", "danger")

    return redirect(url_for('student_bp.view_single_result', submission_id=submission.id))


# ✅ NEW ROUTE FOR FEEDBACK PAGE
@student_bp.route('/feedback/<int:submission_id>')
@login_required
def view_feedback(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.student_id != current_user.id and current_user.role != 'teacher':
        abort(403)

    # TEMP STATIC FEEDBACK DATA FOR TESTING
    feedback_data = [
        {
            "number": 1,
            "student_answer": "x = 3",
            "expected_answer": "x = 3",
            "score": 5,
            "max_score": 5,
            "feedback": "Perfect solution.",
            "override": False,
        },
        {
            "number": 2,
            "student_answer": "Area = 10",
            "expected_answer": "Area = 12",
            "score": 3,
            "max_score": 5,
            "feedback": "You missed the final multiplication step.",
            "override": True,
        },
    ]

    return render_template("student/feedback.html",
                           exam_title=submission.marking_guide.title,
                           feedback_data=feedback_data)
