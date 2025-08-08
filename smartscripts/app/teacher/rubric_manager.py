import uuid
from typing import List, Dict, Optional
from smartscripts.utils.file_ops import duplicate_manifest_for_reference
from smartscripts.utils.file_ops import update_manifest

# In-memory storage simulating database for rubrics
rubrics_db = {}

class RubricItem:
    def __init__(self, criteria: str, max_score: int, description: Optional[str] = None):
        self.criteria = criteria
        self.max_score = max_score
        self.description = description

class Rubric:
    def __init__(self, title: str, items: List[RubricItem], rubric_id: Optional[str] = None):
        self.title = title
        self.items = items
        self.rubric_id = rubric_id or str(uuid.uuid4())

def create_rubric(rubric_data: Dict) -> str:
    items = [RubricItem(**item) for item in rubric_data["items"]]
    rubric = Rubric(title=rubric_data["title"], items=items)
    rubrics_db[rubric.rubric_id] = rubric
    return rubric.rubric_id

def update_rubric(rubric_id: str, rubric_data: Dict) -> bool:
    if rubric_id not in rubrics_db:
        return False
    items = [RubricItem(**item) for item in rubric_data["items"]]
    rubric = Rubric(title=rubric_data["title"], items=items, rubric_id=rubric_id)
    rubrics_db[rubric_id] = rubric
    return True

def get_rubric(rubric_id: str) -> Optional[Dict]:
    rubric = rubrics_db.get(rubric_id)
    if not rubric:
        return None
    return {
        "rubric_id": rubric.rubric_id,
        "title": rubric.title,
        "items": [{"criteria": i.criteria, "max_score": i.max_score, "description": i.description} for i in rubric.items]
    }

def delete_rubric(rubric_id: str) -> bool:
    if rubric_id in rubrics_db:
        del rubrics_db[rubric_id]
        return True
    return False

