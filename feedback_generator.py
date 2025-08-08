# feedback_generator.py
# 📝 NEW: Natural language feedback generator

import difflib
import re


class FeedbackGenerator:
    def __init__(self, similarity_threshold=0.7):
        self.similarity_threshold = similarity_threshold

    def clean_text(self, text):
        """Normalize whitespace and lowercase text for fair comparison."""
        text = text.strip().lower()
        text = re.sub(r'\s+', ' ', text)
        return text

    def calculate_similarity(self, student_answer, model_answer):
        """Return a similarity ratio between two strings."""
        s = difflib.SequenceMatcher(None, student_answer, model_answer)
        return s.ratio()

    def generate_feedback(self, student_answer, model_answer):
        """Generate natural language feedback comparing answers."""
        clean_student = self.clean_text(student_answer)
        clean_model = self.clean_text(model_answer)
        similarity = self.calculate_similarity(clean_student, clean_model)

        if not clean_student:
            return "You left this question blank. Make sure to attempt every question, even if you're unsure."

        if similarity >= 0.9:
            return "Excellent answer! You covered all the key points accurately."
        elif similarity >= 0.7:
            return "Good attempt. You've captured some key ideas, but try to be more specific or complete."
        elif similarity >= 0.5:
            return "Partially correct. Review the main concepts and try to express your answer more clearly."
        else:
            return "Your answer doesn't align with the expected response. Revisit the material and focus on the core concepts."

    def batch_generate(self, answers, model_answers):
        """Generate feedback for multiple answers."""
        feedback_list = []
        for student, model in zip(answers, model_answers):
            feedback = self.generate_feedback(student, model)
            feedback_list.append(feedback)
        return feedback_list


# Example usage
if __name__ == "__main__":
    generator = FeedbackGenerator()
    
    student_ans = "The water cycle involves evaporation and rainfall."
    model_ans = "The water cycle includes evaporation, condensation, and precipitation."

    feedback = generator.generate_feedback(student_ans, model_ans)
    print("Feedback:", feedback)

