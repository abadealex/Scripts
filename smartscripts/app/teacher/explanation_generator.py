from smartscripts.ai.gpt_explainer import generate_explanation
from smartscripts.ai.reasoning_trace import build_reasoning_trace
from smartscripts.utils.file_ops import (
    duplicate_manifest_for_reference,
    update_manifest
)

def generate_detailed_explanation(answer: str, rubric_id: str) -> str:
    """
    Generates a detailed explanation including both a reasoning trace and a GPT explanation.

    Args:
        answer (str): The student's answer.
        rubric_id (str): The rubric ID used for evaluation.

    Returns:
        str: Combined explanation string.
    """
    trace = build_reasoning_trace(answer, rubric_id)
    explanation = generate_explanation(answer=answer, rubric_id=rubric_id)

    return (
        f"?? Reasoning Trace:\n{trace}\n\n"
        f"?? GPT Explanation:\n{explanation}"
    )
