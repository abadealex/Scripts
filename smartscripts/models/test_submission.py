from sqlalchemy import Column, Integer, Float, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from smartscripts.extensions import db

class TestSubmission(db.Model):
    __tablename__ = 'test_submissions'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_path = Column(String(255), nullable=False)
    marked = Column(Boolean, default=False)
    score = Column(Float)
    feedback = Column(Text)
    is_active = Column(Boolean, default=True)

    test = relationship('Test', back_populates='submissions')
    student = relationship('User', back_populates='test_submissions')

    def __repr__(self):
        return f"<TestSubmission {self.id} | Student: {self.student_id} | Test: {self.test_id}>"
