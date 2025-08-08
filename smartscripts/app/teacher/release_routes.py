from flask import Blueprint, redirect, url_for, flash, current_app
from sqlalchemy.exc import SQLAlchemyError

from smartscripts.models import StudentSubmission
from smartscripts.extensions import db  # Ensure you import db from extensions

# ? Define blueprint
release_bp = Blueprint('release_bp', __name__, url_prefix='/release')


@release_bp.route('/results/<int:test_id>', methods=['POST'])
def release_results(test_id):
    """Mark all student submissions for a test as published."""
    try:
        submissions = StudentSubmission.query.filter_by(test_id=test_id).all()

        for s in submissions:
            s.is_published_to_student = True

        db.session.commit()
        flash('? Results successfully released to students.', 'success')

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Database error during result release: {e}', exc_info=True)
        flash('? A database error occurred while releasing results.', 'danger')

    return redirect(url_for('teacher_bp.dashboard_bp.dashboard'))
