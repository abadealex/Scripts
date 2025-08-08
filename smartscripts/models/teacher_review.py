from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from smartscripts.extensions import db

class TeacherReview(db.Model):
    __tablename__ = 'teacher_reviews'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TeacherReview {self.id}>"
