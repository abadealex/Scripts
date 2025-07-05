from datetime import datetime
from typing import Optional
from smartscripts.models import AuditLog  # ORM model
from smartscripts.extensions import db    # SQLAlchemy session


def log_manual_review(
    reviewer_id: str,
    question_id: str,
    old_text: str,
    new_text: str,
    feedback: Optional[str] = None,
    comment: Optional[str] = None
):
    """
    Log a manual review correction or override for audit and retraining purposes.

    Args:
        reviewer_id: Who performed the review.
        question_id: Question affected.
        old_text: Original AI-generated or submitted text.
        new_text: Corrected/edited version.
        feedback: Optional textual feedback left by the reviewer.
        comment: Optional reviewer note (e.g., justification or tags).
    """
    log_entry = AuditLog(
        user_id=reviewer_id,
        question_id=question_id,
        action="manual_override",
        old_text=old_text,
        new_text=new_text,
        feedback=feedback,
        comment=comment,
        timestamp=datetime.utcnow()
    )
    db.session.add(log_entry)
    db.session.commit()


def get_review_history(question_id: str) -> list:
    """
    Fetch the full audit trail for a question.

    Args:
        question_id: The ID of the question to fetch history for.

    Returns:
        List of dicts summarizing manual interventions.
    """
    logs = AuditLog.query.filter_by(question_id=question_id, action="manual_override").all()
    return [
        {
            "reviewer": log.user_id,
            "timestamp": log.timestamp.isoformat(),
            "old_text": log.old_text,
            "new_text": log.new_text,
            "feedback": log.feedback,
            "comment": log.comment
        }
        for log in logs
    ]
