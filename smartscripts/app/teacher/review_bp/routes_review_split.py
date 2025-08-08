from flask import render_template, redirect, url_for, flash, abort, request, current_app
from flask_login import login_required
from smartscripts.extensions import db
from smartscripts.models import Test, PageReview, User
from smartscripts.utils.permissions import teacher_required
from smartscripts.utils.file_helpers import get_image_path_for_page
from . import review_bp
from .utils import is_teacher_or_admin


@review_bp.route('/review_split/<int:test_id>/<int:page_num>')
@login_required
@teacher_required
def review_split_page(test_id: int, page_num: int):
    test = Test.query.get_or_404(test_id)
    if not is_teacher_or_admin(test):
        abort(403)

    image_path = get_image_path_for_page(test_id, page_num)
    if not image_path:
        flash(f"No image found for page {page_num}", "warning")
        return redirect(url_for('teacher_bp.review_test', test_id=test_id))

    prior_review = PageReview.query.filter_by(test_id=test_id, page_num=page_num).first()
    prior_user = User.query.get(prior_review.reviewed_by) if prior_review else None

    return render_template('teacher/review_split.html',
                           test=test,
                           page_num=page_num,
                           image_path=image_path,
                           prior_review=prior_review,
                           prior_review_user=prior_user,
                           next_page_num=page_num + 1)


@review_bp.route('/submit_review/<int:test_id>/<int:page_num>', methods=['POST'])
@login_required
@teacher_required
def submit_review(test_id: int, page_num: int):
    test = Test.query.get_or_404(test_id)
    if not is_teacher_or_admin(test):
        abort(403)

    decision = request.form.get("decision", "").strip().lower()
    comment = request.form.get("comment", "").strip()
    is_front_page = decision == "yes"

    db.session.add(PageReview.query.filter_by(test_id=test_id, page_num=page_num).first() or
                   PageReview(test_id=test_id, page_num=page_num))

    db.session.add(db.session.query(PageReview).filter_by(test_id=test_id, page_num=page_num).first())
    review = PageReview.query.filter_by(test_id=test_id, page_num=page_num).first()

    if review:
        review.is_front_page = is_front_page
        review.reviewed_by = current_app.login_manager._load_user().get_id()
        review.timestamp = db.func.now()
    else:
        db.session.add(PageReview(
            test_id=test_id,
            page_num=page_num,
            is_front_page=is_front_page,
            reviewed_by=current_app.login_manager._load_user().get_id()
        ))

    db.session.add(db.session.query(PageReview).filter_by(test_id=test_id, page_num=page_num).first())
    try:
        db.session.commit()
        flash(f"✅ Review for page {page_num} saved.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[submit_review] DB commit failed: {e}")
        flash(f"❌ Failed to save review: {str(e)}", "danger")

    if get_image_path_for_page(test_id, page_num + 1):
        return redirect(url_for('teacher_bp.review_split_page', test_id=test_id, page_num=page_num + 1))

    flash("ℹ️ All pages reviewed or no next page found.", "info")
    return redirect(url_for('teacher_bp.review_test', test_id=test_id))
