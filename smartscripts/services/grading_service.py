import os
from typing import List, Dict, Optional

from smartscripts.models import TestSubmission, db  # adjust import based on your ORM setup


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
        # TODO: Replace this stub with actual AI grading logic.
        # For example, load file, run AI model, extract grade & feedback.
        grade = "A"  # dummy grade
        feedback = "Excellent work."  # dummy feedback

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
                submission.marked_file_path = self._generate_marked_file_path(submission)
                submission.status = "graded"
                db.session.add(submission)
                count += 1
            except Exception as e:
                print(f"[ERROR] Grading failed for submission {submission.id}: {e}")

        db.session.commit()
        return count

    def _generate_marked_file_path(self, submission: Submission) -> Optional[str]:
        """
        Generate or assign a marked file path for the submission.
        Stub function — customize based on your file storage system.

        Args:
            submission (Submission)

        Returns:
            Optional[str]: Path or URL to the marked file.
        """
        # TODO: Implement actual logic if you create/modify marked files.
        # Return None if no marked file is created.
        return None

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

