import os
import cv2
import numpy as np

# Directory where tick/cross images are stored
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
    if overlay is None or overlay.shape[2] != 4:
        raise ValueError(f"Overlay image must exist and have 4 channels (including alpha).")

    return overlay


def rotate_image(img: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate image around its center by given angle in degrees.

    Args:
        img (np.ndarray): Image to rotate
        angle (float): Rotation angle in degrees

    Returns:
        np.ndarray: Rotated image
    """
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))


def add_overlay(
    image: np.ndarray,
    overlay_type: str,
    position: tuple = (10, 10),
    scale: float | str = 0.15,
    rotation_deg: float = 0,
    strict: bool = True
) -> np.ndarray:
    """
    Adds tick or cross overlay to an image with optional scaling and rotation.

    Args:
        image (np.ndarray): Input image (BGR or grayscale)
        overlay_type (str): 'tick' or 'cross'
        position (tuple): (x, y) top-left placement
        scale (float | str): Scaling factor or "auto" for 5% of image width
        rotation_deg (float): Degrees to rotate overlay
        strict (bool): If False, errors are logged instead of raised

    Returns:
        np.ndarray: Image with overlay
    """
    try:
        overlay = load_overlay_image(overlay_type)

        # Convert grayscale to BGR
        if len(image.shape) == 2 or image.shape[2] == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Auto scaling
        if scale == "auto":
            target_dim = int(min(image.shape[0], image.shape[1]) * 0.05)
            overlay = cv2.resize(overlay, (target_dim, target_dim), interpolation=cv2.INTER_AREA)
        else:
            h, w = overlay.shape[:2]
            overlay = cv2.resize(overlay, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

        if rotation_deg != 0:
            overlay = rotate_image(overlay, rotation_deg)

        # Separate overlay channels
        overlay_rgb = overlay[..., :3]
        alpha_mask = overlay[..., 3:] / 255.0

        x, y = position
        h, w = overlay_rgb.shape[:2]

        if y + h > image.shape[0] or x + w > image.shape[1]:
            raise ValueError("Overlay does not fit in image at specified position.")

        roi = image[y:y+h, x:x+w]
        blended = (1.0 - alpha_mask) * roi + alpha_mask * overlay_rgb
        image[y:y+h, x:x+w] = blended.astype(np.uint8)

    except Exception as e:
        if strict:
            raise
        else:
            print(f"[Overlay Warning] {e}")

    return image


def annotate_batch(images: list[np.ndarray], overlay_type: str, positions: list[tuple], **kwargs) -> list[np.ndarray]:
    """
    Annotate multiple images with overlays (e.g., batch-correct answers).

    Args:
        images (list): List of input images
        overlay_type (str): 'tick' or 'cross'
        positions (list): List of (x, y) tuples per image
        kwargs: Extra arguments passed to `add_overlay`

    Returns:
        list: Annotated images
    """
    annotated = []
    for img, pos in zip(images, positions):
        annotated.append(add_overlay(img, overlay_type, position=pos, **kwargs))
    return annotated
