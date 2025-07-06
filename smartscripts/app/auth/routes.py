from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_principal import Identity, AnonymousIdentity, identity_changed, identity_loaded, RoleNeed, UserNeed
from werkzeug.security import generate_password_hash, check_password_hash

from smartscripts.models import User  # fixed import here
from smartscripts.app.forms import LoginForm, RegisterForm  # assuming forms.py is inside app/

from . import auth_bp  # Blueprint instance

# Identity loading hook
@identity_loaded.connect_via(auth_bp)
def on_identity_loaded(sender, identity):
    from smartscripts.app import principal  # Local import
    identity.user = current_user
    if not current_user.is_anonymous:
        identity.provides.add(UserNeed(current_user.id))
        if current_user.role:
            identity.provides.add(RoleNeed(current_user.role))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            identity_changed.send(
                current_app._get_current_object(),
                identity=Identity(user.id)
            )
            flash('Logged in successfully.', 'success')

            # Redirect based on role
            if user.role == 'teacher':
                return redirect(url_for('teacher_bp.dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student_bp.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_bp.dashboard'))
            else:
                return redirect(url_for('main_bp.index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))

    from smartscripts.app import db  # Local import

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            role=form.role.data.lower()
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed due to a server error.', 'danger')
            print(f"[ERROR] Registration DB Commit: {e}")
    elif request.method == 'POST':
        flash('Please correct the errors below.', 'danger')
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", 'danger')

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    identity_changed.send(
        current_app._get_current_object(),
        identity=AnonymousIdentity()
    )
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
