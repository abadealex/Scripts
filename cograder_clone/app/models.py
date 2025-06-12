from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ------------------- User Model -------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'teacher' or 'student'

    submissions = db.relationship('Submission', backref='user', lazy=True)
    guides = db.relationship('MarkingGuide', backref='teacher', lazy=True)


# ------------------- Marking Guide -------------------

class MarkingGuide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Path to uploaded file (e.g. JSON or PDF)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submissions = db.relationship('Submission', backref='guide', lazy=True)


# ------------------- Submission -------------------

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    guide_id = db.Column(db.Integer, db.ForeignKey('marking_guide.id'), nullable=False)

    answer_filename = db.Column(db.String(255))     # Uploaded answer image/pdf
    graded_image = db.Column(db.String(255))        # Annotated image result
    report_filename = db.Column(db.String(255))     # Final PDF report path

    grade = db.Column(db.Float)
    feedback = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    results = db.relationship('Result', backref='submission', lazy=True)


# ------------------- Result -------------------

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)

    question_number = db.Column(db.Integer)  # Q1 → 1, Q2 → 2, etc.
    is_correct = db.Column(db.Boolean)
    student_answer = db.Column(db.Text)
    expected_answer = db.Column(db.Text)
    score = db.Column(db.Float)
