import os
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, abort, current_app
)
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

from smartscripts.extensions import db
from smartscripts.models import User
from smartscripts.app.forms import TeacherLoginForm, TeacherRegisterForm

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle teacher login."""
    if current_user.is_authenticated:
        return redirect(url_for('teacher_bp.dashboard_bp.dashboard'))

    form = TeacherLoginForm()

    if form.validate_on_submit():
        email = form.email.data or ""
        password = form.password.data or ""

        user = User.query.filter_by(email=email, role='teacher').first()
        if user and password and check_password_hash(user.password, password):
            login_user(user)
            flash("? Logged in successfully.", "info")
            return redirect(url_for('teacher_bp.dashboard_bp.dashboard'))

        flash("? Invalid email or password.", "danger")

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle teacher registration."""
    if current_user.is_authenticated:
        return redirect(url_for('teacher_bp.dashboard_bp.dashboard'))

    form = TeacherRegisterForm()

    if form.validate_on_submit():
        email = form.email.data or ""
        password = form.password.data or ""
        name_value = getattr(form, 'name', None)
        username = name_value.data.strip() if name_value else "Teacher"

        if User.query.filter_by(email=email).first():
            flash("?? Email already registered.", "warning")
            return redirect(url_for('auth_bp.register'))

        if not password:
            flash("? Password cannot be empty.", "danger")
            return redirect(url_for('auth_bp.register'))

        try:
            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                role='teacher'
            )

            db.session.add(new_user)
            db.session.commit()
            flash("? Registration successful. Please log in.", "success")
            return redirect(url_for('auth_bp.login'))
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Registration DB error: {e}")
            flash("? A database error occurred. Please try again.", "danger")

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
def logout():
    """Log out the current user."""
    if current_user.is_authenticated:
        logout_user()
        flash("?? You have been logged out.", "info")

    return redirect(url_for('auth_bp.login'))
