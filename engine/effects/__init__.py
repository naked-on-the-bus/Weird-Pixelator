"""Effect registry and convenience imports.

To add a new effect:
1. Create a new module in engine/effects/
2. Define your effect function(s) with the signature:
       def my_effect(image, parameter, ..., render_scale=1.0):
   Use render_scale to normalize pixel-based parameters so the effect
   looks the same at any resolution.
3. Import and expose the function(s) here.
"""

from engine.effects.pixelate import pixelate
from engine.effects.color import (
    adjust_hue,
    adjust_saturation,
    adjust_contrast,
    adjust_invert,
    invert_image,
    reduce_colors,
    reduce_colors_legacy,
)
from engine.effects.glitch import apply_data_bending, apply_datamosh
from engine.effects.crt import (
    apply_horizontal_distortion,
    apply_screen_curvature,
    apply_phosphor_glow,
    apply_static_noise,
    apply_scanlines,
    apply_rgb_shift,
    apply_vignette,
)
from engine.effects.blend import blend_images, randomize_pixels
from engine.effects.compression import apply_export_compression
from engine.effects.palette import extract_palette
