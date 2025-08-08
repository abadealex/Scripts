import re

def clean_text(text):
    """
    Clean OCR extracted text by:
    - Removing extra whitespace
    - Fixing common OCR misreads (optional)
    - Removing non-printable characters
    """
    if not text:
        return ""

    # Remove non-printable/control characters
    text = ''.join(ch for ch in text if ch.isprintable())

    # Replace multiple whitespace with a single space
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    # Example fix: common OCR confusion between '0' and 'O' (optional)
    # text = text.replace('0', 'O')  

    return text

