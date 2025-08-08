import os
import json
import zipfile
from pathlib import Path
from flask import current_app

import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
from fpdf import FPDF

from smartscripts.analytics.layout_detection import detect_front_pages_via_ocr
from smartscripts.ai.ocr_engine import (
    extract_text_lines_from_image,
    score_front_page,
    is_probable_front_page
)

# Utility: Check if a given image is likely a front page
def is_page_front_page(image_path: str) -> bool:
    lines = extract_text_lines_from_image(image_path)
    text = "\n".join(lines)
    score = score_front_page(text, lines)
    return is_probable_front_page(score)

# Core: Convert PDF pages to images and detect front pages
def convert_pdf_to_images(pdf_path, output_folder, test_id=None, detect_front_pages=False):
    """
    Converts PDF to PNG images in the output_folder.
    Optionally detects front pages and returns split page ranges.

    Returns:
        tuple: (list of image paths, list of (start, end) page ranges)
    """
    poppler_path = r"C:\\Users\\ALEX\\Downloads\\poppler-24.08.0\\Library\\bin"
    images = convert_from_path(pdf_path, poppler_path=poppler_path)
    image_paths = []
    split_metadata = []

    os.makedirs(output_folder, exist_ok=True)

    for i, img in enumerate(images):
        img_path = os.path.join(output_folder, f"{Path(pdf_path).stem}_page_{i + 1}.png")
        img.save(img_path, 'PNG')
        image_paths.append(img_path)

        lines = extract_text_lines_from_image(img_path)
        text = "\n".join(lines)
        score = score_front_page(text, lines)

        if score >= 0.9:
            status = "? Confident"
        elif score >= 0.6:
            status = "?? Needs Review"
        else:
            status = "? Not Front Page"

        split_metadata.append({
            "page_number": i + 1,
            "confidence": round(score, 2),
            "status": status,
            "image_path": img_path
        })

    # Save front page metadata
    if test_id:
        meta_path = os.path.join(output_folder, f"{test_id}_frontpage_status.json")
        with open(meta_path, "w") as f:
            json.dump(split_metadata, f, indent=2)

    # Detect page split points
    page_ranges = []
    if detect_front_pages and test_id:
        front_page_indices = [
            i for i, meta in enumerate(split_metadata)
            if meta["status"] in ("? Confident", "?? Needs Review")
        ]
        for i in range(len(front_page_indices)):
            start = front_page_indices[i] + 1
            end = front_page_indices[i + 1] if i + 1 < len(front_page_indices) else len(image_paths)
            page_ranges.append((start, end))

    return image_paths, page_ranges

# Core: Split PDF using the page ranges determined from front pages
def split_pdf_by_page_ranges(input_pdf_path, page_ranges, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(input_pdf_path)
    output_paths = []

    for i, (start, end) in enumerate(page_ranges, start=1):
        new_doc = fitz.open()
        for page_num in range(start - 1, end):
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        output_path = os.path.join(output_folder, f"split_part_{i}_{start}_{end}.pdf")
        new_doc.save(output_path)
        new_doc.close()
        output_paths.append(output_path)

    doc.close()
    return output_paths

# Wrapper alias for split function
def save_split_pdf(master_pdf_path, page_ranges, output_folder):
    return split_pdf_by_page_ranges(master_pdf_path, page_ranges, output_folder)

# Utility: Rename split student PDFs using matched student list
def rename_student_pdfs(matched_students, pdf_dir, output_dir=None):
    output_dir = output_dir or pdf_dir
    os.makedirs(output_dir, exist_ok=True)
    renamed_files = []

    for student in matched_students:
        orig_path = student.get('original_path')
        student_id = student.get('student_id', '').strip()
        name = student.get('name', '').strip().replace(" ", "_")

        if not student_id or not name or not os.path.exists(orig_path):
            print(f"[WARN] Skipping invalid entry: {student}")
            continue

        filename = f"{student_id}_{name}.pdf"
        new_path = os.path.join(output_dir, filename)

        counter = 1
        while os.path.exists(new_path):
            filename = f"{student_id}_{name}_{counter}.pdf"
            new_path = os.path.join(output_dir, filename)
            counter += 1

        os.rename(orig_path, new_path)

        renamed_files.append({
            "student_id": student_id,
            "name": name,
            "new_path": new_path
        })

        print(f"[INFO] ? Renamed to: {filename}")

    return renamed_files

# Utility: Create a ZIP containing all split PDFs and the presence CSV
def package_results(test_id: str, output_dir: str, pdf_dir: str, presence_csv_path: str):
    zip_path = Path(output_dir) / f"test_{test_id}_processed.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for pdf_file in Path(pdf_dir).glob("*.pdf"):
            zipf.write(pdf_file, arcname=pdf_file.name)
        zipf.write(presence_csv_path, arcname="presence_table.csv")

    print(f"?? Final ZIP created: {zip_path}")
    return str(zip_path)

# End-to-end function: PDF ? Images ? Detect Front Pages ? Split PDF
def auto_split_pdf(pdf_path: str, output_folder: str, test_id: str, confidence_threshold=0.6):
    print(f"[INFO] Starting auto-split for: {pdf_path}")
    image_paths, page_ranges = convert_pdf_to_images(
        pdf_path=pdf_path,
        output_folder=output_folder,
        test_id=test_id,
        detect_front_pages=True
    )

    if not page_ranges:
        print("[WARN] No front pages detected. Skipping split.")
        return []

    print(f"[INFO] ? Detected {len(page_ranges)} segments. Proceeding to split...")
    return split_pdf_by_page_ranges(pdf_path, page_ranges, output_folder)

# ? Alias required by import
split_pdf_by_front_pages = auto_split_pdf


def generate_pdf_report(test_id: int) -> str:
    # Directory to store generated reports
    reports_dir = os.path.join(current_app.instance_path, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    # Output PDF path
    output_path = os.path.join(reports_dir, f'test_report_{test_id}.pdf')

    # ?? Generate a simple PDF using FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt=f"Test Report for Test ID {test_id}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="This is a placeholder report.\nYou can fill in analytics or summaries here.")

    # Save PDF to file
    pdf.output(output_path)

    return output_path
