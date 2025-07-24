from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
)
from flask_login import login_required, current_user
from smartscripts.models import StudentSubmission, Test, MarkingGuide, ExtractedStudentScript
from smartscripts.extensions import db
from smartscripts.utils.permissions import teacher_required

teacher_bp = Blueprint('teacher_bp', __name__, url_prefix='/teacher')

# Import other route modules as needed
from .auth_routes import *
from .dashboard_routes import *
from .upload_routes import *
from .review_routes import *
from .ai_marking_routes import *
from .export_routes import *
from .delete_routes import *
from .misc_routes import *
from .utils import *
from .download_routes import *
from .file_routes import *  # only if these routes are needed here


@teacher_bp.route('/review_test/<int:test_id>')
@login_required
def review_test(test_id):
    test = Test.query.get_or_404(test_id)

    if test.teacher_id != current_user.id and not current_user.is_admin:
        abort(403)

    guide = MarkingGuide.query.filter_by(test_id=test.id).first()

    # Debug logging to check file attributes
    current_app.logger.debug(f"Marking guide: {guide}")
    current_app.logger.debug(f"Marking guide filename: {getattr(guide, 'filename', None)}")
    current_app.logger.debug(f"Rubric filename: {getattr(guide, 'rubric_filename', None)}")
    current_app.logger.debug(f"Answered script filename: {getattr(guide, 'answered_script_filename', None)}")

    # File URLs
    file_guide_url = url_for('file_routes_bp.uploaded_file', filename=guide.filename) if guide and guide.filename else None
    file_rubric_url = url_for('file_routes_bp.uploaded_file', filename=guide.rubric_filename) if guide and guide.rubric_filename else None
    answered_script_url = url_for('file_routes_bp.uploaded_file', filename=guide.answered_script_filename) if guide and guide.answered_script_filename else None

    # Student submissions
    student_submissions = StudentSubmission.query.filter_by(guide_id=guide.id).all() if guide else []
    for submission in student_submissions:
        submission.file_url = url_for('file_routes_bp.uploaded_file', filename=submission.filename) if submission.filename else None

    student_submissions_exist = len(student_submissions) > 0

    # Define upload/review sections
    sections = [
        {
            'title': '📘 Marking Guide',
            'uploaded': bool(guide and guide.filename),
            'upload_url': url_for('teacher_bp.upload_test_materials_existing', test_id=test.id),
            'review_url': file_guide_url
        },
        {
            'title': '📄 Rubric',
            'uploaded': bool(guide and guide.rubric_filename),
            'upload_url': url_for('teacher_bp.upload_test_materials_existing', test_id=test.id),
            'review_url': file_rubric_url
        },
        {
            'title': '🧾 Answered Script',
            'uploaded': bool(guide and guide.answered_script_filename),
            'upload_url': url_for('teacher_bp.upload_test_materials_existing', test_id=test.id),
            'review_url': answered_script_url
        },
        {
            'title': '📄 Student Scripts',
            'uploaded': student_submissions_exist,
            'upload_url': url_for('teacher_bp.upload_test_materials_existing', test_id=test.id),
            'review_url': url_for('teacher_bp.review_extracted_list', test_id=test.id)
        }
    ]

    return render_template(
        'teacher/review_test.html',
        test=test,
        test_id=test.id,
        guide=guide,
        file_guide_url=file_guide_url,
        file_rubric_url=file_rubric_url,
        answered_script_url=answered_script_url,
        student_submissions=student_submissions,
        student_submissions_exist=student_submissions_exist,
        sections=sections
    )


@teacher_bp.route('/review_extracted_list/<int:test_id>', methods=['GET', 'POST'])
@login_required
def review_extracted_list(test_id):
    test = Test.query.get_or_404(test_id)

    if test.teacher_id != current_user.id and not current_user.is_admin:
        abort(403)

    extracted_scripts = ExtractedStudentScript.query.filter_by(test_id=test_id).all()

    if request.method == 'POST':
        updated_data = request.form

        for script in extracted_scripts:
            prefix = f"script_{script.id}_"
            new_name = updated_data.get(prefix + "name", script.student_name).strip()
            new_id = updated_data.get(prefix + "student_id", script.student_id).strip()
            confirmed = updated_data.get(prefix + "confirmed") == "on"

            script.student_name = new_name
            script.student_id = new_id
            script.confirmed = confirmed

        try:
            db.session.commit()
            flash("Extracted student list updated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to update list: {e}", "danger")

        return redirect(url_for('teacher_bp.review_extracted_list', test_id=test_id))

    # GET: Show extracted scripts for review
    return render_template(
        'teacher/review_extracted_list.html',
        test=test,
        extracted_scripts=extracted_scripts
    )


@teacher_bp.route('/review/<int:submission_id>')
@login_required
def review_submission(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    guide = submission.guide
    test = guide.test if guide else None

    if not guide or not test:
        abort(404)

    if test.teacher_id != current_user.id and not current_user.is_admin:
        abort(403)

    file_rubric_url = url_for('file_routes_bp.uploaded_file', filename=guide.rubric_filename) if guide.rubric_filename else None
    file_guide_url = url_for('file_routes_bp.uploaded_file', filename=guide.filename) if guide.filename else None
    answered_script_url = url_for('file_routes_bp.uploaded_file', filename=guide.answered_script_filename) if guide.answered_script_filename else None
    submission_url = url_for('file_routes_bp.uploaded_file', filename=submission.filename) if submission.filename else None

    return render_template(
        'teacher/review.html',
        submission=submission,
        test=test,
        file_guide_url=file_guide_url,
        file_rubric_url=file_rubric_url,
        answered_script_url=answered_script_url,
        submission_url=submission_url
    )


@teacher_bp.route('/review/<int:submission_id>/submit', methods=['POST'])
@login_required
def manual_review_submit(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    guide = submission.guide
    test = guide.test if guide else None

    if not guide or not test:
        abort(404)

    if test.teacher_id != current_user.id and not current_user.is_admin:
        abort(403)

    comments = request.form.get('comments', '').strip()
    new_grade = request.form.get('grade')

    if not comments or not new_grade:
        flash('Grade and comments are required.', 'danger')
        return redirect(url_for('teacher_bp.review_submission', submission_id=submission_id))

    try:
        submission.feedback = comments
        submission.grade = float(new_grade)
        submission.reviewed_at = db.func.now()
        db.session.commit()
        flash('Review submitted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to submit review. Error: {e}', 'danger')

    return redirect(url_for('teacher_bp.review_submission', submission_id=submission_id))


@teacher_bp.route('/confirm_extracted_students/<int:test_id>', methods=['POST'])
@login_required
@teacher_required
def confirm_extracted_students(test_id):
    form_data = request.form
    confirmed_ids = {key.split('_')[1] for key in form_data if key.startswith('confirmed_')}

    scripts = ExtractedStudentScript.query.filter_by(test_id=test_id).all()

    for script in scripts:
        script.confirmed = str(script.id) in confirmed_ids

    try:
        db.session.commit()
        flash("Student script confirmations updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to update confirmations: {str(e)}", "danger")

    return redirect(url_for('teacher_bp.review_extracted_list', test_id=test_id))


@teacher_bp.teardown_app_request
def shutdown_session(exception=None):
    db.session.remove()
