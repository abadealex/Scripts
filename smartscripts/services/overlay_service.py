import cv2
import os
import numpy as np

# Path to overlay assets (tick.png and cross.png) stored in `static/annotated/`
OVERLAY_DIR = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'annotated')
TICK_PATH = os.path.join(OVERLAY_DIR, 'tick.png')
CROSS_PATH = os.path.join(OVERLAY_DIR, 'cross.png')


def load_overlay_image(type_: str):
    """
    Load tick or cross image with alpha channel.
    """
    if type_ == 'tick':
        path = TICK_PATH
    elif type_ == 'cross':
        path = CROSS_PATH
    else:
        raise ValueError("Overlay type must be 'tick' or 'cross'")

    overlay = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if overlay is None:
        raise FileNotFoundError(f"Overlay image not found at: {path}")
    return overlay


def add_overlay(image: np.ndarray, overlay_type: str, position: tuple = (10, 10), scale: float = 0.15) -> np.ndarray:
    """
    Adds tick or cross overlay to a given image using alpha blending.

    Args:
        image (np.ndarray): Original BGR image
        overlay_type (str): 'tick' or 'cross'
        position (tuple): Top-left corner where overlay is placed (x, y)
        scale (float): Scaling factor for overlay image

    Returns:
        np.ndarray: Annotated image
    """
    overlay = load_overlay_image(overlay_type)

    # Resize overlay
    h, w = overlay.shape[:2]
    resized_overlay = cv2.resize(overlay, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    # Separate alpha and color
    overlay_rgb = resized_overlay[..., :3]
    mask = resized_overlay[..., 3:] / 255.0  # Normalize alpha channel

    x, y = position
    h, w = overlay_rgb.shape[:2]

    # Ensure overlay fits in image
    if y + h > image.shape[0] or x + w > image.shape[1]:
        raise ValueError("Overlay does not fit in image at specified position.")

    # Alpha blend overlay onto image
    roi = image[y:y+h, x:x+w]
    blended = (1.0 - mask) * roi + mask * overlay_rgb
    image[y:y+h, x:x+w] = blended.astype(np.uint8)

    return image
