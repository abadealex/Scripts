from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from smartscripts.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    role = Column(String(20), nullable=False)
    registered_on = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)

    # Relationships
    graded_submissions = relationship(
        'StudentSubmission',
        foreign_keys='StudentSubmission.teacher_id',
        back_populates='teacher',
        cascade='all, delete-orphan'
    )
    guides = relationship('MarkingGuide', back_populates='teacher')
    
    # OCR submissions reviewed by this user
    reviewed_ocr_submissions = relationship('OCRSubmission', back_populates='reviewer')

    # Audit logs done by this user
    audit_logs = relationship('AuditLog', back_populates='user', lazy='dynamic')

    tests = relationship('Test', back_populates='teacher')
    test_submissions = relationship('TestSubmission', back_populates='student')
    override_logs = relationship('OCROverrideLog', back_populates='user')
    
    # Added page_reviews for PageReview model relationship
    page_reviews = relationship('PageReview', back_populates='reviewer')

    def __init__(self, username: str, email: str, password: str, role: str):
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
