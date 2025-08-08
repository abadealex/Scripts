import os
from flask import (
    Blueprint, jsonify, flash, redirect,
    url_for, abort, current_app
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from smartscripts.extensions import db
from smartscripts.models import (
    Test, MarkingGuide, StudentSubmission, ExtractedStudentScript
)
from smartscripts.utils.utils import safe_remove

# ?? Register this blueprint in your app factory or __init__.py
delete_bp = Blueprint('delete_bp', __name__)


def delete_submissions_for_guide(guide_id):
    """Helper function to delete all submissions and their files for a marking guide."""
    submissions = StudentSubmission.query.filter_by(guide_id=guide_id).all()
    for submission in submissions:
        safe_remove(submission.file_path)
        db.session.delete(submission)


@delete_bp.route('/delete_test/<int:test_id>', methods=['POST'])
@login_required
def delete_test(test_id):
    test = Test.query.get_or_404(test_id)

    if test.teacher_id != current_user.id and not current_user.is_admin:
        abort(403)

    try:
        # Delete related submissions
        guide_ids = [mg.id for mg in MarkingGuide.query.filter_by(test_id=test.id).all()]
        for guide_id in guide_ids:
            delete_submissions_for_guide(guide_id)

        # Delete marking guides and extracted scripts
        MarkingGuide.query.filter_by(test_id=test.id).delete(synchronize_session=False)
        ExtractedStudentScript.query.filter_by(test_id=test.id).delete(synchronize_session=False)

        # Delete the test itself
        db.session.delete(test)
        db.session.commit()

        flash("? Test and all related data deleted successfully.", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"[DB ERROR] Failed to delete test {test_id}: {e}")
        flash("? Database error while deleting test.", "danger")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[ERROR] Unexpected error deleting test {test_id}: {e}")
        flash("? Unexpected error occurred.", "danger")

    return redirect(url_for('teacher_bp.dashboard_bp.dashboard'))


@delete_bp.route('/delete_all_submissions/<int:guide_id>', methods=['POST'])
@login_required
def delete_all_submissions(guide_id):
    guide = MarkingGuide.query.get_or_404(guide_id)

    if guide.teacher_id != current_user.id:
        abort(403)

    try:
        delete_submissions_for_guide(guide_id)
        db.session.commit()
        flash("? All submissions deleted successfully.", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"[DB ERROR] While deleting submissions for guide {guide_id}: {e}")
        flash("? Database error occurred.", "danger")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[ERROR] Failed to delete submissions for guide {guide_id}: {e}")
        flash("? Failed to delete submissions.", "danger")

    return redirect(url_for('teacher_bp.export_upload_guide_page'))


@delete_bp.route('/delete_guide/<int:guide_id>', methods=['POST'])
@login_required
def delete_marking_guide(guide_id):
    guide = MarkingGuide.query.get_or_404(guide_id)

    if guide.teacher_id != current_user.id:
        abort(403)

    try:
        delete_submissions_for_guide(guide_id)
        db.session.delete(guide)
        db.session.commit()
        flash("? Marking guide and all associated submissions deleted.", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"[DB ERROR] While deleting guide {guide_id}: {e}")
        flash("? Database error occurred.", "danger")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[ERROR] Failed to delete guide {guide_id}: {e}")
        flash("? Failed to delete guide.", "danger")

    return redirect(url_for('teacher_bp.export_upload_guide_page'))

