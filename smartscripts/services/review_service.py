import json
import os
from typing import Optional, Dict

# File to store manual review overrides (could be replaced with DB)
OVERRIDES_FILE = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'reviews.json')

def load_overrides() -> Dict:
    """
    Load manual review overrides from JSON file.
    Returns an empty dict if file doesn't exist.
    """
    if not os.path.exists(OVERRIDES_FILE):
        return {}
    with open(OVERRIDES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_overrides(overrides: Dict):
    """
    Save manual review overrides to JSON file.
    """
    with open(OVERRIDES_FILE, 'w', encoding='utf-8') as f:
        json.dump(overrides, f, indent=4)

def get_override(student_id: str, question_id: str) -> Optional[bool]:
    """
    Retrieve override status for a specific student's question.
    Returns True/False if overridden, None if no override found.
    """
    overrides = load_overrides()
    return overrides.get(student_id, {}).get(question_id)

def set_override(student_id: str, question_id: str, is_correct: bool):
    """
    Save or update override for a student's answer on a question.
    """
    overrides = load_overrides()
    if student_id not in overrides:
        overrides[student_id] = {}
    overrides[student_id][question_id] = is_correct
    save_overrides(overrides)
