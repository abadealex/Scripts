import os
import json
from transformers import pipeline

# Load a transformer model for text generation (replace with OpenAI API if preferred)
generator = pipeline("text-generation", model="gpt2")

def generate_feedback(question: str, student_answer: str, correct_answer: str) -> str:
    prompt = f"""
Question: {question}
Student Answer: {student_answer}
Correct Answer: {correct_answer}

Provide specific, constructive feedback to help the student improve.
"""
    response = generator(prompt, max_length=100, num_return_sequences=1)
    return response[0]['generated_text'].strip()

def generate_feedback_batch(qa_list):
    feedback_list = []
    for qa in qa_list:
        feedback = generate_feedback(
            qa['question'],
            qa['student_answer'],
            qa['correct_answer']
        )
        feedback_list.append({
            "question": qa['question'],
            "feedback": feedback
        })
    return feedback_list

def save_feedback(test_id: str, student_id: str, feedback_data):
    """
    Save generated feedback JSON to uploads/feedback/<test_id>/<student_id>_feedback.json
    """
    feedback_dir = os.path.join("uploads", "feedback", test_id)
    os.makedirs(feedback_dir, exist_ok=True)

    feedback_path = os.path.join(feedback_dir, f"{student_id}_feedback.json")
    with open(feedback_path, "w") as f:
        json.dump(feedback_data, f, indent=2)
    print(f"[INFO] Feedback saved to {feedback_path}")

if __name__ == "__main__":
    # Example QA batch
    sample_qa = [{
        "question": "What is the capital of France?",
        "student_answer": "Berlin",
        "correct_answer": "Paris"
    }]

    feedbacks = generate_feedback_batch(sample_qa)

    for i, fb in enumerate(feedbacks):
        print(f"Q: {fb['question']}\nFeedback: {fb['feedback']}\n")

    # Example saving feedback for test_id and student_id
    test_id = "test_id_A"
    student_id = "student_123"
    save_feedback(test_id, student_id, feedbacks)
