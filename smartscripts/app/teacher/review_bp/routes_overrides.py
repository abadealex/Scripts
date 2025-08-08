import csv
import json
from io import StringIO, BytesIO
from flask import (
    render_template, request, redirect, url_for, flash, current_app, send_file, abort
)
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from smartscripts.extensions import db
from smartscripts.models import (
    Test, OCRSubmission, AttendanceRecord, OCROverrideLog
)
from smartscripts.utils.permissions import teacher_required
from . import review_bp
from .utils import is_teacher_or_admin, apply_ocr_override


@review_bp.route('/submit_overrides/<int:test_id>', methods=['POST'])
@login_required
def submit_overrides(test_id: int):
    test = Test.query.get_or_404(test_id)
    if not is_teacher_or_admin(test):
        abort(403)

    count = int(request.form.get("count", 0))
    updated = 0

    for i in range(count):
        sid = request.form.get(f"submission_id_{i}")
        path = request.form.get(f"pdf_path_{i}")
        name = request.form.get(f"corrected_name_{i}", "").strip()
        stud_id = request.form.get(f"corrected_id_{i}", "").strip()

        sub = None
        if sid:
            try:
                sub = OCRSubmission.query.get(int(sid))
            except ValueError:
                continue
        elif path:
            sub = OCRSubmission.query.filter_by(test_id=test_id, pdf_path=path).first()

        if not sub:
            continue

        if apply_ocr_override(sub, name, stud_id):
            updated += 1

    try:
        db.session.commit()
        flash(f"✅ {updated} override(s) saved.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[submit_overrides] DB commit failed: {e}")
        flash(f"❌ Error saving overrides: {str(e)}", "danger")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return ('', 204)
    return redirect(url_for('teacher_bp.review_test', test_id=test_id))


@review_bp.route('/bulk_review/<int:test_id>')
@login_required
@teacher_required
def bulk_review(test_id: int):
    test = Test.query.get_or_404(test_id)
    return render_template('review_bulk.html', test=test)


@review_bp.route('/submit_bulk_overrides/<int:test_id>', methods=['POST'])
@login_required
@teacher_required
def submit_bulk_overrides(test_id: int):
    file = request.files.get('bulk_file')
    if not file or not file.filename:
        flash('No file uploaded or filename missing.', 'danger')
        return redirect(url_for('teacher_bp.bulk_review', test_id=test_id))

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower()

    try:
        if ext == 'csv':
            content = file.stream.read().decode('utf-8')
            reader = csv.DictReader(StringIO(content))
            overrides = list(reader)
        elif ext == 'json':
            overrides = json.load(file.stream)
        else:
            flash('Unsupported file format. Use CSV or JSON.', 'danger')
            return redirect(url_for('teacher_bp.bulk_review', test_id=test_id))
    except Exception as e:
        flash(f"❌ Failed to parse file: {str(e)}", 'danger')
        return redirect(url_for('teacher_bp.bulk_review', test_id=test_id))

    count = 0
    for entry in overrides:
        student_id = entry.get('student_id')
        if not student_id:
            continue

        present_str = str(entry.get('present', 'yes')).strip().lower()
        present = present_str in ['yes', '1', 'true']

        record = AttendanceRecord.query.filter_by(test_id=test_id, student_id=student_id).first()
        if not record:
            record = AttendanceRecord(test_id=test_id, student_id=student_id)  # <-- construct with kwargs

            db.session.add(record)

        record.present = present  # type: ignore

        log = OCROverrideLog(
            test_id=test_id,
            student_id=student_id,  # make sure these fields exist in your model!
            override_type='bulk_upload',
            previous_value=None,
            new_value=str(present),
            metadata=json.dumps(entry)  # type: ignore if you get errors here
        )
        db.session.add(log)

        count += 1

    try:
        db.session.commit()
        flash(f"✅ {count} override entries processed successfully!", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"[submit_bulk_overrides] DB commit failed: {e}")
        flash("❌ A database error occurred.", "danger")

    return redirect(url_for('teacher_bp.bulk_review', test_id=test_id))


@review_bp.route('/export_overrides/<int:test_id>')
@login_required
@teacher_required
def export_overrides(test_id: int):
    records = AttendanceRecord.query.filter_by(test_id=test_id).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['student_id', 'present'])

    for r in records:
        writer.writerow([r.student_id, 'yes' if r.present else 'no'])

    mem = BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    output.close()

    return send_file(mem,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=f'overrides_test_{test_id}.csv')
