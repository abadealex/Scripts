import os
from flask import (
    Blueprint, current_app, jsonify, abort, render_template, flash
)
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required, current_user
from rq import Retry

from smartscripts.models.student_submission import StudentSubmission
from smartscripts.models.test import Test
from smartscripts.extensions import db
from smartscripts.ai.marking_pipeline import (
    mark_batch_submissions,
    mark_single_submission
)
from smartscripts.tasks.grade_tasks import async_mark_submission

ai_marking_bp = Blueprint('ai_marking', __name__)


def save_marked_image(submission, result):
    """Save annotated image from AI result to disk and update DB path."""
    image_data = result.get("annotated_image_bytes")
    if not image_data:
        current_app.logger.warning(
            f"[AI Marking] No annotated image for submission {submission.id}"
        )
        return None

    marked_dir = os.path.join(
        current_app.config['MARKED_FOLDER'], str(submission.id)
    )
    os.makedirs(marked_dir, exist_ok=True)
    image_path = os.path.join(marked_dir, "annotated.png")

    try:
        with open(image_path, "wb") as f:
            f.write(image_data)

        submission.graded_image = image_path
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"[DB] Error saving graded image path: {e}", exc_info=True
            )
            flash("A database error occurred while saving the graded image.", "danger")
        return image_path
    except Exception as e:
        current_app.logger.error(
            f"[AI Marking] Failed to save marked image for submission {submission.id}: {e}"
        )
        return None


@ai_marking_bp.route('/start_ai_marking/<int:test_id>', methods=['GET'])
@login_required
def start_ai_marking_form(test_id):
    """Render the AI marking page."""
    test = Test.query.get_or_404(test_id)
    if test.teacher_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template("teacher/start_ai_marking.html", test=test)


@ai_marking_bp.route('/start_ai_marking/<int:test_id>', methods=['POST'])
@login_required
def start_ai_marking_batch(test_id):
    """Run synchronous AI marking for all submissions in a test."""
    test = Test.query.get_or_404(test_id)
    if test.teacher_id != current_user.id and not current_user.is_admin:
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        submissions = StudentSubmission.query.filter_by(
            test_id=test.id, teacher_id=current_user.id
        ).all()

        if not submissions:
            return jsonify({"error": "No student submissions found for this test."}), 404

        results = mark_batch_submissions(submissions, test_id)
        for submission, result in zip(submissions, results):
            save_marked_image(submission, result)

        return jsonify({
            "message": f"? AI marking completed for {len(submissions)} submissions."
        })
    except Exception as e:
        current_app.logger.error(
            f"[AI Marking] Error during batch marking for test {test_id}: {e}",
            exc_info=True
        )
        return jsonify({"error": str(e)}), 500


@ai_marking_bp.route('/start_ai_marking/submission/<int:submission_id>', methods=['POST'])
@login_required
def start_ai_marking_single(submission_id):
    """Run AI marking for a single submission."""
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.teacher_id != current_user.id:
        abort(403, "Unauthorized access")

    try:
        result = mark_single_submission(submission)
        save_marked_image(submission, result)
        return jsonify({
            "message": f"? AI marking completed for submission ID {submission_id}."
        })
    except Exception as e:
        current_app.logger.error(
            f"[AI Marking] Failed marking submission {submission_id}: {e}",
            exc_info=True
        )
        return jsonify({"error": str(e)}), 500


@ai_marking_bp.route('/start_ai_grading/<int:test_id>', methods=['POST'])
@login_required
def start_ai_grading_async(test_id):
    """Asynchronously enqueue AI grading jobs using RQ."""
    test = Test.query.get_or_404(test_id)
    if test.teacher_id != current_user.id and not current_user.is_admin:
        return jsonify({"error": "Unauthorized access"}), 403

    if test.is_locked:
        return jsonify({"error": "This test is already locked for grading."}), 400

    submissions = StudentSubmission.query.filter_by(
        test_id=test.id, teacher_id=current_user.id
    ).all()

    if not submissions:
        return jsonify({"error": "No submissions found for this test"}), 404

    try:
        test.is_locked = True
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"[DB] Error locking test: {e}", exc_info=True
            )
            flash("Database error occurred while locking the test.", "danger")
            return jsonify({"error": "Database error while locking test."}), 500

        for submission in submissions:
            current_app.rq.enqueue(
                async_mark_submission,
                submission.file_path,
                test.id,
                submission.student_id,
                test.id,
                retry=Retry(max=3, interval=[10, 30, 60])
            )

        return jsonify({
            "message": f"?? Async AI grading launched for {len(submissions)} submissions."
        })
    except Exception as e:
        current_app.logger.error(
            f"[AI Marking] Async grading error for test {test_id}: {e}",
            exc_info=True
        )
        return jsonify({"error": str(e)}), 500
