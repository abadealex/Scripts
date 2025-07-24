from flask import Blueprint

teacher_bp = Blueprint('teacher_bp', __name__, url_prefix='/teacher')

from .auth_routes import *
from .dashboard_routes import *
from .upload_routes import *
from .review_routes import *
from .ai_marking_routes import *
from .export_routes import *
from .delete_routes import *
from .misc_routes import *
from .utils import *
from .download_routes import *