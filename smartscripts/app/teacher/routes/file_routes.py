from flask import Blueprint, send_from_directory, current_app, jsonify
import os
import threading
import time

file_routes_bp = Blueprint('file_routes_bp', __name__)

# Global OCR progress state (replace with better storage in prod)
ocr_state = {
    "progress": 0
}

@file_routes_bp.route('/uploaded/<path:filename>')
def uploaded_file(filename):
    """
    Serve uploaded files from static/uploads directory.
    Example URL: /uploaded/guides/test_id_A/filename.pdf
    """
    uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
    return send_from_directory(uploads_dir, filename)

@file_routes_bp.route('/start-ocr', methods=['POST'])
def start_ocr():
    """
    Starts OCR processing (simulated here with a background thread).
    In production, replace with proper background task (Celery, RQ, etc).
    """
    ocr_state['progress'] = 0

    def simulate_ocr():
        for i in range(1, 11):
            time.sleep(1)  # simulate work
            ocr_state['progress'] = i * 10

    threading.Thread(target=simulate_ocr).start()
    return '', 204  # No Content response

@file_routes_bp.route('/ocr-progress', methods=['GET'])
def ocr_progress():
    """
    Returns current OCR progress as JSON.
    """
    return jsonify(progress=ocr_state['progress'])
