import collections
from typing import Dict, Any
from flask import Blueprint, jsonify

from smartscripts.utils.file_ops import (
    duplicate_manifest_for_reference,
    update_manifest
)

# Define Blueprint
bias_bp = Blueprint('bias_bp', __name__)

# Dummy in-memory data store for overrides and grading history
grading_history = [
    {"grader_id": "g1", "student_id": "s1", "score": 3, "override": False},
    {"grader_id": "g1", "student_id": "s2", "score": 2, "override": True},
    {"grader_id": "g2", "student_id": "s3", "score": 1, "override": False},
    # Add more entries here as needed
]


def collect_override_stats() -> Dict[str, int]:
    """
    Count number of overrides performed by each grader.

    Returns:
        A dictionary mapping grader_id to override count.
    """
    overrides = collections.Counter()
    for record in grading_history:
        if record.get("override"):
            overrides[record["grader_id"]] += 1
    return dict(overrides)


def generate_bias_heatmap() -> Dict[str, Any]:
    """
    Simulate generation of a grading bias heatmap.

    Returns:
        A dictionary mapping each grader to their average score and override count.
    """
    bias_map = {
        "g1": {"avg_score": 2.5, "overrides": 5},
        "g2": {"avg_score": 3.0, "overrides": 1},
        # Add more graders with statistics as needed
    }
    return bias_map


def generate_bias_report(batch_id: str) -> Dict[str, Any]:
    """
    Generate a full bias report for a specific batch.

    Args:
        batch_id: The identifier of the test batch.

    Returns:
        A structured report with override stats and bias heatmap.
    """
    override_stats = collect_override_stats()
    heatmap = generate_bias_heatmap()
    return {
        "batch_id": batch_id,
        "override_stats": override_stats,
        "bias_heatmap": heatmap,
        "summary": "Bias report generated successfully."
    }


# Route to expose bias report via API
@bias_bp.route('/bias-report/<string:batch_id>', methods=['GET'])
def bias_report(batch_id):
    """
    Endpoint to retrieve grading bias report for a batch.
    """
    report = generate_bias_report(batch_id)
    return jsonify(report)
