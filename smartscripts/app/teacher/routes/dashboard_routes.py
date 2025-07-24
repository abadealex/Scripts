import os
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from flask_wtf.csrf import CSRFError

from smartscripts.models import Test
from smartscripts.extensions import db
from smartscripts.app.forms import CreateTestForm, AIGradingForm

from . import teacher_bp


@teacher_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    create_test_form = CreateTestForm()
    ai_grading_form = AIGradingForm()

    try:
        current_app.logger.debug("Dashboard route accessed")

        # Admin sees all tests, others only their own
        if current_user.is_admin:
            tests = Test.query.options(joinedload(Test.marking_guide)).all()
        else:
            tests = Test.query.options(joinedload(Test.marking_guide)).filter_by(teacher_id=current_user.id).all()

        return render_template(
            'teacher/dashboard.html',
            form=create_test_form,
            ai_grading_form=ai_grading_form,
            tests=tests,
            teacher_name=current_user.username
        )

    except Exception as e:
        current_app.logger.error(f"Error loading dashboard: {e}", exc_info=True)
        flash('An error occurred while processing your request.', 'danger')
        return render_template('errors/error.html', message="Failed to load dashboard.")


@teacher_bp.route('/create_test', methods=['POST'])
@login_required
def create_test():
    form = CreateTestForm()

    if form.validate_on_submit():
        try:
            new_test = Test(
                title=form.test_title.data,
                subject=form.subject.data,
                grade_level=form.grade_level.data,
                exam_date=form.exam_date.data,
                teacher_id=current_user.id
            )
            db.session.add(new_test)
            db.session.commit()

            flash('Test created successfully! Please upload the related materials.', 'success')
            return redirect(url_for('teacher_bp.upload_test_materials_existing', test_id=new_test.id))

        except Exception as e:
            current_app.logger.error(f"Error creating test: {e}", exc_info=True)
            flash('Failed to create test.', 'danger')
            return redirect(url_for('teacher_bp.dashboard'))
    else:
        # Log each validation error
        for field, errors in form.errors.items():
            for error in errors:
                current_app.logger.warning(f"Validation error on {field}: {error}")

        flash('Please correct the errors in the form.', 'danger')
        return redirect(url_for('teacher_bp.dashboard'))


# CSRF error handler
@teacher_bp.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    current_app.logger.error(f"CSRF error: {e.description}", exc_info=True)
    return render_template('errors/400.html', reason=e.description), 400


# Generic 400 error handler
@teacher_bp.app_errorhandler(400)
def handle_bad_request(e):
    current_app.logger.error(f"400 Bad Request: {e}", exc_info=True)
    return render_template('errors/400.html', reason=str(e)), 400
