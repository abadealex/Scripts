from fastapi import APIRouter
from typing import List, Dict
from smartscripts.teacher.fairness_audit import generate_bias_report

router = APIRouter()

@router.get("/audit/bias_report")
async def get_bias_report(batch_id: str):
    report = generate_bias_report(batch_id=batch_id)
    return report

