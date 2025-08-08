from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from smartscripts.extensions import db

class SubmissionManifest(db.Model):
    __tablename__ = 'submission_manifest'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SubmissionManifest {self.name}>"
