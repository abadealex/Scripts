import os
import cv2
import numpy as np

# Directory where tick/cross images are stored
OVERLAY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'overlays'))

def load_overlay_image(type_: str) -> np.ndarray:
    """
    Load tick or cross image with alpha channel.
    """
    if type_ not in ['tick', 'cross']:
        raise ValueError("Overlay type must be 'tick' or 'cross'")

    path = os.path.join(OVERLAY_DIR, f'{type_}.png')
    if not os.path.exists(path):
        raise FileNotFoundError(f"Overlay image not found at: {path}")

    overlay = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if overlay is None or overlay.shape[2] != 4:
        raise ValueError("Overlay image must have 4 channels (including alpha).")

    return overlay


def rotate_image(img: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate image around its center by given angle in degrees.
    """
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))


def smart_position(center: tuple[int, int], overlay_shape: tuple[int, int], image_shape: tuple[int, int]) -> tuple[int, int]:
    """
    Calculate top-left corner from center position, clamped to image boundaries.
    """
    cx, cy = center
    h, w = overlay_shape
    img_h, img_w = image_shape[:2]
    x = max(0, min(cx - w // 2, img_w - w))
    y = max(0, min(cy - h // 2, img_h - h))
    return x, y


def add_overlay(
    image: np.ndarray,
    overlay_type: str,
    position: tuple[int, int] = (10, 10),
    scale: float | str = 0.15,
    rotation_deg: float = 0,
    centered: bool = False,
    strict: bool = True
) -> np.ndarray:
    """
    Adds tick or cross overlay to an image with optional scaling, rotation, centering.
    """
    try:
        overlay = load_overlay_image(overlay_type)

        # Convert grayscale to BGR if needed
        if len(image.shape) == 2 or image.shape[2] == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Resize overlay
        if scale == "auto":
            base = int(min(image.shape[:2]) * 0.05)
            overlay = cv2.resize(overlay, (base, base), interpolation=cv2.INTER_AREA)
        elif isinstance(scale, (float, int)) and 0 < scale <= 2:
            h, w = overlay.shape[:2]
            overlay = cv2.resize(overlay, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        else:
            raise ValueError("Scale must be a float between 0 and 2 or 'auto'")

        if rotation_deg:
            overlay = rotate_image(overlay, rotation_deg)

        overlay_rgb = overlay[..., :3]
        alpha_mask = overlay[..., 3:] / 255.0

        h, w = overlay_rgb.shape[:2]
        x, y = position
        if centered:
            x, y = smart_position((x, y), (h, w), image.shape)

        if y + h > image.shape[0] or x + w > image.shape[1]:
            raise ValueError("Overlay does not fit in image at specified position.")

        roi = image[y:y + h, x:x + w]
        blended = (1.0 - alpha_mask) * roi + alpha_mask * overlay_rgb
        image[y:y + h, x:x + w] = blended.astype(np.uint8)

    except Exception as e:
        if strict:
            raise
        else:
            print(f"[Overlay Warning] {e}")

    return image


def annotate_batch(
    images: list[np.ndarray],
    overlay_type: str,
    positions: list[tuple[int, int]],
    **kwargs
) -> list[np.ndarray]:
    """
    Annotate multiple images with overlay symbols.
    """
    result = []
    for img, pos in zip(images, positions):
        result.append(add_overlay(img, overlay_type, position=pos, **kwargs))
    return result


def generate_overlay(script, scores):
    from smartscripts.utils.image_helpers import draw_marks_on_script, save_overlay_image
    image = draw_marks_on_script(script.pdf_path, scores)
    save_overlay_image(script.id, image)

