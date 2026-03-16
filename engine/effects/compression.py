from io import BytesIO

from PIL import Image


def _jpeg_roundtrip(image, quality, subsampling=2):
    """
    Run an image through JPEG encoding/decoding to introduce compression artifacts.
    """
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality, subsampling=subsampling, optimize=False)
    buffer.seek(0)
    return Image.open(buffer).convert("RGB")


def apply_export_compression(image, profile_name):
    """
    Apply save-only compression that mimics old digital camera artifacts.
    """
    if image is None or not profile_name or profile_name == "No Compression":
        return image

    base = image.convert("RGBA")
    rgb = base.convert("RGB")
    alpha = base.getchannel("A")
    width, height = rgb.size

    if profile_name == "Soft CCD":
        rgb = _jpeg_roundtrip(rgb, quality=58, subsampling=1)
    elif profile_name == "Compact Camera":
        reduced = rgb.resize((max(1, int(width * 0.92)), max(1, int(height * 0.92))), Image.BILINEAR)
        rgb = _jpeg_roundtrip(reduced.resize((width, height), Image.BILINEAR), quality=38, subsampling=2)
    elif profile_name == "Memory Saver":
        reduced = rgb.resize((max(1, int(width * 0.84)), max(1, int(height * 0.84))), Image.BILINEAR)
        rgb = _jpeg_roundtrip(reduced.resize((width, height), Image.BILINEAR), quality=22, subsampling=2)
        rgb = _jpeg_roundtrip(rgb, quality=20, subsampling=2)
    elif profile_name == "Harsh Artifacts":
        reduced = rgb.resize((max(1, int(width * 0.72)), max(1, int(height * 0.72))), Image.NEAREST)
        rgb = _jpeg_roundtrip(reduced.resize((width, height), Image.NEAREST), quality=10, subsampling=2)
        rgb = _jpeg_roundtrip(rgb, quality=8, subsampling=2)
    else:
        return image

    compressed = rgb.convert("RGBA")
    compressed.putalpha(alpha)
    return compressed
