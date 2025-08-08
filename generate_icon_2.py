import numpy as np
import cv2

img = np.zeros((100, 100, 4), dtype=np.uint8)

purple = (255, 0, 255, 255)  # Purple BGRA

cv2.rectangle(img, (20, 20), (80, 80), purple, thickness=-1)

cv2.imwrite('icon_2.png', img)
print("icon_2.png created")

