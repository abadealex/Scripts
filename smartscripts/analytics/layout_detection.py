import os
import re
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Tuple

import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# Load TrOCR model and processor
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Common keywords that appear on exam cover pages
KEYWORDS = ["name", "id", "student", "signature", "date", "index", "admission", "reg"]

def run_trocr(image: np.ndarray) -> str:
    """Run OCR on an image using TrOCR and return lowercased text."""
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    pixel_values = processor(images=pil_img, return_tensors="pt").pixel_values.to(device)
    with torch.no_grad():
        generated_ids = model.generate(pixel_values)
    text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return text.lower().strip()

def detect_form_lines(thresh_image: np.ndarray) -> int:
    """Count form-like lines using morphological operations."""
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

    horizontal_lines = cv2.morphologyEx(thresh_image, cv2.MORPH_OPEN, horizontal_kernel)
    vertical_lines = cv2.morphologyEx(thresh_image, cv2.MORPH_OPEN, vertical_kernel)
    
    combined = cv2.add(horizontal_lines, vertical_lines)
    contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    return len(contours)

def score_front_page(image: np.ndarray) -> float:
    """
    Score how likely the image is a front page using layout + OCR.
    Score = weighted sum of:
        - keyword_score (0.4)
        - layout_score (0.3)
        - title_score (0.3)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, 15, 10)

    ocr_text = run_trocr(image)
    keyword_hits = sum(1 for word in KEYWORDS if word in ocr_text)
    keyword_score = min(keyword_hits / 4, 1.0)  # Cap at 1.0

    title_match = re.search(r"\b(examination|exam)\b", ocr_text)
    title_score = 1.0 if title_match else 0.0

    line_count = detect_form_lines(thresh)
    layout_score = min(line_count / 10, 1.0)  # Normalize

    final_score = (0.4 * keyword_score) + (0.3 * layout_score) + (0.3 * title_score)
    return round(final_score, 3)

def detect_front_pages_via_ocr(image_paths: List[str], threshold: float = 0.5) -> List[Tuple[int, int]]:
    """
    Detect front pages in a list of image paths based on OCR/layout score.
    Returns: List of (start_page, end_page) ranges for each student.
    """
    debug_dir = Path("tmp/front_pages")
    debug_dir.mkdir(parents=True, exist_ok=True)

    front_page_indices = []

    for idx, image_path in enumerate(image_paths):
        image = cv2.imread(image_path)
        if image is None:
            print(f"[!] Failed to read image: {image_path}")
            continue

        score = score_front_page(image)
        if score >= threshold:
            front_page_indices.append(idx)
            debug_output = debug_dir / f"front_page_{idx + 1}.jpg"
            Image.fromarray(image).save(debug_output)
            print(f"[?] Detected front page at page {idx + 1} — Score: {score}")

    # Convert detected front page indices to (start, end) page ranges
    total_pages = len(image_paths)
    page_ranges = []
    for i, start_idx in enumerate(front_page_indices):
        start_page = start_idx + 1  # Convert to 1-based
        end_page = front_page_indices[i + 1] if i + 1 < len(front_page_indices) else total_pages
        page_ranges.append((start_page, end_page))

    return page_ranges

# Optional CLI usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2:
        image_path = sys.argv[1]
        image = cv2.imread(image_path)
        if image is not None:
            score = score_front_page(image)
            print(f"Front page score for {image_path}: {score}")
        else:
            print("Failed to load image.")
    elif len(sys.argv) > 2:
        image_paths = sys.argv[1:]
        ranges = detect_front_pages_via_ocr(image_paths)
        print("Detected front page ranges:", ranges)
    else:
        print("Usage:\n  python script.py image.jpg\n  python script.py page1.jpg page2.jpg ...")
