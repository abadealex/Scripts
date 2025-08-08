from PIL import Image, ImageDraw, ImageFont
import os

def generate_icon_3():
    output_dir = "static/overlays"
    os.makedirs(output_dir, exist_ok=True)

    size = (64, 64)
    image = Image.new("RGBA", size, (255, 255, 255, 0))

    draw = ImageDraw.Draw(image)

    circle_color = (0, 120, 255, 255)  # Blue
    draw.ellipse((8, 8, 56, 56), fill=circle_color)

    try:
                font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    text = "3"

    # Use textbbox to get bounding box of the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(position, text, fill="white", font=font)

    output_path = os.path.join(output_dir, "icon_3.png")
    image.save(output_path)

if __name__ == "__main__":
    generate_icon_3()
    print("icon_3.png generated in static/overlays/")

