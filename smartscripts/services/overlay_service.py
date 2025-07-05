import cv2
import os
import numpy as np

# ✅ Set path to overlays folder (e.g., smartscripts/static/overlays/)
OVERLAY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'overlays'))

def load_overlay_image(type_: str) -> np.ndarray:
    """
    Load tick or cross image with alpha channel.

    Args:
        type_ (str): 'tick' or 'cross'

    Returns:
        np.ndarray: The overlay image with alpha channel
    """
    if type_ not in ['tick', 'cross']:
        raise ValueError("Overlay type must be 'tick' or 'cross'")

    path = os.path.join(OVERLAY_DIR, f'{type_}.png')

    if not os.path.exists(path):
        raise FileNotFoundError(f"Overlay image not found at: {path}")

    overlay = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if overlay is None:
        raise FileNotFoundError(f"Overlay image could not be read at: {path}")
    if overlay.shape[2] != 4:
        raise ValueError(f"Overlay image must have an alpha channel (4 channels), got {overlay.shape[2]}")

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

    # Resize overlay according to scale
    h, w = overlay.shape[:2]
    resized_overlay = cv2.resize(overlay, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    # Separate color and alpha channels
    overlay_rgb = resized_overlay[..., :3]
    alpha_mask = resized_overlay[..., 3:] / 255.0  # Normalize alpha channel to [0,1]

    x, y = position
    h, w = overlay_rgb.shape[:2]

    # Check if overlay fits within the image bounds
    if y + h > image.shape[0] or x + w > image.shape[1]:
        raise ValueError("Overlay does not fit in image at specified position.")

    # Region of interest on original image
    roi = image[y:y+h, x:x+w]

    # Blend overlay with ROI using alpha mask
    blended = (1.0 - alpha_mask) * roi + alpha_mask * overlay_rgb

    # Place blended region back into image
    image[y:y+h, x:x+w] = blended.astype(np.uint8)

    return image
