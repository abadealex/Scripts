from typing import Tuple, List, Optional
from sentence_transformers import SentenceTransformer, util
import openai
import os

# Load sentence embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# Configure OpenAI API key from env variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def compute_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts using sentence embeddings.
    Returns a float between 0 and 1.
    """
    if not text1 or not text2:
        return 0.0

    embeddings = model.encode([text1, text2], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return similarity.item()


def gpt_semantic_similarity(text1: str, text2: str) -> float:
    """
    Use GPT-4 to estimate semantic similarity between two texts.
    Returns a similarity score between 0 and 1.
    This is a fallback or optional refinement (slower, requires API call).
    """
    try:
        prompt = (
            f"On a scale from 0 to 1, how semantically similar are these two texts?\n\n"
            f"Text 1: \"{text1}\"\n"
            f"Text 2: \"{text2}\"\n"
            f"Answer with only a number between 0 and 1."
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0,
        )
        similarity_str = response.choices[0].message.content.strip()
        score = float(similarity_str)
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1
    except Exception as e:
        # Log or handle error here if desired
        return 0.0


def find_best_match(
    student_answer: str,
    expected_answers: List[str],
    threshold: float = 0.7,
    use_gpt_fallback: bool = False,
) -> Tuple[str, float]:
    """
    Find expected answer with highest similarity to student answer.
    Uses embeddings primarily; if use_gpt_fallback=True and score is low, fallback to GPT similarity.
    Returns (best_match_text, similarity_score) or ("", score) if below threshold.
    """
    if not student_answer or not expected_answers:
        return "", 0.0

    best_score = 0.0
    best_answer = ""

    # First pass: embeddings similarity
    for expected in expected_answers:
        score = compute_similarity(student_answer, expected)
        if score > best_score:
            best_score = score
            best_answer = expected

    # If low confidence and GPT fallback enabled, try GPT similarity for best candidate
    if use_gpt_fallback and best_score < threshold and best_answer:
        gpt_score = gpt_semantic_similarity(student_answer, best_answer)
        if gpt_score > best_score:
            best_score = gpt_score

    if best_score >= threshold:
        return best_answer, best_score
    else:
        return "", best_score


def batch_similarity(student_answers: List[str], expected_answers: List[str]) -> List[List[float]]:
    """
    Compute similarity scores matrix between lists of student answers and expected answers.
    Returns 2D list of floats.
    """
    if not student_answers or not expected_answers:
        return []

    student_embeddings = model.encode(student_answers, convert_to_tensor=True)
    expected_embeddings = model.encode(expected_answers, convert_to_tensor=True)
    scores = util.pytorch_cos_sim(student_embeddings, expected_embeddings)
    return scores.cpu().tolist()
