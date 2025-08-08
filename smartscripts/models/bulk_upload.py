from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from smartscripts.extensions import db

class BulkUpload(db.Model):
    """
    Tracks each bulk upload action — storing metadata such as the uploader,
    time of upload, files involved, and any notes for auditing and troubleshooting.
    """
    __tablename__ = 'bulk_uploads'

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    class_list_filename = Column(String(255), nullable=True)         # e.g. "classlist.csv"
    combined_scripts_filename = Column(String(255), nullable=True)   # e.g. "scanned_scripts.pdf"
    notes = Column(Text, nullable=True)                              # optional remarks or error logs

    teacher = relationship("User", backref="bulk_uploads")
    test = relationship("Test", backref="bulk_uploads")

    def __repr__(self):
        return f"<BulkUpload {self.id} for Test {self.test_id}>"
