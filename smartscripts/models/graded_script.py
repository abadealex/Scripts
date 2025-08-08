# smartscripts/models/graded_script.py

from datetime import datetime
from smartscripts.extensions import db

class GradedScript(db.Model):
    __tablename__ = 'graded_scripts'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('student_submissions.id'), nullable=False, unique=True)
    grader_type = db.Column(db.String(20), nullable=False, default='ai')  # 'ai' or 'manual'
    grade = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    rubric_scores = db.Column(db.JSON, nullable=True)  # Stores per-question rubric feedback
    overlay_data = db.Column(db.JSON, nullable=True)  # For frontend PDF overlays
    confidence = db.Column(db.Float, nullable=True)  # Confidence score of the grading
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    submission = db.relationship('StudentSubmission', back_populates='graded_script')

    def __repr__(self):
        return f"<GradedScript id={self.id} submission_id={self.submission_id} grade={self.grade}>"
