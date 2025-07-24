from PIL import Image

def merge_images_vertically(image_paths, output_path):
    images = [Image.open(p) for p in image_paths]
    widths, heights = zip(*(img.size for img in images))

    total_height = sum(heights)
    max_width = max(widths)

    merged_image = Image.new('RGB', (max_width, total_height), color=(255, 255, 255))

    y_offset = 0
    for img in images:
        merged_image.paste(img, (0, y_offset))
        y_offset += img.height

    merged_image.save(output_path)
