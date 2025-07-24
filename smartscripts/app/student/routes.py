import os
from flask import (
    Blueprint, render_template, abort, url_for, jsonify, current_app
)
from flask_login import login_required, current_user

from smartscripts.extensions import db
from smartscripts.models import StudentSubmission, MarkingGuide

from smartscripts.utils.utils import check_student_access
from smartscripts.utils import is_released  # Your helper to check test release

student_bp = Blueprint('student_bp', __name__, url_prefix='/student')  # Use consistent prefix


@student_bp.before_request
@login_required
def require_student_role():
    if current_user.role != 'student':
        abort(403)


@student_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    Student dashboard showing only their results.
    Upload functionality is disabled.
    """
    check_student_access()

    # Fetch submissions belonging to current student only
    submissions = StudentSubmission.query.filter_by(
        student_id=current_user.id
    ).order_by(StudentSubmission.timestamp.desc()).all()

    # Upload is disabled completely, no form passed
    enable_upload = False

    return render_template(
        'student/dashboard.html',
        submissions=submissions,
        enable_upload=enable_upload
    )


# Disable all upload routes for students

@student_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def student_upload():
    abort(403, description="Students are not allowed to upload files.")


@student_bp.route('/upload/bulk', methods=['POST'])
@login_required
def bulk_upload():
    abort(403, description="Students are not allowed to upload files.")


@student_bp.route('/result/<int:submission_id>', methods=['GET'])
@login_required
def view_single_result(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.student_id != current_user.id:
        abort(403)
    return render_template('student/result.html', submission=submission)


@student_bp.route('/results', methods=['GET'])
@login_required
def get_student_results():
    submissions = StudentSubmission.query.filter_by(
        student_id=current_user.id
    ).order_by(StudentSubmission.timestamp.desc()).all()

    def public_path(filename):
        # This builds URLs to annotated images in static folder
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


@student_bp.route('/my_results', methods=['GET'])
@login_required
def view_my_scores():
    submissions = StudentSubmission.query.filter_by(
        student_id=current_user.id
    ).order_by(StudentSubmission.timestamp.desc()).all()
    return render_template("student/my_scores.html", submissions=submissions)


@student_bp.route('/view/<int:test_id>/student/<int:student_id>', methods=['GET'])
@login_required
def view_feedback(test_id, student_id):
    """
    Students (or teachers/admins) can view feedback for a specific test.
    Students can only see their own feedback and only if the test is released.
    """
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

    # URLs to files (adjust accordingly)
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
