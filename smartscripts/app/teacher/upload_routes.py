import os
import csv
import uuid
import zipfile
from io import BytesIO, StringIO
from pathlib import Path

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    jsonify, send_file, current_app, abort
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from smartscripts.extensions import db
from smartscripts.models import Test, AttendanceRecord
from smartscripts.app.forms import TestMaterialsUploadForm
from smartscripts.services.ocr_pipeline import process_combined_student_scripts
from smartscripts.ai.ocr_engine import run_ocr_on_test

upload_bp = Blueprint("upload_bp", __name__, url_prefix='/upload')

ALLOWED_EXTENSIONS = {'.pdf', '.csv'}

UPLOAD_FOLDERS = {
    "question_paper": "question_papers",
    "rubric": "rubrics",
    "marking_guide": "marking_guides",
    "answered_script": "answered_scripts",
    "combined_scripts": "combined_scripts",
    "class_list": "student_lists",
}

FILENAME_FIELDS = {
    "question_paper": "question_paper_filename",
    "rubric": "rubric_filename",
    "marking_guide": "marking_guide_filename",
    "answered_script": "answered_script_filename",
    "combined_scripts": "combined_scripts_filename",
    "class_list": "class_list_filename",
}

def allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder: str, test_id: int, filename: str = None):
    upload_root = Path(current_app.root_path) / 'static' / 'uploads' / folder / str(test_id)
    upload_root.mkdir(parents=True, exist_ok=True)

    if not filename:
        filename = secure_filename(file.filename)

    save_path = upload_root / filename
    file.save(save_path)
    return save_path

def get_file_path(relative_path: Path) -> Path:
    return Path(current_app.root_path) / 'static' / 'uploads' / relative_path

def to_static_url(full_path: Path) -> str:
    """
    Convert an absolute file path (inside static/uploads) to a /static/... URL
    """
    try:
        relative_path = full_path.relative_to(Path(current_app.root_path) / 'static')
    except ValueError:
        # Path not inside static, fallback or raise
        current_app.logger.warning(f"File path {full_path} not under static folder")
        return ""
    return url_for('static', filename=str(relative_path).replace("\\", "/"))

@upload_bp.route("/<int:test_id>", methods=["GET", "POST"])
@login_required
def upload_test_materials(test_id):
    test = Test.query.get_or_404(test_id)

    if test.teacher_id != current_user.id and not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("teacher_bp.dashboard_bp.dashboard"))

    form = TestMaterialsUploadForm(obj=test)

    if form.validate_on_submit():
        try:
            for field, folder in UPLOAD_FOLDERS.items():
                file = request.files.get(field)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    save_uploaded_file(file, folder, test_id, unique_filename)
                    setattr(test, FILENAME_FIELDS[field], unique_filename)
                elif file:
                    flash(f"Invalid file type for {field}.", "warning")
                    return redirect(request.url)

            db.session.commit()
            flash("All materials uploaded successfully.", "success")
            return redirect(url_for("teacher_bp.dashboard_bp.dashboard"))

        except Exception as e:
            db.session.rollback()
            current_app.logger.exception(f"Upload error: {e}")
            flash(f"Error uploading files: {e}", "danger")

    # Pass static URLs of uploaded files to the template
    uploaded_files_urls = {}
    for field, filename_field in FILENAME_FIELDS.items():
        filename = getattr(test, filename_field)
        if filename:
            file_path = Path(current_app.root_path) / 'static' / 'uploads' / UPLOAD_FOLDERS[field] / str(test_id) / filename
            uploaded_files_urls[field] = to_static_url(file_path)
        else:
            uploaded_files_urls[field] = None

    return render_template("teacher/upload_test_materials.html", form=form, test=test, uploaded_files=uploaded_files_urls)

@upload_bp.route("/upload/<file_type>/<int:test_id>", methods=["POST"])
@login_required
def upload_individual_file(file_type, test_id):
    test = Test.query.get_or_404(test_id)

    if test.teacher_id != current_user.id and not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("teacher_bp.dashboard_bp.dashboard"))

    if file_type not in UPLOAD_FOLDERS:
        flash("Invalid file type.", "danger")
        return redirect(url_for("upload_bp.upload_test_materials", test_id=test_id))

    file = request.files.get(file_type)
    if not file:
        flash("No file uploaded.", "warning")
        return redirect(url_for("upload_bp.upload_test_materials", test_id=test_id))
    if not allowed_file(file.filename):
        flash("Invalid file type.", "warning")
        return redirect(url_for("upload_bp.upload_test_materials", test_id=test_id))

    try:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        save_uploaded_file(file, UPLOAD_FOLDERS[file_type], test_id, unique_filename)
        setattr(test, FILENAME_FIELDS[file_type], unique_filename)
        db.session.commit()
        flash(f"{file_type.replace('_', ' ').title()} uploaded successfully.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Upload failed: {e}")
        flash(f"Upload failed: {e}", "danger")

    return redirect(url_for("upload_bp.upload_test_materials", test_id=test_id))

@upload_bp.route("/review/<file_type>/<int:test_id>")
@login_required
def review_file(file_type, test_id):
    test = Test.query.get_or_404(test_id)

    if test.teacher_id != current_user.id and not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("teacher_bp.dashboard_bp.dashboard"))

    if file_type not in FILENAME_FIELDS:
        flash("Invalid file type.", "danger")
        return redirect(url_for("upload_bp.upload_test_materials", test_id=test_id))

    filename = getattr(test, FILENAME_FIELDS[file_type])
    if not filename:
        flash(f"{file_type.replace('_', ' ').title()} not uploaded.", "warning")
        return redirect(url_for("upload_bp.upload_test_materials", test_id=test_id))

    file_path = get_file_path(Path(UPLOAD_FOLDERS[file_type]) / str(test_id) / filename)
    if not file_path.exists():
        flash("File not found.", "warning")
        return redirect(url_for("upload_bp.upload_test_materials", test_id=test_id))

    return send_file(file_path)

