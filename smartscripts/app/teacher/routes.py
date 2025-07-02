import os
import uuid
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app, abort
)
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload

from smartscripts.app import db
from smartscripts.app.models import User, MarkingGuide, StudentSubmission
from smartscripts.app.forms import TeacherLoginForm, TeacherRegisterForm, MarkingGuideUploadForm
from smartscripts.utils.compress_image import compress_image
from smartscripts.utils.utils import check_teacher_access  # ✅ Import added

teacher_bp = Blueprint('teacher_bp', __name__, url_prefix='/teacher')


@teacher_bp.before_request
def require_teacher_role():
    if request.endpoint is None or not request.endpoint.startswith('teacher_bp.'):
        return
    exempt_routes = ['teacher_bp.login', 'teacher_bp.register', 'static']
    if request.endpoint not in exempt_routes:
        if not current_user.is_authenticated or current_user.role != 'teacher':
            abort(403)
        check_teacher_access()  # Optional: for more granular access control


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
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('teacher/login.html', form=form)


@teacher_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('teacher_bp.dashboard'))

    form = TeacherRegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(email=form.email.data, password=hashed_password, role='teacher')
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('teacher_bp.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Teacher registration DB commit failed: {e}")
            flash('Registration failed due to server error.', 'danger')

    return render_template('teacher/register.html', form=form)


@teacher_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
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

        submissions = (
            StudentSubmission.query
            .options(joinedload(StudentSubmission.student))
            .filter_by(guide_id=guide.id)
            .order_by(StudentSubmission.timestamp.desc())
            .all()
        )
        guides_with_submissions.append({
            "guide": guide,
            "submissions": submissions
        })

    return render_template(
        "teacher/dashboard.html",
        guides_with_submissions=guides_with_submissions,
        selected_guide=guide_filter
    )


@teacher_bp.route('/upload-guide', methods=['GET', 'POST'])
@login_required
def upload_guide():
    form = MarkingGuideUploadForm()
    if form.validate_on_submit():
        file = form.file.data

        if not file or not file.filename.strip():
            flash('No file selected.', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        upload_dir = current_app.config.get('UPLOAD_FOLDER_GUIDES', 'uploads/guides')
        
        # Ensure the directory exists
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, unique_name)
        try:
            file.save(file_path)

            # Compress large images (>4MB)
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png')) and os.path.getsize(file_path) > 4 * 1024 * 1024:
                compressed_path = os.path.join(upload_dir, f"compressed_{unique_name}")
                compress_image(file_path, compressed_path)
                os.remove(file_path)
                file_path = compressed_path
                unique_name = os.path.basename(compressed_path)

            # Save marking guide record in DB
            new_guide = MarkingGuide(
                title=form.title.data or filename,
                filename=unique_name,
                teacher_id=current_user.id,
                created_at=datetime.utcnow()
            )
            db.session.add(new_guide)
            db.session.commit()
            flash('Marking guide uploaded successfully.', 'success')
            return redirect(url_for('teacher_bp.dashboard'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to save marking guide: {e}")
            flash('Failed to save marking guide. Please try again.', 'danger')
            return redirect(request.url)

    return render_template('teacher/upload.html', form=form)
