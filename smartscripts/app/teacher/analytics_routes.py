from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from smartscripts.utils.file_ops import duplicate_manifest_for_reference, update_manifest
from smartscripts.models import MarkingGuide, StudentSubmission  # only models here
from smartscripts.extensions import db  # db from extensions, NOT models
import io
import csv


analytics_bp = Blueprint('analytics_bp', __name__, url_prefix='/teacher/analytics')

@analytics_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Teacher analytics dashboard showing uploaded marking guides and related submissions,
    with optional filtering by guide.
    """
    selected_guide_id = request.args.get('guide_id', type=int)

    guides = (
        db.session.query(MarkingGuide)
        .filter(MarkingGuide.teacher_id == current_user.id)
        .order_by(MarkingGuide.upload_date.desc())
    )
    if selected_guide_id:
        guides = guides.filter(MarkingGuide.id == selected_guide_id)

    guides = guides.all()
    guides_with_submissions = []
    for guide in guides:
        submissions = (
            StudentSubmission.query
            .filter_by(guide_id=guide.id)
            .order_by(StudentSubmission.submission_date.desc())
            .all()
        )
        guides_with_submissions.append({
            'guide': guide,
            'submissions': submissions
        })

    return render_template(
        'teacher/analytics_dashboard.html',
        guides_with_submissions=guides_with_submissions,
        selected_guide=selected_guide_id,
    )

@analytics_bp.route('/start_ai_marking/<int:guide_id>', methods=['POST'])
@login_required
def start_ai_marking(guide_id):
    """
    Placeholder for starting AI marking.
    """
    # TODO: Trigger AI marking pipeline
    flash(f"AI marking started for guide ID {guide_id}.", "info")
    return redirect(url_for('analytics_bp.dashboard', guide_id=guide_id))

@analytics_bp.route('/export_submissions/<int:guide_id>/<format>')
@login_required
def export_submissions(guide_id, format):
    """
    Export guide submissions in CSV or PDF format.
    """
    guide = MarkingGuide.query.filter_by(id=guide_id, teacher_id=current_user.id).first_or_404()
    submissions = StudentSubmission.query.filter_by(guide_id=guide_id).all()

    if format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Student Email', 'Filename', 'Grade', 'Status', 'Feedback'])
        for sub in submissions:
            writer.writerow([
                sub.student.email if sub.student else '',
                sub.filename,
                sub.grade or 'Pending',
                sub.review_status or 'Pending',
                sub.feedback or ''
            ])
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"{guide.title}_submissions.csv"
        )
    elif format == 'pdf':
        flash("PDF export is not implemented yet.", "warning")
        return redirect(url_for('analytics_bp.dashboard', guide_id=guide_id))
    else:
        flash("Unsupported export format.", "danger")
        return redirect(url_for('analytics_bp.dashboard', guide_id=guide_id))

@analytics_bp.route('/review/<int:submission_id>')
@login_required
def review(submission_id):
    """
    Manual review page for a submission (stub).
    """
    submission = StudentSubmission.query.get_or_404(submission_id)
    flash(f"Manual review page for submission ID {submission_id} (not implemented yet)", "info")
    return redirect(url_for('analytics_bp.dashboard', guide_id=submission.guide_id))
