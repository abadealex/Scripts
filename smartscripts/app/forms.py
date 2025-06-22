from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from smartscripts.app import db
from smartscripts.app.models import User


teacher_bp = Blueprint('teacher_bp', __name__, url_prefix='/teacher')

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
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(
            email=form.email.data,
            password=hashed_password,
            role='teacher'  # enforce teacher role explicitly
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

@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'teacher':
        abort(403)
    # Load any teacher-specific data if needed here
    return render_template('teacher/dashboard.html')

@teacher_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('teacher_bp.login'))
