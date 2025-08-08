import os
import csv
import shutil
from datetime import datetime

def duplicate_manifest_for_reference(test_id, upload_root):
    src = os.path.join(upload_root, 'manifests', str(test_id), 'manifest.csv')
    dest_dir = os.path.join(upload_root, 'submissions', str(test_id))
    dest = os.path.join(dest_dir, 'manifest.csv')

    if not os.path.exists(src):
        raise FileNotFoundError(f"Manifest not found at: {src}")

    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"📄 Manifest duplicated to: {dest}")


def update_manifest(test_id, student_id, pages_uploaded, upload_root):
    manifest_dir = os.path.join(upload_root, 'manifests', str(test_id))
    os.makedirs(manifest_dir, exist_ok=True)

    manifest_path = os.path.join(manifest_dir, 'manifest.csv')
    rows = []
    found = False

    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['student_id'] == str(student_id):
                    row['pages_uploaded'] = str(pages_uploaded)
                    row['timestamp'] = datetime.utcnow().isoformat()
                    found = True
                rows.append(row)

    if not found:
        rows.append({
            'student_id': str(student_id),
            'pages_uploaded': str(pages_uploaded),
            'timestamp': datetime.utcnow().isoformat()
        })

    with open(manifest_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['student_id', 'pages_uploaded', 'timestamp'])
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Manifest updated: {manifest_path}")

