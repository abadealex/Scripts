import os
import uuid
import traceback
from pathlib import Path
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app, abort, jsonify
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import cv2

from smartscripts.extensions import db
from smartscripts.app.forms import StudentUploadForm
from smartscripts.models import MarkingGuide, StudentSubmission
from smartscripts.utils.utils import allowed_file
from smartscripts.utils.compress_image import compress_image
from smartscripts.utils import check_student_access
from smartscripts.ai.marking_pipeline import mark_submission
from smartscripts.utils.pdf_helpers import convert_pdf_to_images
from smartscripts.ai.ocr_engine import extract_text_from_image


student_bp = Blueprint('student_bp', __name__, url_prefix='/api/student')


def file_size_within_limit(file_obj, max_mb: int) -> bool:
    file_obj.seek(0, os.SEEK_END)
    size = file_obj.tell()
    file_obj.seek(0)
    return size <= max_mb * 1024 * 1024


@student_bp.before_request
@login_required
def require_student_role():
    if current_user.role != 'student':
        abort(403)


@student_bp.route('/dashboard')
@login_required
def dashboard():
    check_student_access()
    submissions = StudentSubmission.query.filter_by(
        student_id=current_user.id
    ).order_by(StudentSubmission.timestamp.desc()).all()
    return render_template('student/dashboard.html', submissions=submissions)


@student_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def student_upload():
    form = StudentUploadForm()
    form.guide_id.choices = [
        (g.id, f"{g.title} ({g.subject})")
        for g in MarkingGuide.query.order_by(MarkingGuide.created_at.desc()).all()
    ]

    if form.validate_on_submit():
        file = form.file.data

        if not file or not file.filename.strip():
            flash('No file selected.', 'danger')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Invalid file type. Only JPG, PNG, or PDF allowed.', 'danger')
            return redirect(request.url)

        max_mb = current_app.config.get('MAX_FILE_SIZE_MB', 10)
        if not file_size_within_limit(file, max_mb):
            flash(f'File exceeds the {max_mb}MB limit.', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        uuid_token = uuid.uuid4().hex
        original_filename = f"{uuid_token}_original_{filename}"
        annotated_filename = f"{uuid_token}_annotated.png"

        upload_dir = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        original_path = os.path.join(upload_dir, original_filename)
        file.save(original_path)

        # Handle PDF conversion to images
        if original_path.lower().endswith('.pdf'):
            image_paths = convert_pdf_to_images(original_path, upload_dir)
            if not image_paths:
                flash('Failed to convert PDF to image.', 'danger')
                return redirect(request.url)
            original_path = image_paths[0]

        # Compress large images
        if original_path.lower().endswith(('.jpg', '.jpeg', '.png')) and os.path.getsize(original_path) > 4 * 1024 * 1024:
            compressed_path = os.path.join(upload_dir, f"compressed_{original_filename}")
            compress_image(original_path, compressed_path)
            os.remove(original_path)
            original_path = compressed_path

        current_app.logger.info(f"Student {current_user.email} uploaded file {filename}")

        guide = MarkingGuide.query.get_or_404(form.guide_id.data)

        try:
            ocr_text = extract_text_from_image(original_path)
            current_app.logger.info(f"OCR text (first 100 chars): {ocr_text[:100]}")

            student_text, similarity_score, annotated_image = mark_submission(
                file_path=original_path,
                guide_id=guide.id,
                student_id=current_user.id,
                threshold=0.75
            )

            annotated_dir = os.path.join(current_app.static_folder, 'annotated', 'cross')
            os.makedirs(annotated_dir, exist_ok=True)
            annotated_path = os.path.join(annotated_dir, annotated_filename)

            if not cv2.imwrite(annotated_path, annotated_image):
                raise IOError(f"Failed to write annotated image to {annotated_path}")

        except Exception as e:
            error_msg = f"Grading error: {str(e)}\n{traceback.format_exc()}"
            current_app.logger.error(error_msg.encode('ascii', 'ignore').decode())
            flash("Grading failed. Please try again later.", "danger")
            return redirect(url_for('student_bp.student_upload'))

        original_file_rel = Path(os.path.relpath(original_path, current_app.static_folder)).as_posix()
        annotated_file_rel = Path(os.path.relpath(annotated_path, current_app.static_folder)).as_posix()

        submission = StudentSubmission(
            student_id=current_user.id,
            guide_id=guide.id,
            subject=guide.subject,
            grade_level=None,
            answer_filename=original_file_rel,
            graded_image=annotated_file_rel,
            report_filename=None,
            grade=similarity_score,
            feedback='',
            ai_confidence=similarity_score,
            timestamp=datetime.utcnow()
        )

        try:
            db.session.add(submission)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"DB Commit failed: {e}")
            flash("Failed to save submission. Please try again.", "danger")
            return redirect(request.url)

        flash('Submission graded successfully!', 'success')
        return redirect(url_for('student_bp.view_single_result', submission_id=submission.id))

    return render_template('student/upload.html', form=form)


