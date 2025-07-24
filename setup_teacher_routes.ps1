# Define root and teacher folder
$root = "smartscripts"
$teacherFolder = Join-Path $root "teacher"

# Create directories if they don't exist
if (-not (Test-Path $teacherFolder)) {
    New-Item -Path $teacherFolder -ItemType Directory | Out-Null
}

# File paths
$initFile = Join-Path $teacherFolder "__init__.py"
$authFile = Join-Path $teacherFolder "auth_routes.py"
$dashboardFile = Join-Path $teacherFolder "dashboard_routes.py"
$uploadFile = Join-Path $teacherFolder "upload_routes.py"
$reviewFile = Join-Path $teacherFolder "review_routes.py"
$aiMarkingFile = Join-Path $teacherFolder "ai_marking_routes.py"
$exportFile = Join-Path $teacherFolder "export_routes.py"
$deleteFile = Join-Path $teacherFolder "delete_routes.py"
$miscFile = Join-Path $teacherFolder "misc_routes.py"
$utilsFile = Join-Path $teacherFolder "utils.py"

# Create __init__.py content with blueprint and imports
$initContent = @"
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
"@

# Write __init__.py
Set-Content -Path $initFile -Value $initContent -Encoding UTF8

# --- Manually split your original routes.py content below and write to files ---
# You need to copy-paste the relevant function and routes into each file below:

# Example: write auth routes
@"
import os
from flask import (
    render_template, request, redirect,
    url_for, flash, abort
)
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from smartscripts.extensions import db
from smartscripts.models import User
from smartscripts.app.forms import TeacherLoginForm, TeacherRegisterForm

from . import teacher_bp

@teacher_bp.route('/login', methods=['GET', 'POST'])
def login():
    # login code here
    pass

@teacher_bp.route('/register', methods=['GET', 'POST'])
def register():
    # register code here
    pass

@teacher_bp.route('/logout')
def logout():
    # logout code here
    pass

"@ | Set-Content -Path $authFile -Encoding UTF8

# Similarly, write placeholder content to other route files:
Set-Content -Path $dashboardFile -Value "# dashboard routes here" -Encoding UTF8
Set-Content -Path $uploadFile -Value "# upload routes here" -Encoding UTF8
Set-Content -Path $reviewFile -Value "# review routes here" -Encoding UTF8
Set-Content -Path $aiMarkingFile -Value "# AI marking routes here" -Encoding UTF8
Set-Content -Path $exportFile -Value "# export routes here" -Encoding UTF8
Set-Content -Path $deleteFile -Value "# delete routes here" -Encoding UTF8
Set-Content -Path $miscFile -Value "# misc routes here" -Encoding UTF8

# Utils file with helper functions
@"
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_file_upload(file, upload_dir, success_msg):
    # your existing handle_file_upload code
    pass
"@ | Set-Content -Path $utilsFile -Encoding UTF8

Write-Host "Folder structure and starter files created at '$teacherFolder'."
Write-Host "Manually copy-paste your actual route codes into respective files."
