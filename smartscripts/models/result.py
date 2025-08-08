from sqlalchemy import Column, Integer, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from smartscripts.extensions import db

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
