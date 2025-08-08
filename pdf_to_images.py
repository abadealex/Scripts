from pdf2image import convert_from_path
import os

# Absolute path to your PDF file
pdf_path = r"C:\Users\ALEX\Desktop\Smartscripts\uploads\submissions\test_id_A\student_123\original.pdf"

# Folder where PNG files will be saved (make sure this folder exists)
output_folder = r"C:\Users\ALEX\Desktop\Smartscripts\uploads\submissions\test_id_A\student_123"

# Path to your Poppler bin folder (adjust if your Poppler is somewhere else)
poppler_path = r"C:\poppler-22.04.0\bin"

# Convert PDF to list of images (one image per page)
images = convert_from_path(pdf_path, dpi=200, poppler_path=poppler_path)

# Save each page as page_1.png, page_2.png, etc.
for i, image in enumerate(images, start=1):
    image_path = os.path.join(output_folder, f"page_{i}.png")
    image.save(image_path, "PNG")

print(f"✅ Generated {len(images)} page(s) as PNG images in: {output_folder}")

