import numpy as np
import cv2
import os

# Create output directory if it doesn't exist
output_dir = os.path.join("static", "overlays")
os.makedirs(output_dir, exist_ok=True)

# Create a transparent image
img = np.zeros((100, 100, 4), dtype=np.uint8)

green = (0, 255, 0, 255)  # Green in BGRA

# Define tick points
points = np.array([[20, 50], [45, 75], [80, 20]], np.int32)
points = points.reshape((-1, 1, 2))

# Draw the tick
cv2.polylines(img, [points], isClosed=False, color=green, thickness=5)

# Save image
tick_path = os.path.join(output_dir, "tick.png")
cv2.imwrite(tick_path, img)
print("tick.png created at", tick_path)

