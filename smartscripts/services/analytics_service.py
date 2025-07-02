from collections import defaultdict
from typing import List, Dict, Tuple

def compute_success_rates(results: List[Dict]) -> Dict[str, float]:
    """
    Calculate success rates per question.
    Args:
        results: List of dicts like {'student_id': ..., 'question_id': ..., 'is_correct': bool}
    Returns:
        Dict mapping question_id -> success rate (0.0 to 1.0)
    """
    question_totals = defaultdict(int)
    question_corrects = defaultdict(int)

    for result in results:
        qid = result['question_id']
        question_totals[qid] += 1
        if result['is_correct']:
            question_corrects[qid] += 1

    success_rates = {
        qid: (question_corrects[qid] / question_totals[qid]) if question_totals[qid] > 0 else 0.0
        for qid in question_totals
    }
    return success_rates

def aggregate_feedback(results: List[Dict]) -> Dict[str, List[str]]:
    """
    Aggregate feedback comments per question.
    Args:
        results: List of dicts like {'question_id': ..., 'feedback': str}
    Returns:
        Dict mapping question_id -> list of feedback strings
    """
    feedback_map = defaultdict(list)
    for result in results:
        qid = result['question_id']
        feedback = result.get('feedback')
        if feedback:
            feedback_map[qid].append(feedback)
    return feedback_map

def compute_average_score(results: List[Dict]) -> float:
    """
    Compute average score across all questions and students.
    Each result dict expected to have 'score' key.
    """
    total_score = 0.0
    count = 0
    for result in results:
        if 'score' in result:
            total_score += result['score']
            count += 1
    return total_score / count if count > 0 else 0.0
