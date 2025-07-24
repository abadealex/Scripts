import os
import zipfile
import re
from werkzeug.utils import secure_filename
from smartscripts.extensions import db
from smartscripts.models import TestSubmission  # Assuming this is the submission model
from smartscripts.ai.marking_pipeline import mark_submission_async, mark_all_for_test

# Define base upload directories (adjust path if needed)
BASE_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

# Key directories according to new structure
ANSWER_DIR = os.path.join(BASE_UPLOAD_DIR, "answers")       # Teacher-provided answer scripts
GUIDE_DIR = os.path.join(BASE_UPLOAD_DIR, "guides")
RUBRIC_DIR = os.path.join(BASE_UPLOAD_DIR, "rubrics")
SUBMISSIONS_DIR = os.path.join(BASE_UPLOAD_DIR, "submissions")  # Student scripts extracted here

# Ensure key directories exist
for d in (ANSWER_DIR, GUIDE_DIR, RUBRIC_DIR, SUBMISSIONS_DIR):
    os.makedirs(d, exist_ok=True)

def determine_destination(filename, test_id):
    """
    Determines where to save a file based on filename and test_id.
    Teacher uploads for:
    - rubrics -> rubrics/test_id/
    - guides  -> guides/test_id/
    - answers -> answers/test_id/
    - submissions (bulk student scripts) -> submissions/test_id/student_id/
    """
    lower_fn = filename.lower()

    if "rubric" in lower_fn:
        dest = os.path.join(RUBRIC_DIR, test_id)
    elif "guide" in lower_fn:
        dest = os.path.join(GUIDE_DIR, test_id)
    elif re.match(r"student_", lower_fn):
        # This is a student submission file: extract student_id and save under submissions
        match = re.match(r"student_([\w\-]+)_.*", filename, re.IGNORECASE)
        if not match:
            raise ValueError(f"Invalid student submission filename format: {filename}")
        student_id = match.group(1)
        dest = os.path.join(SUBMISSIONS_DIR, test_id, f"student_{student_id}")
    else:
        # Default to answers directory if unsure
        dest = os.path.join(ANSWER_DIR, test_id)

    os.makedirs(dest, exist_ok=True)
    return dest

def all_required_components_exist(test_id):
    """
    Checks if guide, rubric, and at least one student submission exist for test_id
    """
    guide_files = os.listdir(os.path.join(GUIDE_DIR, test_id)) if os.path.exists(os.path.join(GUIDE_DIR, test_id)) else []
    rubric_files = os.listdir(os.path.join(RUBRIC_DIR, test_id)) if os.path.exists(os.path.join(RUBRIC_DIR, test_id)) else []

    has_guide = any(f.lower().endswith(".pdf") and "guide" in f.lower() for f in guide_files)
    has_rubric = any(f.lower().endswith(".pdf") and "rubric" in f.lower() for f in rubric_files)

    # Check submissions table for any submissions for this test
    any_submission = TestSubmission.query.filter_by(test_id=test_id).first() is not None

    return has_guide and has_rubric and any_submission

def save_submission(file_storage, test_id):
    """
    Save a single file upload (from teacher) into correct folder,
    and if it's a student script, create a TestSubmission record and trigger async marking.
    """
    filename = secure_filename(file_storage.filename)
    destination_dir = determine_destination(filename, test_id)
    filepath = os.path.join(destination_dir, filename)

    file_storage.save(filepath)
    print(f"📁 Saved file: {filepath}")

    # If this is a student submission file, add DB record & trigger marking
    if destination_dir.startswith(SUBMISSIONS_DIR):
        match = re.match(r"student_([\w\-]+)_", filename, re.IGNORECASE)
        if not match:
            print(f"⚠️ Warning: could not parse student_id from filename {filename}, skipping DB record.")
            return

        student_id = match.group(1)

        submission = TestSubmission(
            test_id=test_id,
            student_id=student_id,
            file_path=filepath,
            marked=False
        )
        db.session.add(submission)
        db.session.commit()
        print(f"✅ Saved submission DB record for student {student_id}")

        # Trigger async marking
        mark_submission_async.delay(submission.id)

def process_bulk_teacher_upload(zip_filepath, test_id):
    """
    This function takes a zip file path uploaded by teacher containing
    multiple student submission scripts + optional rubric/guide/answers,
    extracts files, saves appropriately, creates DB records for student submissions,
    and triggers batch marking if ready.
    """
    if not zipfile.is_zipfile(zip_filepath):
        raise ValueError(f"File {zip_filepath} is not a valid zip archive.")

    extract_dir = os.path.splitext(zip_filepath)[0]  # Extract folder based on zip filename
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"📦 Extracted ZIP: {zip_filepath} → {extract_dir}")

    # Walk extracted folder and save files
    for root, _, files in os.walk(extract_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'rb') as f:
                    class FileWrapper:
                        def __init__(self, filename, fileobj):
                            self.filename = filename
                            self.file = fileobj
                        def save(self, dst):
                            with open(dst, 'wb') as out_f:
                                out_f.write(self.file.read())

                    file_wrapper = FileWrapper(fname, f)
                    save_submission(file_wrapper, test_id)
            except Exception as e:
                print(f"⚠️ Error processing {fname}: {e}")

    # After saving all files, if all components exist, trigger full batch marking
    if all_required_components_exist(test_id):
        print(f"🚀 All required components present for test {test_id}. Triggering batch marking.")
        mark_all_for_test(test_id)
    else:
        print(f"ℹ️ Waiting for all components (guide, rubric, submissions) for test {test_id} before batch marking.")

