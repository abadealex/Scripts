# app/teacher/analytics_dashboard.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.models import MarkingGuide, StudentSubmission, db
import io

teacher_bp = Blueprint('teacher_bp', __name__, url_prefix='/teacher')

@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Teacher dashboard showing uploaded marking guides and submissions,
    with optional filtering by guide.
    """
    selected_guide_id = request.args.get('guide_id', type=int)

    # Query guides uploaded by current teacher with submissions
    query = (
        db.session.query(MarkingGuide)
        .filter(MarkingGuide.teacher_id == current_user.id)
        .order_by(MarkingGuide.upload_date.desc())
    )

    if selected_guide_id:
        query = query.filter(MarkingGuide.id == selected_guide_id)

    guides = query.all()

    # For each guide, get related submissions
    guides_with_submissions = []
    for guide in guides:
        submissions = (
            StudentSubmission.query
            .filter_by(guide_id=guide.id)
            .order_by(StudentSubmission.submission_date.desc())
            .all()
        )
        guides_with_submissions.append({'guide': guide, 'submissions': submissions})

    return render_template(
        'teacher/analytics_dashboard.html',
        guides_with_submissions=guides_with_submissions,
        selected_guide=selected_guide_id,
    )

@teacher_bp.route('/start_ai_marking/<int:guide_id>', methods=['POST'])
@login_required
def start_ai_marking(guide_id):
    """
    Stub for starting AI marking on submissions of a guide.
    """
    # TODO: Implement AI marking logic here
    flash(f"AI marking started for guide ID {guide_id}", "info")
    return redirect(url_for('teacher_bp.dashboard', guide_id=guide_id))

@teacher_bp.route('/export_submissions/<int:guide_id>/<format>')
@login_required
def export_submissions(guide_id, format):
    """
    Export submissions of a guide in CSV or PDF format.
    """
    guide = MarkingGuide.query.filter_by(id=guide_id, teacher_id=current_user.id).first_or_404()
    submissions = StudentSubmission.query.filter_by(guide_id=guide_id).all()

    if format == 'csv':
        # Build CSV data
        import csv
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
        # Stub for PDF export
        flash("PDF export is not implemented yet.", "warning")
        return redirect(url_for('teacher_bp.dashboard', guide_id=guide_id))
    else:
        flash("Unsupported export format.", "danger")
        return redirect(url_for('teacher_bp.dashboard', guide_id=guide_id))

@teacher_bp.route('/review/<int:submission_id>')
@login_required
def review(submission_id):
    """
    Stub route for manual review page of a submission.
    """
    submission = StudentSubmission.query.get_or_404(submission_id)
    # TODO: Add review form and logic here

    flash(f"Manual review page for submission ID {submission_id} (not implemented)", "info")
    return redirect(url_for('teacher_bp.dashboard', guide_id=submission.guide_id))
