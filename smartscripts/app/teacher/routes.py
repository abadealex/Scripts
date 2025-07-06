import os
import uuid
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app, abort, jsonify
)
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload

from smartscripts.extensions import db
from smartscripts.models import User, MarkingGuide, StudentSubmission, AuditLog
from smartscripts.app.forms import TeacherLoginForm, TeacherRegisterForm, MarkingGuideUploadForm
from smartscripts.utils.compress_image import compress_image
from smartscripts.utils.utils import check_teacher_access
from smartscripts.services.bulk_upload_service import process_bulk_files
from smartscripts.services.review_service import process_teacher_review
from smartscripts.ai.ocr_engine import trocr_extract_with_confidence

teacher_bp = Blueprint('teacher_bp', __name__, url_prefix='/teacher')

CONFIDENCE_THRESHOLD = 0.85

# Role check for teacher routes
@teacher_bp.before_request
def require_teacher_role():
    if request.endpoint and request.endpoint.startswith('teacher_bp.') and request.endpoint not in [
        'teacher_bp.login', 'teacher_bp.register', 'static'
    ]:
        if not current_user.is_authenticated or current_user.role != 'teacher':
            abort(403)
        check_teacher_access()

# Login route
@teacher_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('teacher_bp.dashboard'))

    form = TeacherLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, role='teacher').first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('teacher_bp.dashboard'))
        flash('Invalid email or password.', 'danger')

    return render_template('teacher/login.html', form=form)

# Registration route
@teacher_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('teacher_bp.dashboard'))

    form = TeacherRegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(email=form.email.data, password=hashed_password, role='teacher')
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('teacher_bp.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {e}")
            flash('Registration failed due to server error.', 'danger')

    return render_template('teacher/register.html', form=form)

# Logout route
@teacher_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('teacher_bp.login'))

# Dashboard route
@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    guides = MarkingGuide.query.filter_by(teacher_id=current_user.id).all()
    guide_filter = request.args.get("guide_id", type=int)

    guides_with_submissions = []
    for guide in guides:
        if guide_filter and guide.id != guide_filter:
            continue
        submissions = StudentSubmission.query.filter_by(guide_id=guide.id) \
            .options(joinedload(StudentSubmission.student)) \
            .order_by(StudentSubmission.timestamp.desc()).all()

        guides_with_submissions.append({
            "guide": guide,
            "submissions": submissions
        })

    return render_template('teacher/dashboard.html',
                           guides_with_submissions=guides_with_submissions,
                           selected_guide=guide_filter)

# Analytics route
@teacher_bp.route('/analytics')
@login_required
def analytics():
    return render_template('teacher/analytics.html')

# Upload marking guide route
@teacher_bp.route('/upload-guide', methods=['GET', 'POST'])
@login_required
def upload_guide():
    form = MarkingGuideUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        upload_dir = current_app.config.get('UPLOAD_FOLDER_GUIDES', 'uploads/guides')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_name)

        try:
            file.save(file_path)
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png')) and os.path.getsize(file_path) > 4 * 1024 * 1024:
                compressed = os.path.join(upload_dir, f"compressed_{unique_name}")
                compress_image(file_path, compressed)
                os.remove(file_path)
                file_path = compressed
                unique_name = os.path.basename(compressed)

            guide = MarkingGuide(title=form.title.data or filename,
                                 filename=unique_name,
                                 teacher_id=current_user.id,
                                 created_at=datetime.utcnow())
            db.session.add(guide)
            db.session.commit()
            flash('Guide uploaded.', 'success')
            return redirect(url_for('teacher_bp.dashboard'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Guide upload error: {e}")
            flash('Failed to upload guide.', 'danger')

    return render_template('teacher/upload.html', form=form)

# Rubric upload route (Added)
@teacher_bp.route('/rubric', methods=['GET', 'POST'])
@login_required
def rubric():
    # Add rubric upload logic here
    return render_template('teacher/rubric.html')

# Review route (Corrected as per your request)
@teacher_bp.route('/review/<int:submission_id>', methods=['GET'])
@login_required
def review(submission_id):
    # Fetch the submission from the database
    submission = StudentSubmission.query.get(submission_id)

    if submission is None:
        # Handle the case where submission doesn't exist
        return "Submission not found", 404

    # Pass submission_id to the template
    return render_template('teacher/review.html', submission=submission, submission_id=submission_id)

# Manual review submit route (NEW)
@teacher_bp.route('/manual_review/<int:submission_id>', methods=['POST'])
@login_required
def manual_review_submit(submission_id):
    # Fetch the submission to review
    submission = StudentSubmission.query.get(submission_id)

    if submission is None:
        flash('Submission not found.', 'danger')
        return redirect(url_for('teacher_bp.dashboard'))

    # Process review logic here (e.g. grading, feedback)
    # Example of processing the review (this logic can be replaced with your actual review processing code)
    feedback = request.form.get('feedback')
    grade = request.form.get('grade')

    if feedback and grade:
        submission.feedback = feedback
        submission.grade = grade
        db.session.commit()

        flash('Review submitted successfully!', 'success')
    else:
        flash('Please provide feedback and a grade.', 'danger')

    return redirect(url_for('teacher_bp.review', submission_id=submission_id))
