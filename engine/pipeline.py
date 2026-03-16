import numpy as np
from PIL import Image, ImageFilter

from engine.image_object import ImageObject
from engine import effects


def modulate_video_effect_values(app, frame_index, base_values):
    if not app.is_video_mode or not app.video_intensity_controls:
        return dict(base_values)

    specs = app._video_effect_specs()
    values = dict(base_values)
    for key, controls in app.video_intensity_controls.items():
        spec = specs.get(key)
        if spec is None:
            continue

        every_n = max(1, int(float(controls["step"].get())))
        drift_pct = max(0.0, min(100.0, float(controls["drift"].get()))) / 100.0
        if drift_pct <= 0.0:
            continue

        if spec["type"] == "bool":
            if ((frame_index // every_n) % 2) == 1:
                values[key] = not bool(base_values.get(key, False))
            continue

        base_value = float(base_values.get(key, spec["default"]))
        phase = (frame_index / float(every_n)) * 0.35
        wave = float(np.sin(phase))
        candidate = base_value * (1.0 + (wave * drift_pct))

        minimum = float(spec["min"])
        maximum = float(spec["max"])

        if abs(base_value) <= 0.001 and (maximum - minimum) > 0.0:
            midpoint = 0.5 * (minimum + maximum)
            span = 0.5 * (maximum - minimum)
            candidate = midpoint + (span * wave * drift_pct)

        candidate = max(minimum, min(maximum, candidate))
        if spec["type"] == "int":
            candidate = int(round(candidate))
        values[key] = candidate

    return values


def render_frame_with_values(app, source_image, effect_values, for_preview=False, frame_index=0):
    if source_image is None:
        return None

    base_reference_size = app.current_pil_image.size if app.current_pil_image is not None else source_image.size
    base_source = app._crop_to_visible_area(source_image, base_reference_size)
    blend_source = app._crop_to_visible_area(app.blend_image_pil, base_reference_size)

    # Compute the preview size — used both for scaling and as the reference
    # for normalizing pixel-based effect parameters.
    preview_size = app._get_preview_processing_size(base_source.size)

    if for_preview:
        if preview_size != base_source.size:
            base_source = base_source.resize(preview_size, Image.LANCZOS)
            if blend_source is not None:
                blend_source = blend_source.resize(preview_size, Image.LANCZOS)
        render_scale = 1.0
    else:
        # Scale factor that normalizes pixel-based effect parameters so that
        # the full-resolution export matches the preview appearance.
        render_scale = base_source.size[0] / max(1, preview_size[0])

    img = process_effects_on_image(app, base_source, effect_values=effect_values, render_scale=render_scale)
    if blend_source is not None:
        overlay_processed = process_effects_on_image(app, blend_source, effect_values=effect_values, render_scale=render_scale)
        blend_factor = float(app.blend_slider.get()) if hasattr(app, "blend_slider") else 0.0
        if blend_factor > 0.0:
            img = effects.blend_images(img, overlay_processed, blend_factor)

    if img is None:
        return None

    img = app._apply_manual_blending(img, frame_index=frame_index)
    img = apply_crt_effects(app, img, effect_values=effect_values, render_scale=render_scale)
    return app.apply_export_compression(img)


def render_current_image(app, for_preview=False):
    if app.image_object is None or app.current_pil_image is None:
        return None

    base_values = app._collect_effect_values()
    values = modulate_video_effect_values(app, 0, base_values) if app.is_video_mode else base_values
    return render_frame_with_values(app, app.current_pil_image, values, for_preview=for_preview, frame_index=0)


def apply_pipeline(app):
    if app.image_object:
        preview_img = render_current_image(app, for_preview=True)
        if preview_img is not None:
            app.pipeline_image = preview_img
            app.display_image(preview_img)


def process_effects_on_image(app, pil_img, effect_values=None, render_scale=1.0):
    if pil_img is None:
        return None

    if effect_values is None:
        effect_values = app._collect_effect_values()

    arr = np.array(pil_img.convert("RGBA"))
    temp_obj = ImageObject(name="temp", size=pil_img.size, pixel_array=arr)

    scale_factor = float(effect_values.get("pixel_scale", 1.0))
    jitter_val = int(effect_values.get("jitter", 0))
    block_val = int(effect_values.get("block", 0))
    sort_val = int(effect_values.get("sort", 0))

    img = effects.pixelate(temp_obj, scale_factor, jitter_val, block_val, sort_val, render_scale=render_scale)

    hue_shift = int(effect_values.get("hue", 0))
    saturation_factor = float(effect_values.get("saturation", 1.0))
    contrast_factor = float(effect_values.get("contrast", 1.0))
    invert_factor = float(effect_values.get("invert", False))

    img = effects.adjust_hue(img, hue_shift)
    img = effects.adjust_saturation(img, saturation_factor)
    img = effects.adjust_contrast(img, contrast_factor)
    img = effects.adjust_invert(img, invert_factor)

    blur_radius = app._effect_int(effect_values, "blur", 0)
    color_bins = app._effect_int(effect_values, "color_reducer", 256)
    legacy_bins = app._effect_int(effect_values, "legacy_collapse", 256)

    if blur_radius > 0:
        scaled_blur = max(1, int(round(blur_radius * render_scale)))
        img = img.filter(ImageFilter.GaussianBlur(scaled_blur))

    if color_bins < 256:
        img = effects.reduce_colors(img, color_bins)

    if legacy_bins < 256:
        img = effects.reduce_colors_legacy(img, legacy_bins)

    bend_amount = app._effect_float(effect_values, "bending", 0.0)

    if bend_amount > 0.0:
        img = effects.apply_data_bending(img, bend_amount, effect_values.get("bend_mode", app.bend_mode_var.get()))

    datamosh_amount = app._effect_float(effect_values, "datamosh", 0.0)

    if datamosh_amount > 0.0:
        img = effects.apply_datamosh(img, datamosh_amount, effect_values.get("datamosh_mode", app.datamosh_mode_var.get()))

    random_factor = app._effect_float(effect_values, "random_pixels", 0.0)

    if random_factor > 0.0:
        img = effects.randomize_pixels(img, random_factor)

    return img


def apply_crt_effects(app, img, effect_values=None, render_scale=1.0):
    if img is None:
        return None

    if effect_values is None:
        effect_values = app._collect_effect_values()

    scanline_strength = int(effect_values.get("scanlines", 0))
    curvature_strength = int(effect_values.get("curvature", 0))
    distortion_strength = int(effect_values.get("distortion", 0))
    glow_strength = int(effect_values.get("glow", 0))
    noise_strength = int(effect_values.get("noise", 0))
    rgb_shift = int(effect_values.get("rgb_shift", 0))
    vignette_strength = int(effect_values.get("vignette", 0))

    img = effects.apply_horizontal_distortion(img, distortion_strength)
    img = effects.apply_screen_curvature(img, curvature_strength)
    img = effects.apply_scanlines(img, scanline_strength, render_scale=render_scale)
    img = effects.apply_rgb_shift(img, rgb_shift, render_scale=render_scale)
    img = effects.apply_phosphor_glow(img, glow_strength, render_scale=render_scale)
    img = effects.apply_static_noise(img, noise_strength)
    img = effects.apply_vignette(img, vignette_strength)
    return img
