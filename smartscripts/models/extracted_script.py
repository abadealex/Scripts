from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from smartscripts.extensions import db

class ExtractedStudentScript(db.Model):
    """
    Represents a split individual student's script extracted from a combined PDF.
    Includes information like student ID (from OCR), path to the file, confidence score,
    and linkage to the original bulk upload.
    """
    __tablename__ = 'extracted_scripts'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=True)
    original_filename = Column(String(255), nullable=False)
    extracted_pdf_path = Column(String(512), nullable=False)
    ocr_name = Column(String(255), nullable=True)
    ocr_student_id = Column(String(50), nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    page_count = Column(Integer, default=1)
    is_confirmed = Column(Boolean, default=False)
    is_absent = Column(Boolean, default=False)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    bulk_upload_id = Column(Integer, ForeignKey('bulk_uploads.id'), nullable=True)

    test = relationship("Test", backref="extracted_scripts")
    student = relationship("Student", backref="extracted_scripts")
    bulk_upload = relationship("BulkUpload", backref="extracted_scripts")
    page_reviews = db.relationship("PageReview", back_populates="extracted_script", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ExtractedStudentScript id={self.id} student_id={self.student_id} test_id={self.test_id}>"
