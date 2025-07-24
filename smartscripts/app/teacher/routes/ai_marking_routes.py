import os
from flask import current_app, jsonify, request, abort, render_template
from flask_login import login_required, current_user
from smartscripts.models import StudentSubmission, Test
from smartscripts.extensions import db
from smartscripts.ai.marking_pipeline import mark_batch_submissions, mark_single_submission
from rq import Retry
from . import teacher_bp
from smartscripts.tasks.grade_tasks import async_mark_submission # Your RQ task

def save_marked_image(submission, result):
    image_data = result.get("annotated_image_bytes")
    if not image_data:
        current_app.logger.warning(f"No annotated image for submission {submission.id}")
        return None

    marked_dir = os.path.join(current_app.config['MARKED_FOLDER'], str(submission.id))
    os.makedirs(marked_dir, exist_ok=True)
    image_path = os.path.join(marked_dir, "annotated.png")

    try:
        with open(image_path, "wb") as img_file:
            img_file.write(image_data)
        submission.graded_image = image_path
        db.session.commit()
        return image_path
    except Exception as e:
        current_app.logger.error(f"Failed to save annotated image for submission {submission.id}: {e}")
        return None


@teacher_bp.route('/start_ai_marking/<int:test_id>', methods=['GET'])
@login_required
def start_ai_marking_page(test_id):
    test = Test.query.get_or_404(test_id)

    if test.teacher_id != current_user.id and not current_user.is_admin:
        abort(403)

    return render_template("teacher/start_ai_marking.html", test=test)


@teacher_bp.route('/start_ai_marking/<int:test_id>', methods=['POST'])
@login_required
def start_ai_marking_route(test_id):
    try:
        submissions = StudentSubmission.query.filter_by(test_id=test_id, teacher_id=current_user.id).all()
        if not submissions:
            return jsonify({"error": "No submissions found for this test"}), 404

        results = mark_batch_submissions(submissions, test_id)
        for submission, result in zip(submissions, results):
            save_marked_image(submission, result)

        return jsonify({"message": f"Started AI marking on {len(submissions)} submissions."})
    except Exception as e:
        current_app.logger.error(f"Error in batch AI marking: {e}")
        return jsonify({"error": str(e)}), 500


@teacher_bp.route('/start_ai_marking/submission/<int:submission_id>', methods=['POST'])
@login_required
def start_ai_marking_by_submission(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.teacher_id != current_user.id:
        abort(403, "Unauthorized access")

    try:
        result = mark_single_submission(submission)
        save_marked_image(submission, result)
        return jsonify({"message": f"AI marking completed for submission {submission_id}"})
    except Exception as e:
        current_app.logger.error(f"AI marking failed for submission {submission_id}: {e}")
        return jsonify({"error": str(e)}), 500


@teacher_bp.route('/test/<int:test_id>/start_ai_grading', methods=['POST'])
@login_required
def start_ai_grading(test_id):
    test = Test.query.get_or_404(test_id)

    if test.teacher_id != current_user.id and not current_user.is_admin:
        return jsonify({"error": "Unauthorized access"}), 403

    if test.is_locked:
        return jsonify({"error": "Test is already locked for grading."}), 400

    submissions = StudentSubmission.query.filter_by(test_id=test.id, teacher_id=current_user.id).all()
    if not submissions:
        return jsonify({"error": "No submissions found for this test"}), 404

    try:
        # Lock test immediately to prevent duplicate grading
        test.is_locked = True
        db.session.commit()

        # Enqueue async grading tasks for each submission using Flask-RQ2
        for sub in submissions:
            current_app.rq.enqueue(
                async_mark_submission,
                sub.file_path,    # Adjust this attribute if file path differs
                test.id,          # guide_id/test_id
                sub.student_id,
                test.id,
                retry=Retry(max=3, interval=[10, 30, 60])  # Retry policy example
            )

        return jsonify({"message": f"AI grading started asynchronously for {len(submissions)} submissions."})
    except Exception as e:
        current_app.logger.error(f"Error starting async AI grading for test {test_id}: {e}")
        # Optionally unlock test on failure:
        # test.is_locked = False
        # db.session.commit()
        return jsonify({"error": str(e)}), 500
