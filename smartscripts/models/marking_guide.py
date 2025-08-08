from datetime import datetime
from smartscripts.extensions import db

class MarkingGuide(db.Model):
    __tablename__ = 'marking_guide'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(100))
    grade_level = db.Column(db.String(100))
    filename = db.Column(db.String(255), nullable=False)
    rubric_filename = db.Column(db.String(255))
    answered_script_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False, unique=True)

    teacher = db.relationship('User', back_populates='guides')
    test = db.relationship('Test', back_populates='marking_guide')
    submissions = db.relationship('StudentSubmission', back_populates='guide', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MarkingGuide {self.title} ({self.subject})>"
