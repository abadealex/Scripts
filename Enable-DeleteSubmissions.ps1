# Enable-DeleteSubmissions.ps1
# Adds DELETE submission support to SmartScripts

$ErrorActionPreference = "Stop"

# Paths
$apiPath = "smartscripts/api/v1/submissions.py"
$frontendComponentPath = "frontend/src/components/TeacherDashboard.js"
$mainPath = "smartscripts/app/main.py"
$modelsPath = "smartscripts/models.py"

# === 1. Add DELETE endpoint ===
if (Test-Path $apiPath) {
    Copy-Item $apiPath "$apiPath.bak"

    Add-Content $apiPath @"
from flask import Blueprint, request, jsonify
import os
from smartscripts.models import db, Submission
from smartscripts.config import UPLOAD_FOLDER

bp = Blueprint('submissions', __name__)

@bp.route('/submissions/<int:submission_id>', methods=['DELETE'])
def delete_submission(submission_id):
    submission = Submission.query.get(submission_id)
    if not submission:
        return jsonify({'error': 'Submission not found'}), 404

    if submission.filename:
        try:
            filepath = os.path.join(UPLOAD_FOLDER, 'submissions', submission.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500

    db.session.delete(submission)
    db.session.commit()
    return jsonify({'message': 'Submission deleted successfully'}), 200
"@
    Write-Host "✅ DELETE route added to $apiPath"
}

# === 2. Register blueprint ===
if ((Get-Content $mainPath) -notmatch "submissions_bp") {
    Copy-Item $mainPath "$mainPath.bak"
    Add-Content $mainPath @"
from smartscripts.api.v1.submissions import bp as submissions_bp
app.register_blueprint(submissions_bp, url_prefix='/api/v1')
"@
    Write-Host "✅ submissions_bp registered in main.py"
}

# === 3. Ensure Submission model ===
if ((Get-Content $modelsPath) -notmatch "class Submission") {
    Copy-Item $modelsPath "$modelsPath.bak"
    Add-Content $modelsPath @"
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128))
    filename = db.Column(db.String(256))
    grade = db.Column(db.Float)
    status = db.Column(db.String(32))
    feedback = db.Column(db.Text)
"@
    Write-Host "✅ Submission model stub added"
}

# === 4. Add React delete button and handler ===
if (Test-Path $frontendComponentPath) {
    Copy-Item $frontendComponentPath "$frontendComponentPath.bak"

    $reactContent = Get-Content $frontendComponentPath -Raw

    if ($reactContent -notmatch "handleDelete") {

        # Define JS delete handler
        $injection = @"
const handleDelete = async (submissionId) => {
    if (!window.confirm('Are you sure you want to delete this submission?')) return;
    try {
        const response = await fetch(\`/api/v1/submissions/\${submissionId}\`, {
            method: 'DELETE',
        });
        if (response.ok) {
            alert('Submission deleted');
            setSubmissions(prev => prev.filter(s => s.id !== submissionId));
        } else {
            const err = await response.json();
            alert(\`Error: \${err.error}\`);
        }
    } catch (e) {
        alert('Network error while deleting submission');
    }
};
"@

        # Inject JS function
        $reactContent = $reactContent -replace '(?s)(const\s+\[.*?\]\s*=\s*useState\(.*?\);?\s*)', "`$1`n$injection`n"

        # Inject Delete button in table row
        $reactContent = $reactContent -replace '(?<=<td>.*?</td>\s*)', "`$&<td><button onClick={() => handleDelete(submission.id)}>Delete</button></td>`n"

        Set-Content $frontendComponentPath $reactContent
        Write-Host "✅ Frontend delete logic injected"
    } else {
        Write-Host "⚠️ Frontend already contains delete logic"
    }
}

Write-Host "`n🎉 All changes completed successfully. Restart your server and rebuild the frontend."