@student_bp.route('/upload/bulk', methods=['POST'])
@login_required
def bulk_upload():
    files = request.files.getlist('files')
    guide_id = request.form.get('guide_id')

    if not files or not guide_id:
        return jsonify({'error': 'Missing files or guide ID'}), 400

    guide = MarkingGuide.query.get_or_404(guide_id)
    results = []

    for file in files:
        try:
            if not allowed_file(file.filename):
                continue

            filename = secure_filename(file.filename)
            uuid_token = uuid.uuid4().hex
            original_filename = f"{uuid_token}_{filename}"
            upload_dir = os.path.join(current_app.static_folder, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            original_path = os.path.join(upload_dir, original_filename)
            file.save(original_path)

            if original_path.lower().endswith('.pdf'):
                image_paths = convert_pdf_to_images(original_path, upload_dir)
                if not image_paths:
                    continue
                original_path = image_paths[0]

            student_text, similarity_score, annotated_image = mark_submission(
                file_path=original_path,
                guide_id=guide.id,
                student_id=current_user.id,
                threshold=0.75
            )

            annotated_filename = f"{uuid_token}_annotated.png"
            annotated_dir = os.path.join(current_app.static_folder, 'annotated', 'cross')
            os.makedirs(annotated_dir, exist_ok=True)
            annotated_path = os.path.join(annotated_dir, annotated_filename)
            cv2.imwrite(annotated_path, annotated_image)

            original_file_rel = Path(os.path.relpath(original_path, current_app.static_folder)).as_posix()
            annotated_file_rel = Path(os.path.relpath(annotated_path, current_app.static_folder)).as_posix()

            submission = StudentSubmission(
                student_id=current_user.id,
                guide_id=guide.id,
                subject=guide.subject,
                grade_level=None,
                answer_filename=original_file_rel,
                graded_image=annotated_file_rel,
                report_filename=None,
                grade=similarity_score,
                feedback='',
                ai_confidence=similarity_score,
                timestamp=datetime.utcnow()
            )

            db.session.add(submission)
            db.session.commit()

            results.append({
                'filename': filename,
                'grade': similarity_score
            })

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Bulk upload failed for {file.filename}: {e}")

    return jsonify({'status': 'success', 'results': results})


@student_bp.route('/grade/semantic', methods=['POST'])
@login_required
def grade_semantic():
    """
    API for receiving raw text and guide_id, returning grade
    """
    data = request.json
    student_text = data.get('student_text')
    guide_id = data.get('guide_id')

    if not student_text or not guide_id:
        return jsonify({'error': 'Missing student_text or guide_id'}), 400

    try:
        student_text, similarity_score, annotated_image = mark_submission(
            text_input=student_text,
            guide_id=guide_id,
            student_id=current_user.id,
            threshold=0.75
        )
        return jsonify({
            'grade': similarity_score,
            'student_text': student_text
        })
    except Exception as e:
        current_app.logger.error(f"Semantic grading error: {e}")
        return jsonify({'error': 'Grading failed'}), 500


@student_bp.route('/result/<int:submission_id>')
@login_required
def view_single_result(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.student_id != current_user.id:
        abort(403)
    return render_template('student/result.html', submission=submission)


@student_bp.route('/results', methods=['GET'])
@login_required
def get_student_results():
    submissions = StudentSubmission.query.filter_by(
        student_id=current_user.id
    ).order_by(StudentSubmission.timestamp.desc()).all()

    data = {
        "results": [
            {
                "id": s.id,
                "subject": s.subject,
                "grade": s.grade,
                "timestamp": s.timestamp.isoformat(),
                "graded_image": url_for('static', filename=s.graded_image, _external=True)
            }
            for s in submissions
        ]
    }
    return jsonify(data)
