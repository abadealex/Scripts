import cv2
from sentence_transformers import SentenceTransformer, util
from smartscripts.ai.ocr_engine import extract_text_from_image
from smartscripts.services.overlay_service import add_overlay
from smartscripts.utils.text_cleaner import clean_text

# Initialize model once (reuse for efficiency)
model = SentenceTransformer("all-MiniLM-L6-v2")

def fetch_expected_text_from_guide(guide_id: int) -> str:
    """
    Placeholder function to fetch expected answer text for a given guide_id.
    Replace with your actual DB or file retrieval logic.
    """
    # TODO: Replace this with real fetch logic
    return "Expected answer text here"

def compute_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts using SentenceTransformer embeddings.
    """
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
    return similarity

def mark_submission(file_path: str, guide_id: int, student_id: int, threshold: float = 0.75):
    """
    Runs OCR on student's submission image, compares to expected text from guide,
    overlays tick/cross, and returns results.

    Args:
        file_path: path to student's submitted image file
        guide_id: ID of the marking guide (used to get expected text)
        student_id: ID of the student submitting
        threshold: similarity threshold for marking correct

    Returns:
        student_text: OCR extracted and cleaned text from student submission
        similarity_score: float similarity score (0–1)
        annotated_image: OpenCV image with tick/cross overlay
    """

    # 1. Fetch expected text for this guide
    expected_text = fetch_expected_text_from_guide(guide_id)

    # 2. Run OCR on student image and clean text
    raw_text = extract_text_from_image(file_path)
    student_text = clean_text(raw_text)

    # 3. Compute similarity between student answer and expected text
    similarity_score = compute_similarity(student_text, expected_text)

    # 4. Decide if answer is correct based on threshold
    is_correct = similarity_score >= threshold
    overlay_type = 'tick' if is_correct else 'cross'

    # 5. Load student image and add overlay
    image = cv2.imread(file_path)
    annotated_image = add_overlay(image, overlay_type)

    return student_text, similarity_score, annotated_image
