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

# === Import utility functions and classes from submodules ===
from .gpt_explainer import generate_explanation
from .socratic_prompter import generate_socratic_prompt
from .reasoning_trace import build_reasoning_trace
from .bias_detector import detect_bias
from .versioning import VersionControl

# === Export all symbols for convenience ===
__all__ = [
    "embedding_model",
    "ocr_model",
    "ocr_processor",
    "device",
    'generate_explanation',
    'generate_socratic_prompt',
    'build_reasoning_trace',
    'detect_bias',
    'VersionControl'
]
