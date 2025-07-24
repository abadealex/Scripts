from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from smartscripts.teacher.rubric_manager import (
    create_rubric,
    update_rubric,
    get_rubric,
    delete_rubric
)

router = APIRouter()

class RubricItem(BaseModel):
    criteria: str
    max_score: int
    description: Optional[str]

class Rubric(BaseModel):
    rubric_id: Optional[str]
    title: str
    items: List[RubricItem]

@router.post("/rubrics")
async def create_new_rubric(rubric: Rubric):
    rubric_id = create_rubric(rubric)
    return {"rubric_id": rubric_id}

@router.get("/rubrics/{rubric_id}", response_model=Rubric)
async def read_rubric(rubric_id: str):
    rubric = get_rubric(rubric_id)
    if not rubric:
        raise HTTPException(status_code=404, detail="Rubric not found")
    return rubric

@router.put("/rubrics/{rubric_id}")
async def update_existing_rubric(rubric_id: str, rubric: Rubric):
    success = update_rubric(rubric_id, rubric)
    if not success:
        raise HTTPException(status_code=404, detail="Rubric not found")
    return {"status": "updated"}

@router.delete("/rubrics/{rubric_id}")
async def delete_existing_rubric(rubric_id: str):
    success = delete_rubric(rubric_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rubric not found")
    return {"status": "deleted"}
