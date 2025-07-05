import numpy as np
import cv2

# Create a transparent 100x100 image (4 channels: BGRA)
img = np.zeros((100, 100, 4), dtype=np.uint8)

# Draw red lines forming a cross (thickness=5)
color = (0, 0, 255, 255)  # Red color in BGRA with full opacity

cv2.line(img, (20, 20), (80, 80), color, thickness=5)
cv2.line(img, (80, 20), (20, 80), color, thickness=5)

# Save as PNG with transparency
cv2.imwrite('cross.png', img)
print("cross.png created")

