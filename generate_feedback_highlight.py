import numpy as np
import cv2

img = np.zeros((100, 100, 4), dtype=np.uint8)

yellow = (0, 255, 255, 128)  # Yellow with 50% opacity

cv2.rectangle(img, (10, 10), (90, 90), yellow, thickness=-1)

cv2.imwrite('feedback_highlight.png', img)
print("feedback_highlight.png created")
