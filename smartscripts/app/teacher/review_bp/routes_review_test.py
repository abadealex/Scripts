import os
from flask import (
    render_template, request, redirect, url_for, flash,
    abort, current_app, send_file
)
from flask_login import login_required
from smartscripts.extensions import db
from smartscripts.models import Test, MarkingGuide

from . import review_bp
from .utils import file_url, is_teacher_or_admin, get_urls_for_guide


@review_bp.route('/review_test/<int:test_id>')
@login_required
def review_test(test_id: int):
    test = Test.query.get_or_404(test_id)
    if not is_teacher_or_admin(test):
        abort(403)

    guide = MarkingGuide.query.filter_by(test_id=test.id).first()
    student_submissions = []
    if guide:
        from smartscripts.models import StudentSubmission
        student_submissions = StudentSubmission.query.filter_by(guide_id=guide.id).all()

    urls = get_urls_for_guide(guide)

    for sub in student_submissions:
        sub.file_url = file_url(sub.filename)

    sections = [
        {'title': '📕 Marking Guide', 'uploaded': bool(urls.get("guide")), 'review_url': urls.get("guide")},
        {'title': '📋 Rubric', 'uploaded': bool(urls.get("rubric")), 'review_url': urls.get("rubric")},
        {'title': '📝 Answered Script', 'uploaded': bool(urls.get("answered")), 'review_url': urls.get("answered")},
        {'title': '📄 Student Scripts', 'uploaded': bool(student_submissions),
         'review_url': url_for('teacher_bp.review_bp.review_extracted_list', test_id=test.id)},
    ]

    return render_template('teacher/review_test.html',
                           test=test,
                           guide=guide,
                           file_guide_url=urls.get("guide"),
                           file_rubric_url=urls.get("rubric"),
                           answered_script_url=urls.get("answered"),
                           student_submissions=student_submissions,
                           student_submissions_exist=bool(student_submissions),
                           sections=sections)


@review_bp.route('/review_extracted_list/<int:test_id>', methods=['GET', 'POST'])
@login_required
def review_extracted_list(test_id: int):
    test = Test.query.get_or_404(test_id)
    if not is_teacher_or_admin(test):
        abort(403)

    from smartscripts.models import ExtractedStudentScript
    scripts = ExtractedStudentScript.query.filter_by(test_id=test_id).all()

    if request.method == 'POST':
        for s in scripts:
            prefix = f"script_{s.id}_"
            name_val = request.form.get(prefix + "name")
            if name_val:
                s.student_name = name_val.strip()
            id_val = request.form.get(prefix + "student_id")
            if id_val:
                s.student_id = id_val.strip()
            s.confirmed = request.form.get(prefix + "confirmed") == "on"
        try:
            db.session.commit()
            flash("Extracted student list updated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to update list: {e}", "danger")
        return redirect(url_for('teacher_bp.review_bp.review_extracted_list', test_id=test_id))

    return render_template('teacher/review_extracted_list.html', test=test, extracted_scripts=scripts)


@review_bp.route('/review/<int:submission_id>')
@login_required
def review_submission(submission_id: int):
    from smartscripts.models import StudentSubmission
    sub = StudentSubmission.query.get_or_404(submission_id)
    test = sub.guide.test if sub.guide else None
    if not test or not is_teacher_or_admin(test):
        abort(403)

    return render_template('teacher/review.html',
                           submission=sub,
                           test=test,
                           file_guide_url=file_url(sub.guide.filename),
                           file_rubric_url=file_url(sub.guide.rubric_filename),
                           answered_script_url=file_url(sub.guide.answered_script_filename),
                           submission_url=file_url(sub.filename))



@review_bp.route('/review/<int:submission_id>/submit', methods=['POST'])
@login_required
def manual_review_submit(submission_id: int):
    from smartscripts.models import StudentSubmission
    from sqlalchemy.exc import SQLAlchemyError

    sub = StudentSubmission.query.get_or_404(submission_id)
    test = sub.guide.test if sub.guide else None
    if not test or not is_teacher_or_admin(test):
        abort(403)

    comments = request.form.get('comments', '').strip()
    grade_str = request.form.get('grade')

    if not comments or not grade_str:
        flash('Grade and comments are required.', 'danger')
        return redirect(url_for('teacher_bp.review_bp.review_submission', submission_id=submission_id))

    try:
        sub.feedback = comments
        sub.grade = float(grade_str)
        sub.reviewed_at = db.func.now()
        db.session.commit()
        flash('Review submitted successfully.', 'success')
    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        current_app.logger.error(f"[manual_review_submit] Failed: {e}")
        flash('Failed to submit review. Please check your inputs.', 'danger')

    return redirect(url_for('teacher_bp.review_bp.review_submission', submission_id=submission_id))


# === New route: Extract class list ===
@review_bp.route('/extract_class_list/<int:test_id>', methods=['POST'])
@login_required
def extract_class_list(test_id):
    test = Test.query.get_or_404(test_id)
    if not is_teacher_or_admin(test):
        abort(403)

    # TODO: implement class list extraction logic here
    # e.g., read CSV, fuzzy match names/IDs, update attendance records

    flash("Class list extracted successfully.", "success")
    return redirect(url_for('review_bp.review_test', test_id=test_id))


# === File viewer/download ===
def get_abs_path(relative_path: str) -> str:
    return os.path.join(current_app.config['UPLOAD_FOLDER'], relative_path)


@review_bp.route('/review/<file_type>/<int:test_id>')
@login_required
def review_file(file_type, test_id):
    test = Test.query.get_or_404(test_id)
    if not is_teacher_or_admin(test):
        abort(403)

    file_map = {
        "question_paper": test.question_paper_path,
        "rubric": test.rubric_path,
        "marking_guide": test.marking_guide_path,
        "answered_script": test.answered_script_path,
        "combined_scripts": test.combined_scripts_path,
        "class_list": test.class_list_path,
    }

    if file_type not in file_map or not file_map[file_type]:
        flash(f"{file_type.replace('_', ' ').title()} not available.", "warning")
        return redirect(url_for("upload_bp.upload_test_materials", test_id=test_id))

    full_path = get_abs_path(file_map[file_type])
    current_app.logger.info(f"[review_file] Serving file: {full_path}")

    if not os.path.exists(full_path):
        flash(f"File not found on disk: {full_path}", "warning")
        return redirect(url_for("upload_bp.upload_test_materials", test_id=test_id))

    try:
        return send_file(full_path)
    except Exception as e:
        current_app.logger.exception(f"Failed to serve file {file_type}: {e}")
        flash("Could not serve file.", "danger")
        return redirect(url_for("upload_bp.upload_test_materials", test_id=test_id))
