import numpy as np
import cv2
import os

# Define output directory
output_dir = os.path.join("static", "overlays")
os.makedirs(output_dir, exist_ok=True)

# Create transparent canvas (BGRA)
img = np.zeros((100, 100, 4), dtype=np.uint8)

# Define colors
orange = (0, 165, 255, 255)  # Pencil tip - orange
gray = (160, 160, 160, 255)  # Pencil shaft - gray
white_translucent = (255, 255, 255, 100)  # Override box

# Draw pencil shaft (gray rectangle)
cv2.rectangle(img, (30, 60), (70, 65), gray, thickness=-1)

# Draw pencil tip (orange triangle)
tip_points = np.array([[70, 58], [75, 62], [70, 67]], np.int32).reshape((-1, 1, 2))
cv2.fillPoly(img, [tip_points], color=orange)

# Draw override box (semi-transparent white outline)
cv2.rectangle(img, (20, 20), (80, 80), white_translucent, thickness=2)

# Save image
filepath = os.path.join(output_dir, "manual_override.png")
cv2.imwrite(filepath, img)
print("manual_override.png created at:", filepath)

