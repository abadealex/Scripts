# compliance/gdpr.py
from smartscripts.models import User, Submission
from smartscripts.extensions import db
import json

def export_user_data(user_id):
    user = User.query.get(user_id)
    if not user:
        return None

    submissions = Submission.query.filter_by(user_id=user_id).all()
    data = {
        "user": {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
        },
        "submissions": [
            {"id": s.id, "content": s.content, "submitted_at": s.created_at.isoformat()}
            for s in submissions
        ]
    }
    return json.dumps(data, indent=2)

def delete_user_data(user_id):
    Submission.query.filter_by(user_id=user_id).delete()
    User.query.filter_by(id=user_id).delete()
try:
        db.session.commit()
except SQLAlchemyError as e:
db.session.rollback()
current_app.logger.error(f'Database error: {e}')
flash('A database error occurred.', 'danger')

