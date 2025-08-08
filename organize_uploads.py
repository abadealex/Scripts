import os
import shutil
from pathlib import Path

# Base uploads directory (change if needed)
BASE_DIR = Path(r"C:\Users\ALEX\Desktop\Smartscripts\uploads")

# Destination submissions directory
SUBMISSIONS_DIR = BASE_DIR / "submissions"

# List of subfolders inside each submission folder
SUBFOLDERS = ["original", "graded", "feedback", "comments", "overrides"]

def get_submission_id(filename):
    # Assumes submission ID is the first 32 chars of filename (like a hash)
    # e.g. "1eda813fa0a945e8bea8c376d8acf73c_original_anw.pdf"
    # Adjust this function if your submission ID format differs
    base_name = filename.name
    if len(base_name) >= 32:
        return base_name[:32]
    return None

def create_submission_dirs(submission_id):
    submission_path = SUBMISSIONS_DIR / submission_id
    for folder in SUBFOLDERS:
        (submission_path / folder).mkdir(parents=True, exist_ok=True)
    return submission_path

def classify_file(file_path):
    # Example heuristic based on filename or extension:
    name = file_path.name.lower()

    # Customize these rules as needed to route files to correct subfolder
    if "original" in name:
        return "original"
    elif "graded" in name or "marked" in name or "graded" in file_path.parent.name:
        return "graded"
    elif "feedback" in name or "annotated" in name:
        return "feedback"
    elif "comment" in name or file_path.suffix in ['.txt', '.json']:
        return "comments"
    elif "override" in name:
        return "overrides"
    else:
        # Default fallback
        return "original"

def main():
    # Make sure submissions dir exists
    SUBMISSIONS_DIR.mkdir(exist_ok=True)

    # Scan all files in BASE_DIR (skip subfolders submissions/, temp/ etc)
    for entry in BASE_DIR.iterdir():
        if entry.is_file():
            submission_id = get_submission_id(entry)
            if not submission_id:
                print(f"Skipping file with no valid submission ID: {entry.name}")
                continue

            # Create submission folder structure
            submission_path = create_submission_dirs(submission_id)

            # Decide which folder to put the file in
            target_subfolder = classify_file(entry)

            # Move file
            target_path = submission_path / target_subfolder / entry.name
            print(f"Moving {entry.name} -> {target_path}")
            shutil.move(str(entry), str(target_path))

if __name__ == "__main__":
    main()

