from flask import Blueprint
from sqlalchemy.exc import SQLAlchemyError

# Main v1 blueprint prefix
v1_bp = Blueprint('v1_bp', __name__, url_prefix='/v1')

# Import sub-blueprints
from . import auth, submissions, grading, feedback, billing, review

# Register each under /api/v1/
v1_bp.register_blueprint(auth.auth_bp)
v1_bp.register_blueprint(submissions.api_bp)  # The API submissions blueprint
v1_bp.register_blueprint(grading.grading_bp)
v1_bp.register_blueprint(feedback.feedback_bp)
v1_bp.register_blueprint(billing.billing_bp)
v1_bp.register_blueprint(review.v1_review_bp)

