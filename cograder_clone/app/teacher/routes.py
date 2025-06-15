from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from cograder_clone import db  # ✅ Use absolute import
from cograder_clone.app.models import StudentSubmission, MarkingGuide  # ✅ Full path import

teacher_bp = Blueprint('teacher_bp', __name__)  # ✅ Global template directory is used

# Restrict access to teachers only
@teacher_bp.before_request
def require_teacher_role():
    if not current_user.is_authenticated or current_user.role != 'teacher':
        abort(403)

# Teacher dashboard route
@teacher_bp.route('/dashboard')
@login_required
def teacher_dashboard():
    # Get all guides created by this teacher
    guides = MarkingGuide.query.filter_by(teacher_id=current_user.id).all()

    # Optional filter for selected guide
    guide_filter = request.args.get("guide_id", type=int)

    guides_with_submissions = []
    for guide in guides:
        if guide_filter and guide.id != guide_filter:
            continue
        # Load submissions for each guide with student data
        submissions = (
            StudentSubmission.query
            .options(joinedload(StudentSubmission.student))
            .filter_by(guide_id=guide.id)
            .order_by(StudentSubmission.timestamp.desc())
            .all()
        )
        guides_with_submissions.append({
            "guide": guide,
            "submissions": submissions
        })

    return render_template(
        "teacher_dashboard.html",
        guides_with_submissions=guides_with_submissions,
        selected_guide=guide_filter
    )
