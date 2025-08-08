import numpy as np
import cv2

# Create transparent canvas
img = np.zeros((150, 150, 4), dtype=np.uint8)

# Color: Green with full opacity (BGRA)
green = (0, 255, 0, 255)

# Full tick mark: two connected lines (checkmark shape)
tick_points = np.array([[30, 80], [60, 110], [110, 40]], np.int32).reshape((-1, 1, 2))
cv2.polylines(img, [tick_points], isClosed=False, color=green, thickness=8, lineType=cv2.LINE_AA)

# Green cross-out line from top-left to bottom-right
cv2.line(img, (20, 20), (130, 130), green, thickness=10, lineType=cv2.LINE_AA)

# Save the image
cv2.imwrite('crossed_full_tick.png', img)
print("crossed_full_tick.png created")

