# smartscripts/test_marking.py

from marking_pipeline import mark_submission
import cv2

image_path = "examples/student_answer.jpg"
expected_answer = "Photosynthesis is the process by which plants make food using sunlight."

student_text, score, annotated = mark_submission(image_path, expected_answer)

print(f"Student wrote: {student_text}")
print(f"Similarity score: {score:.2f}")

cv2.imwrite("output/annotated_result.png", annotated)

