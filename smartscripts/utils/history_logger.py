import logging
from datetime import datetime
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger("history_logger")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    # Basic handler setup; in your app, you might attach more handlers or integrate with your app logging
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def log_manual_override(action: str, student_id: int, override_details: dict):
    """
    Log a manual override action by a teacher with timestamp and user info.

    :param action: Description of the action performed (e.g. 'score adjusted').
    :param student_id: ID of the student whose marks were overridden.
    :param override_details: Details of the override (e.g. old score, new score, reason).
    """
    user_id = getattr(current_user, "id", "anonymous")
    username = getattr(current_user, "username", "anonymous")

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "username": username,
        "action": action,
        "student_id": student_id,
        "details": override_details,
    }

    logger.info(f"Manual Override: {log_entry}")

from datetime import datetime

def log_override_change(user_id, student_id, field, old_value, new_value, timestamp=None):
    """
    Logs who changed what in the override history.
    """
    timestamp = timestamp or datetime.utcnow()
    print(f"[OVERRIDE] {timestamp} - User {user_id} changed {field} for {student_id} from '{old_value}' to '{new_value}'")
    # Optionally save to a CSV or database


