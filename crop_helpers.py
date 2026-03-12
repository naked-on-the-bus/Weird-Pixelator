
from PIL import Image


def set_crop_entry_value(app, edge, value):
    target_var = app._crop_var(edge)
    app._updating_crop_entries = True
    try:
        target_var.set(str(int(value)))
    finally:
        app._updating_crop_entries = False


def set_crop_preset_value(app, value):
    app._updating_crop_preset = True
    try:
        app.crop_preset_var.set(value)
    finally:
        app._updating_crop_preset = False


def set_crop_controls(app, left, right, top, bottom):
    app._syncing_crop_controls = True
    try:
        app.crop_left_slider.set(left)
        app.crop_right_slider.set(right)
        app.crop_top_slider.set(top)
        app.crop_bottom_slider.set(bottom)
        set_crop_entry_value(app, "left", left)
        set_crop_entry_value(app, "right", right)
        set_crop_entry_value(app, "top", top)
        set_crop_entry_value(app, "bottom", bottom)
    finally:
        app._syncing_crop_controls = False


def get_crop_presets(app):
    return {
        "1:1": 1.0,
        "3:2": 3.0 / 2.0,
        "4:5": 4.0 / 5.0,
        "16:9": 16.0 / 9.0,
        "9:16": 9.0 / 16.0,
        "21:9": 21.0 / 9.0,
    }


def update_crop_metadata(app):
    if app.current_pil_image is None:
        app.crop_size_var.set("Final Size: -")
        set_crop_preset_value(app, "Free")
        app._update_preview_metadata()
        return

    left, top, right, bottom = get_active_crop_box(app, app.current_pil_image.size)
    crop_width = max(1, right - left)
    crop_height = max(1, bottom - top)
    app.crop_size_var.set(f"Final Size: {crop_width} x {crop_height}")

    ratio = crop_width / crop_height if crop_height else 0.0
    matched_preset = "Free"
    for label, target_ratio in get_crop_presets(app).items():
        if abs(ratio - target_ratio) <= 0.03:
            matched_preset = label
            break

    set_crop_preset_value(app, matched_preset)
    app._update_preview_metadata()


def sync_crop_controls_to_image(app, reset_values=True):
    if app.current_pil_image is None:
        max_width = 1
        max_height = 1
    else:
        max_width, max_height = app.current_pil_image.size

    width_limit = max(0, max_width - 1)
    height_limit = max(0, max_height - 1)

    app.crop_left_slider.configure(from_=0, to=width_limit)
    app.crop_right_slider.configure(from_=0, to=width_limit)
    app.crop_top_slider.configure(from_=0, to=height_limit)
    app.crop_bottom_slider.configure(from_=0, to=height_limit)

    if reset_values:
        left = right = top = bottom = 0
    else:
        left, right, top, bottom = app._read_crop_margins(width_limit, height_limit)

    set_crop_controls(app, left, right, top, bottom)
    normalize_crop_controls(app)


def normalize_crop_controls(app, preferred_edge=None):
    if app.current_pil_image is None:
        return

    width, height = app.current_pil_image.size
    width_limit = max(0, width - 1)
    height_limit = max(0, height - 1)

    left, right, top, bottom = app._read_crop_margins(width_limit, height_limit)

    if left + right > width_limit:
        if preferred_edge == "right":
            right = max(0, width_limit - left)
        else:
            left = max(0, width_limit - right)

    if top + bottom > height_limit:
        if preferred_edge == "bottom":
            bottom = max(0, height_limit - top)
        else:
            top = max(0, height_limit - bottom)

    max_left = max(0, width_limit - right)
    max_right = max(0, width_limit - left)
    max_top = max(0, height_limit - bottom)
    max_bottom = max(0, height_limit - top)

    app._syncing_crop_controls = True
    try:
        app.crop_left_slider.configure(to=max_left)
        app.crop_right_slider.configure(to=max_right)
        app.crop_top_slider.configure(to=max_top)
        app.crop_bottom_slider.configure(to=max_bottom)

        app.crop_left_slider.set(min(left, max_left))
        app.crop_right_slider.set(min(right, max_right))
        app.crop_top_slider.set(min(top, max_top))
        app.crop_bottom_slider.set(min(bottom, max_bottom))

        set_crop_entry_value(app, "left", app.crop_left_slider.get())
        set_crop_entry_value(app, "right", app.crop_right_slider.get())
        set_crop_entry_value(app, "top", app.crop_top_slider.get())
        set_crop_entry_value(app, "bottom", app.crop_bottom_slider.get())
    finally:
        app._syncing_crop_controls = False

    update_crop_metadata(app)


