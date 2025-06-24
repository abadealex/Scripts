# --- Standard Library Imports ---
import os

# --- Flask & Flask-Login Imports ---
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app, abort
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)

# --- Werkzeug & SQLAlchemy Imports ---
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload

# --- Local Application Imports ---
from smartscripts.app import db
from smartscripts.app.models import User, MarkingGuide, StudentSubmission
from smartscripts.utils.compress_image import compress_image
from smartscripts.app.forms import (
    TeacherLoginForm, TeacherRegisterForm
)

# --- Blueprint Setup ---
teacher_bp = Blueprint('teacher_bp', __name__, url_prefix='/teacher')


# --- Middleware: Restrict Access to Teachers ---
@teacher_bp.before_request
def require_teacher_role():
    exempt_routes = ['teacher_bp.login', 'teacher_bp.register', 'static']
    if request.endpoint not in exempt_routes:
        if not current_user.is_authenticated or current_user.role != 'teacher':
            abort(403)


# ===========================
#         Auth Routes
# ===========================

@teacher_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('teacher_bp.dashboard'))

    form = TeacherLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data,
            role='teacher'
        ).first()
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
        hashed_password = generate_password_hash(
            form.password.data, method='sha256'
        )
        new_user = User(
            email=form.email.data,
            password=hashed_password,
            role='teacher'
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('teacher_bp.login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed due to server error.', 'danger')
            print(f"[ERROR] Teacher registration DB commit failed: {e}")

    return render_template('teacher/register.html', form=form)


@teacher_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('teacher_bp.login'))


# ===========================
#       Dashboard Route
# ===========================

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


# ===========================
#     Upload Guide Route
# ===========================

@teacher_bp.route('/upload-guide', methods=['GET', 'POST'])
@login_required
def upload_guide():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename.strip() == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        upload_dir = current_app.config['UPLOAD_FOLDER_GUIDES']
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # Compress large images (over 4MB)
        if (
            file_path.lower().endswith(('.jpg', '.jpeg', '.png')) and
            os.path.getsize(file_path) > 4 * 1024 * 1024
        ):
            compressed_path = os.path.join(upload_dir, f"compressed_{filename}")
            compress_image(file_path, compressed_path)
            os.remove(file_path)
            file_path = compressed_path

        flash('Marking guide uploaded successfully.', 'success')
        return redirect(url_for('teacher_bp.dashboard'))

    return render_template('teacher/upload.html')
