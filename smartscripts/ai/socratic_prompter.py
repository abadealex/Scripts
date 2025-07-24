# socratic_prompter.py
# Generates follow-up Socratic questions to guide student improvement

def generate_socratic_prompt(answer_text, explanation_text):
    """
    Create a follow-up Socratic question to encourage student thinking.
    """
    base_prompt = (
        "Based on the student's answer and the explanation, "
        "generate a Socratic question that prompts the student to reflect and improve."
    )
    question = (
        f"{base_prompt}\n\nAnswer:\n{answer_text}\n\nExplanation:\n{explanation_text}\n\n"
        "Socratic Question:"
    )
    # For demonstration, just return a canned question or basic transformation
    # In production, integrate with GPT or a prompt-based generator
    return "What part of the rubric do you think your answer might have missed?"
