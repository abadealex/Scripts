from flask import Blueprint, send_from_directory, abort, current_app
from sqlalchemy.exc import SQLAlchemyError
import os
from werkzeug.utils import safe_join

uploads = Blueprint('uploads', __name__)

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../uploads'))

@uploads.route('/uploads/<path:path>')
def get_upload_file(path):
    safe_path = safe_join(UPLOAD_FOLDER, path)
    if not safe_path:
        current_app.logger.warning(f"Unsafe file path access attempt: {path}")
        abort(404)

    # Extra symlink attack protection
    if not os.path.realpath(safe_path).startswith(os.path.realpath(UPLOAD_FOLDER)):
        current_app.logger.warning(f"Symlink escape attempt: {path}")
        abort(404)

    if not os.path.isfile(safe_path):
        current_app.logger.warning(f"File not found: {safe_path}")
        abort(404)

    return send_from_directory(UPLOAD_FOLDER, path)

