import numpy as np
from PIL import Image


def pixelate(image_object, scale_factor, jitter_val=0, block_val=0, sort_val=0, render_scale=1.0):
    """
    Pixelates the image with 3 blendable glitch styles.
    - jitter_val: Horizontal row jitter (0-100)
    - block_val: Random block displacement (0-100)
    - sort_val: Horizontal pixel sorting (0-100)
    - render_scale: Factor to normalize pixel-based parameters across resolutions.
    """
    if image_object is None:
        return None

    original_width, original_height = image_object.size
    source_arr = np.array(image_object.pixel_array, copy=True)

    # For pixelated previews, do the glitch work on the reduced-resolution image.
    # This preserves the aesthetic while avoiding unnecessary full-resolution passes.
    if scale_factor < 1.0:
        reduced_width = max(1, int(original_width * scale_factor))
        reduced_height = max(1, int(original_height * scale_factor))
        working_img = Image.fromarray(source_arr).resize((reduced_width, reduced_height), Image.NEAREST)
        arr = np.array(working_img)
    else:
        arr = source_arr

    height, width = arr.shape[:2]

    # 1. Style: Row Jitter (Fine horizontal displacement)
    if jitter_val > 0 and width > 1:
        probability = jitter_val / 100.0
        rows = np.flatnonzero(np.random.random(height) < probability)
        if rows.size > 0:
            max_shift = max(1, int(jitter_val / 2 * render_scale))
            shifts = np.random.randint(-max_shift, max_shift + 1, size=rows.size)
            column_indices = (np.arange(width)[None, :] - shifts[:, None]) % width
            arr[rows] = arr[rows[:, None], column_indices]

    # 2. Style: Block Displacement (Large chunks shifted)
    if block_val > 0 and width > 1 and height > 1:
        num_blocks = int(block_val / 5)
        scaled_block = max(1, int(block_val * render_scale))
        for _ in range(num_blocks):
            max_h = max(2, int(height * (block_val / 100)))
            max_w = max(2, int(width * (block_val / 100)))
            h_size = np.random.randint(1, min(height, max_h) + 1)
            w_size = np.random.randint(1, min(width, max_w) + 1)
            y = np.random.randint(0, height - h_size + 1)
            x = np.random.randint(0, width - w_size + 1)
            shift = np.random.randint(-scaled_block, scaled_block + 1)
            arr[y:y+h_size, x:x+w_size] = np.roll(arr[y:y+h_size, x:x+w_size], shift, axis=1)

    # 3. Style: Pixel Sorting (Sort segments by brightness)
    if sort_val > 0 and width > 1 and height > 0:
        for _ in range(int(sort_val)):
            y = np.random.randint(0, height)
            x_start = np.random.randint(0, width - 1)
            max_length = max(2, int(width * (sort_val / 100)))
            length = np.random.randint(1, max_length + 1)
            x_end = min(width, x_start + length)

            # Extract segment
            segment = arr[y, x_start:x_end]
            if len(segment) <= 1:
                continue
            # Sort by sum of RGB values (brightness proxy)
            brightness = np.sum(segment[:, :3], axis=1)
            indices = np.argsort(brightness)
            arr[y, x_start:x_end] = segment[indices]

    # Apply Pixelation (Downsample/Upsample)
    img = Image.fromarray(arr)
    if scale_factor < 1.0:
        img = img.resize((original_width, original_height), Image.NEAREST)

    return img
