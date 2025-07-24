from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, validates
from flask import url_for
from smartscripts.extensions import db


# ------------------- User Model -------------------
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    role = Column(String(20), nullable=False)
    registered_on = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)

    submissions = relationship('StudentSubmission', foreign_keys='StudentSubmission.student_id', back_populates='student')
    graded_submissions = relationship('StudentSubmission', foreign_keys='StudentSubmission.teacher_id', back_populates='teacher')
    guides = relationship('MarkingGuide', back_populates='teacher')
    reviewed_ocr_submissions = relationship('OCRSubmission', back_populates='reviewer')
    audit_logs = relationship('AuditLog', back_populates='user')
    tests = relationship('Test', back_populates='teacher')
    test_submissions = relationship('TestSubmission', back_populates='student')

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# ------------------- Test Model -------------------
class Test(db.Model):
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(100), nullable=False)
    guide_path = Column(String(255), nullable=True)
    rubric_path = Column(String(255), nullable=True)
    exam_date = Column(DateTime, nullable=True)  # ✅ Added field
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    teacher_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    teacher = relationship('User', back_populates='tests')
    scripts = relationship('TestScript', back_populates='test', cascade="all, delete-orphan")
    submissions = relationship('TestSubmission', back_populates='test', cascade="all, delete-orphan")
    marking_guide = relationship('MarkingGuide', back_populates='test', uselist=False)
    student_submissions = relationship('StudentSubmission', back_populates='test')

    @validates('guide_path', 'rubric_path')
    def validate_paths(self, key, value):
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None
        return value

    def __repr__(self):
        return f"<Test {self.title} on {self.exam_date.strftime('%Y-%m-%d') if self.exam_date else 'No Date'}>"

# ------------------- Marking Guide Model -------------------
class MarkingGuide(db.Model):
    __tablename__ = 'marking_guide'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    subject = Column(String(100))
    grade_level = Column(String(100))
    filename = Column(String(255), nullable=False)
    rubric_filename = Column(String(255))
    answered_script_filename = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    upload_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    teacher_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    test_id = Column(Integer, ForeignKey('test.id'), nullable=False, unique=True)

    teacher = relationship('User', back_populates='guides')
    test = relationship('Test', back_populates='marking_guide')
    submissions = relationship('StudentSubmission', back_populates='guide', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MarkingGuide {self.title} ({self.subject})>"


# ------------------- Student Submission Model -------------------
class StudentSubmission(db.Model):
    __tablename__ = 'student_submissions'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    guide_id = Column(Integer, ForeignKey('marking_guide.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    test_id = Column(Integer, ForeignKey('test.id'), nullable=False)

    filename = Column(String(255), nullable=False)
    answer_filename = Column(String(255))
    graded_image = Column(String(255))
    report_filename = Column(String(255))
    grade = Column(Float)
    feedback = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    subject = Column(String(100))
    grade_level = Column(String(100))
    ai_confidence = Column(Float)
    review_status = Column(String(20), default='pending')
    is_active = Column(Boolean, default=True)

    test_script_id = Column(Integer, ForeignKey('test_script.id'), nullable=True)

    student = relationship('User', foreign_keys=[student_id], back_populates='submissions')
    teacher = relationship('User', foreign_keys=[teacher_id], back_populates='graded_submissions')
    guide = relationship('MarkingGuide', back_populates='submissions')
    test = relationship('Test', back_populates='student_submissions')
    test_script = relationship('TestScript')
    results = relationship('Result', back_populates='submission')

    def __repr__(self):
        return f"<StudentSubmission {self.id} by Student {self.student_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "guide_id": self.guide_id,
            "teacher_id": self.teacher_id,
            "test_id": self.test_id,
            "filename": self.filename,
            "answer_filename": self.answer_filename,
            "graded_image": self.graded_image,
            "report_filename": self.report_filename,
            "grade": self.grade,
            "feedback": self.feedback,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "subject": self.subject,
            "grade_level": self.grade_level,
            "ai_confidence": self.ai_confidence,
            "review_status": self.review_status,
            "test_script_id": self.test_script_id
        }

    @property
    def file_path(self):
        return f"uploads/submissions/test_id_{self.test_id}/student_id_{self.student_id}/{self.filename}"

    @property
    def file_url(self):
        return url_for('static', filename=self.file_path)


# ------------------- Test Script Model -------------------
class TestScript(db.Model):
    __tablename__ = 'test_script'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    test_id = Column(Integer, ForeignKey('test.id'), nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)

    test = relationship('Test', back_populates='scripts')

    def __repr__(self):
        return f"<TestScript {self.filename} uploaded on {self.upload_time.strftime('%Y-%m-%d %H:%M:%S')}>"


# ------------------- Test Submission Model -------------------
class TestSubmission(db.Model):
    __tablename__ = 'test_submissions'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('test.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    file_path = Column(String(255), nullable=False)
    marked = Column(Boolean, default=False)
    score = Column(Float)
    feedback = Column(Text)
    is_active = Column(Boolean, default=True)

    test = relationship('Test', back_populates='submissions')
    student = relationship('User', back_populates='test_submissions')

    def __repr__(self):
        return f"<TestSubmission {self.id} | Student: {self.student_id} | Test: {self.test_id}>"


# ------------------- Result Model -------------------
class Result(db.Model):
    __tablename__ = 'result'

    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey('student_submissions.id'), nullable=False)
    question_number = Column(Integer)
    is_correct = Column(Boolean)
    student_answer = Column(Text)
    expected_answer = Column(Text)
    score = Column(Float)

    submission = relationship('StudentSubmission', back_populates='results')

    def __repr__(self):
        return f"<Result Q{self.question_number} Score: {self.score}>"


# ------------------- OCR Submission Model -------------------
class OCRSubmission(db.Model):
    __tablename__ = 'ocr_submission'

    id = Column(Integer, primary_key=True)
    image_path = Column(String(256), nullable=False)
    extracted_text = Column(Text)
    confidence = Column(Float)
    needs_human_review = Column(Boolean, default=False)
    manual_override = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey('user.id'), nullable=True)

    reviewer = relationship('User', back_populates='reviewed_ocr_submissions')
    audit_logs = relationship('AuditLog', back_populates='submission', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<OCRSubmission {self.id} OCR confidence: {self.confidence}>"


# ------------------- Audit Log Model -------------------
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey('ocr_submission.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    question_id = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='audit_logs')
    submission = relationship('OCRSubmission', back_populates='audit_logs')

    def __repr__(self):
        return f"<AuditLog User {self.user_id} Action: {self.action} on Q{self.question_id}>"

class ExtractedStudentScript(db.Model):
    __tablename__ = 'extracted_student_script'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    student_name = db.Column(db.String(128))
    student_id = db.Column(db.String(64))
    page_range = db.Column(db.String(32))
    script_path = db.Column(db.String(255))  # PDF of extracted pages
    confirmed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<ExtractedStudentScript {self.student_name} ({self.student_id}) pages {self.page_range}>"

class SubmissionManifest(db.Model):
    __tablename__ = 'submission_manifest'

    id = Column(Integer, primary_key=True)
    # add your fields here, for example:
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SubmissionManifest {self.name}>"