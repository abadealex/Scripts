import numpy as np
import cv2

img = np.zeros((100, 100, 4), dtype=np.uint8)

blue = (255, 0, 0, 255)  # Blue BGRA

cv2.circle(img, (50, 50), 40, blue, thickness=-1)

cv2.imwrite('icon_1.png', img)
print("icon_1.png created")
