from flask import Blueprint, request, jsonify, abort, current_app
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import SQLAlchemy

bp = Blueprint('feedback', __name__, url_prefix='/feedback')

db = SQLAlchemy()

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, nullable=False, index=True)
    comments = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'comments': self.comments
        }

@bp.before_app_first_request
def create_tables():
    db.create_all()

@bp.route('/', methods=['POST'])
def create_feedback():
    data = request.get_json(force=True)
    submission_id = data.get('submission_id')
    comments = data.get('comments')

    if not submission_id or not comments:
        return jsonify({'error': 'submission_id and comments are required'}), 400

    # Validate types
    if not isinstance(submission_id, int):
        return jsonify({'error': 'submission_id must be an integer'}), 400
    if not isinstance(comments, str) or len(comments.strip()) == 0:
        return jsonify({'error': 'comments must be a non-empty string'}), 400

    feedback = Feedback(submission_id=submission_id, comments=comments.strip())
    try:
                db.session.add(feedback)
try:
        db.session.commit()
except SQLAlchemyError as e:
db.session.rollback()
current_app.logger.error(f'Database error: {e}')
flash('A database error occurred.', 'danger')
    except Exception as e:
        current_app.logger.error(f"Database error while saving feedback: {e}", exc_info=True)
        return jsonify({'error': 'Failed to save feedback'}), 500

    return jsonify(feedback.to_dict()), 201

@bp.route('/<int:feedback_id>', methods=['GET'])
def get_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if not feedback:
        abort(404, description='Feedback not found')
    return jsonify(feedback.to_dict())

@bp.route('/submission/<int:submission_id>', methods=['GET'])
def list_feedback_for_submission(submission_id):
    feedbacks = Feedback.query.filter_by(submission_id=submission_id).all()
    results = [fb.to_dict() for fb in feedbacks]
    return jsonify(results)

# Optional: add update and delete routes for completeness
@bp.route('/<int:feedback_id>', methods=['PUT', 'PATCH'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if not feedback:
        abort(404, description='Feedback not found')

    data = request.get_json(force=True)
    comments = data.get('comments')
    if not comments or not isinstance(comments, str) or len(comments.strip()) == 0:
        return jsonify({'error': 'comments must be a non-empty string'}), 400

    feedback.comments = comments.strip()
    try:
                db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Database error while updating feedback: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update feedback'}), 500

    return jsonify(feedback.to_dict())

@bp.route('/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if not feedback:
        abort(404, description='Feedback not found')

    try:
                db.session.delete(feedback)
try:
        db.session.commit()
except SQLAlchemyError as e:
db.session.rollback()
current_app.logger.error(f'Database error: {e}')
flash('A database error occurred.', 'danger')
    except Exception as e:
        current_app.logger.error(f"Database error while deleting feedback: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete feedback'}), 500

    return jsonify({'message': f'Feedback {feedback_id} deleted successfully.'}), 200

