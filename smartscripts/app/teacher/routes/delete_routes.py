from flask import jsonify, flash, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from smartscripts.models import Test, MarkingGuide, StudentSubmission, ExtractedStudentScript
from smartscripts.extensions import db
from smartscripts.utils.utils import safe_remove, check_teacher_access
from . import teacher_bp


def delete_submissions_for_guide(guide_id):
    """Helper function to delete all submissions for a given marking guide."""
    submissions = StudentSubmission.query.filter_by(guide_id=guide_id).all()
    for submission in submissions:
        safe_remove(submission.file_path)
        db.session.delete(submission)


@teacher_bp.route('/delete_test/<int:test_id>', methods=['POST'])
@login_required
def delete_test(test_id):
    test = Test.query.get_or_404(test_id)

    # Authorization: Only teacher who owns the test or admin can delete
    if test.teacher_id != current_user.id and not current_user.is_admin:
        abort(403)

    try:
        # Delete all submissions for each marking guide under this test
        guide_ids = [mg.id for mg in MarkingGuide.query.filter_by(test_id=test.id).all()]
        for guide_id in guide_ids:
            delete_submissions_for_guide(guide_id)

        # Delete marking guides for this test
        MarkingGuide.query.filter_by(test_id=test.id).delete(synchronize_session=False)

        # Delete extracted student scripts related to this test
        ExtractedStudentScript.query.filter_by(test_id=test.id).delete(synchronize_session=False)

        # Finally delete the test itself
        db.session.delete(test)
        db.session.commit()
        flash("Test and all related submissions deleted successfully.", "success")
    except Exception as e:
        current_app.logger.error(f"Failed to delete test {test_id}: {e}")
        db.session.rollback()
        flash(f"Failed to delete test: {str(e)}", "danger")

    return redirect(url_for('teacher_bp.dashboard'))


@teacher_bp.route('/delete_all_submissions/<int:guide_id>', methods=['POST'])
@login_required
def delete_all_submissions(guide_id):
    guide = MarkingGuide.query.get_or_404(guide_id)

    if guide.teacher_id != current_user.id:
        abort(403)

    try:
        delete_submissions_for_guide(guide_id)
        db.session.commit()
        flash('All submissions deleted successfully.', 'success')
    except Exception as e:
        current_app.logger.error(f"Failed to delete submissions for guide {guide_id}: {e}")
        db.session.rollback()
        flash('Failed to delete submissions.', 'danger')

    return redirect(url_for('teacher_bp.export_upload_guide_page'))


@teacher_bp.route('/delete_guide/<int:guide_id>', methods=['POST'])
@login_required
def delete_marking_guide(guide_id):
    guide = MarkingGuide.query.get_or_404(guide_id)

    if guide.teacher_id != current_user.id:
        abort(403)

    try:
        # Delete all submissions first
        delete_submissions_for_guide(guide_id)

        # Delete the marking guide itself
        db.session.delete(guide)
        db.session.commit()
        flash('Marking guide and all associated submissions deleted.', 'success')
    except Exception as e:
        current_app.logger.error(f"Failed to delete guide {guide_id}: {e}")
        db.session.rollback()
        flash('Failed to delete guide.', 'danger')

    return redirect(url_for('teacher_bp.export_upload_guide_page'))
