import os
from flask import Blueprint, request, jsonify, abort, current_app, url_for
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from smartscripts.models import db, StudentSubmission as Submission
from smartscripts.config import UPLOAD_FOLDER
from smartscripts.ai.grading import start_ai_marking  # Your AI marking trigger function
from smartscripts.services.bulk_upload_service import save_and_mark_batch  # batch upload + marking

submissions_bp = Blueprint('submissions_bp', __name__, url_prefix='/submissions')
api_bp = Blueprint('api_submissions', __name__, url_prefix='/api/v1/submissions')

FILE_FIELDS_TO_DELETE = ['filename', 'answer_filename', 'graded_image', 'report_filename']

# Create a new submission (students only)
@submissions_bp.route('/', methods=['POST'])
@login_required
def create_submission():
    data = request.json
    content = data.get('content')
    if not content:
        return jsonify({'error': 'Content is required'}), 400

    submission = Submission(
        student_id=current_user.id,
        content=content,
        teacher_id=current_user.teacher_id if current_user.role == 'student' else current_user.id
    )
    db.session.add(submission)
    db.session.commit()

    try:
        start_ai_marking(submission.id)
    except Exception as e:
        current_app.logger.error(f"AI marking trigger failed for submission {submission.id}: {e}")

    return jsonify({'id': submission.id, 'content': submission.content}), 201


# Retrieve a submission (students/teachers with access only)
@submissions_bp.route('/<int:submission_id>', methods=['GET'])
@login_required
def get_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)

    # Permission check
    if current_user.role == 'student' and submission.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    if current_user.role == 'teacher' and submission.teacher_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({
        'id': submission.id,
        'content': submission.content,
        'student_id': submission.student_id,
        'teacher_id': submission.teacher_id
    })


# List submissions for current user
@submissions_bp.route('/', methods=['GET'])
@login_required
def list_submissions():
    if current_user.role == 'teacher':
        submissions = Submission.query.filter_by(teacher_id=current_user.id).all()
    else:
        submissions = Submission.query.filter_by(student_id=current_user.id).all()

    return jsonify([
        {
            'id': s.id,
            'content': s.content,
            'student_id': s.student_id,
            'teacher_id': s.teacher_id
        } for s in submissions
    ])


# Update submission (only student owner)
@submissions_bp.route('/<int:submission_id>', methods=['PUT'])
@login_required
def update_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)

    if current_user.role != 'student' or submission.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    content = data.get('content')
    if not content:
        return jsonify({'error': 'Content is required'}), 400

    submission.content = content
    db.session.commit()
    return jsonify({'id': submission.id, 'content': submission.content})


# Delete submission (only teacher owner)
@submissions_bp.route('/<int:submission_id>', methods=['DELETE'])
@login_required
def delete_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)

    if current_user.role != 'teacher' or submission.teacher_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Delete associated files safely
    for field in FILE_FIELDS_TO_DELETE:
        file_path = getattr(submission, field, None)
        if file_path:
            # Secure filename just in case
            safe_file_path = secure_filename(file_path)
            full_path = os.path.join(UPLOAD_FOLDER, 'submissions', safe_file_path)
            try:
                if os.path.exists(full_path):
                    os.remove(full_path)
            except Exception as e:
                current_app.logger.error(f"Failed to delete file {file_path}: {e}")

    db.session.delete(submission)
    db.session.commit()
    return jsonify({'message': f'Submission {submission_id} deleted'}), 200


# List submissions for current user via JWT auth (optional or API use)
@submissions_bp.route('/my_submissions', methods=['GET'])
@jwt_required()
def get_my_submissions():
    current_user_id = get_jwt_identity()
    submissions = Submission.query.filter_by(student_id=current_user_id).all()

    return jsonify([
        {
            "id": s.id,
            "test_id": getattr(s, 'test_id', None),
            "score": s.grade or 0,
            "feedback": s.feedback or '',
            "file_url": url_for('static', filename=s.graded_image.replace('uploads/', ''), _external=True)
            if s.graded_image else None
        }
        for s in submissions
    ])


# Batch upload + start marking (API only) — now with authentication!
@jwt_required()
@api_bp.route('/upload/<test_id>', methods=['POST'])
def upload_submissions(test_id):
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    try:
        submissions = save_and_mark_batch(files, test_id)
        return jsonify({
            "message": f"Uploaded {len(submissions)} submissions and started marking.",
            "submission_ids": [s.id for s in submissions]
        })
    except Exception as e:
        current_app.logger.error(f"Batch upload failed: {e}")
        return jsonify({"error": str(e)}), 400
