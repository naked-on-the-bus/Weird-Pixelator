import colorsys
import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image

import image_effects


def set_palette_text(app, text):
    if not hasattr(app, "palette_values_text"):
        return

    app.palette_values_text.configure(state=tk.NORMAL)
    app.palette_values_text.delete("1.0", tk.END)
    app.palette_values_text.insert("1.0", text)
    app.palette_values_text.configure(state=tk.DISABLED)


def reset_palette_output(app, message=None):
    app.palette_entries = []
    if message is None:
        message = "Load an image and extract a palette from the preview."

    app.palette_status_var.set(message)
    if hasattr(app, "palette_preview_inner"):
        for child in app.palette_preview_inner.winfo_children():
            child.destroy()
        tk.Label(
            app.palette_preview_inner,
            text="Extract a palette to see color swatches here.",
            fg=app.theme["muted"],
            bg=app.theme["panel_soft"],
            justify=tk.LEFT,
            wraplength=300,
        ).pack(anchor="w", padx=0, pady=8)

    set_palette_text(app, "No palette extracted yet.")


def get_color_luminance(app, rgb):
    red, green, blue = rgb
    return (0.2126 * red) + (0.7152 * green) + (0.0722 * blue)


def palette_text_color(app, rgb):
    return "#11131a" if get_color_luminance(app, rgb) >= 150 else app.theme["text"]


def rgb_to_hex(app, rgb):
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def rgb_to_hsl(app, rgb):
    red, green, blue = [channel / 255.0 for channel in rgb]
    hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    return (
        int(round(hue * 360.0)) % 360,
        int(round(saturation * 100.0)),
        int(round(lightness * 100.0)),
    )


def rgb_to_hsv(app, rgb):
    red, green, blue = [channel / 255.0 for channel in rgb]
    hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)
    return (
        int(round(hue * 360.0)) % 360,
        int(round(saturation * 100.0)),
        int(round(value * 100.0)),
    )


def rgb_to_cmyk(app, rgb):
    red, green, blue = [channel / 255.0 for channel in rgb]
    key = 1.0 - max(red, green, blue)
    if key >= 1.0:
        return (0, 0, 0, 100)

    cyan = (1.0 - red - key) / max(0.0001, 1.0 - key)
    magenta = (1.0 - green - key) / max(0.0001, 1.0 - key)
    yellow = (1.0 - blue - key) / max(0.0001, 1.0 - key)
    return (
        int(round(cyan * 100.0)),
        int(round(magenta * 100.0)),
        int(round(yellow * 100.0)),
        int(round(key * 100.0)),
    )


def get_palette_export_formats(app):
    return {
        "PNG Image (1x)": {
            "extension": ".png",
            "filetypes": [("PNG Image", "*.png")],
        },
        "PNG Image (8x)": {
            "extension": ".png",
            "filetypes": [("PNG Image", "*.png")],
        },
        "PNG Image (32x)": {
            "extension": ".png",
            "filetypes": [("PNG Image", "*.png")],
        },
        "PAL File (JASC)": {
            "extension": ".pal",
            "filetypes": [("JASC Palette", "*.pal")],
        },
        "Photoshop ASE": {
            "extension": ".ase",
            "filetypes": [("Adobe Swatch Exchange", "*.ase")],
        },
        "Paint.net TXT": {
            "extension": ".txt",
            "filetypes": [("Paint.net Palette", "*.txt")],
        },
        "GIMP GPL": {
            "extension": ".gpl",
            "filetypes": [("GIMP Palette", "*.gpl")],
        },
        "HEX File": {
            "extension": ".txt",
            "filetypes": [("HEX Palette", "*.txt")],
        },
    }


def format_palette_color(app, rgb):
    hex_value = rgb_to_hex(app, rgb)
    rgb_value = f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
    hsl = rgb_to_hsl(app, rgb)
    hsv = rgb_to_hsv(app, rgb)
    cmyk = rgb_to_cmyk(app, rgb)

    hsl_value = f"hsl({hsl[0]}°, {hsl[1]}%, {hsl[2]}%)"
    hsv_value = f"hsv({hsv[0]}°, {hsv[1]}%, {hsv[2]}%)"
    cmyk_value = f"cmyk({cmyk[0]}%, {cmyk[1]}%, {cmyk[2]}%, {cmyk[3]}%)"
    return f"{hex_value} | {rgb_value} | {hsl_value} | {hsv_value} | {cmyk_value}"


