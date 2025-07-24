import collections
from typing import Dict, Any

# Dummy in-memory data store for overrides and grading history
grading_history = [
    {"grader_id": "g1", "student_id": "s1", "score": 3, "override": False},
    {"grader_id": "g1", "student_id": "s2", "score": 2, "override": True},
    {"grader_id": "g2", "student_id": "s3", "score": 1, "override": False},
    # Add more entries for realistic audit
]

def collect_override_stats() -> Dict[str, int]:
    """Count overrides per grader."""
    overrides = collections.Counter()
    for record in grading_history:
        if record["override"]:
            overrides[record["grader_id"]] += 1
    return dict(overrides)

def generate_bias_heatmap() -> Dict[str, Any]:
    """
    Simple example bias heatmap data structure.
    In real case, analyze grading deviations by grader, student group, etc.
    """
    bias_map = {
        "g1": {"avg_score": 2.5, "overrides": 5},
        "g2": {"avg_score": 3.0, "overrides": 1},
    }
    return bias_map

def generate_bias_report(batch_id: str) -> Dict[str, Any]:
    """
    Generate a comprehensive bias report for a batch.
    Batch id can filter grading history if implemented.
    """
    override_stats = collect_override_stats()
    heatmap = generate_bias_heatmap()
    return {
        "batch_id": batch_id,
        "override_stats": override_stats,
        "bias_heatmap": heatmap,
        "summary": "Report generated successfully."
    }
