import time
import traceback
from flask import current_app
from rq import Retry
from smartscripts.ai.marking_pipeline import mark_submission

def async_mark_submission(file_path: str, guide_id: int, student_id: int, test_id: int, threshold: float = 0.75):
    """
    Wrapper function to call mark_submission asynchronously with retries.
    This function is queued by an RQ worker.
    """
    try:
        result = mark_submission(file_path, guide_id, student_id, test_id, threshold)
        current_app.logger.info(f"✅ Successfully marked submission {student_id} for test {test_id}")
        return result
    except Exception as e:
        current_app.logger.error(
            f"❌ Grading failed for student {student_id}, test {test_id}: {str(e)}\n{traceback.format_exc()}"
        )
        raise  # Raise to let RQ retry if configured

# When enqueueing this task, you can specify retries like:
# queue.enqueue(async_mark_submission, file_path, guide_id, student_id, test_id, retry=Retry(max=3, interval=[10, 30, 60]))
