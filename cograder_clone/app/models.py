from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ------------------- User Model -------------------

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'teacher' or 'student'

    submissions = db.relationship('StudentSubmission', backref='user', lazy=True)
    guides = db.relationship('MarkingGuide', backref='teacher', lazy=True)


# ------------------- Marking Guide -------------------

class MarkingGuide(db.Model):
    __tablename__ = 'marking_guide'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submissions = db.relationship('StudentSubmission', backref='guide', lazy=True)


# ------------------- Student Submission -------------------

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

    results = db.relationship('Result', backref='submission', lazy=True)


# ------------------- Result -------------------

class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('student_submissions.id'), nullable=False)

    question_number = db.Column(db.Integer)
    is_correct = db.Column(db.Boolean)
    student_answer = db.Column(db.Text)
    expected_answer = db.Column(db.Text)
    score = db.Column(db.Float)
