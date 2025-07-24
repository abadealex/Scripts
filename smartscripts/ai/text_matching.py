from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer, util
import openai
import os

# Load the sentence transformer model once
_model = SentenceTransformer("all-MiniLM-L6-v2")

# Configure OpenAI key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")


def compute_embedding_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts using sentence embeddings.
    """
    if not text1 or not text2:
        return 0.0

    embeddings = _model.encode([text1, text2], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return similarity.item()


def gpt_similarity(text1: str, text2: str) -> float:
    """
    Use GPT-4 to assess semantic similarity between two texts.
    Returns a float between 0 and 1.
    """
    try:
        prompt = (
            f"Rate the semantic similarity between the two texts on a scale from 0 to 1.\n\n"
            f"Text 1: \"{text1}\"\n"
            f"Text 2: \"{text2}\"\n"
            f"Respond with only a number between 0 and 1."
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=5
        )
        score_str = response.choices[0].message.content.strip()
        return max(0.0, min(1.0, float(score_str)))
    except Exception as e:
        print(f"[GPT ERROR] {e}")
        return 0.0


def match_answer(
    student_answer: str,
    expected_answers: List[str],
    threshold: float = 0.7,
    use_gpt: bool = False
) -> Tuple[str, float]:
    """
    Find the expected answer most semantically similar to the student's answer.
    Falls back to GPT if score is low and use_gpt=True.
    Returns (best_match, score)
    """
    best_score = 0.0
    best_match = ""

    for expected in expected_answers:
        score = compute_embedding_similarity(student_answer, expected)
        if score > best_score:
            best_score = score
            best_match = expected

    if use_gpt and best_score < threshold and best_match:
        gpt_score = gpt_similarity(student_answer, best_match)
        if gpt_score > best_score:
            best_score = gpt_score

    if best_score >= threshold:
        return best_match, best_score
    return "", best_score


def similarity_matrix(
    student_answers: List[str],
    expected_answers: List[str]
) -> List[List[float]]:
    """
    Returns a matrix of cosine similarities between all student and expected answers.
    """
    if not student_answers or not expected_answers:
        return []

    student_embeds = _model.encode(student_answers, convert_to_tensor=True)
    expected_embeds = _model.encode(expected_answers, convert_to_tensor=True)
    scores = util.pytorch_cos_sim(student_embeds, expected_embeds)

    return scores.cpu().tolist()
