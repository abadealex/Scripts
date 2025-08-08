import os
from flask import (
    Blueprint, render_template, abort, url_for, jsonify,
    current_app, send_file, request, flash, redirect
)
from flask import session as flask_session  # Avoid conflict with SQLAlchemy session
from flask_login import login_required, current_user

from smartscripts.models import StudentSubmission, MarkingGuide, Student
from smartscripts.utils.utils import check_student_access
from smartscripts.utils import is_released

student_bp = Blueprint('student_bp', __name__, url_prefix='/student')


@student_bp.before_request
@login_required
def require_student_role():
    if current_user.role != 'student':
        abort(403)


# ? LOGIN
@student_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        password = request.form['password']
        student = Student.query.filter_by(student_id=student_id).first()
        if student and student.check_password(password):
            flask_session['student_id'] = student_id
            return redirect(url_for('student_bp.view_results'))
        flash('Invalid credentials', 'danger')
    return render_template('student/login.html')


# ? LOGOUT
@student_bp.route('/logout')
def logout():
    flask_session.pop('student_id', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('student_bp.login'))


# ? RESULTS (Portal-style)
@student_bp.route('/results_portal')
def view_results():
    if 'student_id' not in flask_session:
        return redirect(url_for('student_bp.login'))

    sid = flask_session['student_id']
    submissions = StudentSubmission.query.filter_by(
        student_id=sid, is_published_to_student=True
    ).all()
    return render_template('student/view_results.html', submissions=submissions)


# ? DASHBOARD
@student_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    check_student_access()
    submissions = StudentSubmission.query.filter_by(
        student_id=current_user.id
    ).order_by(StudentSubmission.timestamp.desc()).all()
    return render_template(
        'student/dashboard.html',
        submissions=submissions
    )


# ? SINGLE RESULT VIEW
@student_bp.route('/result/<int:submission_id>', methods=['GET'])
@login_required
def view_single_result(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.student_id != current_user.id:
        abort(403)
    return render_template('student/result.html', submission=submission)


# ? JSON RESULTS
@student_bp.route('/results', methods=['GET'])
@login_required
def get_student_results():
    submissions = StudentSubmission.query.filter_by(
        student_id=current_user.id
    ).order_by(StudentSubmission.timestamp.desc()).all()

    def public_path(filename):
        return url_for('static', filename=os.path.join('annotated', 'cross', filename), _external=True)

    data = {
        "results": [
            {
                "id": s.id,
                "subject": s.subject,
                "grade": s.grade,
                "timestamp": s.timestamp.isoformat(),
                "graded_image": public_path(s.graded_image)
            }
            for s in submissions
        ]
    }
    return jsonify(data)


# ? MY SCORES VIEW
@student_bp.route('/my_results', methods=['GET'])
@login_required
def view_my_scores():
    submissions = StudentSubmission.query.filter_by(
        student_id=current_user.id
    ).order_by(StudentSubmission.timestamp.desc()).all()
    return render_template("student/my_scores.html", submissions=submissions)


# ? FEEDBACK VIEW
@student_bp.route('/view/<int:test_id>/student/<int:student_id>', methods=['GET'])
@login_required
def view_feedback(test_id, student_id):
    if current_user.role == 'student' and current_user.id != student_id:
        abort(403)

    if current_user.role == 'student' and not is_released(test_id):
        abort(403, description="Test results not yet released.")

    submission = StudentSubmission.query.join(MarkingGuide).filter(
        StudentSubmission.student_id == student_id,
        MarkingGuide.test_id == test_id
    ).first_or_404()

    guide = submission.guide
    test = guide.test if guide else None

    file_guide_url = url_for('file_routes_bp.uploaded_file', filename=guide.filename) if guide and guide.filename else None
    file_rubric_url = url_for('file_routes_bp.uploaded_file', filename=guide.rubric_filename) if guide and guide.rubric_filename else None
    answered_script_url = url_for('file_routes_bp.uploaded_file', filename=guide.answered_script_filename) if guide and guide.answered_script_filename else None
    submission_url = url_for('file_routes_bp.uploaded_file', filename=submission.filename) if submission and submission.filename else None

    return render_template(
        'student/view_feedback.html',
        test=test,
        guide=guide,
        file_guide_url=file_guide_url,
        file_rubric_url=file_rubric_url,
        answered_script_url=answered_script_url,
        submission=submission,
        submission_url=submission_url
    )


# ? DOWNLOAD MARKED ZIP
@student_bp.route('/download_zip/<int:submission_id>')
@login_required
def download_marked_zip(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.student_id != current_user.id:
        abort(403)

    zip_filename = f"submission_{submission_id}_marked.zip"
    zip_path = os.path.join(current_app.config['MARKED_FOLDER'], zip_filename)

    if not os.path.exists(zip_path):
        abort(404, description="Marked ZIP file not found.")

    return send_file(
        zip_path,
        mimetype='application/zip',
        as_attachment=True,
        download_name=zip_filename
    )
