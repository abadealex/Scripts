import re
from typing import List, Optional
from flask import url_for, current_app
from flask_login import current_user

from smartscripts.extensions import db
from smartscripts.models import Test, MarkingGuide, OCRSubmission, AuditLog
from smartscripts.ai.ocr_engine import detect_keywords_with_positions, extract_text_lines_from_image

AUDIT_FIELD_OCR_NAME = "OCR_NAME"
AUDIT_FIELD_OCR_ID = "OCR_ID"


def file_url(filename: Optional[str]) -> Optional[str]:
    return url_for('file_routes_bp.uploaded_file', filename=filename) if filename else None


def is_teacher_or_admin(test: Test) -> bool:
    return test.teacher_id == current_user.id or current_user.is_admin


def get_urls_for_guide(guide: Optional[MarkingGuide]) -> dict:
    return {
        "guide": file_url(guide.filename) if guide else None,
        "rubric": file_url(guide.rubric_filename) if guide else None,
        "answered": file_url(guide.answered_script_filename) if guide else None,
    }


def get_highlighted_lines(image_path: str) -> List[str]:
    try:
        lines = extract_text_lines_from_image(image_path)
        matches = detect_keywords_with_positions(lines)
        highlighted = []
        for i, line in enumerate(lines):
            for match in matches:
                if match['line'] == i:
                    keyword = re.escape(match['keyword'])
                    line = re.sub(rf"({keyword})", r"<mark>\1</mark>", line, flags=re.IGNORECASE)
            highlighted.append(line)
        return highlighted
    except Exception as e:
        current_app.logger.warning(f"[get_highlighted_lines] Failed: {e}")
        return []


def apply_ocr_override(sub: OCRSubmission, name: str, stud_id: str) -> bool:
    changed = False
    if name and name != sub.corrected_name:
        db.session.add(AuditLog(
            submission_id=sub.id, user_id=current_user.id,
            question_id=AUDIT_FIELD_OCR_NAME,
            action=f"Corrected name from '{sub.corrected_name}' to '{name}'"
        ))
        sub.corrected_name = name
        changed = True

    if stud_id and stud_id != sub.corrected_id:
        db.session.add(AuditLog(
            submission_id=sub.id, user_id=current_user.id,
            question_id=AUDIT_FIELD_OCR_ID,
            action=f"Corrected ID from '{sub.corrected_id}' to '{stud_id}'"
        ))
        sub.corrected_id = stud_id
        changed = True

    if changed:
        sub.manual_override = True
        sub.reviewed_by = current_user.id
    return changed
