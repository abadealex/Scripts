# gpt_explainer.py
# LLM calls for explanation generation using OpenAI API

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_explanation(answer_text, rubric_json):
    """
    Call GPT-4 to generate explanation of why an answer is correct or incorrect based on rubric.
    """
    prompt = (
        f"Given the following rubric:\n{rubric_json}\n\n"
        f"Explain why this answer is correct or incorrect:\n{answer_text}\n"
        "Provide a detailed reasoning trace."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        explanation = response['choices'][0]['message']['content']
        return explanation
    except Exception as e:
        return f"Error generating explanation: {e}"
