# smartscripts/ai/marking_pipeline.py

import cv2
from smartscripts.ai.ocr_engine import run_ocr
from smartscripts.ai.text_matching import compute_similarity
from smartscripts.services.overlay_service import add_overlay
from smartscripts.utils.text_cleaner import clean_text

def mark_submission(image_path: str, expected_text: str, threshold: float = 0.75):
    """
    Runs OCR, compares answer, overlays tick/cross, and returns results.

    Returns:
        - student_text: cleaned OCR output
        - similarity_score: float (0–1)
        - annotated_image: image with tick/cross overlay
    """
    # 1. OCR
    raw_text = run_ocr(image_path)
    student_text = clean_text(raw_text)

    # 2. Compare
    similarity_score = compute_similarity(student_text, expected_text)

    # 3. Tick/cross decision
    is_correct = similarity_score >= threshold
    overlay_type = 'tick' if is_correct else 'cross'

    # 4. Load + annotate image
    image = cv2.imread(image_path)
    annotated_image = add_overlay(image, overlay_type)

    return student_text, similarity_score, annotated_image
