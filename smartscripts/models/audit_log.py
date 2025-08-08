from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from smartscripts.extensions import db

class AuditLog(db.Model):
    """
    Stores a history of significant events such as override changes, deletions,
    bulk uploads, reviews, grading steps, etc., for accountability and traceability.
    """
    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True)
    event_type = Column(String(100), nullable=False)          # e.g., 'override', 'bulk_upload', 'grading', 'manual_review'
    user_id = Column(Integer, ForeignKey('users.id'))          # ForeignKey to User
    test_id = Column(Integer, ForeignKey('tests.id'))          # Optional: associated test
    student_id = Column(String, nullable=True)                 # Optional: affected student
    timestamp = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)                                 # e.g., "Corrected ID from XYZ to ABC"

    # Add ForeignKey to OCRSubmission
    ocr_submission_id = Column(Integer, ForeignKey('ocr_submission.id'), nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='audit_logs')
    ocr_submission = db.relationship('OCRSubmission', back_populates='audit_logs')

    def __repr__(self):
        return f"<AuditLog {self.event_type} on {self.timestamp}>"
