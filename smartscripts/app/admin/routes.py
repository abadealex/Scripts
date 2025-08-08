from flask import Blueprint, render_template
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required
from smartscripts.models import OCRSubmission
# from smartscripts.utils.permissions import admin_required  # TEMP: commented out

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

@admin_bp.route('/corrected_submissions')
@login_required  # ✅ TEMP: login_required only to unblock migration
def corrected_submissions():
    corrected = OCRSubmission.query.filter(
        (OCRSubmission.corrected_name.isnot(None)) |
        (OCRSubmission.corrected_id.isnot(None))
    ).all()
    return render_template('admin/corrected_submissions.html', submissions=corrected)

