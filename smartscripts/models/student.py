from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from smartscripts.extensions import db

class Student(db.Model):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), unique=True, nullable=False, index=True)
    student_id = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    submissions = relationship(
        'StudentSubmission',
        back_populates='student',
        cascade='all, delete-orphan',
        lazy=True
    )

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<Student {self.student_id} - {self.name}>"
