import numpy as np
from PIL import Image


def blend_images(base_image, overlay_image, factor):
    """
    Blend `overlay_image` into `base_image` using `factor` (0.0..1.0).
    The overlay is resized to match the base image size.
    Both images are converted to RGBA to preserve transparency.
    """
    if base_image is None:
        return overlay_image if overlay_image is not None else None
    if overlay_image is None or factor <= 0.0:
        return base_image

    base = base_image.convert("RGBA")
    overlay = overlay_image.convert("RGBA")

    if overlay.size != base.size:
        overlay = overlay.resize(base.size, Image.LANCZOS)

    # Use Image.blend which linearly interpolates between two images
    blended = Image.blend(base, overlay, factor)
    return blended


def randomize_pixels(image, random_factor):
    """
    Optimized randomization of pixel colors based on the random_factor.
    random_factor: 0.0 means no randomization, 1.0 means all pixels are randomized.
    """
    if image is None:
        return None

    arr = np.array(image).astype(float)
    height, width = arr.shape[0], arr.shape[1]
    channels = arr.shape[2] if arr.ndim == 3 else 1

    # Generate random indices for pixels to randomize
    num_pixels = int(random_factor * height * width)
    if num_pixels == 0:
        return image
    indices = np.random.choice(height * width, size=num_pixels, replace=False)

    # Convert flat indices to 2D coordinates
    y_coords, x_coords = np.unravel_index(indices, (height, width))

    # Randomize only RGB channels, preserve alpha if present
    if channels >= 3:
        random_rgb = np.random.randint(0, 256, size=(num_pixels, 3))
        arr[y_coords, x_coords, :3] = random_rgb
    else:
        # Grayscale or unexpected format: randomize the single channel
        arr[y_coords, x_coords] = np.random.randint(0, 256, size=(num_pixels,))

    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), mode=image.mode)
