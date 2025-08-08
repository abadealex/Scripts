import os
import re
import base64
import multiprocessing
from pathlib import Path
from typing import List, Tuple, Optional

import torch
from PIL import Image, ImageOps, ImageChops
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from pdf2image import convert_from_path

# === OpenAI (Optional) ===
try:
    import openai
except ImportError:
    openai = None
    print("⚠️ OpenAI not installed. GPT-based features will be disabled.")

# === Device & Model Setup ===
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
model.to(device)
model.eval()

# === Constants ===
KEYWORDS = [
    "name", "student name", "full name",
    "id", "student id", "reg no", "registration number"
]

def run_ocr_on_test(pdf_path: str) -> dict:
    images = convert_from_path(pdf_path, dpi=300)
    if not images:
        return {"name": "", "id": "", "confidence": 0.0}

    first_page_path = Path("temp_first_page.png")
    images[0].save(first_page_path)

    text = extract_text_from_image(str(first_page_path))
    first_page_path.unlink()

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    name = ""
    student_id = ""
    for line in lines:
        if not student_id and re.match(r"^[A-Za-z0-9\-/]{5,12}$", line):
            student_id = line
        elif not name and re.match(r"^[A-Z][a-zA-Z]{1,}\s[A-Z]?[a-zA-Z]{1,}$", line):
            name = line
        if name and student_id:
            break

    confidence = estimate_ocr_confidence(text)
    return {"name": name, "id": student_id, "confidence": confidence}

# === Helper Functions ===
def preprocess_image(image_path: str) -> Image.Image:
    image = Image.open(image_path)
    image = ImageOps.exif_transpose(image).convert("RGB")
    bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    return image.crop(bbox) if bbox else image

def crop_region(image: Image.Image, box: Tuple[int, int, int, int]) -> Image.Image:
    return image.crop(box)

def estimate_ocr_confidence(text: str) -> float:
    if not text.strip():
        return 0.0
    confidence = 1.0
    if re.search(r"[#@~%^*]{2,}", text):
        confidence -= 0.3
    if len(text.strip()) < 5:
        confidence -= 0.2
    return max(confidence, 0.0)

def run_tr_ocr(image: Image.Image) -> str:
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)
    with torch.no_grad():
        generated_ids = model.generate(pixel_values)
        predicted_texts = processor.batch_decode(generated_ids, skip_special_tokens=True)
    return predicted_texts[0].strip() if predicted_texts else ""

def trocr_extract_with_confidence(image_path: str) -> Tuple[str, float]:
    image = preprocess_image(image_path)
    text = run_tr_ocr(image)
    confidence = estimate_ocr_confidence(text)
    return text, confidence

def gpt4_vision_extract(image_path: str) -> str:
    if not openai or not os.getenv("OPENAI_API_KEY"):
        print("⚠️ GPT-4 Vision skipped: OpenAI not available or API key not set.")
        return ""

    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        with open(image_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all readable handwritten text from this exam page:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
                ]
            }],
            max_tokens=1024
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[GPT-4 Vision Error] {e}")
        return ""

def gpt4_chat_refine(text: str) -> str:
    if not openai or not os.getenv("OPENAI_API_KEY"):
        print("⚠️ GPT-4 Chat skipped: OpenAI not available or API key not set.")
        return text

    if not text:
        return ""
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        prompt = (
            "The following text was extracted from a handwritten exam paper. "
            "Please correct any OCR or formatting errors:\n\n"
            f"{text}\n\nCleaned text:"
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[GPT-4 Chat Error] {e}")
        return text

def extract_text_from_image(image_path: str, confidence_threshold=0.7, do_fallback=True, do_refine=True) -> str:
    print(f"\n📄 Processing {image_path} with TrOCR...")
    trocr_text, confidence = trocr_extract_with_confidence(image_path)
    print(f"🔍 TrOCR text: {trocr_text}\n📈 Confidence: {confidence:.4f}")

    final_text = trocr_text
    if do_fallback and (not trocr_text or confidence < confidence_threshold):
        print("⚠️ Low confidence. Falling back to GPT-4 Vision...")
        vision_text = gpt4_vision_extract(image_path)
        if vision_text:
            print(f"🧠 GPT-4 Vision text: {vision_text}")
            final_text = vision_text

    if do_refine and final_text:
        print("✨ Refining with GPT-4 Chat...")
        final_text = gpt4_chat_refine(final_text)

    return final_text

def _ocr_page(index: int, image: Image.Image) -> str:
    temp_image = Path(f"temp_page_{index + 1}.png")
    image.save(temp_image)
    page_text = extract_text_from_image(str(temp_image))
    temp_image.unlink()
    return f"--- Page {index + 1} ---\n{page_text}"

def extract_text_from_pdf(pdf_path: str, output_text_path: Optional[str] = None) -> str:
    print(f"\n📄 Extracting from PDF: {pdf_path}")
    images = convert_from_path(pdf_path, dpi=300)
    with multiprocessing.Pool() as pool:
        results = pool.starmap(_ocr_page, [(i, img) for i, img in enumerate(images)])

    joined_text = "\n\n".join(results)
    if output_text_path:
        with open(output_text_path, "w", encoding="utf-8") as f:
            f.write(joined_text)
        print(f"✅ Saved to {output_text_path}")

    return joined_text

def extract_text_lines_from_image(image_path: str) -> List[str]:
    text = extract_text_from_image(image_path)
    return [line.strip() for line in text.split("\n") if line.strip()]

def score_front_page(text: str, lines: List[str]) -> float:
    matched_keywords = 0
    top_hits = 0
    for i, line in enumerate(lines[:10]):
        for keyword in KEYWORDS:
            if re.search(rf"\b{keyword}\b", line.lower()):
                matched_keywords += 1
                if i < 5:
                    top_hits += 1
    if matched_keywords == 0:
        return 0.0
    weighted_score = matched_keywords + 0.5 * top_hits
    normalized_score = min(weighted_score / (len(KEYWORDS) + 5), 1.0)
    return round(normalized_score, 3)

def is_probable_front_page(score: float, threshold: float = 0.6) -> bool:
    return score >= threshold

def detect_keywords_with_positions(lines: List[str]) -> List[dict]:
    matches = []
    for i, line in enumerate(lines):
        for keyword in KEYWORDS:
            if re.search(rf"\b{keyword}\b", line.lower()):
                matches.append({'line': i, 'keyword': keyword})
    return matches

def extract_name_id_from_image(image_path: str) -> Tuple[str, str]:
    full_text = extract_text_from_image(image_path)
    lines = [line.strip() for line in full_text.split("\n") if line.strip()]
    
    name = ""
    student_id = ""
    for line in lines:
        if not student_id and re.match(r"^[A-Za-z0-9\-/]{5,12}$", line):
            student_id = line
        elif not name and re.match(r"^[A-Z][a-zA-Z]{1,}\s[A-Z]?[a-zA-Z]{1,}$", line):
            name = line
        if name and student_id:
            break
    
    return name, student_id
