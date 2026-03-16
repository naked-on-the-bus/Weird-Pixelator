import numpy as np
from PIL import Image, ImageFilter


def apply_horizontal_distortion(image, strength):
    """
    Add subtle wavy horizontal distortion like an unstable CRT signal.
    strength: 0-100.
    """
    if image is None or strength <= 0:
        return image

    arr = np.array(image)
    if arr.ndim != 3:
        return image

    height, width = arr.shape[:2]
    amplitude = max(1, int((strength / 100.0) * max(2, width * 0.02)))
    frequency = 2.0 + (strength / 100.0) * 6.0

    distorted = arr.copy()
    rows = np.arange(height)
    offsets = np.round(np.sin(rows / max(1.0, height / frequency) * np.pi * 2.0) * amplitude).astype(int)

    for row, offset in enumerate(offsets):
        distorted[row] = np.roll(arr[row], offset, axis=0)

    return Image.fromarray(distorted, mode=image.mode)


def apply_screen_curvature(image, strength):
    """
    Darken corners and slightly compress edges to suggest CRT glass curvature.
    strength: 0-100.
    """
    if image is None or strength <= 0:
        return image

    arr = np.array(image).astype(np.float32)
    if arr.ndim != 3 or arr.shape[2] < 3:
        return image

    height, width = arr.shape[:2]
    y_indices, x_indices = np.indices((height, width), dtype=np.float32)
    center_x = max((width - 1) / 2.0, 1.0)
    center_y = max((height - 1) / 2.0, 1.0)

    x_norm = (x_indices - center_x) / center_x
    y_norm = (y_indices - center_y) / center_y
    radial = x_norm ** 2 + y_norm ** 2

    amount = strength / 100.0
    edge_mask = 1.0 - np.clip(radial * 0.18 * amount, 0.0, 0.22)
    arr[..., :3] *= edge_mask[..., np.newaxis]

    inset_x = int(width * 0.015 * amount)
    inset_y = int(height * 0.015 * amount)
    if inset_x > 0 or inset_y > 0:
        curved = Image.fromarray(arr.clip(0, 255).astype(np.uint8), mode=image.mode)
        shrunk = curved.resize((max(1, width - inset_x * 2), max(1, height - inset_y * 2)), Image.LANCZOS)
        canvas = Image.new(image.mode, (width, height), (0, 0, 0, 255) if 'A' in image.mode else (0, 0, 0))
        canvas.paste(shrunk, (inset_x, inset_y))
        return canvas

    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), mode=image.mode)


def apply_phosphor_glow(image, strength, render_scale=1.0):
    """
    Add a soft bloom to bright areas for a phosphor glow effect.
    strength: 0-100.
    render_scale: Normalizes blur radius for consistent appearance across resolutions.
    """
    if image is None or strength <= 0:
        return image

    amount = strength / 100.0
    base = image.convert("RGBA")
    radius = max(1, int(round((1 + amount * 6) * render_scale)))
    glow = base.filter(ImageFilter.GaussianBlur(radius))
    return Image.blend(base, glow, min(0.55, amount * 0.55)).convert(image.mode)


def apply_static_noise(image, strength):
    """
    Add RGB noise like CRT static.
    strength: 0-100.
    """
    if image is None or strength <= 0:
        return image

    arr = np.array(image).astype(np.float32)
    if arr.ndim != 3 or arr.shape[2] < 3:
        return image

    amplitude = 5.0 + (strength / 100.0) * 35.0
    noise = np.random.normal(0.0, amplitude, size=arr[..., :3].shape)
    arr[..., :3] += noise
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), mode=image.mode)


def apply_scanlines(image, intensity, render_scale=1.0):
    """
    Add dark horizontal scanlines for a CRT-like display effect.
    intensity: 0-100.
    render_scale: Normalizes scanline spacing for consistent density across resolutions.
    """
    if image is None or intensity <= 0:
        return image

    strength = max(0.0, min(1.0, intensity / 100.0))
    arr = np.array(image).astype(np.float32)

    if arr.ndim != 3 or arr.shape[2] < 3:
        return image

    darken_factor = 1.0 - (0.55 * strength)
    step = max(2, int(round(2 * render_scale)))
    mask = np.ones((arr.shape[0], 1, 1), dtype=np.float32)
    mask[step - 1::step, :, :] = darken_factor
    arr[..., :3] *= mask

    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), mode=image.mode)


def apply_rgb_shift(image, shift_amount, render_scale=1.0):
    """
    Slightly offset the red and blue channels to mimic CRT convergence issues.
    shift_amount: 0-20 pixels.
    render_scale: Normalizes shift distance for consistent appearance across resolutions.
    """
    if image is None or shift_amount <= 0:
        return image

    arr = np.array(image)
    if arr.ndim != 3 or arr.shape[2] < 3:
        return image

    shift = max(1, int(round(shift_amount * render_scale)))
    shifted = arr.copy()
    shifted[..., 0] = np.roll(arr[..., 0], shift, axis=1)
    shifted[..., 2] = np.roll(arr[..., 2], -shift, axis=1)
    return Image.fromarray(shifted, mode=image.mode)


def apply_vignette(image, strength):
    """
    Darken image edges to simulate a curved CRT screen.
    strength: 0-100.
    """
    if image is None or strength <= 0:
        return image

    amount = max(0.0, min(1.0, strength / 100.0))
    arr = np.array(image).astype(np.float32)
    if arr.ndim != 3 or arr.shape[2] < 3:
        return image

    height, width = arr.shape[:2]
    y_indices, x_indices = np.ogrid[:height, :width]
    center_x = max((width - 1) / 2.0, 1.0)
    center_y = max((height - 1) / 2.0, 1.0)

    distance = np.sqrt(((x_indices - center_x) / center_x) ** 2 + ((y_indices - center_y) / center_y) ** 2)
    distance = np.clip(distance / np.sqrt(2.0), 0.0, 1.0)

    mask = 1.0 - (0.85 * amount * (distance ** 1.8))
    mask = np.clip(mask, 0.15, 1.0)
    arr[..., :3] *= mask[..., np.newaxis]

    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), mode=image.mode)
