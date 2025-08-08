import os
from typing import List
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from smartscripts.utils.file_io import ensure_folder_exists


def create_pdf_report(output_path: str, title: str = "Report", content: str = "") -> str:
    ensure_folder_exists(os.path.dirname(output_path))
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2.0, height - 72, title)

    c.setFont("Helvetica", 12)
    text_object = c.beginText(72, height - 108)
    for line in content.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)

    c.showPage()
    c.save()

    return output_path


def annotate_pdf_with_text(input_pdf_path: str, output_pdf_path: str, annotations: List[dict]):
    ensure_folder_exists(os.path.dirname(output_pdf_path))

    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        for ann in annotations:
            if ann['page'] == i:
                font_size = ann.get('font_size', 12)
                can.setFont("Helvetica", font_size)
                can.setFillColorRGB(1, 0, 0)
                can.drawString(ann['x'], ann['y'], ann['text'])
        can.save()
        packet.seek(0)
        overlay_pdf = PdfReader(packet)
        page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

    with open(output_pdf_path, 'wb') as f_out:
        writer.write(f_out)


def annotate_image_with_text(input_image_path: str, output_image_path: str, annotations: List[dict]):
    ensure_folder_exists(os.path.dirname(output_image_path))

    img = Image.open(input_image_path).convert("RGBA")
    txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    font_size = 20
    try:
                font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    for ann in annotations:
        fs = ann.get('font_size', font_size)
        try:
                    font = ImageFont.truetype("arial.ttf", fs)
        except IOError:
            font = ImageFont.load_default()
        color = ann.get('color', (255, 0, 0))
        draw.text((ann['x'], ann['y']), ann['text'], fill=color + (255,), font=font)

    combined = Image.alpha_composite(img, txt_layer)
    combined.convert("RGB").save(output_image_path)

