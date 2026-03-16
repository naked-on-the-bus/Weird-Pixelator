from io import BytesIO

import numpy as np
from PIL import Image


def apply_data_bending(image, amount, mode="Byte Shift"):
    """
    Apply a stable databending-style JPEG byte corruption pass.
    The effect is deterministic for the same image, amount, and mode so the
    live preview does not flicker unpredictably.
    """
    if image is None or amount <= 0:
        return image

    amount = max(0.0, min(100.0, float(amount)))
    base = image.convert("RGBA")
    rgb = base.convert("RGB")
    alpha = base.getchannel("A")

    jpeg_buffer = BytesIO()
    rgb.save(jpeg_buffer, format="JPEG", quality=82, optimize=False)
    source_bytes = jpeg_buffer.getvalue()
    if len(source_bytes) < 1024:
        return image

    start = 512
    end = len(source_bytes) - 2
    if end <= start + 32:
        return image

    sample_step = max(1, len(source_bytes) // 2048)
    seed_sample = np.frombuffer(source_bytes[::sample_step], dtype=np.uint8)
    base_seed = int(seed_sample.sum())
    base_seed += rgb.size[0] * 131 + rgb.size[1] * 17 + int(round(amount * 97))
    base_seed += sum(ord(char) for char in str(mode)) * 13

    def _corrupt_bytes(scale):
        rng = np.random.default_rng(base_seed + int(scale * 1000))
        bent_bytes = bytearray(source_bytes)
        payload = bent_bytes[start:end]
        payload_length = len(payload)
        if payload_length < 64:
            return None

        strength = max(0.02, min(1.0, (amount / 100.0) * scale))
        chunk_size = max(24, min(payload_length // 3, int(payload_length * (0.008 + 0.06 * strength))))
        if chunk_size >= payload_length:
            chunk_size = max(24, payload_length // 4)

        position_limit = max(1, payload_length - chunk_size)
        pos_a = int(rng.integers(0, position_limit))
        pos_b = int(rng.integers(0, position_limit))

        if mode == "Byte Swap":
            chunk_a = payload[pos_a:pos_a + chunk_size]
            chunk_b = payload[pos_b:pos_b + chunk_size]
            payload[pos_a:pos_a + chunk_size] = chunk_b
            payload[pos_b:pos_b + chunk_size] = chunk_a
        elif mode == "Repeat Burst":
            burst = payload[pos_a:pos_a + chunk_size]
            fade = np.linspace(1.0, 0.45, num=len(burst), dtype=np.float32)
            softened = (np.frombuffer(bytes(burst), dtype=np.uint8).astype(np.float32) * fade).clip(0, 255).astype(np.uint8)
            payload[pos_b:pos_b + chunk_size] = softened.tobytes()
        else:
            shift = max(1, min(chunk_size - 1, int(chunk_size * (0.12 + 0.7 * strength))))
            chunk = payload[pos_a:pos_a + chunk_size]
            payload[pos_a:pos_a + chunk_size] = chunk[shift:] + chunk[:shift]

        bent_bytes[start:end] = payload
        return bytes(bent_bytes)

    for scale in (1.0, 0.7, 0.45, 0.25):
        candidate = _corrupt_bytes(scale)
        if candidate is None:
            continue
        try:
            bent = Image.open(BytesIO(candidate)).convert("RGB")
            result = bent.convert("RGBA")
            result.putalpha(alpha)
            return result.convert(image.mode)
        except Exception:
            continue

    return image


def _stack_glitch_bands(stacked, target_height):
    """
    Resample a glitched band stack back to the original height.
    """
    if stacked.shape[0] == target_height:
        return stacked

    sampled_indices = np.linspace(0, stacked.shape[0] - 1, num=target_height)
    sampled_indices = np.clip(np.round(sampled_indices).astype(int), 0, stacked.shape[0] - 1)
    return stacked[sampled_indices]


def _apply_tomato_style_datamosh(arr, amount, mode):
    """
    AVI-style still-image mode using reordered horizontal bands.
    Only `AVI Style` and `Reverse` are handled here.
    """
    height, width = arr.shape[:2]
    seed_sample = arr[::max(1, height // 24), ::max(1, width // 24), :3]
    seed = int(seed_sample.sum()) + width * 53 + height * 29 + int(amount * 101) + sum(ord(ch) for ch in mode)
    rng = np.random.default_rng(seed)

    strength = amount / 100.0
    band_height = max(2, min(max(2, height // 6), int(height * (0.012 + strength * 0.08))))
    bands = []
    for start in range(0, height, band_height):
        end = min(height, start + band_height)
        bands.append(arr[start:end].copy())

    if len(bands) < 2:
        return arr

    if mode == "Reverse":
        final_bands = list(reversed(bands))
    else:
        count = max(2, min(len(bands), 2 + int(round(strength * 8))))
        step = max(1, int(round(1 + (1.0 - strength) * 4)))
        anchor = int(rng.integers(0, len(bands)))
        repeat_count = max(1, int(round(1 + strength * 6)))
        grouped = [bands[index:index + count] for index in range(0, len(bands), step)]
        overlapped = [band for group in grouped for band in group]
        bloom_band = bands[anchor]
        final_bands = overlapped[:anchor] + [bloom_band.copy() for _ in range(repeat_count)] + overlapped[anchor:]

    stacked = np.vstack(final_bands)
    stacked = _stack_glitch_bands(stacked, height)

    if strength > 0.25:
        smear_width = max(1, int(round(width * (0.003 + strength * 0.02))))
        shifted = np.roll(stacked[..., :3], smear_width, axis=1)
        blend_amount = min(0.45, 0.08 + strength * 0.3)
        stacked_rgb = stacked[..., :3].astype(np.float32)
        stacked[..., :3] = (stacked_rgb * (1.0 - blend_amount) + shifted.astype(np.float32) * blend_amount).clip(0, 255).astype(np.uint8)

    return stacked


def _apply_legacy_datamosh(arr, amount, mode):
    """
    Restore two of the earlier macroblock-based datamosh looks.
    """
    height, width = arr.shape[:2]
    block_size = max(4, min(24, 4 + int(amount / 8)))
    result = arr.copy()
    seed = int(arr[::max(1, height // 32), ::max(1, width // 32), :3].sum())
    seed += width * 37 + height * 19 + int(amount * 101) + sum(ord(char) for char in mode)
    rng = np.random.default_rng(seed)

    for y in range(0, height - block_size + 1, block_size):
        for x in range(0, width - block_size + 1, block_size):
            if rng.random() > (amount / 100.0) * 0.72:
                continue

            if mode == "Block Echo":
                source_x = min(width - block_size, max(0, x - block_size * int(1 + amount / 35)))
                source_y = y
            else:
                source_x = min(width - block_size, max(0, x - block_size * int(1 + amount / 30)))
                source_y = max(0, y - int(rng.integers(0, block_size + 1)))

            block = result[source_y:source_y + block_size, source_x:source_x + block_size].copy()

            if mode == "Block Echo":
                tint = np.array([1.05, 0.96, 1.08], dtype=np.float32)
                block[..., :3] = (block[..., :3].astype(np.float32) * tint).clip(0, 255).astype(np.uint8)

            result[y:y + block_size, x:x + block_size] = block

    return result


def apply_datamosh(image, amount, mode="AVI Style"):
    """
    Four-mode datamosh effect:
    - `AVI Style`: tomato-inspired band reorder/duplication
    - `P-Frame Smear`: earlier smear look
    - `Block Echo`: earlier echo look
    - `Reverse`: reversed AVI-style bands
    """
    if image is None or amount <= 0:
        return image

    amount = max(0.0, min(100.0, float(amount)))
    arr = np.array(image.convert("RGBA"))
    if arr.ndim != 3 or arr.shape[2] < 3:
        return image

    height, width = arr.shape[:2]
    if height < 6 or width < 6:
        return image

    if mode in ("AVI Style", "Reverse"):
        glitched = _apply_tomato_style_datamosh(arr, amount, mode)
    else:
        glitched = _apply_legacy_datamosh(arr, amount, mode)

    return Image.fromarray(glitched, mode=image.mode)
