"""
smartscripts.ai
---------------
Initialization of AI-related utilities and shared models for OCR, text matching,
rubric-based scoring, and question alignment.
"""

from sentence_transformers import SentenceTransformer
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch

# === Embedding Model for Text Matching ===
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# === TrOCR Model for OCR ===
ocr_processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
ocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
ocr_model.to(device)
embedding_model.to(device)  # Optional – SBERT works on CPU too

# === Expose all as shared access points ===
__all__ = [
    "embedding_model",
    "ocr_model",
    "ocr_processor",
    "device"
]
