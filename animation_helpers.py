import tkinter as tk
from tkinter import messagebox

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageTk, ImageOps


def update_animation_status(app):
    frame_count = len(app.animation_frames)
    if frame_count == 0:
        app.animation_status_var.set("No frames added yet.")
        return

    first_width, first_height = app.animation_frames[0].size
    suffix = " • showing latest 6" if frame_count > 6 else ""
    app.animation_status_var.set(f"{frame_count} frame(s) • base {first_width} x {first_height}{suffix}")


def refresh_animation_preview_strip(app):
    for child in app.animation_preview_inner.winfo_children():
        child.destroy()

    app.animation_preview_images = []

    if not app.animation_frames:
        empty_label = tk.Label(
            app.animation_preview_inner,
            text="Capture frames from the current preview to build an animation.",
            fg=app.theme["muted"],
            bg=app.theme["panel_soft"],
            justify=tk.LEFT,
            wraplength=300,
        )
        empty_label.pack(anchor="w", padx=12, pady=18)
        update_animation_status(app)
        return

    for column in range(3):
        app.animation_preview_inner.grid_columnconfigure(column, weight=1)

    visible_frames = list(enumerate(app.animation_frames, start=1))[-6:]

    for display_index, (frame_index, frame) in enumerate(visible_frames):
        tile = tk.Frame(
            app.animation_preview_inner,
            bg=app.theme["panel_alt"],
            highlightbackground=app.theme["border"],
            highlightthickness=1,
            bd=0,
        )
        tile.grid(row=display_index // 3, column=display_index % 3, sticky="nsew", padx=4, pady=4)

        thumb = frame.copy()
        thumb.thumbnail((92, 92), Image.LANCZOS)
        photo = ImageTk.PhotoImage(thumb)
        app.animation_preview_images.append(photo)

        preview_label = tk.Label(tile, image=photo, bg=app.theme["panel_alt"])
        preview_label.pack(padx=8, pady=(8, 4))

        caption = tk.Label(
            tile,
            text=f"Frame {frame_index}\n{frame.size[0]} x {frame.size[1]}",
            fg=app.theme["text"],
            bg=app.theme["panel_alt"],
            justify=tk.CENTER,
        )
        caption.pack(padx=8, pady=(0, 8))

    update_animation_status(app)


def get_animation_export_formats(app):
    return {
        "GIF": {
            "extension": ".gif",
            "filetypes": [("GIF Animation", "*.gif")],
        },
        "MP4": {
            "extension": ".mp4",
            "filetypes": [("MP4 Video", "*.mp4")],
        },
        "Animated WebP": {
            "extension": ".webp",
            "filetypes": [("Animated WebP", "*.webp")],
        },
    }


def prepare_animation_frames(app, target_size=None, flatten_alpha=False):
    if not app.animation_frames:
        return []

    if target_size is None:
        target_size = app.animation_frames[0].size

    prepared_frames = []
    for frame in app.animation_frames:
        working = frame.convert("RGBA")
        if working.size != target_size:
            working = ImageOps.pad(working, target_size, method=Image.LANCZOS, color=(0, 0, 0, 255))

        if flatten_alpha:
            background = Image.new("RGB", target_size, (0, 0, 0))
            background.paste(working, mask=working.getchannel("A"))
            prepared_frames.append(background)
        else:
            prepared_frames.append(working)

    return prepared_frames


def add_animation_frame(app):
    if app.image_object is None:
        messagebox.showerror("Error", "Load an image before adding animation frames.")
        return

    frame_image = app.render_current_image(for_preview=False)
    if frame_image is None:
        messagebox.showerror("Error", "Unable to render the current frame.")
        return

    app.animation_frames.append(frame_image.copy())
    refresh_animation_preview_strip(app)


def delete_last_animation_frame(app):
    if not app.animation_frames:
        messagebox.showerror("Error", "There are no animation frames to delete.")
        return

    app.animation_frames.pop()
    refresh_animation_preview_strip(app)


def clear_animation_frames(app):
    app.animation_frames.clear()
    refresh_animation_preview_strip(app)


def open_animation_export_modal(app):
    if not app.animation_frames:
        messagebox.showerror("Error", "Add at least one frame before exporting an animation.")
        return

    formats = get_animation_export_formats(app)
    modal = tk.Toplevel(app.root)
    modal.title("Export Animation")
    modal.configure(bg=app.theme["panel"])
    modal.transient(app.root)
    modal.grab_set()
    modal.resizable(False, False)

    format_var = tk.StringVar(value="GIF")
    fps_var = tk.IntVar(value=8)

    tk.Label(
        modal,
        text=f"Frames: {len(app.animation_frames)}\nFrames with different sizes will be padded to the first frame when exported.",
        fg=app.theme["muted"],
        bg=app.theme["panel"],
        justify=tk.LEFT,
    ).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 8))

    tk.Label(modal, text="Format:", fg=app.theme["text"], bg=app.theme["panel"]).grid(row=1, column=0, sticky="w", padx=12, pady=4)
    format_menu = tk.OptionMenu(modal, format_var, *formats.keys())
    app._style_option_menu(format_menu)
    format_menu.grid(row=1, column=1, sticky="ew", padx=12, pady=4)

    tk.Label(modal, text="FPS:", fg=app.theme["text"], bg=app.theme["panel"]).grid(row=2, column=0, sticky="w", padx=12, pady=4)
    fps_spinbox = tk.Spinbox(
        modal,
        from_=1,
        to=60,
        textvariable=fps_var,
        width=8,
        bg=app.theme["field"],
        fg=app.theme["text"],
        insertbackground=app.theme["text"],
        buttonbackground=app.theme["button"],
        relief=tk.SUNKEN,
        bd=2,
    )
    fps_spinbox.grid(row=2, column=1, sticky="w", padx=12, pady=4)

    button_row = tk.Frame(modal, bg=app.theme["panel"])
    button_row.grid(row=3, column=0, columnspan=2, sticky="e", padx=12, pady=(12, 12))

    tk.Button(button_row, text="Cancel", command=modal.destroy, **app._button_style(app.theme["button"])).pack(side=tk.LEFT, padx=(0, 6))
    tk.Button(
        button_row,
        text="Export",
        command=lambda: export_animation_from_modal(app, modal, format_var.get(), fps_var.get()),
        **app._button_style(app.theme["button_alt"]),
    ).pack(side=tk.LEFT)


