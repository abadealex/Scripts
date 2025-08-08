# compliance/retention_policy.py
from datetime import datetime, timedelta
from smartscripts.models import TestSubmission
from smartscripts.extensions import db

RETENTION_DAYS = 365  # Customize this based on your policy

def enforce_retention_policy():
    cutoff = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
    old_submissions = Submission.query.filter(Submission.created_at < cutoff).all()
    count = len(old_submissions)

    for submission in old_submissions:
        db.session.delete(submission)

try:
        db.session.commit()
except SQLAlchemyError as e:
db.session.rollback()
current_app.logger.error(f'Database error: {e}')
flash('A database error occurred.', 'danger')
    return count

