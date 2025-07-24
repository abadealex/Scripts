import os
from flask import (
    request, redirect, flash, url_for, jsonify,
    current_app, render_template, send_file, abort
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

from smartscripts.models import MarkingGuide, StudentSubmission, Test
from smartscripts.extensions import db
from smartscripts.services.bulk_upload_service import process_bulk_teacher_upload
from smartscripts.services.export_service import export_submissions_to_csv, export_submissions_to_pdf

from . import teacher_bp
from .utils import allowed_file, handle_file_upload

# Correct relative import of form:
from ...forms import TestMaterialsUploadForm

# ===== UPLOAD ROUTES =====

@teacher_bp.route('/upload', methods=['POST'])
@login_required
def export_upload_test():
    # TODO: Implement your test upload logic here
    # Example:
    # form = TestMaterialsUploadForm()
    # if form.validate_on_submit():
    #     # process form data
    #     flash('Test uploaded successfully.', 'success')
    # else:
    #     flash('Upload failed. Check your inputs.', 'danger')
    return redirect(url_for('teacher_bp.export_upload_guide_page'))


@teacher_bp.route('/upload_bulk', methods=['POST'])
@login_required
def export_upload_bulk():
    # TODO: Implement your bulk upload logic here
    # Example:
    # files = request.files.getlist('files')
    # result = process_bulk_files(files, current_user.id)
    # flash(f'Bulk upload processed: {result}', 'success')
    return redirect(url_for('teacher_bp.export_upload_guide_page'))


@teacher_bp.route('/upload_guide', methods=['GET', 'POST'])
@login_required
def export_upload_guide_page():
    form = TestMaterialsUploadForm()
    # Fetch tests related to current user for display
    tests = Test.query.filter_by(teacher_id=current_user.id).all()

    if request.method == 'POST':
        if form.validate_on_submit():
            # Example handling form upload (adjust fields as needed)
            # file = form.marking_guide.data
            # filename = secure_filename(file.filename)
            # Save file and create MarkingGuide object here
            flash('Marking guide uploaded successfully.', 'success')
            return redirect(url_for('teacher_bp.export_upload_guide_page'))
        else:
            flash('Please fix errors in the form.', 'danger')

    return render_template('teacher/upload_test_materials.html', tests=tests, form=form)


@teacher_bp.route('/teacher/upload_script', methods=['POST'])
@login_required
def export_upload_script():
    # TODO: Handle upload of test scripts here
    return redirect(url_for('teacher_bp.export_upload_guide_page'))


@teacher_bp.route('/teacher/upload_rubric', methods=['POST'])
@login_required
def export_upload_rubric():
    # TODO: Handle upload of rubric files here
    return redirect(url_for('teacher_bp.export_upload_guide_page'))


@teacher_bp.route('/teacher/upload_guide', methods=['POST'])
@login_required
def export_upload_guide_api():
    # TODO: API endpoint to accept guide metadata + files
    return jsonify({'status': 'not implemented'}), 501


# ===== EXPORT ROUTES =====

@teacher_bp.route('/export_csv/<int:guide_id>')
@login_required
def export_csv(guide_id):
    guide = MarkingGuide.query.get_or_404(guide_id)
    if guide.teacher_id != current_user.id:
        abort(403)

    try:
        csv_path = export_submissions_to_csv(guide)
        return send_file(csv_path, as_attachment=True)
    except Exception as e:
        current_app.logger.error(f"CSV export failed for guide {guide_id}: {e}")
        flash('Failed to export CSV.', 'danger')
        return redirect(url_for('teacher_bp.export_upload_guide_page'))


@teacher_bp.route('/export_pdf/<int:guide_id>')
@login_required
def export_pdf(guide_id):
    guide = MarkingGuide.query.get_or_404(guide_id)
    if guide.teacher_id != current_user.id:
        abort(403)

    try:
        pdf_path = export_submissions_to_pdf(guide)
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        current_app.logger.error(f"PDF export failed for guide {guide_id}: {e}")
        flash('Failed to export PDF.', 'danger')
        return redirect(url_for('teacher_bp.export_upload_guide_page'))


@teacher_bp.route('/export_submissions/<int:guide_id>/<string:format>')
@login_required
def export_submissions(guide_id, format):
    guide = MarkingGuide.query.get_or_404(guide_id)
    if guide.teacher_id != current_user.id:
        abort(403)

    try:
        if format == 'csv':
            file_path = export_submissions_to_csv(guide)
        elif format == 'pdf':
            file_path = export_submissions_to_pdf(guide)
        else:
            flash('Unsupported export format.', 'warning')
            return redirect(url_for('teacher_bp.export_upload_guide_page'))

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        current_app.logger.error(f"Export ({format}) failed for guide {guide_id}: {e}")
        flash(f'Failed to export {format.upper()}.', 'danger')
        return redirect(url_for('teacher_bp.export_upload_guide_page'))
