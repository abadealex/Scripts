# smartscripts/teacher/routes.py

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

from smartscripts.app import db
from smartscripts.app.models import User, MarkingGuide, StudentSubmission, AuditLog
from smartscripts.app.forms import TeacherLoginForm, TeacherRegisterForm, MarkingGuideUploadForm
from smartscripts.utils.compress_image import compress_image
from smartscripts.utils.utils import check_teacher_access
from smartscripts.services.bulk_upload_service import process_bulk_files
from smartscripts.services.review_service import process_teacher_review
from smartscripts.ai.ocr_engine import trocr_extract_with_confidence

teacher_bp = Blueprint('teacher_bp', __name__, url_prefix='/teacher')

CONFIDENCE_THRESHOLD = 0.85


@teacher_bp.before_request
def require_teacher_role():
    if request.endpoint and request.endpoint.startswith('teacher_bp.') and request.endpoint not in [
        'teacher_bp.login', 'teacher_bp.register', 'static'
    ]:
        if not current_user.is_authenticated or current_user.role != 'teacher':
            abort(403)
        check_teacher_access()


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


@teacher_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('teacher_bp.login'))


@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    guides = MarkingGuide.query.filter_by(teacher_id=current_user.id).all()
    guide_filter = request.args.get("guide_id", type=int)

    guides_with_submissions = []
    for guide in guides:
        if guide_filter and guide.id != guide_filter:
            continue
        submissions = StudentSubmission.query.filter_by(guide_id=guide.id)\
            .options(joinedload(StudentSubmission.student))\
            .order_by(StudentSubmission.timestamp.desc()).all()

        guides_with_submissions.append({
            "guide": guide,
            "submissions": submissions
        })

    return render_template('teacher/dashboard.html',
                           guides_with_submissions=guides_with_submissions,
                           selected_guide=guide_filter)


@teacher_bp.route('/analytics')
@login_required
def analytics():
    return render_template('teacher/analytics.html')


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


@teacher_bp.route('/rubric-upload', methods=['GET', 'POST'])
@login_required
def rubric():
    if request.method == 'POST':
        rubric_file = request.files.get('rubric_file')
        exam_title = request.form.get('exam_title')
        if not rubric_file:
            flash('No file provided.', 'danger')
            return redirect(request.url)

        filename = secure_filename(rubric_file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        upload_dir = current_app.config.get('UPLOAD_FOLDER_RUBRICS', 'uploads/rubrics')
        os.makedirs(upload_dir, exist_ok=True)

        try:
            rubric_file.save(os.path.join(upload_dir, unique_name))
            flash(f'Rubric "{exam_title}" uploaded.', 'success')
            return redirect(url_for('teacher_bp.dashboard'))
        except Exception as e:
            current_app.logger.error(f"Rubric upload error: {e}")
            flash('Rubric upload failed.', 'danger')

    return render_template('teacher/rubric_upload.html')


@teacher_bp.route('/review/<int:submission_id>', methods=['GET'])
@login_required
def review(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.guide.teacher_id != current_user.id:
        abort(403)

    return render_template('teacher/review.html',
                           submission=submission,
                           student_name=submission.student.username)


@teacher_bp.route('/manual_review_submit/<int:submission_id>', methods=['POST'])
@login_required
def manual_review_submit(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.guide.teacher_id != current_user.id:
        abort(403)

    for result in submission.results:
        score = request.form.get(f"score_{result.question_number}")
        comment = request.form.get(f"comment_{result.question_number}")
        if score:
            try:
                result.score = float(score)
            except ValueError:
                continue
        if comment:
            result.feedback = comment

    db.session.commit()
    flash('Review submitted.', 'success')
    return redirect(url_for('teacher_bp.dashboard'))


@teacher_bp.route('/upload/bulk', methods=['POST'])
@login_required
def upload_bulk():
    files = request.files.getlist('files')
    if not files:
        return jsonify({'status': 'error', 'message': 'No files provided.'}), 400

    upload_dir = current_app.config.get('UPLOAD_FOLDER_BULK', 'uploads/bulk')
    os.makedirs(upload_dir, exist_ok=True)
    saved_paths = []

    for file in files:
        name = secure_filename(file.filename)
        if name:
            path = os.path.join(upload_dir, name)
            file.save(path)
            saved_paths.append(path)

    try:
        process_bulk_files(saved_paths)
        return jsonify({'status': 'success', 'files_received': len(saved_paths)})
    except Exception as e:
        current_app.logger.error(f"Bulk upload error: {e}")
        return jsonify({'status': 'error', 'message': 'Processing failed.'}), 500


@teacher_bp.route('/review_script', methods=['POST'])
@login_required
def review_script():
    submission_id = request.json.get("submission_id")
    submission = StudentSubmission.query.get(submission_id)

    if not submission or submission.guide.teacher_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    extracted_text, confidence = trocr_extract_with_confidence(submission.image_path)
    submission.extracted_text = extracted_text
    submission.confidence = confidence
    submission.needs_human_review = confidence < CONFIDENCE_THRESHOLD
    db.session.commit()

    return jsonify({
        "extracted_text": extracted_text,
        "confidence": confidence,
        "needs_human_review": submission.needs_human_review
    })


@teacher_bp.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    submission_id = request.json.get("submission_id")
    corrected_text = request.json.get("corrected_text")
    manual_override = request.json.get("manual_override", False)

    submission = StudentSubmission.query.get(submission_id)
    if not submission or submission.guide.teacher_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    original_text = submission.extracted_text
    if manual_override and corrected_text != original_text:
        submission.extracted_text = corrected_text
        submission.reviewed_by = current_user.id
        submission.manual_override = True

        audit = AuditLog(
            submission_id=submission.id,
            user_id=current_user.id,
            action="manual_override",
            old_text=original_text,
            new_text=corrected_text
        )
        db.session.add(audit)

    db.session.commit()
    return jsonify({"success": True})
