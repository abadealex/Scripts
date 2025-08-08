import os
import csv
import argparse
from smartscripts.app import create_app  # ✅ Add this to use app context
from smartscripts.ai.text_matching import match_ocr_ids_to_class
from smartscripts.services.bulk_upload_service import store_attendance_records

def load_class_list(csv_path: str):
    class_list = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            class_list.append({
                "student_id": row.get("student_id", "").strip(),
                "name": row.get("name", "").strip()
            })
    return class_list

def load_extracted_ids(txt_path: str):
    with open(txt_path, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def main():
    parser = argparse.ArgumentParser(description="Manual attendance generator from OCR IDs.")
    parser.add_argument("--test-id", required=True, help="Test ID to associate records with")
    parser.add_argument("--class-list", required=True, help="Path to class list CSV (with 'student_id' and 'name' columns)")
    parser.add_argument("--ocr-ids", required=True, help="Path to TXT file containing OCR'd student IDs (one per line)")
    
    args = parser.parse_args()

    class_list = load_class_list(args.class_list)
    extracted_ids = load_extracted_ids(args.ocr_ids)

    matched_ids, unmatched_ids = match_ocr_ids_to_class(extracted_ids, class_list)

    print(f"\n✅ Matched: {len(matched_ids)} IDs")
    print(f"❌ Unmatched: {len(unmatched_ids)} IDs\n")

    if unmatched_ids:
        print("❌ Unmatched OCR IDs:")
        for uid in unmatched_ids:
            print(f" - {uid}")

    store_attendance_records(test_id=args.test_id, class_list=class_list, matched_ids=set(matched_ids))

    print(f"\n📋 Attendance records saved for test: {args.test_id}")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():  # ✅ Ensure db.session and Flask features work
        main()

