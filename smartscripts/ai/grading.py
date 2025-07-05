# smartscripts/ai/grading.py

def mark_submission(file_path, guide):
    # Dummy grading logic – replace with actual AI or grading process
    print(f"[INFO] Grading file: {file_path} using guide: {guide.title}")
    
    return {
        "grade": 85.0,
        "feedback": "Good job overall. Review question 3.",
        "question_scores": [
            {"question_number": 1, "score": 5, "is_correct": True},
            {"question_number": 2, "score": 4, "is_correct": True},
            {"question_number": 3, "score": 2, "is_correct": False},
        ],
        "ai_confidence": 0.92,
    }
