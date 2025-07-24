from flask import Blueprint

# Create the main API blueprint with a prefix
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import v1 version blueprints
from smartscripts.api.v1 import submissions, auth, grading, feedback, billing, review

# Register all v1 blueprints under /api/v1/
from smartscripts.api.v1 import v1_bp  # This will be your v1 root bp

api_bp.register_blueprint(v1_bp)
