from flask import Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from smartscripts.extensions import db
from smartscripts.models import Test, MarkingGuide
from smartscripts.utils.permissions import teacher_required

file_routes_bp = Blueprint('file_routes_bp', __name__, url_prefix='/teacher')

def is_teacher_or_admin(test):
    return test.teacher_id == current_user.id or current_user.is_admin

@file_routes_bp.route('/delete_file/<int:test_id>/<string:file_type>', methods=['POST'])
@login_required
@teacher_required
def delete_uploaded_file(test_id: int, file_type: str):
    test = Test.query.get_or_404(test_id)
    if not is_teacher_or_admin(test):
        abort(403)

    guide = MarkingGuide.query.filter_by(test_id=test.id).first()
    if not guide:
        flash('âŒ No marking guide found.', 'danger')
        return redirect(url_for('teacher_bp.review_bp.review_test', test_id=test_id))  # Corrected blueprint

    if file_type == 'guide':
        guide.filename = None
    elif file_type == 'rubric':
        guide.rubric_filename = None
    elif file_type == 'answered':
        guide.answered_script_filename = None
    else:
        flash('âŒ Invalid file type.', 'danger')
        return redirect(url_for('teacher_bp.review_bp.review_test', test_id=test_id))  # Corrected blueprint

    try:
        db.session.commit()
        flash(f'âœ… {file_type.capitalize()} file deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'âŒ Error deleting file: {str(e)}', 'danger')

    return redirect(url_for('teacher_bp.review_bp.review_test', test_id=test_id))  # Corrected blueprint

