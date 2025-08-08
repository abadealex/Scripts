from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from smartscripts.extensions import db

class AttendanceRecord(db.Model):
    """
    Stores attendance information for a specific test and student.
    Supports manual and OCR-derived attendance checks.
    """
    __tablename__ = 'attendance_record'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    student_id = Column(String, nullable=False)
    name = Column(String)
    present = Column(Boolean, default=False)

    # OCR fields
    detected_name = Column(String)
    detected_id = Column(String)
    corrected_name = Column(String)
    corrected_id = Column(String)
    pdf_path = Column(String)

    def __repr__(self):
        return f"<AttendanceRecord Test={self.test_id}, Student={self.student_id}, Present={self.present}>"
