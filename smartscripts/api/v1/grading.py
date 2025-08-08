import os
import json
import logging
from typing import Dict, List, Any
from flask import Blueprint, request, jsonify, current_app, url_for
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest

api = Blueprint("grading_api", __name__)

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {"json"}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def grade_question(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Grade a single question using dummy logic (replace with AI grading).
    Supports partial credit.
    """
    q_number = question.get("question_number")
    student_answer = question.get("student_answer", "")
    correct_answer = question.get("correct_answer", "")
    max_score = question.get("max_score", 5)

    if not all([q_number, correct_answer]):
        current_app.logger.warning(f"Missing required grading fields in question: {question}")
        return {
            "question_number": q_number,
            "score": 0.0,
            "is_correct": False,
            "student_answer": student_answer,
            "expected_answer": correct_answer,
            "max_score": max_score,
        }

    # Simple grading logic
    try:
                student_answer_stripped = student_answer.strip().lower()
        correct_answer_stripped = correct_answer.strip().lower()
    except Exception as e:
        current_app.logger.error(f"Error normalizing answers: {e}")
        student_answer_stripped = student_answer
        correct_answer_stripped = correct_answer

    if student_answer_stripped == correct_answer_stripped:
        score = max_score
        is_correct = True
    elif student_answer_stripped and correct_answer_stripped in student_answer_stripped:
        score = round(max_score * 0.5, 2)  # partial match
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
        "max_score": max_score,
    }


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


def mark_submission(file_path: str, guide: Dict[str, Any]) -> Dict[str, Any]:
    """
    Grade a student's submission based on a grading guide (rubric).
    Supports partial scoring per question.
    """
    current_app.logger.info(f"Grading file: {file_path} using guide: {guide.get('title', 'Untitled Guide')}")

    try:
                with open(file_path, "r") as f:
            submission = json.load(f)
    except Exception as e:
        current_app.logger.error(f"Failed to read submission JSON: {e}")
        raise BadRequest("Invalid submission JSON file.")

    student_answers = submission.get("answers", [])
    questions = guide.get("questions", [])

    if not questions:
        current_app.logger.error("Grading guide has no questions.")
        raise BadRequest("Grading guide has no questions.")

    question_results = []
    total_score = 0.0
    max_total = 0.0

    for q in questions:
        q_number = q.get("question_number")
        correct_answer = q.get("correct_answer")
        max_score = q.get("max_score", 5)

        # Defensive: skip if missing key
        if q_number is None or correct_answer is None:
            current_app.logger.warning(f"Skipping question with missing data: {q}")
            continue

        student_answer = next(
            (a.get("answer", "") for a in student_answers if a.get("question_number") == q_number), ""
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

    return {
        "grade": overall_grade,
        "feedback": generate_feedback(question_results),
        "question_scores": question_results,
        "ai_confidence": round(0.9 + 0.1 * (overall_grade / 100), 3),  # Simulated confidence
    }


@api.route("/grade", methods=["POST"])
def grade():
    """
    Endpoint to accept submission file upload and grade it.
    Expects multipart/form-data with keys:
    - file: the submission JSON file (required)
    - test_id: test identifier (required)
    - student_id: student identifier (required)
    - guide: grading guide JSON (optional, else load default from guides/{test_id}.json)
    """
    try:
                if "file" not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file type"}), 400

        test_id = request.form.get("test_id")
        student_id = request.form.get("student_id")
        guide_json = request.form.get("guide")

        if not all([test_id, student_id]):
            return jsonify({"error": "Missing test_id or student_id"}), 400

        # Sanitize IDs to prevent path traversal
        test_id = secure_filename(test_id)
        student_id = secure_filename(student_id)

        filename = secure_filename(file.filename)
        submission_dir = os.path.join("uploads", "submissions", test_id, student_id)
        os.makedirs(submission_dir, exist_ok=True)
        submission_path = os.path.join(submission_dir, filename)
        file.save(submission_path)

        # Load grading guide
        if guide_json:
            try:
                        guide = json.loads(guide_json)
            except Exception:
                return jsonify({"error": "Invalid guide JSON"}), 400
        else:
            guide_path = os.path.join("guides", f"{test_id}.json")
            if os.path.exists(guide_path):
                with open(guide_path, "r") as gf:
                    guide = json.load(gf)
            else:
                return jsonify({"error": "No grading guide provided or found"}), 400

        # Mark the submission
        result = mark_submission(submission_path, guide)

        # Save feedback JSON and create dummy annotated PNG in marked/
        marked_dir = os.path.join("marked", test_id, student_id)
        os.makedirs(marked_dir, exist_ok=True)

        feedback_path = os.path.join(marked_dir, "feedback.json")
        with open(feedback_path, "w") as f:
            json.dump(result, f, indent=2)

        annotated_path = os.path.join(marked_dir, "annotated.png")
        if not os.path.exists(annotated_path):
            try:
                        from PIL import Image, ImageDraw
                img = Image.new("RGB", (400, 200), color=(255, 255, 255))
= ImageDraw.Draw(img)
                d.text((10, 80), f"Annotated Result for {student_id}", fill=(0, 0, 0))
                img.save(annotated_path)
            except ImportError:
                current_app.logger.warning("Pillow not installed; skipping annotated image creation.")

        # Return relative paths for feedback and annotated image
        feedback_url = f"/{feedback_path.replace(os.sep, '/')}"
        annotated_url = f"/{annotated_path.replace(os.sep, '/')}"

        current_app.logger.info(f"Graded submission for student {student_id} test {test_id}: {result['grade']}%")

        return jsonify({
            "grade": result["grade"],
            "feedback": result["feedback"],
            "ai_confidence": result["ai_confidence"],
            "question_scores": result["question_scores"],
            "feedback_json": feedback_url,
            "annotated_image": annotated_url
        }), 200

    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error during grading: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

