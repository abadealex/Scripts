import os
import shutil
from typing import List
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}


def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_folder_exists(folder_path: str):
    """Create the folder if it doesn't exist."""
    os.makedirs(folder_path, exist_ok=True)


def save_file(file_storage, upload_folder: str, prefix: str = "") -> str:
    """
    Save an uploaded file securely with an optional prefix.
    Returns the saved file path.
    """
    ensure_folder_exists(upload_folder)
    filename = secure_filename(file_storage.filename)
    if prefix:
        filename = f"{prefix}_{filename}"
    filepath = os.path.join(upload_folder, filename)
    file_storage.save(filepath)
    return filepath


def save_multiple_files(files: List, upload_folder: str, prefix: str = "") -> List[str]:
    """
    Save multiple uploaded files and return a list of saved paths.
    """
    saved_paths = []
    ensure_folder_exists(upload_folder)
    for index, file_storage in enumerate(files):
        indexed_prefix = f"{prefix}_{index}" if prefix else f"{index}"
        if file_storage and allowed_file(file_storage.filename):
            path = save_file(file_storage, upload_folder, indexed_prefix)
            saved_paths.append(path)
    return saved_paths


def delete_files(file_paths: List[str]) -> List[str]:
    """
    Delete multiple files. Returns a list of successfully deleted file paths.
    """
    deleted = []
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                deleted.append(path)
        except Exception as e:
            print(f"[ERROR] Could not delete {path}: {e}")
    return deleted


def move_files(file_paths: List[str], target_folder: str) -> List[str]:
    """
    Move files to a target folder. Returns new file paths.
    """
    ensure_folder_exists(target_folder)
    moved = []
    for path in file_paths:
        try:
            if os.path.exists(path):
                filename = os.path.basename(path)
                target_path = os.path.join(target_folder, filename)
                shutil.move(path, target_path)
                moved.append(target_path)
        except Exception as e:
            print(f"[ERROR] Could not move {path}: {e}")
    return moved


def create_pdf_report(output_path: str, title: str = "Report", content: str = "") -> str:
    """
    Create a simple PDF report saved at output_path.

    Args:
        output_path (str): Path where the PDF file will be saved.
        title (str): Title of the PDF report.
        content (str): Content/body of the PDF report.

    Returns:
        str: The output_path of the created PDF.
    """
    ensure_folder_exists(os.path.dirname(output_path))
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Draw title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2.0, height - 72, title)

    # Draw content below the title
    c.setFont("Helvetica", 12)
    text_object = c.beginText(72, height - 108)
    for line in content.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)

    c.showPage()
    c.save()

    return output_path
