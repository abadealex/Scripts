from flask import Blueprint

# Blueprint for all review-related routes
review_bp = Blueprint('review_bp', __name__, url_prefix='/teacher')

# Register all route modules to attach their routes to the review_bp blueprint
from . import (
    routes_review_test,
    routes_review_split,
    routes_overrides,
    routes_files,
    routes_ai_grading
)

# Optional: utility functions can be imported here or used directly from review_bp/utils.py
from . import utils
