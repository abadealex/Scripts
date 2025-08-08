import numpy as np
import cv2
import os

# Output directory
output_dir = os.path.join("static", "overlays")
os.makedirs(output_dir, exist_ok=True)

def save_image(filename, img):
    path = os.path.join(output_dir, filename)
    cv2.imwrite(path, img)
    print(f"{filename} saved at {path}")

# 1. cross.png – red cross
def create_cross():
    img = np.zeros((150, 150, 4), dtype=np.uint8)
    red = (0, 0, 255, 255)
    cv2.line(img, (30, 30), (120, 120), red, 8, cv2.LINE_AA)
    cv2.line(img, (120, 30), (30, 120), red, 8, cv2.LINE_AA)
    save_image("cross.png", img)

# 2. tick.png – green tick
def create_tick():
    img = np.zeros((150, 150, 4), dtype=np.uint8)
    green = (0, 255, 0, 255)
    pts = np.array([[30, 80], [65, 115], [120, 30]], np.int32).reshape((-1, 1, 2))
    cv2.polylines(img, [pts], False, green, 8, cv2.LINE_AA)
    save_image("tick.png", img)

# 3. half_tick.png – green tick with diagonal line
def create_half_tick():
    img = np.zeros((150, 150, 4), dtype=np.uint8)
    green = (0, 255, 0, 255)
    pts = np.array([[30, 80], [65, 115], [120, 30]], np.int32).reshape((-1, 1, 2))
    cv2.polylines(img, [pts], False, green, 8, cv2.LINE_AA)
    cv2.line(img, (20, 20), (130, 130), green, 10, cv2.LINE_AA)
    save_image("half_tick.png", img)

# 4. feedback_highlight.png – yellow transparent rectangle
def create_feedback_highlight():
    img = np.zeros((150, 150, 4), dtype=np.uint8)
    yellow = (0, 255, 255, 100)
    cv2.rectangle(img, (20, 20), (130, 130), yellow, thickness=-1)
    save_image("feedback_highlight.png", img)

# 5. icon_1.png – solid blue circle
def create_icon_1():
    img = np.zeros((150, 150, 4), dtype=np.uint8)
    blue = (255, 0, 0, 255)
    cv2.circle(img, (75, 75), 50, blue, thickness=-1, lineType=cv2.LINE_AA)
    save_image("icon_1.png", img)

# 6. icon_2.png – solid purple square
def create_icon_2():
    img = np.zeros((150, 150, 4), dtype=np.uint8)
    purple = (255, 0, 255, 255)
    cv2.rectangle(img, (40, 40), (110, 110), purple, thickness=-1)
    save_image("icon_2.png", img)

# 7. icon_3.png – solid orange triangle
def create_icon_3():
    img = np.zeros((150, 150, 4), dtype=np.uint8)
    orange = (0, 165, 255, 255)  # BGR for orange
    pts = np.array([[75, 30], [30, 120], [120, 120]], np.int32).reshape((-1,1,2))
    cv2.fillPoly(img, [pts], orange, lineType=cv2.LINE_AA)
    save_image("icon_3.png", img)

# 8. manual_override.png – blue square with white M letter (150x150 to match others)
def create_manual_override():
    img = np.zeros((150, 150, 4), dtype=np.uint8)
    blue = (255, 0, 0, 255)
    cv2.rectangle(img, (20, 20), (130, 130), blue, thickness=-1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'M', (45, 115), font, 4, (255, 255, 255, 255), 10, cv2.LINE_AA)
    save_image("manual_override.png", img)

# 9. marked_background.png – light gray translucent background rectangle (150x150)
def create_marked_background():
    img = np.zeros((150, 150, 4), dtype=np.uint8)
    gray = (200, 200, 200, 120)  # light gray + transparency
    cv2.rectangle(img, (0, 0), (150, 150), gray, thickness=-1)
    save_image("marked_background.png", img)

# 10. crossed_full_tick.png – green tick with red cross on top (150x150)
def create_crossed_full_tick():
    img = np.zeros((150, 150, 4), dtype=np.uint8)
    green = (0, 255, 0, 255)
    red = (0, 0, 255, 255)
    pts = np.array([[30, 80], [65, 115], [120, 30]], np.int32).reshape((-1,1,2))
    cv2.polylines(img, [pts], False, green, 8, cv2.LINE_AA)
    cv2.line(img, (30, 30), (120, 120), red, 8, cv2.LINE_AA)
    cv2.line(img, (120, 30), (30, 120), red, 8, cv2.LINE_AA)
    save_image("crossed_full_tick.png", img)

# Generate all images
create_cross()
create_tick()
create_half_tick()
create_feedback_highlight()
create_icon_1()
create_icon_2()
create_icon_3()
create_manual_override()
create_marked_background()
create_crossed_full_tick()

