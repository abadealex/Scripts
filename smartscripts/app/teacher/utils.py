import os
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

utils_bp = Blueprint('utils_bp', __name__)  # ? This is what was missing

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_file_upload(file, upload_dir, success_msg):
    if not file or file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        return jsonify({"message": success_msg, "filename": filename}), 200

    return jsonify({"error": "File type not allowed"}), 400

# Optional test route
@utils_bp.route('/ping')
def ping():
    return 'pong'
