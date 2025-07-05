import os
from PIL import Image
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import openai

# Setup device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Initialize TrOCR
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-stage1")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-stage1")
model.to(device)

# OpenAI API key from env (make sure to set it!)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


def trocr_extract_with_confidence(image_path):
    """
    Extract text from image using TrOCR and return text + confidence score.
    """
    image = Image.open(image_path).convert("RGB")
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)

    # Generate with scores and return dict
    outputs = model.generate(
        pixel_values,
        output_scores=True,
        return_dict_in_generate=True,
        max_length=512,
        num_beams=5,
    )
    generated_ids = outputs.sequences
    scores = outputs.sequences_scores  # log probabilities tensor

    confidence = scores.exp().item()  # convert log prob to normal prob

    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text.strip(), confidence


def gpt4_vision_extract(image_path):
    """
    Use GPT-4 Vision (or DALL·E) API to extract text from image.
    This is a placeholder; you need your own GPT-4 Vision integration or API.
    """
    with open(image_path, "rb") as img_file:
        response = openai.Image.create(
            file=img_file,
            model="gpt-4-vision-preview",  # hypothetical model name
            task="extract_text"
        )
    extracted_text = response.get("text", "")
    return extracted_text.strip()


def gpt4_chat_refine(text):
    """
    Use GPT-4 chat to clean/refine extracted text.
    """
    if not text:
        return ""

    prompt = (
        "Please clean up and correct any errors in the following extracted text:\n\n"
        f"{text}\n\nCleaned text:"
    )

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000,
    )
    refined_text = completion.choices[0].message.content.strip()
    return refined_text


def extract_text_from_image(image_path, confidence_threshold=0.7, do_fallback=True, do_refine=True):
    """
    Extract text with TrOCR and fallback to GPT-4 Vision if confidence is low.
    Optionally refine text with GPT-4 Chat.
    
    confidence_threshold: below this, triggers fallback or review.
    """

    print("Running TrOCR with confidence estimation...")
    trocr_text, confidence = trocr_extract_with_confidence(image_path)
    print(f"TrOCR extracted text: {trocr_text}")
    print(f"Confidence score: {confidence:.4f}")

    gpt4_text = ""
    if do_fallback and (not trocr_text or confidence < confidence_threshold):
        print("TrOCR confidence low or empty text, falling back to GPT-4 Vision...")
        gpt4_text = gpt4_vision_extract(image_path)
        print(f"GPT-4 Vision extracted text: {gpt4_text}")

    final_text = gpt4_text if gpt4_text else trocr_text

    if do_refine and final_text:
        print("Refining extracted text with GPT-4 Chat...")
        final_text = gpt4_chat_refine(final_text)

    return final_text


if __name__ == "__main__":
    test_image = "sample_image.png"  # replace with your image file path
    extracted_text = extract_text_from_image(test_image)
    print("\nFinal Extracted Text:\n", extracted_text)
