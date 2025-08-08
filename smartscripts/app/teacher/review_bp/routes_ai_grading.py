from flask import request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user

from smartscripts.models import Test
from smartscripts.utils.permissions import teacher_required

from . import review_bp  # ✅ Use the unified blueprint

def is_teacher_or_admin(test):
    return test.teacher_id == current_user.id or current_user.is_admin

@review_bp.route('/start_ai_grading/<int:test_id>', methods=['POST'])  # ✅ Unified route
@login_required
@teacher_required
def start_ai_grading(test_id: int):
    test = Test.query.get_or_404(test_id)
    if not is_teacher_or_admin(test):
        abort(403)

    try:
        # TODO: Replace with actual grading logic
        # ai_grading_service.grade_all(test_id)
        flash('✅ AI grading started successfully.', 'success')
    except Exception as e:
        current_app.logger.error(f"[AI_GRADING] Failed: {e}")
        flash('❌ Failed to start AI grading.', 'danger')

    return redirect(url_for('teacher_bp.review_test', test_id=test_id))
