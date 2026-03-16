import os

import imageio.v2 as imageio
import numpy as np
from PIL import Image
from tkinter import filedialog, messagebox

from engine.image_object import ImageObject


def is_video_path(path):
    ext = os.path.splitext(path)[1].lower()
    return ext in {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}


def close_video_preview_window(app):
    if app.video_preview_window is not None and app.video_preview_window.winfo_exists():
        app.video_preview_window.destroy()


def read_video_source_snapshot(file_path):
    reader = imageio.get_reader(file_path)
    try:
        first = reader.get_data(0)
        meta = reader.get_meta_data() or {}
        fps = float(meta.get("fps", 12.0) or 12.0)
        frame_count = 0
        try:
            frame_count = int(meta.get("nframes", 0) or 0)
        except Exception:
            frame_count = 0
        if frame_count <= 0:
            try:
                frame_count = int(reader.count_frames())
            except Exception:
                frame_count = 0
    finally:
        reader.close()

    return Image.fromarray(first).convert("RGBA"), fps, frame_count


def apply_loaded_media(app, file_path, img, is_video_mode, video_fps=12.0, video_frame_count=0, select_intensity_tab=False):
    width, height = img.size
    pixel_array = np.array(img)

    app.image_object = ImageObject(name=os.path.basename(file_path), size=(width, height), pixel_array=pixel_array)
    app.image_source_path = file_path
    app.current_pil_image = img
    app.is_video_mode = bool(is_video_mode)
    app.video_source_path = file_path if is_video_mode else None
    app.video_frame_count = max(0, int(video_frame_count)) if is_video_mode else 0
    app.video_fps = max(1.0, float(video_fps)) if is_video_mode else 12.0

    app._sync_media_tabs()
    app._reset_controls_for_new_image()
    app.disable_manual_blending()
    if is_video_mode:
        app._refresh_video_intensity_controls(force=True)
    app._update_video_action_buttons()
    app.pipeline_image = img.copy()
    app.display_image(img)

    if select_intensity_tab and is_video_mode:
        try:
            app.controls_notebook.select(app.intensity_tab)
        except Exception:
            pass


def execute_upload(app):
    try:
        file_path = filedialog.askopenfilename(
            title="Select an Image or Video",
            filetypes=[
                ("Supported Media", "*.png *.jpg *.jpeg *.gif *.bmp *.mp4 *.mov *.avi *.mkv *.webm *.m4v"),
                ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Video Files", "*.mp4 *.mov *.avi *.mkv *.webm *.m4v"),
            ]
        )

        if not file_path:
            return

        if is_video_path(file_path):
            app._load_video_file(file_path)
        else:
            app._load_image_file(file_path)

    except Exception as e:
        print(f"Error loading or processing media: {e}")
        messagebox.showerror("Error", f"Failed to load media: {e}")
