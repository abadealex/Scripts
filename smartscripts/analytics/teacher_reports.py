# analytics/teacher_reports.py
from analytics.engagement_tracker import get_events
from collections import defaultdict
from datetime import datetime

def generate_teacher_report(teacher_id: int):
    events = get_events()
    teacher_events = [e for e in events if e['user_id'] == teacher_id]

    feature_counts = defaultdict(int)
    for e in teacher_events:
        feature_counts[e['feature']] += 1

    report = {
        'teacher_id': teacher_id,
        'report_generated_at': datetime.utcnow().isoformat(),
        'feature_usage_counts': feature_counts
    }
    return report

