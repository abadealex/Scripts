# scripts/test_front_page_scoring.py

import os
from smartscripts.ai.ocr_engine import (
    extract_text_lines_from_image,
    score_front_page,
    is_probable_front_page,
    detect_keywords_with_positions
)

def test_folder(folder_path):
    for filename in sorted(os.listdir(folder_path)):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        image_path = os.path.join(folder_path, filename)
        print(f"\n🖼️ {filename}")
        lines = extract_text_lines_from_image(image_path)
        text = "\n".join(lines)

        score = score_front_page(text, lines)
        print(f"📈 Score: {score:.2f} ({'✅ front page' if is_probable_front_page(score) else '❌ not front page'})")

        matches = detect_keywords_with_positions(lines)
        for match in matches:
            print(f"🔍 Line {match['line'] + 1}: found keyword '{match['keyword']}'")

if __name__ == "__main__":
    # ✅ Update this path to your image folder
    test_folder("C:/Users/ALEX/Desktop/Smartscripts/data/scanned_images/")

