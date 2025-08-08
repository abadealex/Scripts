import os
import json
import cv2
from celery import shared_task
from flask import current_app, flash
from sqlalchemy.exc import SQLAlchemyError
from sentence_transformers import SentenceTransformer, util

from smartscripts.ai.ocr_engine import extract_text_from_image
from smartscripts.services.overlay_service import add_overlay
from smartscripts.utils.text_cleaner import clean_text
from smartscripts.models import StudentSubmission
from smartscripts.extensions import db

# Load embedding model once globally
model = SentenceTransformer("all-MiniLM-L6-v2")


def fetch_expected_text_from_guide(test_id: int) -> str:
    guide_path = os.path.join("uploads", "guides", str(test_id), "guide.txt")
    if os.path.isfile(guide_path):
        with open(guide_path, "r", encoding="utf-8") as f:
            return f.read()
    raise FileNotFoundError(f"Guide file not found for test_id={test_id} at {guide_path}")


def compute_similarity(text1: str, text2: str) -> float:
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    return util.pytorch_cos_sim(embedding1, embedding2).item()


def update_marked_submission(submission_id: int, score: float, feedback: str, marked_file_path: str):
    submission = StudentSubmission.query.get(submission_id)
    if not submission:
        raise ValueError(f"Submission ID {submission_id} not found.")

    submission.score = score
    submission.feedback = feedback
    submission.marked = True
    submission.file_path = marked_file_path
    submission.status = "graded"

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error: {e}")
        flash("A database error occurred.", "danger")

    # Save feedback JSON
    feedback_dir = os.path.join("uploads", "feedback", str(submission.test_id), str(submission.student_id))
    os.makedirs(feedback_dir, exist_ok=True)
    feedback_path = os.path.join(feedback_dir, "feedback.json")
    feedback_data = {
        "submission_id": submission.id,
        "score": score,
        "feedback": feedback,
        "marked_file": marked_file_path
    }
    with open(feedback_path, "w", encoding="utf-8") as f:
        json.dump(feedback_data, f, indent=2)

    print(f"? Submission {submission_id} updated with score={score:.2f} and feedback saved.")


def mark_submission(file_path: str, test_id: int, student_id: int, threshold: float = 0.75):
    try:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Input file '{file_path}' does not exist.")

        expected_text = fetch_expected_text_from_guide(test_id)
        if not expected_text or len(expected_text.strip()) < 10:
            raise ValueError("Expected text is invalid or too short.")

        raw_text = extract_text_from_image(file_path)
        if not raw_text or len(raw_text.strip()) < 20:
            raise ValueError("OCR text too short or failed.")

        student_text = clean_text(raw_text)
        if not student_text:
            raise ValueError("Text cleaning produced empty result.")

        similarity_score = compute_similarity(student_text, expected_text)
        is_correct = similarity_score >= threshold
        overlay_type = 'tick' if is_correct else 'cross'

        image = cv2.imread(file_path)
        if image is None:
            raise ValueError("Failed to load image for annotation.")

        annotated_image = add_overlay(image, overlay_type)
        if annotated_image is None:
            raise ValueError("Failed to generate annotated image.")

        marked_dir = os.path.join("uploads", "marked", str(test_id), str(student_id))
        os.makedirs(marked_dir, exist_ok=True)
        marked_filename = f"marked_{os.path.basename(file_path)}"
        marked_path = os.path.join(marked_dir, marked_filename)

        if not cv2.imwrite(marked_path, annotated_image):
            raise IOError(f"Failed to write annotated image to {marked_path}")

        submission = StudentSubmission.query.filter_by(student_id=student_id, test_id=test_id).first()
        if not submission:
            raise ValueError(f"No submission found for student_id={student_id}, test_id={test_id}.")

        update_marked_submission(
            submission_id=submission.id,
            score=round(similarity_score * 100, 2),
            feedback="Auto-marked based on answer similarity.",
            marked_file_path=marked_path
        )

        return {
            "student_id": student_id,
            "similarity_score": similarity_score,
            "student_text": student_text,
            "marked_path": marked_path
        }

    except Exception as e:
        error_message = f"? mark_submission failed for student_id={student_id}, test_id={test_id}: {str(e)}"
        print(error_message)
        if current_app:
            current_app.logger.error(error_message)
        raise


@shared_task
def mark_submission_async(submission_id):
    submission = StudentSubmission.query.get(submission_id)
    if not submission:
        print(f"Submission {submission_id} not found.")
        return

    print(f"Marking submission {submission.id} at {submission.file_path}...")

    try:
        result = mark_submission(
            file_path=submission.file_path,
            test_id=submission.test_id,
            student_id=submission.student_id
        )
        print(f"? Finished marking submission {submission_id} with score {result['similarity_score']:.2f}")
    except Exception as e:
        print(f"? Error marking submission {submission_id}: {e}")
        if current_app:
            current_app.logger.error(f"Async marking error: {e}")


def mark_batch_submissions(submissions: list):
    results = []
    for submission in submissions:
        try:
            result = mark_submission(
                file_path=submission.file_path,
                test_id=submission.test_id,
                student_id=submission.student_id
            )
            results.append(result)
        except Exception as e:
            error_msg = f"Batch marking error for submission {submission.id}: {e}"
            print(error_msg)
            if current_app:
                current_app.logger.error(error_msg)
    return results


def mark_all_for_test(test_id):
    submissions = StudentSubmission.query.filter_by(test_id=test_id, marked=False).all()
    if not submissions:
        print(f"?? No unmarked submissions found for test_id={test_id}")
        return

    print(f"?? Queuing {len(submissions)} submissions for batch marking (test_id={test_id})...")
    for submission in submissions:
        print(f"?? Queuing submission ID {submission.id} for student {submission.student_id}")
        mark_submission_async.delay(submission.id)


def mark_single_submission(submission):
    return mark_submission(
        file_path=submission.file_path,
        test_id=submission.test_id,
        student_id=submission.student_id
    )


def mark_all_submissions_in_folder(test_id: int):
    base_dir = os.path.join("uploads", "submissions", str(test_id))
    if not os.path.exists(base_dir):
        print(f"No submissions found for test {test_id}")
        return []

    results = []
    for student_id in os.listdir(base_dir):
        student_dir = os.path.join(base_dir, student_id)
        if os.path.isdir(student_dir):
            for filename in os.listdir(student_dir):
                file_path = os.path.join(student_dir, filename)
                try:
                    result = mark_submission(file_path, test_id, student_id)
                    results.append(result)
                except Exception as e:
                    print(f"Failed to mark submission {file_path}: {e}")
    return results
