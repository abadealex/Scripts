from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, current_app, send_file, abort, jsonify
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid
import json

from cograder_clone import db  # Absolute import of db
from cograder_clone.app.models import MarkingGuide, StudentSubmission, Result  # Correct model imports
from cograder_clone.app.forms import StudentUploadForm  # Absolute import of form
from cograder_clone.app.utils import allowed_file, grade_submission, grade_answers  # Absolute import of utils

student_bp = Blueprint('student_bp', __name__)

# Student upload route (image/PDF)
@student_bp.route('/student/upload', methods=['GET', 'POST'])
@login_required
def student_upload():
    form = StudentUploadForm()
    form.guide_id.choices = [(g.id, g.title) for g in MarkingGuide.query.all()]

    if form.validate_on_submit():
        file = form.file.data

        # Validate file presence
        if not file or file.filename.strip() == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)

        # Validate file type
        if not allowed_file(file.filename):
            flash('Invalid file type. Only JPG, JPEG, PNG, and PDF are allowed.', 'danger')
            return redirect(request.url)

        # Check file size
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        max_mb = current_app.config.get('MAX_FILE_SIZE_MB', 10)
        if file_length > max_mb * 1024 * 1024:
            flash(f'File exceeds the {max_mb}MB size limit.', 'danger')
            return redirect(request.url)

        # Save file with unique name
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        upload_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, unique_name)
        file.save(filepath)

        current_app.logger.info(f"Student {current_user.email} uploaded {filename}")

        guide = MarkingGuide.query.get_or_404(form.guide_id.data)

        # Grade the submission
        try:
            result = grade_submission(filepath, guide, current_user.email, output_dir=upload_dir)
        except Exception as e:
            current_app.logger.error(f"Grading error: {str(e)}")
            flash(f"Grading failed: {str(e)}", "danger")
            return redirect(request.url)

        # Save submission record
        submission = StudentSubmission(
            student_id=current_user.id,
            guide_id=guide.id,
            answer_filename=filepath,
            graded_image=result.get('annotated_file'),
            report_filename=result.get('pdf_report'),
            grade=result.get('total_score'),
            feedback=result.get('feedback', ''),
            timestamp=datetime.utcnow()
        )
        db.session.add(submission)
        db.session.commit()

        flash('Submission graded successfully!', 'success')
        return redirect(url_for('student_bp.view_single_result', submission_id=submission.id))

    return render_template('student_upload.html', form=form)


# View all submissions for current student
@student_bp.route('/student/results')
@login_required
def view_results():
    submissions = StudentSubmission.query.filter_by(student_id=current_user.id)\
        .order_by(StudentSubmission.timestamp.desc()).all()
    return render_template('student_results.html', submissions=submissions)


# View a single submission result
@student_bp.route('/student/result/<int:submission_id>')
@login_required
def view_single_result(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if submission.student_id != current_user.id:
        abort(403)
    return render_template('view_result.html', result=submission)


# Download specific PDF report for submission
@student_bp.route('/student/download_report/<int:submission_id>')
@login_required
def download_report_by_id(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    if current_user.role == 'student' and submission.student_id != current_user.id:
        abort(403)

    if not submission.report_filename or not os.path.exists(submission.report_filename):
        flash("PDF report not available.", "danger")
        return redirect(url_for('student_bp.view_single_result', submission_id=submission.id))

    return send_file(
        submission.report_filename,
        as_attachment=True,
        download_name=f"{current_user.email}_Graded_Report.pdf"
    )


# Serve secure marked images or reports by filename
@student_bp.route('/download/<filename>')
@login_required
def download_file_by_name(filename):
    allowed_extensions = ('.pdf', '.jpg', '.jpeg', '.png')
    if not filename.lower().endswith(allowed_extensions):
        abort(400, description="Invalid file type.")

    file_path = os.path.join(current_app.config['MARKED_FOLDER'], filename)
    if not os.path.exists(file_path):
        abort(404, description="File not found.")

    return send_file(file_path, as_attachment=True)


# JSON API endpoint: submit answers and get grading feedback
@student_bp.route('/student/submit', methods=['POST'])
@login_required
def student_submit():
    data = request.get_json()
    if not data or 'answers' not in data or 'guide_id' not in data:
        return jsonify({"error": "Missing required data"}), 400

    guide = MarkingGuide.query.get(data['guide_id'])
    if not guide:
        return jsonify({"error": "Marking guide not found"}), 404

    student_answers = data['answers']  # Expected dict like {"Q1": "...", "Q2": "..."}

    try:
        graded, score, total = grade_answers(guide, student_answers)
    except Exception as e:
        current_app.logger.error(f"Grading error in /student/submit: {str(e)}")
        return jsonify({"error": "Grading failed"}), 500

    # Save structured result
    result = Result(
        student_id=current_user.id,
        guide_id=guide.id,
        raw_score=score,
        total=total,
        breakdown=json.dumps(graded),
        timestamp=datetime.utcnow()
    )
    db.session.add(result)
    db.session.commit()

    return jsonify({
        "score": score,
        "total": total,
        "breakdown": graded
    }), 200
