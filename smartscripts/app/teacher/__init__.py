from flask import Blueprint

# Main teacher blueprint
teacher_bp = Blueprint('teacher_bp', __name__, url_prefix='/teacher')

# Import each sub-blueprint explicitly
from .auth_routes import auth_bp
from .dashboard_routes import dashboard_bp
from .ai_marking_routes import ai_marking_bp
from .export_routes import export_bp
from .delete_routes import delete_bp
from .misc_routes import misc_bp
from .utils import utils_bp
from .download_routes import download_bp
from .file_routes import file_bp
from .upload_routes import upload_bp
from .analytics_routes import analytics_bp
from .release_routes import release_bp
from .review_bp import review_bp

# ✅ NEW: Import manage_routes
from .manage_routes import manage_routes

# Register each sub-blueprint under teacher_bp
teacher_bp.register_blueprint(auth_bp)
teacher_bp.register_blueprint(dashboard_bp)
teacher_bp.register_blueprint(review_bp)
teacher_bp.register_blueprint(ai_marking_bp)
teacher_bp.register_blueprint(export_bp)
teacher_bp.register_blueprint(delete_bp)
teacher_bp.register_blueprint(misc_bp)
teacher_bp.register_blueprint(utils_bp)
teacher_bp.register_blueprint(download_bp)
teacher_bp.register_blueprint(file_bp)
teacher_bp.register_blueprint(upload_bp, url_prefix='/upload')
teacher_bp.register_blueprint(analytics_bp)
teacher_bp.register_blueprint(release_bp)

# Register manage_routes under teacher_bp, optionally with a URL prefix
teacher_bp.register_blueprint(manage_routes, url_prefix='/manage')
