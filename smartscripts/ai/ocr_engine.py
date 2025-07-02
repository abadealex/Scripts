# smartscripts/ai/ocr_engine.py
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch
import os

# Load model and processor once (small model for now)
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def extract_text_from_image(image_path):
    image = Image.open(image_path).convert("RGB")
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text.strip()


# smartscripts/ai/text_matching.py
from sentence_transformers import SentenceTransformer, util
import numpy as np

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_similarity(student_answer, expected_answer):
    embeddings = model.encode([student_answer, expected_answer], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return similarity.item()


def is_answer_correct(student_answer, expected_answer, threshold=0.7):
    score = get_similarity(student_answer, expected_answer)
    return score >= threshold, score


# smartscripts/services/overlay_service.py
import cv2
import numpy as np
import os

TICK_PATH = os.path.join("smartscripts", "app", "static", "annotated", "tick.png")
CROSS_PATH = os.path.join("smartscripts", "app", "static", "annotated", "cross.png")

def overlay_image(base_img, overlay_img, pos):
    x, y = pos
    h, w, _ = overlay_img.shape
    overlay = overlay_img[:, :, :3]
    mask = overlay_img[:, :, 3:] / 255.0
    roi = base_img[y:y+h, x:x+w]
    base_img[y:y+h, x:x+w] = (1.0 - mask) * roi + mask * overlay
    return base_img


def mark_answer_on_image(image_path, is_correct, position):
    base_img = cv2.imread(image_path)
    overlay_path = TICK_PATH if is_correct else CROSS_PATH
    overlay_img = cv2.imread(overlay_path, cv2.IMREAD_UNCHANGED)
    result_img = overlay_image(base_img, overlay_img, position)
    marked_path = image_path.replace("answers", "marked")
    cv2.imwrite(marked_path, result_img)
    return marked_path
