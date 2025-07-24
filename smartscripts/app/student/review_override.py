# app/student/review_override.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from smartscripts.models import StudentSubmission, db

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/review_override/<int:submission_id>', methods=['POST'])
@login_required
def review_override(submission_id):
    """
    Endpoint to manually adjust the review of a student submission.
    Only the student who owns the submission can override their review.
    """
    submission = StudentSubmission.query.get_or_404(submission_id)

    if submission.student_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    new_score = data.get('score')
    new_feedback = data.get('feedback')

    if new_score is not None:
        submission.score = new_score
    if new_feedback:
        submission.feedback = new_feedback

    db.session.commit()

    return jsonify({
        "message": "Review overridden successfully",
        "submission_id": submission.id,
        "score": submission.score,
        "feedback": submission.feedback
    })
