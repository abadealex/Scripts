import os
from pathlib import Path

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    current_app
)
from flask_login import login_required, current_user
from flask_wtf.csrf import CSRFError 
from sqlalchemy.orm import joinedload

from smartscripts.extensions import db
from smartscripts.models import Test, AttendanceRecord
from smartscripts.app.forms import CreateTestForm, AIGradingForm
from smartscripts.services.test_creation_service import create_new_test_record
from smartscripts.utils.file_helpers import get_file_path

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/dashboard')

# Mapping file types to upload folders (matches your structure)
FILE_TYPE_TO_FOLDER = {
    "marking_guide": "marking_guides",
    "class_list": "student_lists",  # Use student_lists instead of deprecated class_lists
    "rubric": "rubrics",
    "combined_scripts": "combined_scripts",
    "answered_script": "answered_scripts",
    "question_paper": "question_papers",
}

# Corresponding model path attributes
FILE_TYPE_TO_MODEL_PATH_ATTR = {
    "marking_guide": "marking_guide_path",
    "class_list": "class_list_path",
    "rubric": "rubric_path",
    "combined_scripts": "combined_scripts_path",
    "answered_script": "answered_script_path",
    "question_paper": "question_paper_path",
}


def get_valid_tests_for_user(user):
    query = Test.query.options(joinedload(Test.marking_guide))
    tests = query.all() if user.is_admin else query.filter_by(teacher_id=user.id).all()

    valid_tests = [
        test for test in tests
        if test.title and test.subject and test.grade_level and test.id is not None
    ]

    for test in valid_tests:
        # Load attendance records for dashboard display
        test.attendance_records = AttendanceRecord.query.filter_by(test_id=test.id).all()
        # Check that all required files exist and have a path set
        test.all_required_files_uploaded = all([
            getattr(test, FILE_TYPE_TO_MODEL_PATH_ATTR.get(fp, ''), None)
            for fp in ("class_list", "combined_scripts", "marking_guide", "rubric")
        ])

    return valid_tests


@dashboard_bp.route('/', methods=['GET'])
@login_required
def dashboard():
    current_app.logger.debug("Dashboard route accessed")

    create_test_form = CreateTestForm()
    ai_grading_form = AIGradingForm()

    try:
        valid_tests = get_valid_tests_for_user(current_user)
        return render_template(
            'teacher/dashboard.html',
            form=create_test_form,
            ai_grading_form=ai_grading_form,
            uploaded_tests=valid_tests,
            teacher_name=current_user.username
        )
    except Exception as e:
        current_app.logger.error(f"Error loading dashboard: {e}", exc_info=True)
        flash('An error occurred while processing your request.', 'danger')
        return render_template('errors/error.html', message="Failed to load dashboard.")


@dashboard_bp.route('/create_test', methods=['POST'])
@login_required
def create_test():
    form = CreateTestForm()
    current_app.logger.debug("Create test route POST hit")

    if not form.validate_on_submit():
        current_app.logger.warning("CreateTestForm validation failed")
        flash('Please correct the errors in the form.', 'danger')

        valid_tests = get_valid_tests_for_user(current_user)

        return render_template(
            'teacher/dashboard.html',
            form=form,
            ai_grading_form=AIGradingForm(),
            uploaded_tests=valid_tests,
            teacher_name=current_user.username
        )

    try:
        new_test = create_new_test_record(
            title=(form.test_title.data or '').strip(),
            subject=form.subject.data,
            exam_date=form.exam_date.data,
            grade_level=form.grade_level.data,
            description=form.description.data,
            teacher_id=current_user.id
        )

        if new_test is None:
            flash('Failed to create test due to database error.', 'danger')
            return redirect(url_for('dashboard_bp.dashboard'))

        current_app.logger.info(f"New test created with ID {new_test.id} by user {current_user.id}")
        flash('Test created successfully! Now upload class list and other materials.', 'success')

        return redirect(url_for('upload_bp.upload_test_materials', test_id=new_test.id))

    except Exception as e:
        current_app.logger.error(f"Error creating test: {e}", exc_info=True)
        db.session.rollback()
        flash('Failed to create test.', 'danger')
        return redirect(url_for('dashboard_bp.dashboard'))


@dashboard_bp.route('/delete_file/<int:test_id>/<file_type>', methods=['POST'])
@login_required
def delete_file(test_id: int, file_type: str):
    try:
        test = Test.query.get_or_404(test_id)

        if test.teacher_id != current_user.id and not current_user.is_admin:
            flash("Unauthorized", "danger")
            return redirect(url_for('dashboard_bp.dashboard'))

        if file_type not in FILE_TYPE_TO_MODEL_PATH_ATTR:
            flash("Invalid file type.", "danger")
            return redirect(url_for('dashboard_bp.dashboard'))

        path_attr = FILE_TYPE_TO_MODEL_PATH_ATTR[file_type]
        file_path_str = getattr(test, path_attr, None)
        if not file_path_str:
            flash("File path not set.", "warning")
            return redirect(url_for('dashboard_bp.dashboard'))

        # Build full absolute path to file under static/uploads/<folder>/<test_id>/
        folder = FILE_TYPE_TO_FOLDER[file_type]
        abs_path = get_file_path(file_path_str)

        if abs_path.exists():
            abs_path.unlink()
            # Clear path attribute in DB and commit
            setattr(test, path_attr, None)
            db.session.commit()
            flash(f"{file_type.replace('_', ' ').capitalize()} deleted successfully.", "info")
        else:
            flash("File not found.", "warning")

    except Exception as e:
        current_app.logger.error(f"Error deleting {file_type} file for test {test_id}: {e}", exc_info=True)
        flash("Deletion failed.", "danger")

    return redirect(url_for('dashboard_bp.dashboard'))


@dashboard_bp.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    current_app.logger.error(f"CSRF error: {e.description}", exc_info=True)
    return render_template('errors/400.html', reason=e.description), 400


@dashboard_bp.app_errorhandler(400)
def handle_bad_request(e):
    current_app.logger.error(f"400 Bad Request: {e}", exc_info=True)
    return render_template('errors/400.html', reason=str(e)), 400
