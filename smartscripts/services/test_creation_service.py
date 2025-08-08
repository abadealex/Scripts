# smartscripts/services/test_creation_service.py

from smartscripts.models import Test
from smartscripts.extensions import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app, flash

def create_new_test_record(title, subject, exam_date, grade_level, description, teacher_id):
    try:
        new_test = Test(
            title=title,
            subject=subject,
            exam_date=exam_date,
            grade_level=grade_level,
            description=description,
            teacher_id=teacher_id,
            created_at=datetime.utcnow()
        )
        db.session.add(new_test)
        db.session.commit()
        return new_test  # only return if commit succeeded
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Database error: {e}')
        flash('A database error occurred.', 'danger')
        return None
