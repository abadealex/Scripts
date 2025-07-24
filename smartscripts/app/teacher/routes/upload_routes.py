import os
import json
import csv
from datetime import datetime

import pandas as pd
from flask import (
    jsonify, render_template, request, redirect, flash, url_for, current_app
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from smartscripts.app.forms import TestMaterialsUploadForm
from smartscripts.models import MarkingGuide, StudentSubmission, Test
from smartscripts.extensions import db
from smartscripts.tasks.ocr_tasks import run_ocr_on_test, run_ocr_on_merged_pdf
from smartscripts.utils.permissions import teacher_required
from smartscripts.utils import save_file, create_test_directories

from . import teacher_bp


def log_upload_event(test_id, user_id, upload_type, filename, student_id=None):
    upload_root = current_app.config.get('UPLOAD_FOLDER')
    if not upload_root:
        current_app.logger.error("UPLOAD_FOLDER not configured for audit logging")
        return

    audit_dir = current_app.config.get('UPLOAD_FOLDER_AUDIT_LOGS') or os.path.join(upload_root, 'audit_logs')
    os.makedirs(audit_dir, exist_ok=True)

    log_filename = f"uploads_{datetime.utcnow().strftime('%Y-%m-%d')}.log"
    log_path = os.path.join(audit_dir, log_filename)

    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'test_id': test_id,
        'student_id': student_id or '-',
        'user_id': user_id,
        'type': upload_type,
        'file': filename
    }

    with open(log_path, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


@teacher_bp.route('/upload/class_list/<int:test_id>', methods=['POST'])
@login_required
@teacher_required
def upload_class_list(test_id):
    file = request.files.get('file')
    if not file or not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are allowed'}), 400

    filename = secure_filename('class_list.csv')
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'class_lists', str(test_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    try:
        df = pd.read_csv(file_path)
        required_columns = {'student_id', 'name', 'email'}
        if not required_columns.issubset(df.columns):
            return jsonify({'error': 'CSV must include student_id, name, email'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    log_upload_event(test_id, current_user.id, 'class_list', file_path)
    return jsonify({'message': f'Class list for test {test_id} uploaded successfully'})


@teacher_bp.route('/upload_test_materials/<int:test_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def upload_test_materials_existing(test_id):
    test = Test.query.filter_by(id=test_id, teacher_id=current_user.id).first_or_404()
    form = TestMaterialsUploadForm()

    if form.validate_on_submit():
        try:
            create_test_directories(test.id)
            marking_guide = None

            if form.marking_guide.data and form.marking_guide.data.filename:
                mg_path = save_file(form.marking_guide.data, 'guides', test.id)
                log_upload_event(test.id, current_user.id, 'guide', mg_path)
                marking_guide = MarkingGuide(
                    filename=mg_path,
                    title=f"Marking Guide for {test.title}",
                    subject=test.subject,
                    grade_level=test.grade_level,
                    teacher_id=current_user.id,
                    test_id=test.id
                )
                db.session.add(marking_guide)
                db.session.flush()
                test.guide_path = mg_path

            if form.rubric.data and form.rubric.data.filename:
                rubric_path = save_file(form.rubric.data, 'rubrics', test.id)
                log_upload_event(test.id, current_user.id, 'rubric', rubric_path)
                test.rubric_path = rubric_path
                if marking_guide:
                    marking_guide.rubric_filename = rubric_path

            if form.answered_script.data and form.answered_script.data.filename:
                answered_script_path = save_file(form.answered_script.data, 'answers', test.id)
                log_upload_event(test.id, current_user.id, 'script', answered_script_path)
                test.answered_script_path = answered_script_path
                if marking_guide:
                    marking_guide.answered_script_filename = answered_script_path

            student_ids = request.form.getlist('student_ids')
            files = form.student_scripts.data

            if len(student_ids) != len(files):
                flash("Mismatch between number of student IDs and uploaded files.", "danger")
                return redirect(request.url)

            class_list_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'], 'class_lists', str(test_id), 'class_list.csv'
            )
            if not os.path.exists(class_list_path):
                flash("Class list CSV not found. Upload it before submissions.", "danger")
                return redirect(request.url)

            valid_ids = pd.read_csv(class_list_path)['student_id'].astype(str).tolist()

            from PyPDF2 import PdfReader

            for file, student_id_str in zip(files, student_ids):
                try:
                    student_id = int(student_id_str)
                except (ValueError, TypeError):
                    flash(f"Invalid student ID '{student_id_str}'. Must be an integer.", "danger")
                    return redirect(request.url)

                if str(student_id) not in valid_ids:
                    flash(f"Student ID {student_id} not found in class list.", "danger")
                    return redirect(request.url)

                if file and file.filename:
                    file.stream.seek(0)
                    try:
                        pages_uploaded = len(PdfReader(file.stream).pages)
                    except Exception:
                        pages_uploaded = 1
                    file.stream.seek(0)

                    rel_path = save_file(file, 'submissions', test.id, student_id=student_id)
                    log_upload_event(test.id, current_user.id, 'submission', rel_path, student_id=student_id)

                    update_submission_manifest(test.id, student_id, pages_uploaded)

                    submission = StudentSubmission(
                        test_id=test.id,
                        guide_id=marking_guide.id if marking_guide else None,
                        teacher_id=current_user.id,
                        filename=rel_path,
                        subject=test.subject,
                        grade_level=test.grade_level,
                        student_id=student_id
                    )
                    db.session.add(submission)

            db.session.commit()
            flash("Files uploaded and processed successfully!", "success")
            return redirect(url_for('teacher_bp.dashboard'))

        except Exception as e:
            current_app.logger.error(f"Error uploading files for test {test_id}: {e}", exc_info=True)
            db.session.rollback()
            flash("An error occurred uploading files. Please try again.", "danger")

    elif request.method == 'POST':
        flash("Please correct the errors in the form below.", "danger")
        current_app.logger.debug(f"Form errors: {form.errors}")

    return render_template("teacher/upload_test_materials.html", form=form, test=test)


@teacher_bp.route('/upload-merged', methods=['GET', 'POST'])
@login_required
@teacher_required
def upload_merged_scripts():
    if request.method == 'POST':
        uploaded_file = request.files.get('merged_file')
        if uploaded_file and uploaded_file.filename:
            filename = save_file(uploaded_file, 'merged', current_user.id)
            abs_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            test_id = request.form.get('test_id') or 0

            task = run_ocr_on_merged_pdf.delay(int(test_id), abs_path)

            flash("Merged script uploaded. OCR started in background.", "success")
            return redirect(url_for('teacher_bp.dashboard'))

    return render_template('teacher/upload_merged_scripts.html')


@teacher_bp.route('/run_ocr', methods=['POST'])
@login_required
@teacher_required
def run_ocr():
    data = request.get_json() or {}
    test_id = data.get('test_id')
    student_id = data.get('student_id', current_user.id)

    if not test_id or not student_id:
        return jsonify({'error': 'Missing test_id or student_id in request'}), 400

    current_app.logger.info(f"Starting OCR task for test_id={test_id}, student_id={student_id}")
    task = run_ocr_on_test.delay(test_id, student_id)
    return jsonify({'task_id': task.id})


def update_submission_manifest(test_id, student_id, pages_uploaded):
    manifest_path = os.path.join(
        current_app.config['UPLOAD_FOLDER'], 'submissions', str(test_id), 'manifest.csv'
    )
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)

    rows = []
    found = False
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['student_id'] == str(student_id):
                    row['pages_uploaded'] = str(pages_uploaded)
                    row['timestamp'] = datetime.utcnow().isoformat()
                    found = True
                rows.append(row)

    if not found:
        rows.append({
            'student_id': str(student_id),
            'pages_uploaded': str(pages_uploaded),
            'timestamp': datetime.utcnow().isoformat()
        })

    with open(manifest_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['student_id', 'pages_uploaded', 'timestamp'])
        writer.writeheader()
        writer.writerows(rows)
