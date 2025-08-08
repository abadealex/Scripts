from flask import Blueprint, render_template
from smartscripts.models import Test  # ✅ Still fine to import here

manage_routes = Blueprint('manage_routes', __name__)

@manage_routes.route('/manage/<int:test_id>', endpoint='manage_test_files')
def manage_test_files(test_id):
    from smartscripts.models import StudentSubmission  # 👈 Lazy import here

    test = Test.query.get_or_404(test_id)

    file_guide_url = getattr(test, 'file_guide_url', None)
    file_rubric_url = getattr(test, 'file_rubric_url', None)
    answered_script_url = getattr(test, 'answered_script_url', None)
    submission_url = getattr(test, 'submission_url', None)

    submission = StudentSubmission.query.filter_by(test_id=test.id).first()

    return render_template(
        'teacher/review.html',
        test=test,
        file_guide_url=file_guide_url,
        file_rubric_url=file_rubric_url,
        answered_script_url=answered_script_url,
        submission_url=submission_url,
        submission=submission
    )
