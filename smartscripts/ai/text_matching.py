from typing import List, Tuple, Dict
from sentence_transformers import SentenceTransformer, util
import openai
import os
from dotenv import load_dotenv
from difflib import SequenceMatcher
import csv

# -------------------- Setup --------------------

load_dotenv()  # Load .env variables

# Load sentence transformer model once
_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load OpenAI key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
openai.api_key = OPENAI_API_KEY

# -------------------- Embedding-Based Similarity --------------------

def compute_embedding_similarity(text1: str, text2: str) -> float:
    if not text1 or not text2:
        return 0.0

    embeddings = _model.encode([text1, text2], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return similarity.item()

def similarity_matrix(student_answers: List[str], expected_answers: List[str]) -> List[List[float]]:
    if not student_answers or not expected_answers:
        return []

    student_embeds = _model.encode(student_answers, convert_to_tensor=True)
    expected_embeds = _model.encode(expected_answers, convert_to_tensor=True)
    sim_matrix = util.pytorch_cos_sim(student_embeds, expected_embeds)

    return sim_matrix.cpu().tolist()

# -------------------- GPT-4 Similarity Fallback --------------------

def gpt_similarity(text1: str, text2: str) -> float:
    if not text1 or not text2:
        return 0.0

    prompt = (
        f"Rate the semantic similarity between the two texts on a scale from 0 to 1.\n\n"
        f"Text 1: \"{text1}\"\n"
        f"Text 2: \"{text2}\"\n\n"
        f"Respond with only a number between 0 and 1."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=5,
        )
        score_str = response.choices[0].message.content.strip()
        return max(0.0, min(1.0, float(score_str)))
    except Exception as e:
        print(f"[GPT-4 Similarity Error] {e}")
        return 0.0

# -------------------- Matching Logic --------------------

def match_answer(
    student_answer: str,
    expected_answers: List[str],
    threshold: float = 0.7,
    use_gpt: bool = False
) -> Tuple[str, float]:
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

# -------------------- Fuzzy Matching for OCR IDs --------------------

def fuzzy_match_id(
    ocr_id: str,
    class_ids: List[str],
    threshold: float = 0.85
) -> Tuple[str, float]:
    best_score = 0.0
    best_match = ""

    for cid in class_ids:
        score = SequenceMatcher(None, ocr_id, cid).ratio()
        if score > best_score:
            best_score = score
            best_match = cid

    return (best_match, best_score) if best_score >= threshold else ("", 0.0)

def fuzzy_match_name(
    ocr_name: str,
    class_names: List[str],
    threshold: float = 0.8
) -> Tuple[str, float]:
    best_score = 0.0
    best_match = ""

    for cname in class_names:
        score = SequenceMatcher(None, ocr_name.lower(), cname.lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = cname

    return (best_match, best_score) if best_score >= threshold else ("", 0.0)

def match_ocr_ids_to_class(
    extracted_ids: List[str],
    class_list: List[dict],
    threshold: float = 0.85
) -> Tuple[List[str], List[str]]:
    class_ids = [s["student_id"] for s in class_list]
    matched_ids = []
    unmatched_ids = []

    for ocr_id in extracted_ids:
        match, score = fuzzy_match_id(ocr_id, class_ids, threshold)
        if match:
            matched_ids.append(match)
        else:
            unmatched_ids.append(ocr_id)

    return matched_ids, unmatched_ids

def fuzzy_match_students(
    extracted_list: List[Tuple[str, str]],
    class_list: List[dict],
    id_threshold: float = 0.85,
    name_threshold: float = 0.8
) -> Tuple[List[dict], List[Tuple[str, str]], List[dict]]:
    matched = []
    unmatched = []
    scores = []

    for ocr_id, ocr_name in extracted_list:
        best_match = None
        best_score = 0.0

        for student in class_list:
            sid = student.get("student_id", "")
            sname = student.get("name", "")
            id_score = SequenceMatcher(None, ocr_id, sid).ratio()
            name_score = SequenceMatcher(None, ocr_name.lower(), sname.lower()).ratio()
            avg_score = (id_score + name_score) / 2

            if avg_score > best_score:
                best_score = avg_score
                best_match = student

        if best_score >= ((id_threshold + name_threshold) / 2):
            matched.append({
                "ocr_id": ocr_id,
                "ocr_name": ocr_name,
                "matched_student": best_match,
                "match_score": round(best_score, 3)
            })
        else:
            unmatched.append((ocr_id, ocr_name))

        scores.append({
            "ocr_id": ocr_id,
            "ocr_name": ocr_name,
            "best_match": best_match,
            "match_score": round(best_score, 3)
        })

    return matched, unmatched, scores

def fuzzy_match_ids(
    extracted_ids: List[str],
    class_list: List[Dict[str, str]],
    threshold: float = 0.85,
    mode: str = "fuzzy"
) -> List[Dict[str, str]]:
    class_ids = [s["student_id"] for s in class_list]
    matches = []

    for ocr_id in extracted_ids:
        best_match = ""
        best_score = 0.0

        for class_id in class_ids:
            if mode == "exact":
                score = 1.0 if ocr_id.strip() == class_id.strip() else 0.0
            else:
                score = SequenceMatcher(None, ocr_id.strip(), class_id.strip()).ratio()

            if score > best_score:
                best_score = score
                best_match = class_id

        if best_score >= threshold:
            matches.append({
                "ocr_id": ocr_id,
                "matched_id": best_match,
                "score": round(best_score, 4)
            })

    return sorted(matches, key=lambda x: x["score"], reverse=True)

def export_matches_to_csv(matches: List[Dict[str, str]], path: str):
    fieldnames = ["ocr_id", "matched_id", "score"]
    try:
        with open(path, mode="w", newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(matches)
    except Exception as e:
        print(f"[CSV Export Error] {e}")

def fuzzy_match_name_and_id_students(
    extracted_pairs: List[Dict[str, str]],
    class_list: List[Dict[str, str]],
    threshold: float = 0.85,
    mode: str = "fuzzy",
    name_weight: float = 0.5
) -> List[Dict[str, str]]:
    matches = []

    for extracted in extracted_pairs:
        ocr_id = extracted["id"]
        ocr_name = extracted["name"]

        best_match = None
        best_score = 0.0

        for student in class_list:
            class_id = student["student_id"]
            class_name = student["student_name"]

            if mode == "exact":
                id_score = 1.0 if ocr_id.strip() == class_id.strip() else 0.0
                name_score = 1.0 if ocr_name.strip().lower() == class_name.strip().lower() else 0.0
            else:
                id_score = SequenceMatcher(None, ocr_id.strip(), class_id.strip()).ratio()
                name_score = SequenceMatcher(None, ocr_name.strip().lower(), class_name.strip().lower()).ratio()

            combined_score = (1 - name_weight) * id_score + name_weight * name_score

            if combined_score > best_score:
                best_score = combined_score
                best_match = {
                    "ocr_name": ocr_name,
                    "ocr_id": ocr_id,
                    "matched_name": class_name,
                    "matched_id": class_id,
                    "name_score": round(name_score, 4),
                    "id_score": round(id_score, 4),
                    "combined_score": round(combined_score, 4)
                }

        if best_match and best_score >= threshold:
            matches.append(best_match)

    return sorted(matches, key=lambda x: x["combined_score"], reverse=True)

def export_name_id_matches_to_csv(matches: List[Dict[str, str]], path: str):
    fieldnames = ["ocr_name", "ocr_id", "matched_name", "matched_id", "name_score", "id_score", "combined_score"]
    try:
        with open(path, mode="w", newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(matches)
    except Exception as e:
        print(f"[CSV Export Error] {e}")

def match_student_to_classlist(detected_name, detected_id, class_list):
    """
    Stub implementation to match a detected student to a class list.
    Replace this with fuzzy logic or ID matching later.
    """
    # For now, always return unmatched
    return {
        "matched": False,
        "matched_name": None,
        "matched_id": None,
        "confidence": 0.0
    }
