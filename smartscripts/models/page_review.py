from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Boolean, Float, DateTime, String
from sqlalchemy.orm import relationship
from smartscripts.extensions import db

class PageReview(db.Model):
    """
    Stores manual or AI-based review for a specific page in an extracted student script.
    Supports tracking of confidence, front page status, reviewer actions, and override flags.
    """
    __tablename__ = 'page_reviews'

    id = db.Column(db.Integer, primary_key=True)
    extracted_script_id = db.Column(db.Integer, db.ForeignKey('extracted_scripts.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    is_front_page = db.Column(db.Boolean, default=False)
    review_comment = db.Column(db.String(500), nullable=True)
    confidence_score = db.Column(db.Float, default=0.0)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    override_flag = db.Column(db.Boolean, default=False)

    # Relationships
    extracted_script = db.relationship("ExtractedStudentScript", back_populates="page_reviews")
    reviewer = db.relationship("User", back_populates="page_reviews")
    test = db.relationship("Test", back_populates="page_reviews")

    def __repr__(self):
        return f"<PageReview id={self.id} page={self.page_number} front={self.is_front_page}>"