def copy_palette_hex(app, rgb):
    hex_value = rgb_to_hex(app, rgb)
    app.root.clipboard_clear()
    app.root.clipboard_append(hex_value)
    app.root.update_idletasks()
    app.palette_status_var.set(f"Copied {hex_value} to the clipboard.")


def palette_file_stem(app):
    if app.image_object is None or not getattr(app.image_object, "name", None):
        return "Weird_Pixelator_Palette"

    name_root, _ext = os.path.splitext(app.image_object.name)
    cleaned = name_root.strip() or "Weird_Pixelator_Palette"
    return f"{cleaned}_palette"


def write_palette_png(app, file_path, entries, scale):
    colors = [entry["rgb"] for entry in entries]
    swatch_size = max(1, int(scale))
    palette_image = Image.new("RGB", (len(colors) * swatch_size, swatch_size))

    for index, rgb in enumerate(colors):
        swatch = Image.new("RGB", (swatch_size, swatch_size), rgb)
        palette_image.paste(swatch, (index * swatch_size, 0))

    palette_image.save(file_path)


def write_palette_jasc(app, file_path, entries):
    lines = ["JASC-PAL", "0100", str(len(entries))]
    for entry in entries:
        red, green, blue = entry["rgb"]
        lines.append(f"{red} {green} {blue}")

    with open(file_path, "w", encoding="utf-8") as palette_file:
        palette_file.write("\n".join(lines) + "\n")


def write_palette_hex_file(app, file_path, entries):
    lines = [rgb_to_hex(app, entry["rgb"]) for entry in entries]
    with open(file_path, "w", encoding="utf-8") as palette_file:
        palette_file.write("\n".join(lines) + "\n")


def write_palette_gpl(app, file_path, entries):
    lines = [
        "GIMP Palette",
        f"Name: {palette_file_stem(app)}",
        "Columns: 4",
        "#",
    ]
    for index, entry in enumerate(entries, start=1):
        red, green, blue = entry["rgb"]
        lines.append(f"{red:3d} {green:3d} {blue:3d} Color {index}")

    with open(file_path, "w", encoding="utf-8") as palette_file:
        palette_file.write("\n".join(lines) + "\n")


def write_palette_paintnet(app, file_path, entries):
    lines = [
        "; paint.net Palette File",
        "; Generated by Weird Pixelator",
        "; Colors are written as AARRGGBB hex values",
    ]
    for entry in entries:
        red, green, blue = entry["rgb"]
        lines.append(f"FF{red:02X}{green:02X}{blue:02X}")

    with open(file_path, "w", encoding="utf-8") as palette_file:
        palette_file.write("\n".join(lines) + "\n")


def write_palette_ase(app, file_path, entries):
    blocks = []
    for index, entry in enumerate(entries, start=1):
        red, green, blue = entry["rgb"]
        name = f"Color {index}"
        name_data = name.encode("utf-16be") + b"\x00\x00"
        name_length = len(name) + 1
        block_data = b"".join(
            [
                struct.pack(">H", name_length),
                name_data,
                b"RGB ",
                struct.pack(">fff", red / 255.0, green / 255.0, blue / 255.0),
                struct.pack(">H", 0),
            ]
        )
        blocks.append(struct.pack(">HI", 0x0001, len(block_data)) + block_data)

    header = struct.pack(">4sHHI", b"ASEF", 1, 0, len(blocks))
    with open(file_path, "wb") as palette_file:
        palette_file.write(header)
        for block in blocks:
            palette_file.write(block)


