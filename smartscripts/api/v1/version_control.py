from fastapi import APIRouter, HTTPException
from smartscripts.api.v1.version_control import rollback_to_version, get_version_logs
from typing import List, Dict

router = APIRouter()

@router.get("/version_control/logs")
async def get_logs():
    logs = get_version_logs()
    return logs

@router.post("/version_control/rollback")
async def rollback(version_hash: str):
    success = rollback_to_version(version_hash)
    if not success:
        raise HTTPException(status_code=400, detail="Rollback failed")
    return {"status": "rollback successful"}

