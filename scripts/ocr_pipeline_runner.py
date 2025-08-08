import logging
from pathlib import Path
from celery import shared_task

from smartscripts.ai import ocr_engine
from smartscripts.utils import pdf_helpers  # 🔁 Updated import (was: file_utils)

# Configure logging
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
    output_dir = submission_dir

    if not submission_dir.exists():
        error_msg = f"Submission directory not found: {submission_dir}"
        logging.error(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        return {'status': 'failed', 'reason': error_msg}

    pdf_path = submission_dir / "original.pdf"
    if not pdf_path.exists():
        error_msg = f"PDF not found: {pdf_path}"
        logging.error(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        return {'status': 'failed', 'reason': error_msg}

    # ✅ Step 1: Convert PDF to images + Detect front pages
    try:
                image_paths, front_page_ranges = pdf_helpers.convert_pdf_to_images(
            pdf_path=pdf_path,
            output_folder=output_dir,
            test_id=str(test_id),
            detect_front_pages=True
        )
        logging.info(f"Converted PDF to {len(image_paths)} images")
        logging.info(f"Detected front page ranges: {front_page_ranges}")
    except Exception as e:
        logging.error(f"PDF to image conversion failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {'status': 'failed', 'reason': str(e)}

    # Step 2: Run OCR on each image
    total_pages = len(image_paths)
    for idx, image_path in enumerate(image_paths, start=1):
        try:
                    ocr_result = ocr_engine.run_ocr(image_path)
            ocr_text_path = output_dir / f"page_{idx}.txt"
            ocr_text_path.write_text(ocr_result, encoding="utf-8")
            logging.info(f"OCR completed for page {idx}/{total_pages}")

            self.update_state(state='PROGRESS', meta={
                'current': idx,
                'total': total_pages,
                'progress': int((idx / total_pages) * 100)
            })
        except Exception as e:
            logging.error(f"OCR failed for {image_path.name}: {e}")
            # Optional: skip or fail depending on design

    logging.info(f"OCR pipeline completed successfully for {submission_dir.name}")
    return {
        'status': 'success',
        'message': 'OCR completed',
        'front_page_ranges': front_page_ranges
    }

