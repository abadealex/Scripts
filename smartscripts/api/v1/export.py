from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import csv
import json
from tempfile import NamedTemporaryFile

router = APIRouter()

EXPORT_BASE_DIR = "uploads/final_exports"

def get_export_path(test_id: str, export_type: str):
    """
    Constructs the export file path based on test_id and type.
    Supports csv, json, and pdf (assuming pre-generated).
    """
    test_dir = os.path.join(EXPORT_BASE_DIR, test_id)
    if not os.path.exists(test_dir):
        raise FileNotFoundError("Test export directory not found.")

    if export_type == "csv":
        file_path = os.path.join(test_dir, "final_marksheet.csv")
    elif export_type == "json":
        file_path = os.path.join(test_dir, "final_feedback.json")
    elif export_type == "pdf":
        file_path = os.path.join(test_dir, "final_marked.pdf")
    else:
        raise ValueError("Unsupported export type.")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Export file {file_path} does not exist.")
    
    return file_path


@router.get("/export/{test_id}/{export_type}")
async def download_export(test_id: str, export_type: str):
    """
    Endpoint to download an export file for a given test and export type.
    export_type: csv, json, or pdf
    """
    try:
                file_path = get_export_path(test_id, export_type)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return FileResponse(path=file_path, filename=os.path.basename(file_path), media_type="application/octet-stream")


@router.get("/export/{test_id}/summary")
async def export_summary(test_id: str):
    """
    Generates a simple summary JSON export on the fly for a given test_id.
    This can be extended to aggregate scores, average grades, etc.
    """
    test_dir = os.path.join(EXPORT_BASE_DIR, test_id)
    feedback_file = os.path.join(test_dir, "final_feedback.json")
    if not os.path.isfile(feedback_file):
        raise HTTPException(status_code=404, detail="Summary feedback file not found.")
    
    with open(feedback_file, "r") as f:
        feedback_data = json.load(f)
    
    # Example: summarize total average grade (you can customize)
    avg_grade = None
    if isinstance(feedback_data, list) and feedback_data:
        avg_grade = sum(item.get("grade", 0) for item in feedback_data) / len(feedback_data)
    elif isinstance(feedback_data, dict) and "grade" in feedback_data:
        avg_grade = feedback_data["grade"]

    summary = {
        "test_id": test_id,
        "average_grade": avg_grade,
        "num_submissions": len(feedback_data) if isinstance(feedback_data, list) else 1,
    }
    return summary

