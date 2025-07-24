from datetime import datetime
from typing import Optional
from smartscripts.models import AuditLog  # ORM model
from smartscripts.extensions import db    # SQLAlchemy session


def log_manual_review(
    reviewer_id: str,
    question_id: str,
    original_text: str,
    corrected_text: str,
    feedback: Optional[str] = None,
    comment: Optional[str] = None
):
    """
    Log a manual review correction or override for audit and retraining purposes.
    """
    log_entry = AuditLog(
        user_id=reviewer_id,
        question_id=question_id,
        action="manual_override",
        original_text=original_text,
        corrected_text=corrected_text,
        feedback=feedback,
        comment=comment,
        timestamp=datetime.utcnow()
    )
    db.session.add(log_entry)
    db.session.commit()


def get_review_history(question_id: str) -> list:
    """
    Fetch the full audit trail for a question.
    """
    logs = AuditLog.query.filter_by(question_id=question_id, action="manual_override").all()
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


def get_override(question_id: str, reviewer_id: Optional[str] = None):
    """
    Retrieve the latest manual override for a question.
    """
    query = AuditLog.query.filter_by(question_id=question_id, action="manual_override")
    if reviewer_id:
        query = query.filter_by(user_id=reviewer_id)
    return query.order_by(AuditLog.timestamp.desc()).first()


def set_override(
    reviewer_id: str,
    question_id: str,
    original_text: str,
    corrected_text: str,
    feedback: Optional[str] = None,
    comment: Optional[str] = None
):
    """
    Create and save a new manual override entry.
    """
    override_log = AuditLog(
        user_id=reviewer_id,
        question_id=question_id,
        action="manual_override",
        original_text=original_text,
        corrected_text=corrected_text,
        feedback=feedback,
        comment=comment,
        timestamp=datetime.utcnow()
    )
    db.session.add(override_log)
    db.session.commit()
    return override_log


def process_teacher_review(
    reviewer_id: str,
    question_id: str,
    original_text: str,
    corrected_text: str,
    feedback: Optional[str] = None,
    comment: Optional[str] = None
):
    """
    Process a teacher's review by logging it and setting an override.
    """
    log_manual_review(
        reviewer_id=reviewer_id,
        question_id=question_id,
        original_text=original_text,
        corrected_text=corrected_text,
        feedback=feedback,
        comment=comment,
    )

    override = set_override(
        reviewer_id=reviewer_id,
        question_id=question_id,
        original_text=original_text,
        corrected_text=corrected_text,
        feedback=feedback,
        comment=comment,
    )

    return override
