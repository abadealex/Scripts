from collections import defaultdict, Counter
from datetime import datetime
from typing import List, Dict, Optional
import csv
from smartscripts.models import AuditLog
from smartscripts.extensions import db


def compute_success_rates(results: List[Dict]) -> Dict[str, float]:
    question_totals = defaultdict(int)
    question_corrects = defaultdict(int)

    for result in results:
        qid = result['question_id']
        question_totals[qid] += 1
        if result['is_correct']:
            question_corrects[qid] += 1

    return {
        qid: question_corrects[qid] / question_totals[qid]
        for qid in question_totals
    }


def compute_average_score(results: List[Dict]) -> float:
    total_score = 0.0
    count = 0
    for result in results:
        if 'score' in result:
            total_score += result['score']
            count += 1
    return total_score / count if count else 0.0


def aggregate_feedback(results: List[Dict]) -> Dict[str, List[str]]:
    feedback_map = defaultdict(list)
    for result in results:
        qid = result['question_id']
        feedback = result.get('feedback')
        if feedback:
            feedback_map[qid].append(feedback)
    return feedback_map


def export_manual_corrections(csv_filepath: str = "manual_corrections.csv"):
    corrections = AuditLog.query.filter_by(action="manual_override").all()
    with open(csv_filepath, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["question_id", "old_text", "new_text", "reviewer", "timestamp"])
        for c in corrections:
            writer.writerow([
                c.question_id or "",
                (c.old_text or "").replace('"', '""'),
                (c.new_text or "").replace('"', '""'),
                c.user_id or "",
                c.timestamp.isoformat() if c.timestamp else ""
            ])
    print(f"Exported {len(corrections)} manual corrections to {csv_filepath}")


def compute_grading_distribution(results: List[Dict], bins: Optional[List[int]] = None) -> Dict[str, int]:
    """
    Computes score distribution histogram for analysis.
    Args:
        results: List of dicts with 'score' keys.
        bins: List of bin thresholds (e.g., [0, 50, 70, 85, 100]).

    Returns:
        Dict bin_label -> count of students.
    """
    if bins is None:
        bins = [0, 50, 70, 85, 100]

    distribution = Counter()
    for result in results:
        score = result.get("score", 0)
        for i in range(1, len(bins)):
            if bins[i - 1] <= score < bins[i]:
                label = f"{bins[i - 1]}–{bins[i]-1}"
                distribution[label] += 1
                break
        else:
            if score >= bins[-1]:
                distribution[f"{bins[-1]}+"] += 1

    return dict(distribution)


def average_manual_review_time() -> float:
    """
    Estimate average time (in seconds) taken for manual reviews by computing
    time difference between creation timestamps in audit logs.

    Returns:
        Average seconds per review (float)
    """
    reviews = AuditLog.query.filter_by(action="manual_override").order_by(AuditLog.timestamp).all()
    if len(reviews) < 2:
        return 0.0

    time_diffs = []
    for i in range(1, len(reviews)):
        delta = reviews[i].timestamp - reviews[i - 1].timestamp
        time_diffs.append(delta.total_seconds())

    return sum(time_diffs) / len(time_diffs)
