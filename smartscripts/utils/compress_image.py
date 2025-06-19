from PIL import Image
import os

def compress_image(input_path, output_path, max_size_kb=4000):
    img = Image.open(input_path)
    quality = 95
    while True:
        img.save(output_path, optimize=True, quality=quality)
        size_kb = os.path.getsize(output_path) / 1024
        if size_kb <= max_size_kb or quality <= 10:
            break
        quality -= 5
    return output_path
