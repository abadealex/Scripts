# ocr_engine.py

from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch

# Load model and processor
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-stage1")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-stage1")

# Optional: Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


def extract_text_from_image(image_path):
    """
    Extract text from an image using Microsoft's TrOCR.
    """
    # Load and preprocess image
    image = Image.open(image_path).convert("RGB")
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)

    # Generate output IDs from model
    generated_ids = model.generate(pixel_values)

    # Decode output IDs to string
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    return generated_text


# Example usage
if __name__ == "__main__":
    test_image = "sample_image.png"  # Replace with your image path
    text = extract_text_from_image(test_image)
    print("Extracted Text:", text)