def export_animation_from_modal(app, modal, format_name, fps_value):
    formats = get_animation_export_formats(app)
    format_info = formats.get(format_name)
    if format_info is None:
        messagebox.showerror("Error", "Unsupported animation format.")
        return

    try:
        fps = max(1, min(60, int(fps_value)))
    except (TypeError, ValueError):
        messagebox.showerror("Error", "FPS must be a whole number between 1 and 60.")
        return

    file_path = app._ask_save_file(
        title="Export Animation",
        defaultextension=format_info["extension"],
        filetypes=format_info["filetypes"],
        initialfile=f"Weird_Pixellator_Animation{format_info['extension']}",
    )
    if not file_path:
        return

    app._run_export_with_feedback(
        export_callable=lambda: export_animation(app, file_path, format_name, fps),
        failure_message="Failed to export animation",
        success_message=f"Animation exported to {file_path}",
        on_success=modal.destroy,
    )


def export_animation(app, file_path, format_name, fps):
    if not app.animation_frames:
        raise ValueError("No animation frames available.")

    duration_ms = max(1, int(round(1000 / max(1, fps))))
    base_width, base_height = app.animation_frames[0].size

    if format_name == "GIF":
        frames = prepare_animation_frames(app, target_size=(base_width, base_height), flatten_alpha=False)
        frames[0].save(
            file_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration_ms,
            loop=0,
            disposal=2,
        )
        return

    if format_name == "Animated WebP":
        frames = prepare_animation_frames(app, target_size=(base_width, base_height), flatten_alpha=False)
        frames[0].save(
            file_path,
            format="WEBP",
            save_all=True,
            append_images=frames[1:],
            duration=duration_ms,
            loop=0,
            lossless=True,
            quality=90,
            method=6,
        )
        return

    if format_name == "MP4":
        video_size = (base_width + (base_width % 2), base_height + (base_height % 2))
        frames = prepare_animation_frames(app, target_size=video_size, flatten_alpha=True)
        with imageio.get_writer(
            file_path,
            fps=fps,
            codec="libx264",
            quality=8,
            pixelformat="yuv420p",
            macro_block_size=1,
        ) as writer:
            for frame in frames:
                writer.append_data(np.array(frame))
        return

    raise ValueError(f"Unsupported export format: {format_name}")
