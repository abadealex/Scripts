import os
from typing import List, Dict, Optional

from smartscripts.models import Submission, db  # adjust import based on your ORM setup

GUIDE_DIR = "uploads/guides"
RUBRIC_DIR = "uploads/rubrics"
SUBMISSION_DIR = "uploads/submissions"
MARKED_DIR = "uploads/marked"


class GradingService:
    """
    Service class to coordinate batch grading of submissions.
    """

    def __init__(self):
        pass

    def get_submissions_by_batch(self, batch_name: str) -> List[Submission]:
        """
        Retrieve all submissions that belong to a given batch.

        Args:
            batch_name (str): The batch identifier.

        Returns:
            List[Submission]: List of submission objects in the batch.
        """
        return Submission.query.filter(Submission.batch_name == batch_name).all()

    def run_ai_marking(self, submission: Submission) -> Dict[str, Optional[str]]:
        """
        Perform AI marking on a single submission.
        Stub method — replace with actual AI grading logic.

        Args:
            submission (Submission): Submission instance to grade.

        Returns:
            Dict[str, Optional[str]]: Dict containing 'grade' and 'feedback'.
        """
        test_id = submission.test_id
        student_id = submission.student_id

        # Paths
        submission_path = os.path.join(SUBMISSION_DIR, str(test_id), str(student_id), os.path.basename(submission.file_path))
        guide_dir = os.path.join(GUIDE_DIR, str(test_id))
        rubric_path = os.path.join(RUBRIC_DIR, f"{test_id}.json")
        marked_dir = os.path.join(MARKED_DIR, str(test_id), str(student_id))
        os.makedirs(marked_dir, exist_ok=True)
        marked_file_path = os.path.join(marked_dir, os.path.basename(submission.file_path))

        # Dummy grading logic - replace with actual
        grade = "A"  # dummy grade
        feedback = "Excellent work."  # dummy feedback

        # Simulate writing annotated output
        with open(marked_file_path, 'w') as f:
            f.write("Annotated feedback overlay placeholder")

        submission.marked_file_path = marked_file_path

        return {"grade": grade, "feedback": feedback}

    def grade_batch(self, batch_name: str) -> int:
        """
        Process grading for all submissions in the batch.

        Args:
            batch_name (str): The batch identifier.

        Returns:
            int: Number of submissions graded successfully.
        """
        submissions = self.get_submissions_by_batch(batch_name)
        count = 0

        for submission in submissions:
            try:
                result = self.run_ai_marking(submission)
                submission.grade = result.get("grade")
                submission.feedback = result.get("feedback")
                submission.status = "graded"
                db.session.add(submission)
                count += 1
            except Exception as e:
                print(f"[ERROR] Grading failed for submission {submission.id}: {e}")

        db.session.commit()
        return count

    def _generate_marked_file_path(self, submission: Submission) -> Optional[str]:
        """
        Deprecated in favor of logic in run_ai_marking().
        """
        return submission.marked_file_path

    def trigger_manual_review(self, submission_id: int):
        """
        Mark a submission for manual review.

        Args:
            submission_id (int)
        """
        submission = Submission.query.get(submission_id)
        if submission:
            submission.status = "manual_review"
            db.session.add(submission)
            db.session.commit()
