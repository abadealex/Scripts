import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file_storage, upload_folder, prefix=""):
    """
    Save an uploaded file securely with an optional prefix.
    Returns the saved file path.
    """
    filename = secure_filename(file_storage.filename)
    if prefix:
        filename = f"{prefix}_{filename}"
    filepath = os.path.join(upload_folder, filename)
    file_storage.save(filepath)
    return filepath

def ensure_folder_exists(folder_path):
    """Create the folder if it doesn't exist."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
