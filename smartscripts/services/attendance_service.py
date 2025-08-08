import csv
from pathlib import Path
from typing import List, Dict, Tuple

def generate_presence_csv(
    test_id: str,
    class_list: List[Dict[str, str]],
    detected_ids: List[str],
    output_dir: str
) -> str:
    """
    Generate a presence CSV report based on OCR-detected student IDs.
    
    Args:
        test_id: ID of the test.
        class_list: List of dicts with keys 'student_id' (and optionally 'name').
        detected_ids: List of OCR-detected student IDs (exact or fuzzy matched).
        output_dir: Directory where CSV will be saved.

    Returns:
        Path to saved CSV file.
    """
    os.makedirs(output_dir, exist_ok=True)
    present_ids = set(detected_ids)
    presence_data = []

    for student in class_list:
        student_id = student.get("student_id")
        name = student.get("name", "")
        status = "Present" if student_id in present_ids else "Absent"
        presence_data.append({
            "student_id": student_id,
            "name": name,
            "status": status
        })

    output_path = Path(output_dir) / f"presence_table_{test_id}.csv"
    with open(output_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["student_id", "name", "status"])
        writer.writeheader()
        writer.writerows(presence_data)

    print(f"🧾 Presence table saved to: {output_path}")
    return str(output_path)