def get_active_crop_box(app, image_size):
    width, height = image_size
    width_limit = max(0, width - 1)
    height_limit = max(0, height - 1)

    left, right, top, bottom = app._read_crop_margins(width_limit, height_limit)

    if left + right > width_limit:
        left = max(0, width_limit - right)
    if top + bottom > height_limit:
        top = max(0, height_limit - bottom)

    return (left, top, width - right, height - bottom)


def crop_to_visible_area(app, pil_img, reference_size=None):
    if pil_img is None:
        return None

    target_size = reference_size if reference_size is not None else pil_img.size
    working_img = pil_img
    if pil_img.size != target_size:
        working_img = pil_img.resize(target_size, Image.LANCZOS)

    crop_box = get_active_crop_box(app, target_size)
    if crop_box == (0, 0, target_size[0], target_size[1]):
        return working_img

    return working_img.crop(crop_box)


def update_crop(app, edge=None):
    if app._syncing_crop_controls:
        return

    normalize_crop_controls(app, preferred_edge=edge)
    app.request_preview_update()


def reset_crop(app):
    set_crop_controls(app, 0, 0, 0, 0)
    normalize_crop_controls(app)
    set_crop_preset_value(app, "Free")
    app.request_preview_update()


def apply_crop_preset(app, preset_name):
    if app._updating_crop_preset or app.current_pil_image is None:
        return

    if preset_name == "Free":
        set_crop_preset_value(app, "Free")
        return

    target_ratio = get_crop_presets(app).get(preset_name)
    if target_ratio is None:
        return

    width, height = app.current_pil_image.size
    left, top, right, bottom = get_active_crop_box(app, (width, height))
    current_width = max(1, right - left)
    current_height = max(1, bottom - top)

    if current_width / current_height > target_ratio:
        target_height = current_height
        target_width = max(1, int(round(target_height * target_ratio)))
    else:
        target_width = current_width
        target_height = max(1, int(round(target_width / target_ratio)))

    target_width = min(width, max(1, target_width))
    target_height = min(height, max(1, target_height))

    center_x = (left + right) / 2.0
    center_y = (top + bottom) / 2.0
    new_left = int(round(center_x - (target_width / 2.0)))
    new_top = int(round(center_y - (target_height / 2.0)))
    new_left = max(0, min(width - target_width, new_left))
    new_top = max(0, min(height - target_height, new_top))

    new_right = width - (new_left + target_width)
    new_bottom = height - (new_top + target_height)

    set_crop_controls(app, new_left, new_right, new_top, new_bottom)
    normalize_crop_controls(app)
    set_crop_preset_value(app, preset_name)
    app.request_preview_update()


def commit_crop_entry(app, edge):
    if app._updating_crop_entries or app._syncing_crop_controls:
        return

    slider = app._crop_slider(edge)
    target_var = app._crop_var(edge)

    current_value = int(float(slider.get()))
    raw_value = target_var.get().strip().lower().replace("px", "")

    if app.current_pil_image is None:
        max_value = 0
    else:
        width, height = app.current_pil_image.size
        if edge == "left":
            max_value = max(0, width - 1 - int(float(app.crop_right_slider.get())))
        elif edge == "right":
            max_value = max(0, width - 1 - int(float(app.crop_left_slider.get())))
        elif edge == "top":
            max_value = max(0, height - 1 - int(float(app.crop_bottom_slider.get())))
        else:
            max_value = max(0, height - 1 - int(float(app.crop_top_slider.get())))

    try:
        parsed_value = int(float(raw_value))
    except ValueError:
        parsed_value = current_value

    clamped_value = max(0, min(max_value, parsed_value))
    set_crop_entry_value(app, edge, clamped_value)

    if current_value != clamped_value:
        slider.set(clamped_value)

    normalize_crop_controls(app, preferred_edge=edge)
    app.request_preview_update()
