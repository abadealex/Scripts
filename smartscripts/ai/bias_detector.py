# bias_detector.py
# Audits grading history to detect systemic bias patterns

import statistics

def detect_bias(grading_data):
    """
    Analyze grading data to find bias patterns.
    grading_data: list of dicts, each with keys: grader_id, student_group, score
    Returns a summary of detected bias.
    """
    group_scores = {}
    for record in grading_data:
        group = record['student_group']
        score = record['score']
        group_scores.setdefault(group, []).append(score)

    bias_report = {}
    overall_avg = statistics.mean([rec['score'] for rec in grading_data])

    for group, scores in group_scores.items():
        avg = statistics.mean(scores)
        deviation = avg - overall_avg
        bias_report[group] = {
            'average_score': avg,
            'deviation_from_overall': deviation,
            'count': len(scores),
            'biased': abs(deviation) > 5  # example threshold
        }
    return bias_report
