# smartscripts/tasks/ocr_tasks.py

import logging
from pathlib import Path
from celery import shared_task

from smartscripts.ai import ocr_engine
from smartscripts.utils import file_utils

# Configure logging (optional, depends if Celery logs are captured)
logging.basicConfig(
    filename="logs/ocr_pipeline.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

@shared_task(bind=True)
def run_ocr_on_test(self, test_id, student_id):
    logging.info(f"Starting OCR pipeline for test: {test_id}, student: {student_id}")

    root_dir = Path("uploads/submissions")
    submission_dir = root_dir / str(test_id) / str(student_id)
    output_dir = submission_dir  # Save output here

    if not submission_dir.exists():
        error_msg = f"Submission directory not found: {submission_dir}"
        logging.error(error_msg)
        # Optionally: raise self.retry or self.update_state for failure
        self.update_state(state='FAILURE', meta={'error': error_msg})
        return {'status': 'failed', 'reason': error_msg}

    pdf_path = submission_dir / "original.pdf"
    if not pdf_path.exists():
        error_msg = f"PDF not found: {pdf_path}"
        logging.error(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        return {'status': 'failed', 'reason': error_msg}

    # Step 1: Convert PDF to images
    try:
        image_paths = file_utils.convert_pdf_to_images(pdf_path, output_dir)
        logging.info(f"Converted PDF to {len(image_paths)} images")
    except Exception as e:
        logging.error(f"PDF to image conversion failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {'status': 'failed', 'reason': str(e)}

    # Step 2: Run OCR on each image with progress update
    total_pages = len(image_paths)
    for idx, image_path in enumerate(image_paths, start=1):
        try:
            ocr_result = ocr_engine.run_ocr(image_path)
            ocr_text_path = output_dir / f"page_{idx}.txt"
            ocr_text_path.write_text(ocr_result, encoding="utf-8")
            logging.info(f"OCR completed for page {idx}/{total_pages}")

            # Update task state with progress info
            self.update_state(state='PROGRESS', meta={
                'current': idx,
                'total': total_pages,
                'progress': int((idx / total_pages) * 100)
            })
        except Exception as e:
            logging.error(f"OCR failed for {image_path.name}: {e}")
            # Continue or fail depending on your design; here continue

    logging.info(f"OCR pipeline completed successfully for {submission_dir.name}")
    return {'status': 'success', 'message': 'OCR completed'}
