from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from smartscripts.extensions import db


class TestScript(db.Model):
    __tablename__ = 'test_script'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)

    # Add other columns here as needed, for example:
    filename = Column(String(255), nullable=False)
    page_count = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test = relationship('Test', back_populates='scripts')

    # This is the key relationship that links back to StudentSubmission:
    submission = relationship('StudentSubmission', back_populates='test_script', uselist=False)

    def __repr__(self):
        return f"<TestScript #{self.id} for Test {self.test_id}>"
