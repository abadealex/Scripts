import os
import openai

# Ensure your API key is loaded from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_gpt(prompt: str, model: str = "gpt-4", temperature: float = 0.7, max_tokens: int = 300) -> str:
    """
    Call OpenAI's GPT model with a prompt and return the response text.
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"[GPT ERROR] {e}")
        return "Sorry, I couldn't generate a response."

def generate_feedback(question: str, student_answer: str, correct_answer: str) -> str:
    """
    Generates helpful feedback using GPT based on the student's answer.
    """
    prompt = f"""
You are a helpful teacher. Give constructive, specific feedback to a student.

Question: {question}
Student's Answer: {student_answer}
Correct Answer: {correct_answer}

Feedback:
"""
    return call_gpt(prompt)

def summarize_text(text: str) -> str:
    """
    Summarize a given text using GPT.
    """
    prompt = f"Summarize the following text in a few sentences:\n\n{text}"
    return call_gpt(prompt)

def explain_answer(question: str, correct_answer: str) -> str:
    """
    Explain why the correct answer is correct in a student-friendly way.
    """
    prompt = f"""
Explain the correct answer to the following question in a simple and clear way:

Question: {question}
Correct Answer: {correct_answer}

Explanation:
"""
    return call_gpt(prompt)
