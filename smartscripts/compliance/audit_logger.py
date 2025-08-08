# compliance/audit_logger.py
from datetime import datetime
from smartscripts.extensions import db

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    action = db.Column(db.String(255), nullable=False)
    metadata = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def log_action(user_id=None, action="", metadata=None):
    entry = AuditLog(user_id=user_id, action=action, metadata=metadata or {})
    db.session.add(entry)
try:
        db.session.commit()
except SQLAlchemyError as e:
db.session.rollback()
current_app.logger.error(f'Database error: {e}')
flash('A database error occurred.', 'danger')

def log_audit_event(action, user_id, details):
    """
    Logs a structured audit trail event.
    """
    print(f"[AUDIT] Action: {action} | User: {user_id} | Details: {details}")
    # Optional: save to file or database


