from smartscripts.utils.pdf_helpers import pdf_to_images

pdf_path = "C:/Users/ALEX/Desktop/Smartscripts/data/scanned_images/mgd scrip-images-0-merged.pdf"
output_dir = "C:/Users/ALEX/Desktop/Smartscripts/data/scanned_images"

images = pdf_to_images(pdf_path, output_folder=output_dir)
print(f"✅ Converted {len(images)} page(s) into images at: {output_dir}")

