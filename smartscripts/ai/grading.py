import json
import os
from typing import Dict, List, Any

# Simulated rubric for demo purposes
def grade_question(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Grade a single question using dummy logic (replace with AI grading).
    Supports partial credit.
    """
    q_number = question["question_number"]
    student_answer = question["student_answer"]
    correct_answer = question["correct_answer"]
    max_score = question.get("max_score", 5)

    # Basic string matching (replace with real NLP later)
    if student_answer.strip().lower() == correct_answer.strip().lower():
        score = max_score
        is_correct = True
    elif student_answer and correct_answer.lower() in student_answer.lower():
        score = round(max_score * 0.5, 2)
        is_correct = False
    else:
        score = 0.0
        is_correct = False

    return {
        "question_number": q_number,
        "score": score,
        "is_correct": is_correct,
        "student_answer": student_answer,
        "expected_answer": correct_answer,
    }


def mark_submission(file_path: str, guide: Dict[str, Any]) -> Dict[str, Any]:
    """
    Grade a student's submission and save feedback to uploads/feedback/<test_id>/<student_id>_feedback.json
    """
    print(f"[INFO] Grading file: {file_path} using guide: {guide.get('title', 'Untitled Guide')}")

    # Load student answers
    with open(file_path, "r") as f:
        submission = json.load(f)

    student_answers = submission.get("answers", [])
    questions = guide.get("questions", [])

    question_results = []
    total_score = 0.0
    max_total = 0.0

    for q in questions:
        q_number = q["question_number"]
        correct_answer = q["correct_answer"]
        max_score = q.get("max_score", 5)

        student_answer = next(
            (a["answer"] for a in student_answers if a["question_number"] == q_number), ""
        )

        result = grade_question({
            "question_number": q_number,
            "student_answer": student_answer,
            "correct_answer": correct_answer,
            "max_score": max_score
        })

        total_score += result["score"]
        max_total += max_score
        question_results.append(result)

    overall_grade = round((total_score / max_total) * 100, 2) if max_total else 0.0

    # Prepare feedback
    result_data = {
        "grade": overall_grade,
        "feedback": generate_feedback(question_results),
        "question_scores": question_results,
        "ai_confidence": 0.9 + 0.1 * (overall_grade / 100),
    }

    # 🟨 Extract test_id and student_id from path
    try:
                parts = file_path.split(os.sep)
        test_id = parts[-3]
        student_id = parts[-2]
    except IndexError:
        print("[ERROR] Invalid file_path structure.")
        return result_data

    # 🟩 Save feedback to uploads/feedback/<test_id>/<student_id>_feedback.json
    feedback_dir = os.path.join("uploads", "feedback", test_id)
    os.makedirs(feedback_dir, exist_ok=True)

    feedback_path = os.path.join(feedback_dir, f"{student_id}_feedback.json")
    with open(feedback_path, "w") as f:
        json.dump(result_data, f, indent=2)

    print(f"[INFO] Saved feedback to: {feedback_path}")
    return result_data


def generate_feedback(question_scores: List[Dict[str, Any]]) -> str:
    """
    Generate simple feedback based on incorrect or low-scoring questions.
    """
    flagged = [q for q in question_scores if not q["is_correct"] or q["score"] < q.get("max_score", 5)]
    if not flagged:
        return "Excellent work. All answers are correct!"

    feedback_lines = ["Overall good effort. Here’s what to review:"]
    for q in flagged:
        feedback_lines.append(
            f" - Question {q['question_number']}: expected something closer to '{q['expected_answer']}'"
        )
    return "\n".join(feedback_lines)


if __name__ == "__main__":
    # Example usage
    sample_guide = {
        "title": "Sample Grading Guide",
        "questions": [
            {"question_number": 1, "correct_answer": "Water boils at 100°C", "max_score": 5},
            {"question_number": 2, "correct_answer": "Photosynthesis needs sunlight", "max_score": 5},
            {"question_number": 3, "correct_answer": "The capital of Japan is Tokyo", "max_score": 5},
        ]
    }

    # Simulated test/student path
    sample_submission_path = "uploads/submissions/test_id_A/student_123/submission.json"
    result = mark_submission(sample_submission_path, sample_guide)
    print(json.dumps(result, indent=2))

def apply_gpt_scoring(answer, rubric, model_answer=None):
    from smartscripts.ai.gpt_utils import call_gpt_model, build_prompt, parse_score, parse_feedback

    prompt = build_prompt(answer, rubric, model_answer)
    response = call_gpt_model(prompt)
    return parse_score(response), parse_feedback(response)

