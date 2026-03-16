import numpy as np
from PIL import Image


def extract_palette(image, color_count):
    """
    Extract a representative palette from an image.
    Returns a list of dicts with `rgb`, `count`, and `ratio` keys.
    """
    if image is None:
        return []

    color_count = max(1, min(256, int(color_count)))
    rgba = image.convert("RGBA")
    arr = np.array(rgba)

    if arr.ndim != 3 or arr.shape[2] < 3:
        return []

    alpha = arr[..., 3] if arr.shape[2] >= 4 else None
    if alpha is not None and np.any(alpha > 0):
        rgb_pixels = arr[alpha > 0][:, :3]
        if rgb_pixels.size == 0:
            return []
        palette_source = Image.fromarray(rgb_pixels.reshape((-1, 1, 3)).astype(np.uint8), mode="RGB")
    else:
        palette_source = rgba.convert("RGB")

    quantized = palette_source.quantize(colors=color_count, method=Image.MEDIANCUT)
    palette_values = quantized.getpalette() or []
    palette_indices = np.array(quantized).reshape(-1)
    if palette_indices.size == 0:
        return []

    unique_indices, counts = np.unique(palette_indices, return_counts=True)
    total = max(1, int(np.sum(counts)))
    entries = []

    for palette_index, count in zip(unique_indices.tolist(), counts.tolist()):
        offset = int(palette_index) * 3
        if offset + 2 >= len(palette_values):
            continue

        rgb = tuple(int(channel) for channel in palette_values[offset:offset + 3])
        entries.append({
            "rgb": rgb,
            "count": int(count),
            "ratio": float(count) / float(total),
        })

    entries.sort(key=lambda entry: entry["count"], reverse=True)
    return entries[:color_count]
