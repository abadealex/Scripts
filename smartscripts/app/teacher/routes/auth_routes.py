import os
from flask import (
    render_template, request, redirect,
    url_for, flash, abort
)
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from smartscripts.extensions import db
from smartscripts.models import User
from smartscripts.app.forms import TeacherLoginForm, TeacherRegisterForm

from . import teacher_bp

@teacher_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('teacher_bp.dashboard'))

    form = TeacherLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, role='teacher').first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully.", "info")
            return redirect(url_for('teacher_bp.dashboard'))
        else:
            flash("Invalid email or password.", "danger")

    return render_template('teacher/login.html', form=form)


teacher_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('teacher_bp.dashboard'))

    form = TeacherRegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered.", "warning")
            return redirect(url_for('teacher_bp.register'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password,
            role='teacher'
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('teacher_bp.login'))

    return render_template('teacher/register.html', form=form)

@teacher_bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You have been logged out.", "info")
    return redirect(url_for('teacher_bp.login'))

