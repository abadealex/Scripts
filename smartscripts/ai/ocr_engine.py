import os
import torch
import base64
from PIL import Image, ImageOps, ImageChops
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from pdf2image import convert_from_path
import openai

# === Setup ===
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load TrOCR model and processor
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-stage1")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-stage1")
model.to(device)

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
openai.api_key = OPENAI_API_KEY


# === Preprocessing (for mobile images) ===
def preprocess_image(image_path):
    image = Image.open(image_path)
    image = ImageOps.exif_transpose(image)
    image = image.convert("RGB")

    # Crop white borders
    bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if bbox:
        image = image.crop(bbox)

    return image


# === TrOCR Extraction ===
def trocr_extract_with_confidence(image_path):
    image = preprocess_image(image_path)
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)

    try:
        outputs = model.generate(
            pixel_values,
            output_scores=True,
            return_dict_in_generate=True,
            max_length=512,
            num_beams=5,
        )
        generated_ids = outputs.sequences
        scores = outputs.sequences_scores
        confidence = scores.exp().item()
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return text.strip(), confidence
    except Exception as e:
        print(f"[TrOCR] Error: {e}")
        return "", 0.0


# === GPT-4 Vision OCR Fallback ===
def gpt4_vision_extract(image_path):
    try:
        with open(image_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode("utf-8")

        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all readable handwritten text from this exam page:"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                    ],
                }
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[GPT-4 Vision] Error: {e}")
        return ""


# === GPT-4 Refinement ===
def gpt4_chat_refine(text):
    if not text:
        return ""

    prompt = (
        "The following text was extracted from a handwritten exam paper. "
        "Please correct any OCR or formatting errors:\n\n"
        f"{text}\n\nCleaned text:"
    )

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[GPT-4 Chat] Error: {e}")
        return text


# === Main Image Text Extraction Pipeline ===
def extract_text_from_image(image_path, confidence_threshold=0.7, do_fallback=True, do_refine=True):
    print(f"\n🔍 Processing {image_path} with TrOCR...")
    trocr_text, confidence = trocr_extract_with_confidence(image_path)
    print(f"📝 TrOCR text: {trocr_text}\n📈 Confidence: {confidence:.4f}")

    gpt4_text = ""
    if do_fallback and (not trocr_text or confidence < confidence_threshold):
        print("⚠️ Low confidence. Falling back to GPT-4 Vision...")
        gpt4_text = gpt4_vision_extract(image_path)
        print(f"📸 GPT-4 Vision text: {gpt4_text}")

    final_text = gpt4_text if gpt4_text else trocr_text

    if do_refine and final_text:
        print("✨ Refining with GPT-4 Chat...")
        final_text = gpt4_chat_refine(final_text)

    return final_text


# === PDF Batch Extraction Pipeline ===
def extract_text_from_pdf(pdf_path, output_text_path=None):
    print(f"\n📄 Extracting text from PDF: {pdf_path}")
    images = convert_from_path(pdf_path, dpi=300)
    extracted_texts = []

    for i, image in enumerate(images):
        img_path = f"temp_page_{i + 1}.png"
        image.save(img_path)
        text = extract_text_from_image(img_path)
        extracted_texts.append(f"--- Page {i+1} ---\n{text}")
        os.remove(img_path)

    full_text = "\n\n".join(extracted_texts)

    if output_text_path:
        with open(output_text_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"📝 Text saved to: {output_text_path}")

    return full_text


# === Run Example ===
if __name__ == "__main__":
    # For single image
    # result = extract_text_from_image("sample_image.png")

    # For multi-page student script (PDF)
    pdf_result = extract_text_from_pdf("student_script.pdf", output_text_path="ocr_output.txt")

    print("\n✅ Final Extracted Text:\n", pdf_result)
