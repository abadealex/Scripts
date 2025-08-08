from datetime import datetime
from typing import Optional, List, Dict
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from smartscripts.models import AuditLog  # ORM model
from smartscripts.extensions import db    # SQLAlchemy session


def _commit_session():
    """
    Helper to commit a session with rollback and logging.
    """
    try:
                db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Database error during audit log commit: {e}')
        raise


def log_manual_override(
    reviewer_id: str,
    question_id: str,
    original_text: str,
    corrected_text: str,
    feedback: Optional[str] = None,
    comment: Optional[str] = None
) -> AuditLog:
    """
    Log a manual override action for audit and training purposes.
    """
    entry = AuditLog(
        user_id=reviewer_id,
        question_id=question_id,
        action="manual_override",
        original_text=original_text,
        corrected_text=corrected_text,
        feedback=feedback,
        comment=comment,
        timestamp=datetime.utcnow()
    )
    db.session.add(entry)
    _commit_session()
    return entry


def get_review_history(question_id: str) -> List[Dict]:
    """
    Retrieve the full audit trail of manual overrides for a given question.
    """
    logs = AuditLog.query.filter_by(
        question_id=question_id,
        action="manual_override"
    ).order_by(AuditLog.timestamp.desc()).all()

    return [
        {
            "reviewer": log.user_id,
            "timestamp": log.timestamp.isoformat(),
            "original_text": log.original_text,
            "corrected_text": log.corrected_text,
            "feedback": log.feedback,
            "comment": log.comment
        }
        for log in logs
    ]


def get_latest_override(
    question_id: str,
    reviewer_id: Optional[str] = None
) -> Optional[AuditLog]:
    """
    Get the latest override log entry for a question, optionally filtered by reviewer.
    """
    query = AuditLog.query.filter_by(
        question_id=question_id,
        action="manual_override"
    )
    if reviewer_id:
        query = query.filter_by(user_id=reviewer_id)
    return query.order_by(AuditLog.timestamp.desc()).first()


def process_teacher_review(
    reviewer_id: str,
    question_id: str,
    original_text: str,
    corrected_text: str,
    feedback: Optional[str] = None,
    comment: Optional[str] = None
) -> AuditLog:
    """
    Process a teacher's manual review — logs it and commits override in one step.
    """
    return log_manual_override(
        reviewer_id=reviewer_id,
        question_id=question_id,
        original_text=original_text,
        corrected_text=corrected_text,
        feedback=feedback,
        comment=comment
    )


def override_diff(old_data: dict, new_data: dict) -> dict:
    """
    Return a diff dictionary showing changes between original and new override data.
    Format: { field: (old_value, new_value) }
    """
    return {
        key: (old_data[key], new_data[key])
        for key in old_data
        if old_data[key] != new_data.get(key)
    }


# Optional stub for score override — to be implemented later
def apply_score_override(
    student_id: str,
    question_id: str,
    new_score: float,
    feedback: Optional[str] = None
):
    """
    Placeholder: Manually override a student's score and feedback for a question.
    TODO: Load student submission and update score/feedback fields.
    """
    pass

def get_override(test_id, student_id):
    # TODO: Implement override fetching logic
    return None

def set_override(test_id, student_id, data):
    # TODO: Implement override setting logic
    pass

