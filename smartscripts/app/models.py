from datetime import datetime
from smartscripts.extensions import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship


# ------------------- User Model -------------------

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    registered_on = db.Column(db.DateTime, default=db.func.current_timestamp())

    submissions = relationship('StudentSubmission', back_populates='student', lazy=True)
    guides = relationship('MarkingGuide', backref='teacher', lazy=True)
    reviewed_submissions = relationship('Submission', backref='reviewer', lazy=True)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# ------------------- Marking Guide Model -------------------

class MarkingGuide(db.Model):
    __tablename__ = 'marking_guide'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(100))
    grade_level = db.Column(db.String(100))  # New field added
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    submissions = relationship('StudentSubmission', backref='guide', lazy=True)

    def __repr__(self):
        return f"<MarkingGuide {self.title} ({self.subject})>"


# ------------------- Student Submission Model -------------------

class StudentSubmission(db.Model):
    __tablename__ = 'student_submissions'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    guide_id = db.Column(db.Integer, db.ForeignKey('marking_guide.id'), nullable=False)

    answer_filename = db.Column(db.String(255))
    graded_image = db.Column(db.String(255))
    report_filename = db.Column(db.String(255))

    grade = db.Column(db.Float)
    feedback = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    subject = db.Column(db.String(100))  # Existing field
    grade_level = db.Column(db.String(100))  # New field added
    ai_confidence = db.Column(db.Float)  # New field added

    student = relationship('User', back_populates='submissions')
    results = relationship('Result', backref='submission', lazy=True)

    def __repr__(self):
        return f"<StudentSubmission {self.id} by Student {self.student_id}>"


# ------------------- Result Model -------------------

class Result(db.Model):
    __tablename__ = 'result'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('student_submissions.id'), nullable=False)

    question_number = db.Column(db.Integer)
    is_correct = db.Column(db.Boolean)
    student_answer = db.Column(db.Text)
    expected_answer = db.Column(db.Text)
    score = db.Column(db.Float)

    def __repr__(self):
        return f"<Result Q{self.question_number} Score: {self.score}>"


# ------------------- Submission Model (OCR + Review) -------------------
# This is the new model for tracking OCR extraction and review

class Submission(db.Model):
    __tablename__ = 'submission'

    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(256), nullable=False)
    extracted_text = db.Column(db.Text)
    confidence = db.Column(db.Float)
    needs_human_review = db.Column(db.Boolean, default=False)
    manual_override = db.Column(db.Boolean, default=False)

    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"<Submission {self.id} OCR confidence: {self.confidence}>"


# ------------------- Audit Log Model -------------------

class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(64))
    old_text = db.Column(db.Text)
    new_text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog submission_id={self.submission_id} action={self.action}>"
