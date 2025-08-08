import os
import json

# Base directory
base_dir = "uploads"

# Directory structure to create
structure = {
    "answers": ["test_id_A.pdf", "test_id_B.pdf", "README.md"],
    "guides/test_id_A": ["guide.pdf"],
    "guides/test_id_B": ["guide.pdf"],
    "guides": ["README.md"],
    "rubrics": ["test_id_A.json", "test_id_B.json", "README.md"],
    "rubric_versions/test_id_A": ["v1.json", "v2.json"],
    "rubric_versions/test_id_B": ["v1.json"],
    "submissions/test_id_A/student_123": ["original.pdf", "page_1.png", "page_2.png"],
    "submissions/test_id_B/student_456": ["original.pdf", "page_1.png"],
    "submissions": ["README.md"],
    "marked/test_id_A/student_123": ["feedback.json", "annotated.png"],
    "marked/test_id_B/student_456": ["feedback.json", "annotated.png"],
    "audit_logs/test_id_A": ["audit_2025-07-16.json"],
    "audit_logs/test_id_B": ["audit_2025-07-15.json"],
    "bulk": ["upload_batch_1.zip", "upload_config.csv"],
    "": [
        "feedback_data.csv", "feedback_json.json", "marked_json.json",
        "marked_pdf.pdf", "mark_overrides.csv"
    ]
}

# Dummy content
def dummy_content(filename):
    if filename.endswith(".json"):
        return json.dumps({"mock": "data"}, indent=2)
    elif filename.endswith(".csv"):
        return "id,value\n1,sample"
    elif filename.endswith(".md"):
        return "# README\nThis is a placeholder."
    elif filename.endswith(".pdf"):
        return "%PDF-1.4\n%EOF"
    elif filename.endswith(".png"):
        return "PNGDATA"
    elif filename.endswith(".zip"):
        return "PKZIPDATA"
    else:
        return "This is a dummy file."

# Create the structure and write files
for folder, files in structure.items():
    path = os.path.join(base_dir, folder)
    os.makedirs(path, exist_ok=True)
    for filename in files:
        file_path = os.path.join(path, filename)
        content = dummy_content(filename)
        # Write binary content if needed
        if filename.endswith((".pdf", ".png", ".zip")):
            with open(file_path, "wb") as f:
                f.write(content.encode("latin1"))  # dummy binary data
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

print(f"✅ Mock uploads directory created at ./{base_dir}/")

