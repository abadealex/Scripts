from pdf2image import convert_from_path
import os

def convert_pdf_to_images(pdf_path, output_folder):
    poppler_path = r"C:\Users\ALEX\Downloads\poppler-24.08.0\Library\bin"  # Optional but safe
    images = convert_from_path(pdf_path, poppler_path=poppler_path)
    image_paths = []
    for i, img in enumerate(images):
        img_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{i+1}.png")
        img.save(img_path, 'PNG')
        image_paths.append(img_path)
    return image_paths
