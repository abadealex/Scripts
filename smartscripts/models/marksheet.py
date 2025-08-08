from datetime import datetime
from smartscripts.extensions import db

class Marksheet(db.Model):
    __tablename__ = 'marksheets'

    id = db.Column(db.Integer, primary_key=True)

    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False, unique=True)
    test = db.relationship('Test', back_populates='marksheet')

    final_pdf_path = db.Column(db.String(512))      # ZIP of marked scripts or combined PDF
    final_excel_path = db.Column(db.String(512))    # Excel summary path

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Marksheet for Test {self.test_id}>"
