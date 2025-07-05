from typing import Tuple, List
from sentence_transformers import SentenceTransformer, util

# Load model once when this module is imported
model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_similarity(text1: str, text2: str) -> float:
    """
    Computes cosine similarity between two texts using embeddings.
    Returns a float between 0 and 1.
    """
    if not text1 or not text2:
        return 0.0

    embeddings = model.encode([text1, text2], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return similarity.item()

def find_best_match(student_answer: str, expected_answers: List[str], threshold: float = 0.7) -> Tuple[str, float]:
    """
    Finds the expected answer with the highest similarity to the student answer.
    Returns (best_match_text, similarity_score) if above threshold; else ("", score).
    """
    if not student_answer or not expected_answers:
        return "", 0.0

    best_score = 0.0
    best_answer = ""

    for expected in expected_answers:
        score = compute_similarity(student_answer, expected)
        if score > best_score:
            best_score = score
            best_answer = expected

    if best_score >= threshold:
        return best_answer, best_score
    else:
        return "", best_score

def batch_similarity(student_answers: List[str], expected_answers: List[str]) -> List[List[float]]:
    """
    Compares a list of student answers against a list of expected answers.
    Returns a 2D list of similarity scores for each pair.
    """
    if not student_answers or not expected_answers:
        return []

    student_embeddings = model.encode(student_answers, convert_to_tensor=True)
    expected_embeddings = model.encode(expected_answers, convert_to_tensor=True)
    scores = util.pytorch_cos_sim(student_embeddings, expected_embeddings)
    return scores.cpu().tolist()
