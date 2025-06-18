from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from cograder_clone.app import db  # ✅ CORRECT
import re

auth = Blueprint('auth', __name__)

def is_valid_email(email):
    regex = r'^\S+@\S+\.\S+$'
    return re.match(regex, email) is not None

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))  # Redirect logged-in users

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', category='success')
            if user.role == 'teacher':
                return redirect(url_for('main.teacher_dashboard'))
            else:
                return redirect(url_for('main.student_dashboard'))
        else:
            flash('Invalid email or password.', category='danger')

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))  # Redirect logged-in users

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', '')

        if not is_valid_email(email):
            flash('Please enter a valid email address.', category='danger')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long.', category='danger')
        elif role not in ['teacher', 'student']:
            flash('Please select a valid role.', category='danger')
        else:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered.', category='danger')
            else:
                new_user = User(
                    email=email,
                    password=generate_password_hash(password, method='sha256'),
                    role=role
                )
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful. You can now log in.', category='success')
                return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', category='info')
    return redirect(url_for('auth.login'))
