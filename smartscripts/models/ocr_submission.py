from smartscripts.extensions import db
from datetime import datetime

class OCRSubmission(db.Model):
    __tablename__ = 'ocr_submission'

    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(256), nullable=False)
    extracted_text = db.Column(db.Text)
    confidence = db.Column(db.Float)
    needs_human_review = db.Column(db.Boolean, default=False)
    manual_override = db.Column(db.Boolean, default=False)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # FK to User model
    corrected_name = db.Column(db.String(255))
    corrected_id = db.Column(db.String(64))

    # Relationship to User model (reviewer)
    reviewer = db.relationship('User', back_populates='reviewed_ocr_submissions')

    # Relationship to AuditLog (one-to-many)
    audit_logs = db.relationship(
        'AuditLog',
        back_populates='ocr_submission',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<OCRSubmission {self.id} OCR confidence: {self.confidence}>"
