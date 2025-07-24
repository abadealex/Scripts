# reasoning_trace.py
# Builds a trace of reasoning steps explaining why an answer was marked wrong

def build_reasoning_trace(rubric, student_answer):
    """
    Create a step-by-step reasoning trace comparing student answer to rubric.
    """
    trace = []
    for criterion, details in rubric.items():
        expected = details.get("expected_answer", "")
        weight = details.get("weight", 1)
        if expected.lower() not in student_answer.lower():
            trace.append(
                f"Criterion '{criterion}' was not met: expected '{expected}', "
                f"but answer did not include this. Weight: {weight}"
            )
        else:
            trace.append(f"Criterion '{criterion}' met.")
    if not trace:
        trace.append("Answer meets all rubric criteria.")
    return trace
