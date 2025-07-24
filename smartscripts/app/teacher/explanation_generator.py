from smartscripts.ai.gpt_explainer import generate_explanation
from smartscripts.ai.reasoning_trace import build_reasoning_trace

def generate_detailed_explanation(answer: str, rubric_id: str) -> str:
    """
    Coordinate the generation of a reasoning trace and GPT explanation text.
    """
    trace = build_reasoning_trace(answer, rubric_id)
    explanation = generate_explanation(answer=answer, rubric_id=rubric_id)
    detailed = f"Reasoning Trace:\n{trace}\n\nGPT Explanation:\n{explanation}"
    return detailed
