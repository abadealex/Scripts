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
from smartscripts.app.utils import allowed_file, grade_submission
from smartscripts.utils.utils import check_student_access
from smartscripts.utils.compress_image import compress_image

# Blueprint setup
student_bp = Blueprint('student_bp', __name__, url_prefix='/student')


# Access control for all student routes
@student_bp.before_request
@login_required
def require_student_role():
    if current_user.role != 'student':
        abort(403)


# ✅ Step 1: Add student dashboard route
@student_bp.route('/dashboard')
@login_required
def dashboard():
    check_student_access()  # Ensures student permissions
    return render_template('student/dashboard.html')  # Make sure this template exists


# Student upload route
@student_bp.route('/upload', methods=['GET', 'POST'])
def student_upload():
    form = StudentUploadForm()

    # Populate marking guide dropdown
    form.guide_id.choices = [
        (g.id, g.title) for g in MarkingGuide.query.order_by(MarkingGuide.created_at.desc()).all()
    ]

    if form.validate_on_submit():
        file = form.file.data

        if not file or not file.filename.strip():
            flash('No file selected.', 'danger')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Invalid file type. Only JPG, JPEG, PNG, and PDF are allowed.', 'danger')
            return redirect(request.url)

        # Check file size
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)

        max_mb = current_app.config.get('MAX_FILE_SIZE_MB', 10)
        if file_length > max_mb * 1024 * 1024:
            flash(f'File exceeds the {max_mb}MB limit.', 'danger')
            return redirect(request.url)

        # Secure and unique filename
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"

        upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        filepath = os.path.join(upload_dir, unique_name)
        file.save(filepath)

        # Compress large images
        if filepath.lower().endswith(('.jpg', '.jpeg', '.png')) and os.path.getsize(filepath) > 4 * 1024 * 1024:
            compressed_path = os.path.join(upload_dir, f"compressed_{unique_name}")
            compress_image(filepath, compressed_path)
            os.remove(filepath)
            filepath = compressed_path
            unique_name = os.path.basename(compressed_path)

        current_app.logger.info(f"Student {current_user.email} uploaded file {filename}")

        guide = MarkingGuide.query.get_or_404(form.guide_id.data)

        try:
            result = grade_submission(filepath, guide, current_user.email, output_dir=upload_dir)
        except Exception as e:
            current_app.logger.error(f"Grading error: {str(e)}")
            flash(f"Grading failed: {str(e)}", "danger")
            return redirect(request.url)

        annotated_file = result.get('annotated_file')
        pdf_report = result.get('pdf_report')

        # Store relative paths
        if annotated_file and annotated_file.startswith(upload_dir):
            annotated_file = os.path.relpath(annotated_file, upload_dir)
        if pdf_report and pdf_report.startswith(upload_dir):
            pdf_report = os.path.relpath(pdf_report, upload_dir)

        submission = StudentSubmission(
            student_id=current_user.id,
            guide_id=guide.id,
            answer_filename=unique_name,
            graded_image=annotated_file,
            report_filename=pdf_report,
            grade=result.get('total_score'),
            feedback=result.get('feedback', ''),
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

        flash('Submission graded and uploaded successfully!', 'success')
        return redirect(url_for('student_bp.view_single_result', submission_id=submission.id))

    return render_template('student/upload.html', form=form)


# View a single submission result
@student_bp.route('/submission/<int:submission_id>')
@login_required
def view_single_result(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)

    # Access control
    if submission.student_id != current_user.id and current_user.role != 'teacher':
        abort(403)

    return render_template('student/view_result.html', submission=submission)
