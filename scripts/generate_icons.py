import os
from PIL import Image, ImageDraw

# Define the output folder relative to this script
output_folder = os.path.join(os.path.dirname(__file__), '../static/images')

# Ensure the directory exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Helper function to save image to the output folder
def save_image(img, filename):
    path = os.path.join(output_folder, filename)
    img.save(path)
    print(f"Saved {filename} at {path}")

# Create a solid color tick icon
def create_tick():
    img = Image.new('RGBA', (40, 40), color='white')  # White background
    draw = ImageDraw.Draw(img)
    draw.line((10, 20, 20, 30), fill="green", width=3)
    draw.line((20, 30, 30, 10), fill="green", width=3)
    img = img.convert("RGB")  # Remove alpha channel
    save_image(img, 'tick.png')

# Create a solid color cross icon
def create_cross():
    img = Image.new('RGBA', (40, 40), color='white')
    draw = ImageDraw.Draw(img)
    draw.line((10, 10, 30, 30), fill="red", width=3)
    draw.line((10, 30, 30, 10), fill="red", width=3)
    img = img.convert("RGB")
    save_image(img, 'cross.png')

# Create a solid color half-tick icon
def create_half_tick():
    img = Image.new('RGBA', (40, 40), color='white')
    draw = ImageDraw.Draw(img)
    draw.line((10, 20, 30, 20), fill="orange", width=3)
    img = img.convert("RGB")
    save_image(img, 'half_tick.png')

# Create a solid feedback highlight icon
def create_feedback_highlight():
    img = Image.new('RGBA', (40, 40), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([5, 5, 35, 35], fill="yellow")
    img = img.convert("RGB")
    save_image(img, 'feedback_highlight.png')

# Create a solid manual override icon
def create_manual_override():
    img = Image.new('RGBA', (40, 40), color='white')
    draw = ImageDraw.Draw(img)
    draw.polygon([(10, 5), (30, 5), (20, 35)], fill="blue")
    img = img.convert("RGB")
    save_image(img, 'manual_override.png')

# Create a simple marked background icon
def create_marked_background():
    img = Image.new('RGB', (200, 200), color='lightgray')
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 190, 190], outline="black", width=5)
    save_image(img, 'marked_background.png')

if __name__ == '__main__':
    create_tick()
    create_cross()
    create_half_tick()
    create_feedback_highlight()
    create_manual_override()
    create_marked_background()
