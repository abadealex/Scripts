# analytics/feedback_quality_metrics.py
def score_feedback_quality(comment: str) -> float:
    # Simple heuristic: score based on length & presence of constructive keywords
    keywords = ['improve', 'good', 'well done', 'consider', 'try', 'please']
    score = len(comment) / 200  # normalized length score (example)
    
    keyword_hits = sum(1 for k in keywords if k in comment.lower())
    score += 0.1 * keyword_hits
    return min(score, 1.0)  # cap score at 1.0

def feedback_quality_summary(feedback_list):
    scores = [score_feedback_quality(fb.get('comments', '')) for fb in feedback_list]
    avg_score = sum(scores) / len(scores) if scores else 0
    return {
        'average_quality_score': avg_score,
        'total_feedback': len(feedback_list)
    }