@upload_bp.route("/delete_file/<int:test_id>/<file_type>", methods=["POST"])
@login_required
def delete_file(test_id, file_type):
    test = Test.query.get_or_404(test_id)

    if test.teacher_id != current_user.id and not current_user.is_admin:
        abort(403)

    if file_type not in FILENAME_FIELDS:
        flash("Invalid file type.", "danger")
        return redirect(url_for("upload_bp.upload_test_materials", test_id=test_id))

    filename = getattr(test, FILENAME_FIELDS[file_type])
    if not filename:
        flash("File not set.", "warning")
        return redirect(url_for("upload_bp.upload_test_materials", test_id=test_id))

    file_path = get_file_path(Path(UPLOAD_FOLDERS[file_type]) / str(test_id) / filename)
    if file_path.exists():
        try:
            file_path.unlink()
            setattr(test, FILENAME_FIELDS[file_type], None)
            db.session.commit()
            flash(f"{file_type.replace('_', ' ').title()} deleted successfully.", "info")
        except Exception as e:
            current_app.logger.error(f"Failed to delete file: {e}")
            flash(f"Deletion failed: {e}", "danger")
    else:
        flash("File not found or already deleted.", "warning")

    return redirect(url_for("upload_bp.upload_test_materials", test_id=test_id))

@upload_bp.route("/upload_bulk_scripts/<int:test_id>", methods=["GET", "POST"])
@login_required
def upload_bulk_scripts(test_id):
    test = Test.query.get_or_404(test_id)

    if test.teacher_id != current_user.id and not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("teacher_bp.dashboard_bp.dashboard"))

    if request.method == "POST":
        try:
            class_list_file = request.files.get("class_list")
            combined_pdf_file = request.files.get("scripts_pdf")

            if not class_list_file or not combined_pdf_file:
                flash("Both class list and combined scripts files must be uploaded.", "warning")
                return redirect(request.url)

            cl_filename = secure_filename(class_list_file.filename)
            cp_filename = secure_filename(combined_pdf_file.filename)

            cl_unique = f"{uuid.uuid4().hex}_{cl_filename}"
            cp_unique = f"{uuid.uuid4().hex}_{cp_filename}"

            save_uploaded_file(class_list_file, "student_lists", test_id, cl_unique)
            save_uploaded_file(combined_pdf_file, "combined_scripts", test_id, cp_unique)

            test.class_list_filename = cl_unique
            test.combined_scripts_filename = cp_unique

            db.session.commit()

            result = process_combined_student_scripts(
                test_id=test.id,
                scripts_pdf_path=test.combined_scripts_path,
                class_list_path=test.class_list_path,
            )

            return render_template(
                "teacher/upload_confirmation.html",
                test=test,
                matched=result.get("matched", []),
                unmatched=result.get("unmatched", []),
                summary=result.get("summary", {}),
                split_paths=result.get("split_paths", {}),
            )
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception(f"Error processing bulk scripts: {e}")
            flash(f"Error processing bulk scripts: {e}", "danger")
            return redirect(request.url)

    return render_template("teacher/upload_test_materials.html", test=test, form=your_form_instance)

@upload_bp.route("/download_all/<int:test_id>")
@login_required
def download_all(test_id):
    extracted_dir = get_file_path(Path("extracted") / str(test_id))
    if not extracted_dir.exists():
        flash("No extracted scripts found.", "warning")
        return redirect(url_for("teacher_bp.dashboard_bp.dashboard"))

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(extracted_dir):
            for file in files:
                abs_path = Path(root) / file
                rel_path = abs_path.relative_to(extracted_dir)
                zipf.write(abs_path, arcname=str(rel_path))

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"extracted_test_{test_id}.zip"
    )

@upload_bp.route("/download_presence_csv/<int:test_id>")
@login_required
def download_presence_csv(test_id):
    test = Test.query.get_or_404(test_id)
    records = AttendanceRecord.query.filter_by(test_id=test.id).all()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["Detected Name", "Detected ID", "Corrected Name", "Corrected ID", "Present"])
    for rec in records:
        writer.writerow([
            rec.detected_name,
            rec.detected_id,
            rec.corrected_name,
            rec.corrected_id,
            "Yes" if rec.is_present else "No"
        ])

    return send_file(
        BytesIO(si.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"presence_table_test_{test_id}.csv"
    )

@upload_bp.route("/reprocess_ocr/<int:test_id>/<int:record_id>")
@login_required
def reprocess_ocr(test_id, record_id):
    record = AttendanceRecord.query.get_or_404(record_id)

    if not record.pdf_path:
        flash("PDF path not found.", "danger")
        return redirect(url_for("review.review_test", test_id=test_id))

    abs_path = get_file_path(record.pdf_path)
    if not abs_path.exists():
        flash("PDF file missing on disk.", "danger")
        return redirect(url_for("review.review_test", test_id=test_id))

    try:
        result = run_ocr_on_test(str(abs_path))
        record.detected_name = result.get("name", "")
        record.detected_id = result.get("id", "")
        record.ocr_confidence = result.get("confidence", 0.0)
        db.session.commit()
        flash("OCR reprocessed successfully.", "success")
    except Exception as e:
        flash(f"OCR reprocessing failed: {e}", "danger")

    return redirect(url_for("review.review_test", test_id=test_id))
