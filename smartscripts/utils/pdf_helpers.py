import os
import fitz  # PyMuPDF for PDF manipulation
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
from fpdf import FPDF


def convert_pdf_to_images(pdf_path, output_folder):
    """
    Convert each page of a PDF to PNG images saved in the output_folder.
    Returns a list of file paths to the generated images.
    """
    poppler_path = r"C:\Users\ALEX\Downloads\poppler-24.08.0\Library\bin"  # Adjust as needed
    images = convert_from_path(pdf_path, poppler_path=poppler_path)
    image_paths = []

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, img in enumerate(images):
        img_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{i+1}.png")
        img.save(img_path, 'PNG')
        image_paths.append(img_path)

    return image_paths


def re_render_annotated_pdf(pdf_path, output_folder, override_markings):
    """
    Re-render the annotated script PDF based on override markings.
    """
    page_images = convert_pdf_to_images(pdf_path, output_folder)
    annotated_image_paths = []

    for page_num, image_path in enumerate(page_images, start=1):
        img = Image.open(image_path).convert("RGBA")
        overlay = Image.new("RGBA", img.size)
        draw = ImageDraw.Draw(overlay)

        annotations = override_markings.get(page_num, [])
        for annotation in annotations:
            if annotation['type'] == 'text':
                position = annotation.get('position', (10, 10))
                content = annotation.get('content', '')
                color = annotation.get('color', (255, 0, 0, 255))
                draw.text(position, content, fill=color)

            elif annotation['type'] == 'rectangle':
                bbox = annotation.get('bbox', (0, 0, 100, 100))
                color = annotation.get('color', (255, 0, 0, 128))
                draw.rectangle(bbox, outline=color, width=3)

            elif annotation['type'] == 'image':
                overlay_path = annotation.get('path')
                position = annotation.get('position', (0, 0))
                if overlay_path and os.path.exists(overlay_path):
                    overlay_img = Image.open(overlay_path).convert("RGBA")
                    overlay.paste(overlay_img, position, overlay_img)

        combined = Image.alpha_composite(img, overlay)
        annotated_path = os.path.join(output_folder, f"annotated_page_{page_num}.png")
        combined.convert("RGB").save(annotated_path, "PNG")

        annotated_image_paths.append(annotated_path)

    return annotated_image_paths


def generate_marksheet(batch_id, output_path="marksheet.pdf"):
    """
    Generate a marksheet PDF for a given batch_id.
    Compiles student grades and comments into a table-style document.
    """
    # Mocked data source — replace this with your DB/service integration
    def get_student_marks_for_batch(batch_id):
        return [
            {"student_id": "S001", "name": "Alice Johnson", "grade": 88, "comments": "Great improvement!"},
            {"student_id": "S002", "name": "Bob Smith", "grade": 73, "comments": "Solid effort but room to grow."},
            {"student_id": "S003", "name": "Charlie Lee", "grade": 92, "comments": "Excellent work throughout."},
        ]

    student_data = get_student_marks_for_batch(batch_id)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Marksheet Report – Batch {batch_id}", ln=True, align="C")

    # Table header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, "Student ID", 1)
    pdf.cell(60, 10, "Name", 1)
    pdf.cell(30, 10, "Grade", 1)
    pdf.cell(60, 10, "Comments", 1)
    pdf.ln()

    # Table rows
    pdf.set_font("Arial", "", 12)
    for student in student_data:
        pdf.cell(40, 10, student["student_id"], 1)
        pdf.cell(60, 10, student["name"], 1)
        pdf.cell(30, 10, str(student["grade"]), 1)
        pdf.multi_cell(60, 10, student["comments"], 1)

    # Save file
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pdf.output(output_path)
    return output_path


def split_pdf_by_page_ranges(input_pdf_path, page_ranges, output_folder):
    """
    Split the PDF into multiple PDFs based on a list of (start_page, end_page) tuples.
    Pages are 1-indexed.
    
    Args:
        input_pdf_path (str): Path to the source PDF.
        page_ranges (list of tuples): List of (start_page, end_page) tuples.
        output_folder (str): Directory to save the split PDFs.

    Returns:
        list of str: Paths to the saved split PDFs.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = fitz.open(input_pdf_path)
    output_paths = []

    for i, (start, end) in enumerate(page_ranges, start=1):
        # Create new PDF for the page range
        new_doc = fitz.open()
        for page_num in range(start - 1, end):  # zero-based index in fitz
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
        output_path = os.path.join(output_folder, f"split_part_{i}_{start}_{end}.pdf")
        new_doc.save(output_path)
        new_doc.close()
        output_paths.append(output_path)

    doc.close()
    return output_paths


def save_per_student_pdfs(master_pdf_path, student_page_mapping, base_output_folder):
    """
    Save individual PDFs per student by splitting the master PDF based on page ranges.
    
    Args:
        master_pdf_path (str): The full combined PDF path.
        student_page_mapping (dict): Mapping {student_id: (start_page, end_page)}.
            Pages are 1-indexed.
        base_output_folder (str): Base folder to save per-student PDFs.
    
    Returns:
        dict: Mapping {student_id: saved_pdf_path}
    """
    if not os.path.exists(base_output_folder):
        os.makedirs(base_output_folder)

    doc = fitz.open(master_pdf_path)
    student_pdf_paths = {}

    for student_id, (start_page, end_page) in student_page_mapping.items():
        new_doc = fitz.open()
        for page_num in range(start_page - 1, end_page):
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        student_folder = os.path.join(base_output_folder, "student_scripts")
        if not os.path.exists(student_folder):
            os.makedirs(student_folder)
        output_path = os.path.join(student_folder, f"{student_id}_script.pdf")
        new_doc.save(output_path)
        new_doc.close()
        student_pdf_paths[student_id] = output_path

    doc.close()
    return student_pdf_paths


def save_split_pdf(master_pdf_path, page_ranges, output_folder):
    """
    The function named 'save_split_pdf' to fix your ImportError.
    It splits a PDF into multiple smaller PDFs based on page ranges
    and saves them in the output_folder.

    Args:
        master_pdf_path (str): The source PDF path.
        page_ranges (list of tuples): List of (start_page, end_page) tuples.
        output_folder (str): Directory to save split PDFs.

    Returns:
        list of str: List of saved PDF file paths.
    """
    return split_pdf_by_page_ranges(master_pdf_path, page_ranges, output_folder)
