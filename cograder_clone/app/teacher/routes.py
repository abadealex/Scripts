from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user
from app.models import StudentSubmission, MarkingGuide
from sqlalchemy.orm import joinedload

teacher_bp = Blueprint('teacher_bp', __name__, template_folder='../templates')

# Role restriction
@teacher_bp.before_request
def require_teacher_role():
    if not current_user.is_authenticated or current_user.role != 'teacher':
        abort(403)

# Teacher Dashboard
@teacher_bp.route('/dashboard')
@login_required
def teacher_dashboard():
    # Fetch teacher's guides
    guides = MarkingGuide.query.filter_by(teacher_id=current_user.id).all()

    # Optional: Filter by guide_id (from dropdown)
    guide_filter = request.args.get("guide_id", type=int)

    # Prepare data: list of dicts with guide + its submissions
    guides_with_submissions = []
    for guide in guides:
        submissions_query = StudentSubmission.query.options(joinedload('student')).filter_by(guide_id=guide.id)
        if guide_filter and guide.id != guide_filter:
            continue
        submissions = submissions_query.order_by(StudentSubmission.timestamp.desc()).all()
        guides_with_submissions.append({
            "guide": guide,
            "submissions": submissions
        })

    return render_template(
        "teacher_dashboard.html",
        guides_with_submissions=guides_with_submissions,
        selected_guide=guide_filter
    )
