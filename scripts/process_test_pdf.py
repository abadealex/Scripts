import os
from pathlib import Path
from smartscripts.utils.pdf_helpers import (
    convert_pdf_to_images,
    split_pdf_by_page_ranges,
    rename_student_pdfs
)
from smartscripts.utils.file_helpers import load_class_list
from smartscripts.ai.ocr_engine import extract_name_id_from_image
from smartscripts.ai.text_matching import match_ocr_with_classlist

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def main():
    # === Config ===
    test_id = 1
    pdf_path = "uploads/tests/test_1/student_scripts.pdf"
    class_list_path = "uploads/tests/test_1/class_list.csv"
    output_folder = f"outputs/test_{test_id}/pages"
    split_output_folder = f"outputs/test_{test_id}/split_pdfs"

    ensure_dir(output_folder)
    ensure_dir(split_output_folder)

    print("🔄 Converting PDF to images and detecting front pages...")
    image_paths, page_ranges = convert_pdf_to_images(
        pdf_path=pdf_path,
        output_folder=output_folder,
        test_id=test_id,
        detect_front_pages=True
    )

    print(f"📄 Found {len(page_ranges)} student scripts.")

    print("✂️ Splitting PDF using detected ranges...")
    split_paths = split_pdf_by_page_ranges(pdf_path, page_ranges, split_output_folder)

    print("📋 Loading class list...")
    class_list = load_class_list(class_list_path)

    print("🔍 Performing OCR and matching with class list...")
    matched_students = []
    for img_path, pdf_path in zip(image_paths, split_paths):
        result = extract_name_id_from_image(img_path)
        match = match_ocr_with_classlist(result, class_list)
        match["pdf_path"] = pdf_path
        matched_students.append(match)

    print("📝 Renaming split PDFs...")
    rename_student_pdfs(matched_students, pdf_dir=split_output_folder)

    print("✅ All done!")

if __name__ == "__main__":
    main()

