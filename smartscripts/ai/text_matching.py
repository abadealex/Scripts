from typing import Tuple
from sentence_transformers import SentenceTransformer, util
import torch

# Load model once when this module is imported
model = SentenceTransformer("all-MiniLM-L6-v2")  # Fast and good for semantic similarity

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


def find_best_match(student_answer: str, expected_answers: list, threshold: float = 0.7) -> Tuple[str, float]:
    """
    Finds the expected answer with the highest similarity to the student answer.
    Returns (best_match_text, similarity_score)
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

    return best_answer, best_score if best_score >= threshold else ("", best_score)


def batch_similarity(student_answers: list, expected_answers: list) -> list:
    """
    Compares a list of student answers against a list of expected answers.
    Returns a list of (similarity scores) for each pair.
    """
    student_embeddings = model.encode(student_answers, convert_to_tensor=True)
    expected_embeddings = model.encode(expected_answers, convert_to_tensor=True)
    scores = util.pytorch_cos_sim(student_embeddings, expected_embeddings)
    return scores.cpu().tolist()