def export_palette_file(app, entries):
    format_name = app.palette_format_var.get()
    format_info = get_palette_export_formats(app).get(format_name)
    if format_info is None:
        raise ValueError("Unsupported palette format.")

    initial_dir = app.folder_path.get().strip() or os.getcwd()
    file_path = filedialog.asksaveasfilename(
        title="Save Palette",
        defaultextension=format_info["extension"],
        filetypes=format_info["filetypes"],
        initialdir=initial_dir,
        initialfile=f"{palette_file_stem(app)}{format_info['extension']}",
    )
    if not file_path:
        return None

    if format_name == "PNG Image (1x)":
        write_palette_png(app, file_path, entries, 1)
    elif format_name == "PNG Image (8x)":
        write_palette_png(app, file_path, entries, 8)
    elif format_name == "PNG Image (32x)":
        write_palette_png(app, file_path, entries, 32)
    elif format_name == "PAL File (JASC)":
        write_palette_jasc(app, file_path, entries)
    elif format_name == "Photoshop ASE":
        write_palette_ase(app, file_path, entries)
    elif format_name == "Paint.net TXT":
        write_palette_paintnet(app, file_path, entries)
    elif format_name == "GIMP GPL":
        write_palette_gpl(app, file_path, entries)
    elif format_name == "HEX File":
        write_palette_hex_file(app, file_path, entries)
    else:
        raise ValueError("Unsupported palette format.")

    return file_path


def sorted_palette_entries(app):
    entries = list(app.palette_entries)
    sort_mode = app.palette_sort_var.get()

    if sort_mode == "Hue":
        entries.sort(key=lambda entry: rgb_to_hsv(app, entry["rgb"]))
        return entries

    if sort_mode == "Brightness":
        entries.sort(key=lambda entry: get_color_luminance(app, entry["rgb"]))
        return entries

    entries.sort(key=lambda entry: (-entry["count"], -get_color_luminance(app, entry["rgb"])))
    return entries


def update_palette_count(app, _=None):
    if app.palette_entries:
        extract_palette_from_preview_internal(app, save_to_file=False)


def update_palette_display(app, _=None):
    if not app.palette_entries:
        reset_palette_output(app, app.palette_status_var.get())
        return

    for child in app.palette_preview_inner.winfo_children():
        child.destroy()

    sorted_entries = sorted_palette_entries(app)
    for column in range(8):
        app.palette_preview_inner.grid_columnconfigure(column, weight=1)

    for index, entry in enumerate(sorted_entries):
        rgb = entry["rgb"]
        hex_value = rgb_to_hex(app, rgb)
        tile = tk.Frame(
            app.palette_preview_inner,
            bg=hex_value,
            highlightbackground=hex_value,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
            width=14,
            height=14,
        )
        tile.grid(row=index // 8, column=index % 8, sticky="nsew", padx=0, pady=0)
        tile.grid_propagate(False)

        for widget in (tile,):
            widget.bind("<Button-1>", lambda _event, color=rgb: copy_palette_hex(app, color))

    lines = []
    for index, entry in enumerate(sorted_entries, start=1):
        color_text = format_palette_color(app, entry["rgb"])
        ratio_text = f"{entry['ratio'] * 100:.1f}%"
        lines.append(f"{index}. {color_text} • {ratio_text}")

    set_palette_text(app, "\n".join(lines))


def extract_palette_from_preview_internal(app, save_to_file=False):
    if app.image_object is None or app.current_pil_image is None:
        messagebox.showerror("Error", "Load an image before extracting a palette.")
        return

    preview_image = app.render_current_image(for_preview=True)
    if preview_image is None:
        messagebox.showerror("Error", "Unable to render the current preview for palette extraction.")
        return

    color_count = max(2, min(24, int(float(app.palette_count_slider.get()))))
    entries = image_effects.extract_palette(preview_image, color_count)
    if not entries:
        reset_palette_output(app, "No colors could be extracted from the current preview.")
        return

    app.palette_entries = entries
    app.palette_status_var.set(f"Extracted {len(entries)} colors from the current preview.")
    update_palette_display(app)

    if save_to_file:
        file_path = export_palette_file(app, sorted_palette_entries(app))
        if file_path:
            app.palette_status_var.set(f"Saved palette to {os.path.basename(file_path)}")


def extract_palette_from_preview(app):
    extract_palette_from_preview_internal(app, save_to_file=False)


def save_palette_as(app):
    if not app.palette_entries:
        messagebox.showerror("Error", "Extract a palette before saving it.")
        return

    try:
        file_path = export_palette_file(app, sorted_palette_entries(app))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save palette: {e}")
        return

    if file_path:
        app.palette_status_var.set(f"Saved palette to {os.path.basename(file_path)}")
