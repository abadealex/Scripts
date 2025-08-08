from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from flask import url_for, has_request_context
from smartscripts.extensions import db


class StudentSubmission(db.Model):
    __tablename__ = 'student_submissions'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    guide_id = Column(Integer, ForeignKey('marking_guide.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'))  # nullable=True → optional for ungraded
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    test_script_id = Column(Integer, ForeignKey('test_script.id'))  # nullable=True → if not yet assigned

    filename = Column(String(255), nullable=False)
    answer_filename = Column(String(255))
    graded_image = Column(String(255))
    report_filename = Column(String(255))

    grade = Column(Float)
    feedback = Column(Text)
    ai_confidence = Column(Float)
    review_status = Column(String(20), default='pending')

    timestamp = Column(DateTime, default=datetime.utcnow)
    subject = Column(String(100))
    grade_level = Column(String(100))
    is_active = Column(Boolean, default=True)

    # Relationships
    student = relationship('Student', back_populates='submissions')
    teacher = relationship('User', foreign_keys=[teacher_id], back_populates='graded_submissions')
    guide = relationship('MarkingGuide', back_populates='submissions')
    test = relationship('Test', back_populates='student_submissions')
    test_script = relationship('TestScript', back_populates='submission')  # key fix here
    results = relationship('Result', back_populates='submission', cascade="all, delete-orphan")
    graded_script = relationship('GradedScript', back_populates='submission', uselist=False)

    @property
    def file_path(self):
        return f"uploads/submissions/test_id_{self.test_id}/student_id_{self.student_id}/{self.filename}"

    @property
    def file_url(self):
        if has_request_context():
            return url_for('static', filename=self.file_path)
        return None

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

    def __repr__(self):
        return f"<StudentSubmission #{self.id} for Test {self.test_id} by Student {self.student_id}>"

    def __str__(self):
        return f"Submission #{self.id} – Test: {self.test_id}, Student: {self.student_id}"
