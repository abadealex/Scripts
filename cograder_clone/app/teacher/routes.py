import os
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    current_app, abort
)
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from cograder_clone.app import db
from cograder_clone.app.models import StudentSubmission, MarkingGuide
from cograder_clone.utils.compress_image import compress_image

teacher_bp = Blueprint('teacher_bp', __name__)

# Restrict access to teachers only
@teacher_bp.before_request
def require_teacher_role():
    if not current_user.is_authenticated or current_user.role != 'teacher':
        abort(403)

# Teacher dashboard
@teacher_bp.route('/dashboard')
@login_required
def teacher_dashboard():
    guides = MarkingGuide.query.filter_by(teacher_id=current_user.id).all()
    guide_filter = request.args.get("guide_id", type=int)

    guides_with_submissions = []
    for guide in guides:
        if guide_filter and guide.id != guide_filter:
            continue
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

# Upload new marking guide (PDF/Image)
@teacher_bp.route('/upload-guide', methods=['GET', 'POST'])
@login_required
def upload_guide():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename.strip() == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        upload_dir = current_app.config['UPLOAD_FOLDER_GUIDES']
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # Compress large images
        if file_path.lower().endswith(('.jpg', '.jpeg', '.png')) and os.path.getsize(file_path) > 4 * 1024 * 1024:
            compressed_path = os.path.join(upload_dir, f"compressed_{filename}")
            compress_image(file_path, compressed_path)
            os.remove(file_path)
            file_path = compressed_path

        flash('Marking guide uploaded successfully.', 'success')
        return redirect(url_for('teacher_bp.upload_guide'))

    return render_template('teacher/upload.html')
