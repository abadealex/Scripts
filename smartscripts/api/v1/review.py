from flask import Blueprint, request, jsonify, abort
from flask_login import login_required, current_user
from smartscripts.models import StudentSubmission
from smartscripts.services import review_service
from smartscripts.models import db

v1_review_bp = Blueprint('v1_review_bp', __name__, url_prefix='/reviews')


@v1_review_bp.route('/<int:submission_id>', methods=['GET'])
@login_required
def get_review(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)

    # Students can only see their own submission reviews
    if current_user.role == 'student' and submission.student_id != current_user.id:
        abort(403)

    try:
        review_data = review_service.get_review_history(str(submission_id))
        return jsonify({
            "submission_id": submission_id,
            "review_history": review_data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@v1_review_bp.route('/<int:submission_id>/feedback', methods=['POST'])
@login_required
def post_feedback(submission_id):
    if current_user.role != 'teacher':
        abort(403)

    data = request.get_json()
    question_id = data.get("question_id")
    new_text = data.get("new_text") or data.get("original_text")  # support both
    new_text = data.get("new_text") or data.get("corrected_text")  # support both
    feedback = data.get("feedback")
    comment = data.get("comment")

    if not all([question_id, new_text, new_text]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        override = review_service.process_teacher_review(
            reviewer_id=current_user.id,
            question_id=question_id,
            original_text=new_text,
            corrected_text=new_text,
            feedback=feedback,
            comment=comment
        )

        return jsonify({
            "message": "Feedback submitted successfully",
            "override": {
                "id": override.id,
                "question_id": override.question_id,
                "new_text": override.new_text,
                "feedback": override.feedback,
                "comment": override.comment,
                "timestamp": override.timestamp.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
