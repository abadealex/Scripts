import os
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}


def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file_storage, upload_folder: str, prefix: str = "") -> str:
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


def ensure_folder_exists(folder_path: str):
    """Create the folder if it doesn't exist."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def create_pdf_report(output_path: str, title: str = "Report", content: str = ""):
    """
    Create a simple PDF report saved at output_path.

    Args:
        output_path (str): Path where the PDF file will be saved.
        title (str): Title of the PDF report.
        content (str): Content/body of the PDF report.

    Returns:
        str: The output_path of the created PDF.
    """
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
