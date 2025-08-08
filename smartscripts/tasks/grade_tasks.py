import time
import traceback
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from rq import Retry
from smartscripts.ai.marking_pipeline import mark_submission
from smartscripts.extensions import celery
from smartscripts.celery_app import celery


def async_mark_submission(file_path: str, guide_id: int, student_id: int, test_id: int, threshold: float = 0.75):
    """
    Wrapper function to call mark_submission asynchronously with retries.
    This function is queued by an RQ worker.
    """
    try:
        result = mark_submission(file_path, guide_id, student_id, test_id, threshold)
        current_app.logger.info(f"? Successfully marked submission {student_id} for test {test_id}")
        return result
    except Exception as e:
        current_app.logger.error(
            f"? Grading failed for student {student_id}, test {test_id}: {str(e)}\n{traceback.format_exc()}"
        )
        raise  # Raise to let RQ retry if configured


# When enqueueing this task, you can specify retries like:
# queue.enqueue(async_mark_submission, file_path, guide_id, student_id, test_id, retry=Retry(max=3, interval=[10, 30, 60]))


@celery.task(bind=True)
def async_grade_all_students(self, test_id):
    from smartscripts.services.grading_service import grade_student_script
    from smartscripts.models import Test

    test = Test.query.get(test_id)
    for script in test.student_scripts:
        try:
            grade_student_script(script)
        except Exception as e:
            self.retry(exc=e, countdown=5)
