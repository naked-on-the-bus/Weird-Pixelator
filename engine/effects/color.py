import numpy as np
from PIL import Image, ImageEnhance


def adjust_hue(image, hue_shift):
    """
    Adjusts the hue of the image.
    hue_shift: Value in degrees (-180 to 180).
    """
    if image is None:
        return None

    img = image.convert("HSV")
    arr = np.array(img)
    arr[..., 0] = (arr[..., 0].astype(int) + int(hue_shift * 255 / 360)) % 256
    return Image.fromarray(arr, mode="HSV").convert(image.mode)


def adjust_saturation(image, saturation_factor):
    """
    Adjusts the saturation of the image.
    saturation_factor: 1.0 is no change, <1.0 is less saturated, >1.0 is more saturated.
    """
    if image is None:
        return None

    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(saturation_factor)


def adjust_contrast(image, contrast_factor):
    """
    Adjusts the contrast of the image.
    contrast_factor: 1.0 is no change, <1.0 is less contrast, >1.0 is more contrast.
    """
    if image is None:
        return None

    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(contrast_factor)


def adjust_invert(image, invert_factor):
    """
    Gradually inverts the image colors based on the invert_factor.
    invert_factor: 0.0 is original, 1.0 is fully inverted.
    """
    if image is None:
        return None

    arr = np.array(image).astype(float)

    # Separate RGB and Alpha channels if present
    if arr.ndim == 3 and arr.shape[2] == 4:
        rgb = arr[..., :3]
        alpha = arr[..., 3:]
    else:
        rgb = arr
        alpha = None

    inverted_rgb = 255 - rgb  # Fully inverted for RGB
    blended_rgb = rgb * (1 - invert_factor) + inverted_rgb * invert_factor

    if alpha is not None:
        combined = np.concatenate((blended_rgb, alpha), axis=-1)
        mode = "RGBA"
    else:
        combined = blended_rgb
        mode = "RGB"

    return Image.fromarray(combined.clip(0, 255).astype(np.uint8), mode=mode)


def invert_image(image, invert_state):
    """
    Conditionally inverts the image colors based on invert_state.
    Only inverts RGB channels, leaving alpha (transparency) unchanged.
    """
    if image is None or not invert_state:
        return image

    arr = np.array(image).astype(float)
    # Separate RGB and Alpha channels
    rgb = arr[..., :3]
    alpha = arr[..., 3:] if arr.shape[-1] == 4 else None

    # Invert only the RGB channels
    inverted_rgb = 255 - rgb

    # Combine back with Alpha channel if it exists
    if alpha is not None:
        combined = np.concatenate((inverted_rgb, alpha), axis=-1)
    else:
        combined = inverted_rgb

    # Ensure the output is in the correct mode
    mode = "RGBA" if alpha is not None else "RGB"
    return Image.fromarray(combined.clip(0, 255).astype(np.uint8), mode=mode)


def reduce_colors(image, color_bins):
    """
    Reduces the number of colors in the image by quantizing the color space.
    color_bins: Number of color bins (e.g., 256 for full color, lower for fewer colors).
    """
    if image is None:
        return None

    # Clamp color_bins to valid range
    color_bins = max(1, min(256, int(color_bins)))

    # Use Pillow's quantize for better color reduction (palette-based)
    # Preserve alpha channel if present
    img = image.convert("RGBA")
    arr = np.array(img)
    has_alpha = (arr.ndim == 3 and arr.shape[2] == 4)

    if has_alpha:
        # Separate alpha, quantize RGB, then reattach alpha
        rgb_img = Image.fromarray(arr[..., :3], mode="RGB")
        quant = rgb_img.quantize(colors=color_bins, method=Image.MEDIANCUT)
        quant_rgb = quant.convert("RGB")
        quant_arr = np.array(quant_rgb)
        combined = np.dstack((quant_arr, arr[..., 3]))
        return Image.fromarray(combined, mode="RGBA")
    else:
        rgb_img = image.convert("RGB")
        quant = rgb_img.quantize(colors=color_bins, method=Image.MEDIANCUT)
        return quant.convert(image.mode)


def reduce_colors_legacy(image, color_bins):
    """
    Legacy/broken color reducer kept for aesthetic: coarse quantization
    that also affects alpha (matches the previous buggy behavior you liked).
    """
    if image is None:
        return None

    arr = np.array(image)
    color_bins = max(1, min(256, int(color_bins)))
    factor = max(1, 256 // color_bins)

    # Apply naive quantization to the entire array (including alpha if present)
    quantized_arr = (arr // factor) * factor + factor // 2
    return Image.fromarray(quantized_arr.clip(0, 255).astype(np.uint8), mode=image.mode)
