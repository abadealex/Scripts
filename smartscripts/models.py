from datetime import datetime
from smartscripts.extensions import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(50), default='student')  # e.g., student, teacher, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)
    bulk_submissions = db.relationship('BulkFileSubmission', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    additional_info = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<AuditLog user_id={self.user_id} action={self.action}>"


class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    submission_id = db.Column(db.Integer, nullable=True)  # optional link to submission if you have
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Feedback user_id={self.user_id} resolved={self.resolved}>"


class BulkFileSubmission(db.Model):
    __tablename__ = 'bulk_file_submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')  # e.g., pending, processing, completed, failed
    error_message = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<BulkFileSubmission id={self.id} user_id={self.user_id} status={self.status}>"
