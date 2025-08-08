import numpy as np
import cv2

img = np.zeros((100, 100, 4), dtype=np.uint8)

gray = (200, 200, 200, 100)  # Light gray with 40% opacity

cv2.rectangle(img, (0, 0), (100, 100), gray, thickness=-1)

cv2.imwrite('marked_background.png', img)
print("marked_background.png created")

