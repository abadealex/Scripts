import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import os

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()

        if text.strip():
            print(f"[Page {page_num+1}] Extracted text using PyMuPDF.")
            full_text += f"\n--- Page {page_num+1} ---\n{text}\n"
        else:
            print(f"[Page {page_num+1}] No text found, falling back to OCR.")
            images = convert_from_path(pdf_path, first_page=page_num + 1, last_page=page_num + 1)
            if images:
                image = images[0]
                ocr_text = pytesseract.image_to_string(image)
                full_text += f"\n--- Page {page_num+1} (OCR) ---\n{ocr_text}\n"
            else:
                print(f"[Page {page_num+1}] Unable to render image for OCR.")
    return full_text

def extract_text_from_folder(folder_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            print(f"Processing: {pdf_path}")
            text = extract_text_from_pdf(pdf_path)
            output_file = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_extracted.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"✅ Saved extracted text to {output_file}\n")

if __name__ == "__main__":
    input_folder = r"C:\Users\ALEX\Desktop\Smartscripts\smartscripts\app\static\uploads\student_scripts"
    output_folder = r"C:\Users\ALEX\Desktop\Smartscripts\output"
    extract_text_from_folder(input_folder, output_folder)

