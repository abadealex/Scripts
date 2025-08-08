from datetime import datetime
from smartscripts.extensions import db

class OCROverrideLog(db.Model):
    __tablename__ = 'ocr_override_logs'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    student_id = db.Column(db.String(50), nullable=True)
    override_type = db.Column(db.String(50), nullable=True)
    previous_value = db.Column(db.String(255), nullable=True)
    new_value = db.Column(db.String(255), nullable=True)
    override_metadata = db.Column(db.Text, nullable=True)  # ✅ Renamed

    pdf_path = db.Column(db.String, nullable=True)
    old_name = db.Column(db.String)
    old_id = db.Column(db.String)
    new_name = db.Column(db.String)
    new_id = db.Column(db.String)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    test = db.relationship('Test', back_populates='override_logs')
    user = db.relationship('User', back_populates='override_logs')

