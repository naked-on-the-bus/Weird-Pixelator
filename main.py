import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import colorsys
import os
import struct
from io import BytesIO
from PIL import Image, ImageTk, ImageOps
import numpy as np
import imageio.v2 as imageio
from image_object import ImageObject
import image_effects
import media_io_helpers
import export_helpers
import render_pipeline_helpers
import ui_builders
import palette_helpers
import animation_helpers
import crop_helpers

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Weird Pixelator")
        self.is_macos = self.root.tk.call("tk", "windowingsystem") == "aqua"

        self.image_object = None
        self.image_source_path = None
        self.current_pil_image = None
        self.pipeline_image = None
        self.full_resolution_image = None
        self.blend_image_pil = None
        self.randomize_settings = self._create_randomize_settings()
        self.preview_delay_ms = 75
        self._pending_preview_job = None
        self._suspend_preview_updates = False
        self._updating_crop_entries = False
        self._syncing_crop_controls = False
        self.crop_left_var = tk.StringVar(value="0")
        self.crop_right_var = tk.StringVar(value="0")
        self.crop_top_var = tk.StringVar(value="0")
        self.crop_bottom_var = tk.StringVar(value="0")
        self.crop_size_var = tk.StringVar(value="Final Size: -")
        self.crop_preset_var = tk.StringVar(value="Free")
        self._updating_crop_preset = False
        self.export_compression_var = tk.StringVar(value="No Compression")
        self.animation_frames = []
        self.animation_preview_images = []
        self.animation_status_var = tk.StringVar(value="No frames added yet.")
        self.video_source_path = None
        self.video_fps = 12.0
        self.video_frame_count = 0
        self.is_video_mode = False
        self.video_intensity_controls = {}
        self.video_intensity_active_keys = []
        self.video_intensity_rows = {}
        self.video_preview_window = None
        self.video_preview_images = []
        self.video_preview_index = 0
        self.video_status_var = tk.StringVar(value="Load a video to configure frame intensity controls.")
        self.manual_blend_bytes = b""
        self.manual_blend_enabled = False
        self.manual_blend_editor_window = None
        self.manual_blend_text_widget = None
        self.manual_blend_status_var = tk.StringVar(value="No manual text data loaded.")
        self.manual_blend_encoding_var = tk.StringVar(value="Hex")
        self.manual_blend_encoding_trace_id = None
        self.manual_blend_live_editing = False
        self.manual_blend_direct_reopen_var = tk.BooleanVar(value=False)
        self.manual_blend_source_bytes = b""
        self._manual_blend_pending_job = None
        self.palette_entries = []
        self.palette_status_var = tk.StringVar(value="Load an image and extract a palette from the preview.")
        self.palette_format_var = tk.StringVar(value="HEX File")
        self.palette_sort_var = tk.StringVar(value="Frequency")
        self.bend_mode_var = tk.StringVar(value="Byte Shift")
        self.datamosh_mode_var = tk.StringVar(value="AVI Style")
        self.theme_name_var = tk.StringVar(value="Classic Gray")
        self.invert_state = tk.BooleanVar(value=False)
        self.folder_path = tk.StringVar()
        self.blend_filename_var = tk.StringVar(value="No file")
        self.preview_title_var = tk.StringVar(value="No image loaded")
        self.preview_hint_var = tk.StringVar(value="Upload an image to start creating a glitchy preview.")
        self._slider_value_bindings = []
        self.themes = self._create_theme_presets()
        self.theme = self.themes[self.theme_name_var.get()]

        self.root.geometry("1080x720")
        self.root.minsize(920, 660)
        self._build_ui_shell()
        self._sync_crop_controls_to_image(reset_values=True)
        self._refresh_animation_preview_strip()
        self._render_empty_preview()

    def _create_theme_presets(self):
        """
        Return the available app themes.
        """
        return {
            "Classic Gray": {
                "bg": "#c0c0c0",
                "panel": "#d4d0c8",
                "panel_alt": "#ece9d8",
                "panel_soft": "#f3f0e4",
                "border": "#7f7f7f",
                "text": "#111111",
                "muted": "#4e4e4e",
                "canvas": "#808080",
                "field": "#ffffff",
                "field_border": "#7f9db9",
                "accent": "#0a246a",
                "accent_soft": "#b6c7e5",
                "button": "#d4d0c8",
                "button_alt": "#e6e2d8",
                "shadow_dark": "#808080",
                "shadow_light": "#ffffff",
            },
            "XP Blue": {
                "bg": "#dbe7f7",
                "panel": "#ece9d8",
                "panel_alt": "#ffffff",
                "panel_soft": "#f7f4ea",
                "border": "#7f9db9",
                "text": "#0f1728",
                "muted": "#4f6280",
                "canvas": "#6f8db9",
                "field": "#ffffff",
                "field_border": "#7f9db9",
                "accent": "#1f5fbf",
                "accent_soft": "#c8daf5",
                "button": "#d6e3f5",
                "button_alt": "#eef4fd",
                "shadow_dark": "#7f9db9",
                "shadow_light": "#ffffff",
            },
            "Olive Retro": {
                "bg": "#d6d6c2",
                "panel": "#d9d3be",
                "panel_alt": "#ece7d5",
                "panel_soft": "#f5f1e5",
                "border": "#8a8673",
                "text": "#232117",
                "muted": "#5f5a46",
                "canvas": "#8d9278",
                "field": "#fffdf6",
                "field_border": "#9fa27f",
                "accent": "#4f6b2b",
                "accent_soft": "#cfd9b6",
                "button": "#d6d0b8",
                "button_alt": "#e8e2cb",
                "shadow_dark": "#8a8673",
                "shadow_light": "#fffdf6",
            },
            "Windows 98 Beige": {
                "bg": "#c9c1b2",
                "panel": "#d8d0c4",
                "panel_alt": "#efe7da",
                "panel_soft": "#f7f1e7",
                "border": "#8b8173",
                "text": "#1d1a16",
                "muted": "#655c52",
                "canvas": "#8f877c",
                "field": "#fffaf2",
                "field_border": "#9d9283",
                "accent": "#7a0000",
                "accent_soft": "#d8beb8",
                "button": "#d8d0c4",
                "button_alt": "#e8dfd1",
                "shadow_dark": "#8b8173",
                "shadow_light": "#fffaf2",
            },
            "Dark Retro": {
                "bg": "#2e2a26",
                "panel": "#3a342f",
                "panel_alt": "#4a433d",
                "panel_soft": "#544c45",
                "border": "#161311",
                "text": "#f2eadf",
                "muted": "#c2b5a3",
                "canvas": "#1b1714",
                "field": "#241f1b",
                "field_border": "#8a7a67",
                "accent": "#c86b2a",
                "accent_soft": "#7b6758",
                "button": "#4a433d",
                "button_alt": "#5a5148",
                "shadow_dark": "#161311",
                "shadow_light": "#7a6e62",
            },
            "Terminal Green": {
                "bg": "#0b120b",
                "panel": "#132013",
                "panel_alt": "#1a2a1a",
                "panel_soft": "#1f331f",
                "border": "#2f5a2f",
                "text": "#8cff8c",
                "muted": "#5fb35f",
                "canvas": "#050805",
                "field": "#091009",
                "field_border": "#2f5a2f",
                "accent": "#00ff66",
                "accent_soft": "#1f4f2c",
                "button": "#183018",
                "button_alt": "#204020",
                "shadow_dark": "#041004",
                "shadow_light": "#3b6f3b",
            },
        }

    def _build_ui_shell(self):
        """
        Build or rebuild the main app shell for the current theme.
        """
        ui_builders.build_ui_shell(self)

    def _capture_ui_state(self):
        """
        Capture current widget state so the UI can be rebuilt for theme changes.
        """
        slider_names = [
            'pixel_slider', 'jitter_slider', 'block_slider', 'sort_slider',
            'hue_slider', 'saturation_slider', 'contrast_slider',
            'random_pixel_slider', 'blur_slider', 'color_reducer_slider', 'legacy_color_slider', 'bend_slider', 'datamosh_slider',
            'blend_slider', 'curvature_slider', 'distortion_slider', 'glow_slider',
            'noise_slider', 'scanline_slider', 'rgb_shift_slider', 'vignette_slider',
        ]
        slider_values = {}
        for name in slider_names:
            if hasattr(self, name):
                slider_values[name] = float(getattr(self, name).get())

        selected_tab = 0
        if hasattr(self, 'controls_notebook'):
            try:
                selected_tab = self.controls_notebook.index(self.controls_notebook.select())
            except tk.TclError:
                selected_tab = 0

        palette_entries = [dict(entry) for entry in self.palette_entries]

        return {
            'sliders': slider_values,
            'invert_state': bool(self.invert_state.get()),
            'crop_values': {
                'left': self.crop_left_var.get(),
                'right': self.crop_right_var.get(),
                'top': self.crop_top_var.get(),
                'bottom': self.crop_bottom_var.get(),
            },
            'crop_preset': self.crop_preset_var.get(),
            'export_compression': self.export_compression_var.get(),
            'folder_path': self.folder_path.get(),
            'blend_image_pil': self.blend_image_pil,
            'blend_filename': self.blend_filename_var.get(),
            'palette_entries': palette_entries,
            'palette_status': self.palette_status_var.get(),
            'palette_format': self.palette_format_var.get(),
            'palette_sort': self.palette_sort_var.get(),
            'bend_mode': self.bend_mode_var.get(),
            'datamosh_mode': self.datamosh_mode_var.get(),
            'selected_tab': selected_tab,
            'is_video_mode': self.is_video_mode,
            'video_source_path': self.video_source_path,
            'video_fps': self.video_fps,
            'video_frame_count': self.video_frame_count,
            'video_intensity_settings': {
                key: {
                    'step': int(float(control['step'].get())),
                    'drift': float(control['drift'].get()),
                }
                for key, control in self.video_intensity_controls.items()
            },
        }

    def _restore_ui_state(self, state):
        """
        Restore widget state after a themed UI rebuild.
        """
        self.begin_bulk_update()
        try:
            for name, value in state['sliders'].items():
                if hasattr(self, name):
                    getattr(self, name).set(value)

            self.invert_state.set(state['invert_state'])
            self.export_compression_var.set(state['export_compression'])
            self.folder_path.set(state['folder_path'])
            self.blend_image_pil = state['blend_image_pil']
            self.blend_filename_var.set(state['blend_filename'])
            self.palette_format_var.set(state['palette_format'])
            self.palette_sort_var.set(state['palette_sort'])
            self.bend_mode_var.set(state.get('bend_mode', 'Byte Shift'))
            self.datamosh_mode_var.set(state.get('datamosh_mode', 'AVI Style'))
            self.is_video_mode = bool(state.get('is_video_mode', False))
            self.video_source_path = state.get('video_source_path')
            self.video_fps = float(state.get('video_fps', 12.0) or 12.0)
            self.video_frame_count = int(state.get('video_frame_count', 0) or 0)

            self._sync_crop_controls_to_image(reset_values=True)
            left = int(float(state['crop_values']['left'])) if state['crop_values']['left'] else 0
            right = int(float(state['crop_values']['right'])) if state['crop_values']['right'] else 0
            top = int(float(state['crop_values']['top'])) if state['crop_values']['top'] else 0
            bottom = int(float(state['crop_values']['bottom'])) if state['crop_values']['bottom'] else 0
            self._set_crop_controls(left, right, top, bottom)
            self._normalize_crop_controls()
            self._set_crop_preset_value(state['crop_preset'])
        finally:
            self.end_bulk_update(refresh=False)

        self.palette_entries = state['palette_entries']
        self.palette_status_var.set(state['palette_status'])
        if self.palette_entries:
            self.update_palette_display()
        else:
            self._reset_palette_output(state['palette_status'])

        self._refresh_animation_preview_strip()
        self._sync_media_tabs()
        self._refresh_video_intensity_controls(force=True)
        for key, values in state.get('video_intensity_settings', {}).items():
            control = self.video_intensity_controls.get(key)
            if control is None:
                continue
            control['step'].set(values.get('step', 1))
            control['drift'].set(values.get('drift', 25.0))
        self._update_video_action_buttons()

        if hasattr(self, 'controls_notebook'):
            try:
                self.controls_notebook.select(state['selected_tab'])
            except tk.TclError:
                pass

        if self.image_object is not None and self.current_pil_image is not None:
            self.apply_pipeline()
        else:
            self._render_empty_preview()

    def set_theme(self, theme_name):
        """
        Apply a named theme and rebuild the interface.
        """
        if theme_name not in self.themes:
            return

        state = self._capture_ui_state() if hasattr(self, 'app_shell') else None
        self.theme_name_var.set(theme_name)
        self.theme = self.themes[theme_name]
        self._build_ui_shell()

        if state is not None:
            self._restore_ui_state(state)

    def open_app_settings(self):
        """
        Open app settings, including theme selection.
        """
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.configure(bg=self.theme["panel"])
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)

        tk.Label(
            win,
            text="Theme",
            fg=self.theme["text"],
            bg=self.theme["panel"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))

        theme_var = tk.StringVar(value=self.theme_name_var.get())
        theme_menu = tk.OptionMenu(win, theme_var, *self.themes.keys())
        self._style_option_menu(theme_menu)
        theme_menu.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))

        button_row = tk.Frame(win, bg=self.theme["panel"])
        button_row.grid(row=2, column=0, sticky="e", padx=12, pady=(0, 12))

        def apply_and_close():
            selected_theme = theme_var.get()
            win.destroy()
            self.set_theme(selected_theme)

        tk.Button(button_row, text="Cancel", command=win.destroy, **self._button_style(self.theme["button"])).pack(side=tk.LEFT, padx=(0, 6))
        tk.Button(button_row, text="Apply", command=apply_and_close, **self._button_style(self.theme["button_alt"])).pack(side=tk.LEFT)

    def _configure_notebook_style(self):
        """
        Configure a compact classic notebook style for the right sidebar tabs.
        """
        ui_builders.configure_notebook_style(self)

    def _build_header(self):
        """
        Build the compact top bar.
        """
        ui_builders.build_header(self)

    def _build_preview_panel(self):
        """
        Build the left preview area.
        """
        ui_builders.build_preview_panel(self)

    def _build_control_sidebar(self):
        """
        Build the compact tabbed control sidebar.
        """
        ui_builders.build_control_sidebar(self)

    def _build_adjust_tab(self):
        """
        Build the main effect controls tab.
        """
        self.edit_tab.grid_columnconfigure(0, weight=1)
        self.edit_tab.grid_columnconfigure(1, weight=1)

        self.pixelate_frame, pixelate_body = self._create_card(self.edit_tab, "Pixelate")
        self.pixelate_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 8))
        self.jitter_slider = self._create_compact_slider(pixelate_body, "Row Jitter", 0, 100, self.update_effects, initial=0)
        self.block_slider = self._create_compact_slider(pixelate_body, "Block Shift", 0, 100, self.update_effects, initial=0)
        self.sort_slider = self._create_compact_slider(pixelate_body, "Pixel Sort", 0, 100, self.update_effects, initial=0)
        self.pixel_slider = self._create_compact_slider(
            pixelate_body,
            "Pixelate",
            1.0,
            0.01,
            self.update_effects,
            resolution=0.01,
            initial=1.0,
            formatter=lambda value: f"{float(value):.2f}"
        )

        self.colorize_frame, colorize_body = self._create_card(self.edit_tab, "Colorize")
        self.colorize_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 8))
        self.hue_slider = self._create_compact_slider(colorize_body, "Hue Shift", -180, 180, self.update_colorize, initial=0)
        self.saturation_slider = self._create_compact_slider(
            colorize_body,
            "Saturation",
            0.0,
            2.0,
            self.update_colorize,
            resolution=0.1,
            initial=1.0,
            formatter=lambda value: f"{float(value):.1f}"
        )
        self.contrast_slider = self._create_compact_slider(
            colorize_body,
            "Contrast",
            0.5,
            2.0,
            self.update_colorize,
            resolution=0.1,
            initial=1.0,
            formatter=lambda value: f"{float(value):.1f}"
        )
        self.invert_button = tk.Checkbutton(
            colorize_body,
            text="Invert Colors",
            variable=self.invert_state,
            command=self.toggle_invert,
            bg=self.theme["panel"],
            fg=self.theme["text"],
            activebackground=self.theme["panel"],
            activeforeground=self.theme["text"],
            selectcolor=self.theme["field"],
            highlightthickness=0,
            bd=0,
            anchor="w"
        )
        self.invert_button.pack(fill=tk.X, pady=(4, 0))

        self.randomize_frame, randomize_body = self._create_card(self.edit_tab, "Randomize")
        self.randomize_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=(0, 8))
        self.randomize_button = tk.Button(
            randomize_body,
            text="Randomize Effects",
            command=self.randomize_effects,
            **self._button_style(self.theme["button"])
        )
        self.randomize_button.pack(fill=tk.X)
        self.random_pixel_slider = self._create_compact_slider(
            randomize_body,
            "Random Pixels",
            0.0,
            1.0,
            self.update_random_pixels,
            resolution=0.01,
            initial=0.0,
            formatter=lambda value: f"{float(value):.2f}"
        )
        self.randomize_settings_inline = tk.Button(
            randomize_body,
            text="Choose Randomized Controls",
            command=self.open_randomize_settings,
            **self._button_style(self.theme["button_alt"])
        )
        self.randomize_settings_inline.pack(fill=tk.X, pady=(6, 0))

        self.confuser_frame, confuser_body = self._create_card(self.edit_tab, "Confuser")
        self.confuser_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 0), pady=(0, 8))
        self.blur_slider = self._create_compact_slider(confuser_body, "Blur", 0, 10, self.update_confuser, initial=0)
        self.color_reducer_slider = self._create_compact_slider(confuser_body, "Color Reducer", 2, 256, self.update_confuser, initial=256)
        self.legacy_color_slider = self._create_compact_slider(confuser_body, "Color Collapse", 2, 256, self.update_confuser, initial=256)

        self.blend_frame, blend_body = self._create_card(self.edit_tab, "Blend")
        self.blend_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.upload_blend_button = tk.Button(
            blend_body,
            text="Upload Blend Image",
            command=self.upload_blend_image,
            **self._button_style(self.theme["button"])
        )
        self.upload_blend_button.pack(fill=tk.X)
        tk.Label(
            blend_body,
            textvariable=self.blend_filename_var,
            fg=self.theme["muted"],
            bg=self.theme["panel"],
            anchor="w"
        ).pack(fill=tk.X, pady=(6, 2))
        self.blend_slider = self._create_compact_slider(
            blend_body,
            "Blend Factor",
            0.0,
            1.0,
            self.update_blend,
            resolution=0.01,
            initial=0.0,
            formatter=lambda value: f"{float(value):.2f}"
        )

    def _build_glitch_tab(self):
        """
        Build databending and datamoshing controls.
        """
        self.glitch_tab.grid_columnconfigure(0, weight=1)
        self.glitch_tab.grid_columnconfigure(1, weight=1)

        self.bending_frame, bending_body = self._create_card(self.glitch_tab, "Bending")
        self.bending_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 8))
        tk.Label(bending_body, text="Mode", fg=self.theme["text"], bg=self.theme["panel"], anchor="w").pack(fill=tk.X)
        self.bend_mode_menu = tk.OptionMenu(
            bending_body,
            self.bend_mode_var,
            "Byte Shift",
            "Byte Swap",
            "Repeat Burst",
            command=self.update_bending,
        )
        self._style_option_menu(self.bend_mode_menu)
        self.bend_mode_menu.pack(fill=tk.X, pady=(4, 8))
        self.bend_slider = self._create_compact_slider(
            bending_body,
            "Corruption",
            0,
            100,
            self.update_bending,
            initial=0,
        )

        self.datamosh_frame, datamosh_body = self._create_card(self.glitch_tab, "Data Moshing")
        self.datamosh_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 8))
        tk.Label(datamosh_body, text="Mode", fg=self.theme["text"], bg=self.theme["panel"], anchor="w").pack(fill=tk.X)
        self.datamosh_mode_menu = tk.OptionMenu(
            datamosh_body,
            self.datamosh_mode_var,
            "AVI Style",
            "P-Frame Smear",
            "Block Echo",
            "Reverse",
            command=self.update_datamosh,
        )
        self._style_option_menu(self.datamosh_mode_menu)
        self.datamosh_mode_menu.pack(fill=tk.X, pady=(4, 8))
        self.datamosh_slider = self._create_compact_slider(
            datamosh_body,
            "Intensity",
            0,
            100,
            self.update_datamosh,
            initial=0,
        )

        self.manual_blend_frame, manual_blend_body = self._create_card(self.glitch_tab, "Manual Blending")
        self.manual_blend_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.manual_blend_button = tk.Button(
            manual_blend_body,
            text="Open Text Editor",
            command=self.open_manual_blend_editor,
            **self._button_style(self.theme["button_alt"])
        )
        self.manual_blend_button.pack(fill=tk.X)
        self.manual_blend_clear_button = tk.Button(
            manual_blend_body,
            text="Disable Manual Blending",
            command=self.disable_manual_blending,
            **self._button_style(self.theme["button"])
        )
        self.manual_blend_clear_button.pack(fill=tk.X, pady=(6, 0))
        tk.Label(
            manual_blend_body,
            textvariable=self.manual_blend_status_var,
            fg=self.theme["muted"],
            bg=self.theme["panel"],
            anchor="w",
            justify=tk.LEFT,
            wraplength=320,
        ).pack(fill=tk.X, pady=(8, 0))

    def _build_finish_tab(self):
        """
        Build the finishing and export controls tab.
        """
        self.finish_tab.grid_columnconfigure(0, weight=1)

        self.crt_frame, crt_body = self._create_card(self.finish_tab, "CRT Finish")
        self.crt_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))

        crt_grid = tk.Frame(crt_body, bg=self.theme["panel"])
        crt_grid.pack(fill=tk.X)
        crt_grid.grid_columnconfigure(0, weight=1)
        crt_grid.grid_columnconfigure(1, weight=1)

        crt_left = tk.Frame(crt_grid, bg=self.theme["panel"])
        crt_left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        crt_right = tk.Frame(crt_grid, bg=self.theme["panel"])
        crt_right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.curvature_slider = self._create_compact_slider(crt_left, "Curvature", 0, 100, self.update_crt, initial=0)
        self.glow_slider = self._create_compact_slider(crt_left, "Glow", 0, 100, self.update_crt, initial=0)
        self.rgb_shift_slider = self._create_compact_slider(crt_left, "RGB Shift", 0, 20, self.update_crt, initial=0)
        self.vignette_slider = self._create_compact_slider(crt_left, "Vignette", 0, 100, self.update_crt, initial=0)

        self.distortion_slider = self._create_compact_slider(crt_right, "Distortion", 0, 100, self.update_crt, initial=0)
        self.noise_slider = self._create_compact_slider(crt_right, "Noise", 0, 100, self.update_crt, initial=0)
        self.scanline_slider = self._create_compact_slider(crt_right, "Scanlines", 0, 100, self.update_crt, initial=0)

        self.export_frame, export_body = self._create_card(self.finish_tab, "Export")
        self.export_frame.grid(row=1, column=0, sticky="nsew")
        tk.Label(export_body, text="Save Style", fg=self.theme["text"], bg=self.theme["panel"], anchor="w").pack(fill=tk.X)
        self.export_compression_menu = tk.OptionMenu(
            export_body,
            self.export_compression_var,
            "No Compression",
            "Soft CCD",
            "Compact Camera",
            "Memory Saver",
            "Harsh Artifacts",
            command=self.update_export_compression
        )
        self._style_option_menu(self.export_compression_menu)
        self.export_compression_menu.pack(fill=tk.X, pady=(4, 8))

        tk.Label(export_body, text="Save Folder", fg=self.theme["text"], bg=self.theme["panel"], anchor="w").pack(fill=tk.X)
        folder_row = tk.Frame(export_body, bg=self.theme["panel"])
        folder_row.pack(fill=tk.X, pady=(4, 0))
        self.folder_entry = tk.Entry(folder_row, textvariable=self.folder_path, **self._entry_style())
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.browse_button = tk.Button(
            folder_row,
            text="Browse",
            command=self.select_folder,
            **self._button_style(self.theme["button_alt"])
        )
        self.browse_button.pack(side=tk.LEFT, padx=(8, 0))

        button_row = tk.Frame(export_body, bg=self.theme["panel"])
        button_row.pack(fill=tk.X, pady=(10, 0))
        self.save_png_button = tk.Button(
            button_row,
            text="Save As",
            command=self.save_as,
            **self._button_style(self.theme["button"])
        )
        self.save_png_button.pack(side=tk.LEFT)
        self.video_preview_button = tk.Button(
            button_row,
            text="See Video Preview",
            command=self.open_video_preview_window,
            **self._button_style(self.theme["button_alt"])
        )
        self.video_preview_button.pack(side=tk.LEFT, padx=(8, 0))
        tk.Label(
            export_body,
            text="Compression affects preview and final export.",
            fg=self.theme["muted"],
            bg=self.theme["panel"],
            anchor="w"
        ).pack(fill=tk.X, pady=(8, 0))
        self._update_video_action_buttons()

    def _build_crop_tab(self):
        """
        Build the crop controls tab.
        """
        self.crop_tab.grid_columnconfigure(0, weight=1)
        self.crop_frame, crop_body = self._create_card(self.crop_tab, "Crop & Aspect")
        self.crop_frame.grid(row=0, column=0, sticky="nsew")

        crop_grid = tk.Frame(crop_body, bg=self.theme["panel"])
        crop_grid.pack(fill=tk.X)
        crop_grid.grid_columnconfigure(0, weight=1)
        crop_grid.grid_columnconfigure(1, weight=1)

        self.crop_left_slider, self.crop_left_entry = self._create_crop_control(crop_grid, 0, 0, "left", "Left")
        self.crop_right_slider, self.crop_right_entry = self._create_crop_control(crop_grid, 0, 1, "right", "Right")
        self.crop_top_slider, self.crop_top_entry = self._create_crop_control(crop_grid, 1, 0, "top", "Top")
        self.crop_bottom_slider, self.crop_bottom_entry = self._create_crop_control(crop_grid, 1, 1, "bottom", "Bottom")

        footer = tk.Frame(crop_body, bg=self.theme["panel"])
        footer.pack(fill=tk.X, pady=(8, 0))
        footer.grid_columnconfigure(0, weight=1)
        footer.grid_columnconfigure(1, weight=0)

        self.crop_size_label = tk.Label(
            footer,
            textvariable=self.crop_size_var,
            fg=self.theme["muted"],
            bg=self.theme["panel"],
            anchor="w"
        )
        self.crop_size_label.grid(row=0, column=0, sticky="w")

        preset_row = tk.Frame(footer, bg=self.theme["panel"])
        preset_row.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        preset_row.grid_columnconfigure(1, weight=1)
        tk.Label(preset_row, text="Preset", fg=self.theme["text"], bg=self.theme["panel"]).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.crop_preset_menu = tk.OptionMenu(
            preset_row,
            self.crop_preset_var,
            "Free",
            "1:1",
            "3:2",
            "4:5",
            "16:9",
            "9:16",
            "21:9",
            command=self.apply_crop_preset
        )
        self._style_option_menu(self.crop_preset_menu)
        self.crop_preset_menu.grid(row=0, column=1, sticky="ew")

        self.reset_crop_button = tk.Button(
            crop_body,
            text="Reset Crop",
            command=self.reset_crop,
            **self._button_style(self.theme["button_alt"])
        )
        self.reset_crop_button.pack(fill=tk.X, pady=(10, 0))

    def _build_animation_tab(self):
        """
        Build the compact animation tab without scrollbars.
        """
        self.animate_tab.grid_columnconfigure(0, weight=1)
        self.animation_frame, animation_body = self._create_card(self.animate_tab, "Animation Frames")
        self.animation_frame.grid(row=0, column=0, sticky="nsew")

        self.animation_button_row = tk.Frame(animation_body, bg=self.theme["panel"])
        self.animation_button_row.pack(fill=tk.X)
        self.add_frame_button = tk.Button(
            self.animation_button_row,
            text="Add Frame",
            command=self.add_animation_frame,
            **self._button_style(self.theme["button"])
        )
        self.add_frame_button.pack(side=tk.LEFT)

        self.delete_frame_button = tk.Button(
            self.animation_button_row,
            text="Delete Last",
            command=self.delete_last_animation_frame,
            **self._button_style(self.theme["button_alt"])
        )
        self.delete_frame_button.pack(side=tk.LEFT, padx=(8, 0))

        self.export_animation_button = tk.Button(
            self.animation_button_row,
            text="Export",
            command=self.open_animation_export_modal,
            **self._button_style(self.theme["accent_soft"])
        )
        self.export_animation_button.pack(side=tk.RIGHT)

        self.animation_status_label = tk.Label(
            animation_body,
            textvariable=self.animation_status_var,
            fg=self.theme["muted"],
            bg=self.theme["panel"],
            anchor="w",
            justify=tk.LEFT
        )
        self.animation_status_label.pack(fill=tk.X, pady=(8, 6))

        self.animation_preview_inner = tk.Frame(
            animation_body,
            bg=self.theme["panel_soft"],
            highlightbackground=self.theme["border"],
            highlightthickness=1,
            bd=0
        )
        self.animation_preview_inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            animation_body,
            text="The panel shows the latest frames so the layout stays compact.",
            fg=self.theme["muted"],
            bg=self.theme["panel"],
            anchor="w"
        ).pack(fill=tk.X, pady=(8, 0))

    def _build_intensity_tab(self):
        """
        Build the video intensity modulation tab.
        """
        self.intensity_tab.grid_columnconfigure(0, weight=1)
        self.intensity_frame, intensity_body = self._create_card(self.intensity_tab, "Frame Intensity", self.video_status_var)
        self.intensity_frame.grid(row=0, column=0, sticky="nsew")

        self.intensity_scroll_wrap = tk.Frame(
            intensity_body,
            bg=self.theme["panel_soft"],
            highlightbackground=self.theme["border"],
            highlightthickness=1,
            bd=0,
        )
        self.intensity_scroll_wrap.pack(fill=tk.BOTH, expand=True)

        self.intensity_canvas = tk.Canvas(
            self.intensity_scroll_wrap,
            bg=self.theme["panel_soft"],
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,
        )
        self.intensity_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.intensity_scrollbar = tk.Scrollbar(
            self.intensity_scroll_wrap,
            orient=tk.VERTICAL,
            command=self.intensity_canvas.yview,
        )
        self.intensity_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.intensity_canvas.configure(yscrollcommand=self.intensity_scrollbar.set)

        self.intensity_inner = tk.Frame(self.intensity_canvas, bg=self.theme["panel_soft"])
        self.intensity_window_id = self.intensity_canvas.create_window((0, 0), window=self.intensity_inner, anchor="nw")

        self.intensity_inner.bind(
            "<Configure>",
            lambda _event: self.intensity_canvas.configure(scrollregion=self.intensity_canvas.bbox("all")),
        )
        self.intensity_canvas.bind(
            "<Configure>",
            lambda event: self.intensity_canvas.itemconfigure(self.intensity_window_id, width=event.width),
        )

        tk.Label(
            intensity_body,
            text="Each active effect can vary over time for video frames.",
            fg=self.theme["muted"],
            bg=self.theme["panel"],
            anchor="w",
        ).pack(fill=tk.X, pady=(8, 0))

        self._refresh_video_intensity_controls(force=True)

    def _build_palette_tab(self):
        """
        Build the palette extraction tab.
        """
        self.palette_tab.grid_columnconfigure(0, weight=1)
        self.palette_frame, palette_body = self._create_card(self.palette_tab, "Palette", self.palette_status_var)
        self.palette_frame.grid(row=0, column=0, sticky="nsew")

        self.palette_count_slider = self._create_compact_slider(
            palette_body,
            "Color Count",
            2,
            24,
            self.update_palette_count,
            initial=8,
        )

        format_row = tk.Frame(palette_body, bg=self.theme["panel"])
        format_row.pack(fill=tk.X, pady=(0, 6))
        tk.Label(format_row, text="Format", fg=self.theme["text"], bg=self.theme["panel"], anchor="w").pack(anchor="w")
        self.palette_format_menu = tk.OptionMenu(
            format_row,
            self.palette_format_var,
            "PNG Image (1x)",
            "PNG Image (8x)",
            "PNG Image (32x)",
            "PAL File (JASC)",
            "Photoshop ASE",
            "Paint.net TXT",
            "GIMP GPL",
            "HEX File",
        )
        self._style_option_menu(self.palette_format_menu)
        self.palette_format_menu.pack(fill=tk.X, pady=(4, 0))

        sort_row = tk.Frame(palette_body, bg=self.theme["panel"])
        sort_row.pack(fill=tk.X, pady=(0, 8))
        tk.Label(sort_row, text="Sort Colors", fg=self.theme["text"], bg=self.theme["panel"], anchor="w").pack(anchor="w")
        self.palette_sort_menu = tk.OptionMenu(
            sort_row,
            self.palette_sort_var,
            "Frequency",
            "Hue",
            "Brightness",
            command=self.update_palette_display,
        )
        self._style_option_menu(self.palette_sort_menu)
        self.palette_sort_menu.pack(fill=tk.X, pady=(4, 0))

        self.extract_palette_button = tk.Button(
            palette_body,
            text="Extract Palette",
            command=self.extract_palette_from_preview,
            **self._button_style(self.theme["accent_soft"])
        )
        self.extract_palette_button.pack(fill=tk.X, pady=(0, 6))

        self.save_palette_button = tk.Button(
            palette_body,
            text="Save Palette As",
            command=self.save_palette_as,
            **self._button_style(self.theme["button_alt"])
        )
        self.save_palette_button.pack(fill=tk.X, pady=(0, 10))

        preview_label = tk.Label(
            palette_body,
            text="Preview (click a swatch to copy HEX)",
            fg=self.theme["text"],
            bg=self.theme["panel"],
            anchor="w"
        )
        preview_label.pack(fill=tk.X)

        self.palette_preview_inner = tk.Frame(
            palette_body,
            bg=self.theme["panel_soft"],
            highlightbackground=self.theme["panel_soft"],
            highlightthickness=0,
            bd=0
        )
        self.palette_preview_inner.pack(fill=tk.X, pady=(4, 10))

        values_label = tk.Label(
            palette_body,
            text="Palette Values",
            fg=self.theme["text"],
            bg=self.theme["panel"],
            anchor="w"
        )
        values_label.pack(fill=tk.X)

        self.palette_values_text = tk.Text(
            palette_body,
            height=12,
            wrap=tk.WORD,
            bg=self.theme["field"],
            fg=self.theme["text"],
            insertbackground=self.theme["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.theme["field_border"],
            highlightcolor=self.theme["accent"],
            bd=0,
            padx=10,
            pady=10,
        )
        self.palette_values_text.pack(fill=tk.BOTH, expand=True)
        self.palette_values_text.configure(state=tk.DISABLED)
        self._reset_palette_output()

    def _create_card(self, parent, title, subtitle=None, stretch=False):
        """
        Create a classic desktop group container and return the card plus its body frame.
        """
        card = tk.Frame(
            parent,
            bg=self.theme["panel"],
            relief=tk.RAISED,
            bd=2,
            highlightthickness=0,
        )
        if stretch:
            card.grid_propagate(True)

        header = tk.Frame(card, bg=self.theme["panel"])
        header.pack(fill=tk.X, padx=12, pady=(10, 6))
        tk.Label(
            header,
            text=title,
            fg=self.theme["text"],
            bg=self.theme["panel"],
            font=("Helvetica", 11, "bold")
        ).pack(anchor="w")

        if subtitle is not None:
            tk.Label(
                header,
                textvariable=subtitle if isinstance(subtitle, tk.Variable) else None,
                text=subtitle if not isinstance(subtitle, tk.Variable) else None,
                fg=self.theme["muted"],
                bg=self.theme["panel"],
                justify=tk.LEFT,
                wraplength=340
            ).pack(anchor="w", pady=(3, 0))

        body = tk.Frame(card, bg=self.theme["panel"])
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        return card, body

    def _set_palette_text(self, text):
        """
        Update the palette text output.
        """
        palette_helpers.set_palette_text(self, text)

    def _reset_palette_output(self, message=None):
        """
        Clear palette output widgets and status.
        """
        palette_helpers.reset_palette_output(self, message)

    def _get_color_luminance(self, rgb):
        """
        Return perceived luminance for an RGB tuple.
        """
        return palette_helpers.get_color_luminance(self, rgb)

    def _palette_text_color(self, rgb):
        """
        Choose dark or light text for a swatch.
        """
        return palette_helpers.palette_text_color(self, rgb)

    def _rgb_to_hex(self, rgb):
        """
        Convert RGB to hex.
        """
        return palette_helpers.rgb_to_hex(self, rgb)

    def _rgb_to_hsl(self, rgb):
        """
        Convert RGB to HSL components.
        """
        return palette_helpers.rgb_to_hsl(self, rgb)

    def _rgb_to_hsv(self, rgb):
        """
        Convert RGB to HSV components.
        """
        return palette_helpers.rgb_to_hsv(self, rgb)

    def _rgb_to_cmyk(self, rgb):
        """
        Convert RGB to CMYK components.
        """
        return palette_helpers.rgb_to_cmyk(self, rgb)

    def _get_palette_export_formats(self):
        """
        Return supported palette export formats.
        """
        return palette_helpers.get_palette_export_formats(self)

    def _format_palette_color(self, rgb):
        """
        Format a palette color for the on-screen value list.
        """
        return palette_helpers.format_palette_color(self, rgb)

    def _copy_palette_hex(self, rgb):
        """
        Copy a swatch HEX value to the clipboard.
        """
        palette_helpers.copy_palette_hex(self, rgb)

    def _palette_file_stem(self):
        """
        Return a base filename for palette exports.
        """
        return palette_helpers.palette_file_stem(self)

    def _write_palette_png(self, file_path, entries, scale):
        """
        Save the palette as a PNG swatch strip.
        """
        palette_helpers.write_palette_png(self, file_path, entries, scale)

    def _write_palette_jasc(self, file_path, entries):
        """
        Save the palette as a JASC PAL file.
        """
        palette_helpers.write_palette_jasc(self, file_path, entries)

    def _write_palette_hex_file(self, file_path, entries):
        """
        Save the palette as a plain HEX list.
        """
        palette_helpers.write_palette_hex_file(self, file_path, entries)

    def _write_palette_gpl(self, file_path, entries):
        """
        Save the palette as a GIMP GPL file.
        """
        palette_helpers.write_palette_gpl(self, file_path, entries)

    def _write_palette_paintnet(self, file_path, entries):
        """
        Save the palette as a Paint.net text palette.
        """
        palette_helpers.write_palette_paintnet(self, file_path, entries)

    def _write_palette_ase(self, file_path, entries):
        """
        Save the palette as an Adobe Swatch Exchange file.
        """
        palette_helpers.write_palette_ase(self, file_path, entries)

    def _export_palette_file(self, entries):
        """
        Save the current palette in the selected export format.
        """
        return palette_helpers.export_palette_file(self, entries)

    def _sorted_palette_entries(self):
        """
        Return palette entries in the currently selected sort order.
        """
        return palette_helpers.sorted_palette_entries(self)

    def update_palette_count(self, _=None):
        """
        Re-extract the palette when a palette already exists and the count changes.
        """
        palette_helpers.update_palette_count(self, _)

    def update_palette_display(self, _=None):
        """
        Refresh the palette swatches and value list.
        """
        palette_helpers.update_palette_display(self, _)

    def _extract_palette_from_preview(self, save_to_file=False):
        """
        Extract a palette from the current rendered preview image.
        """
        palette_helpers.extract_palette_from_preview_internal(self, save_to_file=save_to_file)

    def extract_palette_from_preview(self):
        """
        Extract a palette from the current preview.
        """
        palette_helpers.extract_palette_from_preview(self)

    def save_palette_as(self):
        """
        Save the current extracted palette using the selected export format.
        """
        palette_helpers.save_palette_as(self)

    def _style_option_menu(self, menu):
        """
        Apply the shared dark style to an OptionMenu.
        """
        if self.is_macos:
            field_bg = "#d7dbe4"
            text_color = "#11131a"
            active_bg = "#c8cfdb"
        else:
            field_bg = self.theme["field"]
            text_color = self.theme["text"]
            active_bg = self.theme["panel_alt"]

        menu.configure(
            bg=field_bg,
            fg=text_color,
            activebackground=active_bg,
            activeforeground=text_color,
            highlightthickness=1,
            highlightbackground=self.theme["border"],
            bd=2,
            relief=tk.RAISED,
            width=14,
            anchor="w"
        )
        menu["menu"].configure(bg=field_bg, fg=text_color, activebackground=active_bg, activeforeground=text_color)

    def _entry_style(self):
        """
        Shared entry styling.
        """
        return {
            "bg": self.theme["field"],
            "fg": self.theme["text"],
            "insertbackground": self.theme["text"],
            "relief": tk.SUNKEN,
            "highlightthickness": 1,
            "highlightbackground": self.theme["field_border"],
            "highlightcolor": self.theme["accent"],
            "bd": 2,
        }

    def _create_compact_slider(self, parent, label_text, from_, to, command, resolution=1, initial=0, formatter=None):
        """
        Create a compact slider row with a live numeric readout.
        """
        row = tk.Frame(parent, bg=self.theme["panel"])
        row.pack(fill=tk.X, pady=(0, 6))

        header = tk.Frame(row, bg=self.theme["panel"])
        header.pack(fill=tk.X)
        tk.Label(header, text=label_text, fg=self.theme["text"], bg=self.theme["panel"], anchor="w").pack(side=tk.LEFT)

        value_var = tk.StringVar()
        tk.Label(header, textvariable=value_var, fg=self.theme["muted"], bg=self.theme["panel"], anchor="e").pack(side=tk.RIGHT)

        scale_var = tk.DoubleVar(value=initial)
        format_value = formatter or (lambda value: str(int(round(float(value)))))
        value_var.set(format_value(initial))

        def sync_label(*_args):
            value_var.set(format_value(scale_var.get()))

        scale_var.trace_add("write", sync_label)
        self._slider_value_bindings.append((scale_var, value_var))

        scale = tk.Scale(
            row,
            from_=from_,
            to=to,
            resolution=resolution,
            orient=tk.HORIZONTAL,
            variable=scale_var,
            showvalue=False,
            bg=self.theme["panel"],
            fg=self.theme["text"],
            troughcolor=self.theme["button_alt"],
            activebackground=self.theme["accent"],
            highlightthickness=0,
            bd=1,
            relief=tk.FLAT,
            sliderlength=18,
            width=10,
            command=command,
        )
        scale.pack(fill=tk.X, pady=(3, 0))
        scale.set(initial)
        return scale

    def _crop_var(self, edge):
        return {
            "left": self.crop_left_var,
            "right": self.crop_right_var,
            "top": self.crop_top_var,
            "bottom": self.crop_bottom_var,
        }[edge]

    def _crop_slider(self, edge):
        return {
            "left": self.crop_left_slider,
            "right": self.crop_right_slider,
            "top": self.crop_top_slider,
            "bottom": self.crop_bottom_slider,
        }[edge]

    def _read_crop_margins(self, width_limit, height_limit):
        left = min(width_limit, max(0, int(float(self.crop_left_slider.get()))))
        right = min(width_limit, max(0, int(float(self.crop_right_slider.get()))))
        top = min(height_limit, max(0, int(float(self.crop_top_slider.get()))))
        bottom = min(height_limit, max(0, int(float(self.crop_bottom_slider.get()))))
        return left, right, top, bottom

    def _create_crop_control(self, parent, row, column, edge, label):
        """
        Create a compact crop control with entry and slider.
        """
        target_var = self._crop_var(edge)

        container = tk.Frame(parent, bg=self.theme["panel"])
        container.grid(row=row, column=column, sticky="nsew", padx=(0, 6) if column == 0 else (6, 0), pady=(0, 8))
        parent.grid_rowconfigure(row, weight=1)

        header = tk.Frame(container, bg=self.theme["panel"])
        header.pack(fill=tk.X)
        tk.Label(header, text=label, fg=self.theme["text"], bg=self.theme["panel"], anchor="w").pack(side=tk.LEFT)
        entry = tk.Entry(header, textvariable=target_var, width=7, justify=tk.RIGHT, **self._entry_style())
        entry.pack(side=tk.RIGHT)
        entry.bind("<Return>", lambda _event: self.commit_crop_entry(edge))
        entry.bind("<FocusOut>", lambda _event: self.commit_crop_entry(edge))

        slider = tk.Scale(
            container,
            from_=0,
            to=0,
            resolution=1,
            orient=tk.HORIZONTAL,
            bg=self.theme["panel"],
            fg=self.theme["text"],
            troughcolor=self.theme["button_alt"],
            activebackground=self.theme["accent"],
            highlightthickness=0,
            bd=1,
            relief=tk.FLAT,
            sliderlength=18,
            width=10,
            showvalue=False,
            command=lambda _value: self.update_crop(edge)
        )
        slider.pack(fill=tk.X, pady=(4, 0))
        slider.set(0)
        return slider, entry

    def _render_empty_preview(self):
        """
        Draw an empty-state placeholder in the preview canvas.
        """
        self.canvas.delete("all")
        self.canvas.update_idletasks()
        canvas_width = max(1, self.canvas.winfo_width())
        canvas_height = max(1, self.canvas.winfo_height())
        self.canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill=self.theme["canvas"], outline="")
        self.canvas.create_text(
            canvas_width / 2,
            canvas_height / 2 - 12,
            text="No image loaded",
            fill=self.theme["text"],
            font=("Helvetica", 16, "bold")
        )
        self.canvas.create_text(
            canvas_width / 2,
            canvas_height / 2 + 16,
            text="Upload a file to start editing.",
            fill=self.theme["muted"],
            font=("Helvetica", 11)
        )

    def _update_preview_metadata(self, rendered_size=None):
        """
        Refresh the preview title and status text.
        """
        if self.image_object is None or self.current_pil_image is None:
            self.preview_title_var.set("No image loaded")
            self.preview_hint_var.set("Upload an image or video to start creating a glitchy preview.")
            return

        source_width, source_height = self.current_pil_image.size
        self.preview_title_var.set(self.image_object.name)

        if self.is_video_mode:
            preview_text = f"Video {source_width} x {source_height} • {self.video_fps:.2f} fps"
            if self.video_frame_count > 0:
                preview_text += f" • {self.video_frame_count} frame(s)"
        else:
            preview_text = f"Source {source_width} x {source_height}"
        crop_text = self.crop_size_var.get()
        if crop_text and crop_text != "Final Size: -":
            preview_text += f" • {crop_text}"
        if rendered_size is not None and rendered_size != (source_width, source_height):
            preview_text += f" • Preview {rendered_size[0]} x {rendered_size[1]}"

        self.preview_hint_var.set(preview_text)

    def _button_style(self, background):
        """
        Shared button styling for the classic UI.
        """
        if self.is_macos:
            background = "#d4d0c8" if background != self.theme["accent_soft"] else "#dbe7f7"
            foreground = "#11131a"
            active_background = "#c6c1b8" if background != "#dbe7f7" else "#c8d8f2"
            disabled_foreground = "#5f6776"
        else:
            foreground = self.theme["text"]
            active_background = self.theme["panel_alt"]
            disabled_foreground = foreground

        return {
            "bg": background,
            "fg": foreground,
            "activebackground": active_background,
            "activeforeground": foreground,
            "disabledforeground": disabled_foreground,
            "highlightbackground": self.theme["shadow_light"],
            "highlightcolor": self.theme["shadow_light"],
            "bd": 2,
            "relief": tk.RAISED,
            "padx": 12,
            "pady": 8,
        }

    def _create_randomize_settings(self):
        """
        Create the default Randomize settings state.
        """
        keys = [
            'pixel_scale', 'jitter', 'block', 'sort',
            'hue', 'saturation', 'contrast', 'invert',
            'random_pixels', 'blur', 'color_reducer', 'legacy_collapse', 'bending', 'datamosh', 'blend',
            'curvature', 'distortion', 'glow', 'noise', 'rgb_shift', 'scanlines', 'vignette',
            'compression'
        ]
        defaults = {key: True for key in keys}
        defaults['random_pixels'] = False
        defaults['blur'] = False
        defaults['legacy_collapse'] = False
        defaults['bending'] = False
        defaults['datamosh'] = False
        return {key: tk.BooleanVar(value=defaults[key]) for key in keys}

    def _video_effect_specs(self):
        """
        Return metadata for effects that can be modulated over video frames.
        """
        return {
            "pixel_scale": {"label": "Pixelate", "default": 1.0, "min": 0.01, "max": 1.0, "type": "float"},
            "jitter": {"label": "Row Jitter", "default": 0.0, "min": 0.0, "max": 100.0, "type": "int"},
            "block": {"label": "Block Shift", "default": 0.0, "min": 0.0, "max": 100.0, "type": "int"},
            "sort": {"label": "Pixel Sort", "default": 0.0, "min": 0.0, "max": 100.0, "type": "int"},
            "hue": {"label": "Hue Shift", "default": 0.0, "min": -180.0, "max": 180.0, "type": "int"},
            "saturation": {"label": "Saturation", "default": 1.0, "min": 0.0, "max": 2.0, "type": "float"},
            "contrast": {"label": "Contrast", "default": 1.0, "min": 0.5, "max": 2.0, "type": "float"},
            "invert": {"label": "Invert Colors", "default": False, "type": "bool"},
            "random_pixels": {"label": "Random Pixels", "default": 0.0, "min": 0.0, "max": 1.0, "type": "float"},
            "blur": {"label": "Blur", "default": 0.0, "min": 0.0, "max": 10.0, "type": "int"},
            "color_reducer": {"label": "Color Reducer", "default": 256.0, "min": 2.0, "max": 256.0, "type": "int"},
            "legacy_collapse": {"label": "Color Collapse", "default": 256.0, "min": 2.0, "max": 256.0, "type": "int"},
            "bending": {"label": "Corruption", "default": 0.0, "min": 0.0, "max": 100.0, "type": "float"},
            "datamosh": {"label": "Datamosh", "default": 0.0, "min": 0.0, "max": 100.0, "type": "float"},
            "curvature": {"label": "Curvature", "default": 0.0, "min": 0.0, "max": 100.0, "type": "int"},
            "distortion": {"label": "Distortion", "default": 0.0, "min": 0.0, "max": 100.0, "type": "int"},
            "glow": {"label": "Glow", "default": 0.0, "min": 0.0, "max": 100.0, "type": "int"},
            "noise": {"label": "Noise", "default": 0.0, "min": 0.0, "max": 100.0, "type": "int"},
            "scanlines": {"label": "Scanlines", "default": 0.0, "min": 0.0, "max": 100.0, "type": "int"},
            "rgb_shift": {"label": "RGB Shift", "default": 0.0, "min": 0.0, "max": 20.0, "type": "int"},
            "vignette": {"label": "Vignette", "default": 0.0, "min": 0.0, "max": 100.0, "type": "int"},
        }

    def _collect_effect_values(self):
        """
        Snapshot current effect control values.
        """
        return {
            "pixel_scale": float(self.pixel_slider.get()),
            "jitter": float(self.jitter_slider.get()),
            "block": float(self.block_slider.get()),
            "sort": float(self.sort_slider.get()),
            "hue": float(self.hue_slider.get()),
            "saturation": float(self.saturation_slider.get()),
            "contrast": float(self.contrast_slider.get()),
            "invert": bool(self.invert_state.get()),
            "random_pixels": float(self.random_pixel_slider.get()),
            "blur": float(self.blur_slider.get()),
            "color_reducer": float(self.color_reducer_slider.get()),
            "legacy_collapse": float(self.legacy_color_slider.get()),
            "bending": float(self.bend_slider.get()),
            "bend_mode": self.bend_mode_var.get(),
            "datamosh": float(self.datamosh_slider.get()),
            "datamosh_mode": self.datamosh_mode_var.get(),
            "curvature": float(self.curvature_slider.get()),
            "distortion": float(self.distortion_slider.get()),
            "glow": float(self.glow_slider.get()),
            "noise": float(self.noise_slider.get()),
            "scanlines": float(self.scanline_slider.get()),
            "rgb_shift": float(self.rgb_shift_slider.get()),
            "vignette": float(self.vignette_slider.get()),
        }

    def _get_active_video_effect_keys(self, effect_values=None):
        """
        Return effect keys currently active enough to appear in the Intensity tab.
        """
        if effect_values is None:
            effect_values = self._collect_effect_values()

        specs = self._video_effect_specs()
        active = []
        for key, spec in specs.items():
            value = effect_values.get(key)
            default = spec["default"]
            if spec["type"] == "bool":
                if bool(value) != bool(default):
                    active.append(key)
                continue

            if abs(float(value) - float(default)) > 0.001:
                active.append(key)

        return active

    def _on_video_intensity_change(self, _=None):
        """
        Refresh preview when an Intensity control changes.
        """
        self.request_preview_update()

    def _refresh_video_intensity_controls(self, force=False):
        """
        Build dynamic Intensity controls for active effects in video mode.
        """
        if not hasattr(self, "intensity_inner"):
            return

        if not self.is_video_mode:
            for child in self.intensity_inner.winfo_children():
                child.destroy()
            self.video_intensity_controls = {}
            self.video_intensity_rows = {}
            self.video_intensity_active_keys = []
            self.video_status_var.set("Load a video to configure frame intensity controls.")
            return

        effect_values = self._collect_effect_values()
        active_keys = self._get_active_video_effect_keys(effect_values)
        if not force and active_keys == self.video_intensity_active_keys:
            return

        previous_values = {
            key: {
                "step": int(float(control["step"].get())),
                "drift": float(control["drift"].get()),
            }
            for key, control in self.video_intensity_controls.items()
        }

        for child in self.intensity_inner.winfo_children():
            child.destroy()

        self.video_intensity_controls = {}
        self.video_intensity_rows = {}
        self.video_intensity_active_keys = list(active_keys)

        if not active_keys:
            self.video_status_var.set("No active effects yet. Move sliders or randomize controls to populate this tab.")
            tk.Label(
                self.intensity_inner,
                text="Intensity controls appear here as soon as an effect is active.",
                fg=self.theme["muted"],
                bg=self.theme["panel_soft"],
                justify=tk.LEFT,
                wraplength=300,
            ).pack(anchor="w", padx=10, pady=10)
            return

        self.video_status_var.set(f"{len(active_keys)} effect(s) active. Configure frame cadence and change amount.")
        specs = self._video_effect_specs()
        for key in active_keys:
            spec = specs[key]
            saved = previous_values.get(key, {"step": 1, "drift": 25.0})
            section = tk.Frame(self.intensity_inner, bg=self.theme["panel"], relief=tk.RAISED, bd=1)
            section.pack(fill=tk.X, padx=8, pady=(8, 0))

            tk.Label(
                section,
                text=spec["label"],
                fg=self.theme["text"],
                bg=self.theme["panel"],
                anchor="w",
                font=("Helvetica", 10, "bold"),
            ).pack(fill=tk.X, padx=8, pady=(8, 4))

            body = tk.Frame(section, bg=self.theme["panel"])
            body.pack(fill=tk.X, padx=8, pady=(0, 8))

            step_slider = self._create_compact_slider(
                body,
                "Every N Frames",
                1,
                24,
                self._on_video_intensity_change,
                resolution=1,
                initial=saved["step"],
                formatter=lambda value: str(int(round(float(value)))),
            )
            drift_slider = self._create_compact_slider(
                body,
                "Value Change %",
                0,
                100,
                self._on_video_intensity_change,
                resolution=1,
                initial=saved["drift"],
                formatter=lambda value: f"{int(round(float(value)))}%",
            )

            self.video_intensity_rows[key] = section
            self.video_intensity_controls[key] = {
                "step": step_slider,
                "drift": drift_slider,
            }

    def _sync_media_tabs(self):
        """
        Toggle notebook tabs according to current media mode.
        """
        if not hasattr(self, "controls_notebook"):
            return

        if self.is_video_mode:
            try:
                self.controls_notebook.tab(self.animate_tab, state="hidden")
            except tk.TclError:
                pass
            try:
                self.controls_notebook.tab(self.intensity_tab, state="normal")
            except tk.TclError:
                pass
            try:
                if self.controls_notebook.select() == str(self.animate_tab):
                    self.controls_notebook.select(self.glitch_tab)
            except tk.TclError:
                pass
        else:
            try:
                self.controls_notebook.tab(self.intensity_tab, state="hidden")
            except tk.TclError:
                pass
            try:
                self.controls_notebook.tab(self.animate_tab, state="normal")
            except tk.TclError:
                pass

    def _update_video_action_buttons(self):
        """
        Enable or disable video-related buttons based on active media mode.
        """
        state = tk.NORMAL if self.is_video_mode and self.video_source_path else tk.DISABLED
        if hasattr(self, "video_preview_button"):
            self.video_preview_button.configure(state=state)

    def _update_animation_status(self):
        """
        Refresh the frame counter shown in the animation section.
        """
        animation_helpers.update_animation_status(self)

    def _update_animation_scroll_region(self, _event=None):
        """
        Legacy no-op kept for compatibility with the updated compact layout.
        """
        return

    def _resize_animation_preview_window(self, event):
        """
        Legacy no-op kept for compatibility with the updated compact layout.
        """
        return

    def _refresh_animation_preview_strip(self):
        """
        Rebuild the compact thumbnail grid for captured animation frames.
        """
        animation_helpers.refresh_animation_preview_strip(self)

    def _get_animation_export_formats(self):
        """
        Return the supported animation export formats.
        """
        return animation_helpers.get_animation_export_formats(self)

    def _prepare_animation_frames(self, target_size=None, flatten_alpha=False):
        """
        Normalize captured frames to a shared export size.
        """
        return animation_helpers.prepare_animation_frames(self, target_size=target_size, flatten_alpha=flatten_alpha)

    def add_animation_frame(self):
        """
        Capture the current full-resolution render as the next animation frame.
        """
        animation_helpers.add_animation_frame(self)

    def delete_last_animation_frame(self):
        """
        Remove the most recently captured animation frame.
        """
        animation_helpers.delete_last_animation_frame(self)

    def clear_animation_frames(self):
        """
        Remove all captured animation frames.
        """
        animation_helpers.clear_animation_frames(self)

    def open_animation_export_modal(self):
        """
        Open a modal window for choosing animation export settings.
        """
        animation_helpers.open_animation_export_modal(self)

    def _default_output_dir(self):
        return export_helpers.default_output_dir(self)

    def _ask_save_file(self, title, defaultextension, filetypes, initialfile):
        return export_helpers.ask_save_file(self, title, defaultextension, filetypes, initialfile)

    def _run_export_with_feedback(self, export_callable, failure_message, success_message, on_success=None):
        return export_helpers.run_export_with_feedback(export_callable, failure_message, success_message, on_success=on_success)

    def _export_animation_from_modal(self, modal, format_name, fps_value):
        """
        Validate modal settings and export the animation.
        """
        animation_helpers.export_animation_from_modal(self, modal, format_name, fps_value)

    def export_animation(self, file_path, format_name, fps):
        """
        Export the captured frame sequence to the selected animation format.
        """
        return animation_helpers.export_animation(self, file_path, format_name, fps)

    def _reset_controls_for_new_image(self):
        """
        Reset all effect controls so a newly loaded image starts clean.
        """
        self.begin_bulk_update()
        try:
            self.pixel_slider.set(1.0)
            self.jitter_slider.set(0)
            self.block_slider.set(0)
            self.sort_slider.set(0)

            self.hue_slider.set(0)
            self.saturation_slider.set(1.0)
            self.contrast_slider.set(1.0)
            self.invert_state.set(False)

            self.random_pixel_slider.set(0.0)

            self.blur_slider.set(0)
            self.color_reducer_slider.set(256)
            self.legacy_color_slider.set(256)
            self.bend_slider.set(0)
            self.bend_mode_var.set("Byte Shift")
            self.datamosh_slider.set(0)
            self.datamosh_mode_var.set("AVI Style")

            self.curvature_slider.set(0)
            self.distortion_slider.set(0)
            self.glow_slider.set(0)
            self.noise_slider.set(0)
            self.scanline_slider.set(0)
            self.rgb_shift_slider.set(0)
            self.vignette_slider.set(0)

            self.blend_slider.set(0.0)
            self.blend_image_pil = None
            self.blend_filename_var.set("No file")
            self.export_compression_var.set("No Compression")
            self._sync_crop_controls_to_image(reset_values=True)
            self.clear_animation_frames()
            self._reset_palette_output("Ready to extract a palette from the current preview.")
            self.video_intensity_controls = {}
            self.video_intensity_rows = {}
            self.video_intensity_active_keys = []
            self.manual_blend_bytes = b""
            self.manual_blend_enabled = False
            self.manual_blend_live_editing = False
            self.manual_blend_source_bytes = b""
            self.manual_blend_status_var.set("No manual text data loaded.")

            self.pipeline_image = None
            self.full_resolution_image = None
        finally:
            self.end_bulk_update(refresh=False)
        self._refresh_video_intensity_controls(force=True)
        self._update_video_action_buttons()

    def _set_crop_entry_value(self, edge, value):
        """
        Update a crop entry without triggering recursive commits.
        """
        crop_helpers.set_crop_entry_value(self, edge, value)

    def _set_crop_preset_value(self, value):
        """
        Update the crop preset selector without triggering preset reapplication.
        """
        crop_helpers.set_crop_preset_value(self, value)

    def _set_crop_controls(self, left, right, top, bottom):
        """
        Update all crop controls in one synchronized operation.
        """
        crop_helpers.set_crop_controls(self, left, right, top, bottom)

    def _get_crop_presets(self):
        """
        Return supported crop aspect presets.
        """
        return crop_helpers.get_crop_presets(self)

    def _update_crop_metadata(self):
        """
        Refresh the live crop size readout and preset state.
        """
        crop_helpers.update_crop_metadata(self)

    def _sync_crop_controls_to_image(self, reset_values=True):
        """
        Sync crop slider ranges and values to the currently loaded image.
        """
        crop_helpers.sync_crop_controls_to_image(self, reset_values=reset_values)

    def _normalize_crop_controls(self, preferred_edge=None):
        """
        Clamp crop margins so the remaining visible area is always at least 1 pixel.
        """
        crop_helpers.normalize_crop_controls(self, preferred_edge=preferred_edge)

    def _get_active_crop_box(self, image_size):
        """
        Return the active crop rectangle as left, top, right, bottom.
        """
        return crop_helpers.get_active_crop_box(self, image_size)

    def _crop_to_visible_area(self, pil_img, reference_size=None):
        """
        Crop an image to the currently visible area.
        """
        return crop_helpers.crop_to_visible_area(self, pil_img, reference_size=reference_size)

    def update_crop(self, edge=None):
        """
        Update crop entries and refresh the preview.
        """
        crop_helpers.update_crop(self, edge=edge)

    def reset_crop(self):
        """
        Reset all crop values back to the full image.
        """
        crop_helpers.reset_crop(self)

    def apply_crop_preset(self, preset_name):
        """
        Apply a predefined aspect ratio to the visible crop area.
        """
        crop_helpers.apply_crop_preset(self, preset_name)

    def commit_crop_entry(self, edge):
        """
        Apply a typed crop size, clamping it to the image bounds.
        """
        crop_helpers.commit_crop_entry(self, edge)

    def begin_bulk_update(self):
        """
        Temporarily suspend preview refreshes while multiple controls are updated.
        """
        self._suspend_preview_updates = True
        if self._pending_preview_job is not None:
            self.root.after_cancel(self._pending_preview_job)
            self._pending_preview_job = None

    def end_bulk_update(self, refresh=True):
        """
        Resume preview refreshes after a batch of control updates.
        """
        self._suspend_preview_updates = False
        if refresh:
            self.request_preview_update(immediate=True)

    def request_preview_update(self, immediate=False):
        """
        Schedule or perform an interactive preview refresh.
        """
        if self._suspend_preview_updates:
            return

        if self.is_video_mode:
            self._refresh_video_intensity_controls()

        if self._pending_preview_job is not None:
            self.root.after_cancel(self._pending_preview_job)
            self._pending_preview_job = None

        if immediate:
            self.apply_pipeline()
        else:
            self._pending_preview_job = self.root.after(self.preview_delay_ms, self._run_scheduled_preview)

    def _run_scheduled_preview(self):
        """
        Execute the deferred preview render.
        """
        self._pending_preview_job = None
        if not self._suspend_preview_updates:
            self.apply_pipeline()

    def _crt_effects_enabled(self):
        """
        Return True when any CRT control is active.
        """
        return any([
            int(self.curvature_slider.get()) > 0,
            int(self.distortion_slider.get()) > 0,
            int(self.glow_slider.get()) > 0,
            int(self.noise_slider.get()) > 0,
            int(self.scanline_slider.get()) > 0,
            int(self.rgb_shift_slider.get()) > 0,
            int(self.vignette_slider.get()) > 0,
        ])

    def _get_preview_processing_size(self, image_size):
        """
        Return the target image size for interactive preview processing.
        """
        self.canvas.update_idletasks()
        canvas_width = max(1, self.canvas.winfo_width())
        canvas_height = max(1, self.canvas.winfo_height())

        img_width, img_height = image_size
        ratio = min(canvas_width / img_width, canvas_height / img_height, 1.0)
        preview_scale = min(1.0, ratio * 1.25)

        return (
            max(1, int(img_width * preview_scale)),
            max(1, int(img_height * preview_scale)),
        )

    def update_export_compression(self, _=None):
        """
        Refresh the preview when the export compression style changes.
        """
        self.request_preview_update()

    def apply_export_compression(self, img):
        """
        Apply the selected export compression profile to an image.
        """
        profile = self.export_compression_var.get() if hasattr(self, 'export_compression_var') else "No Compression"
        return image_effects.apply_export_compression(img, profile)

    def _get_manual_blend_seed_bytes(self):
        """
        Return source bytes used to initialize the manual blending text editor.
        """
        max_bytes = 262144

        def encode_compact_jpeg(source_image):
            if source_image is None:
                return b""

            working = source_image.convert("RGB")
            for quality in (90, 84, 78, 70, 62):
                for scale in (1.0, 0.85, 0.7, 0.55):
                    if scale < 1.0:
                        new_size = (
                            max(1, int(working.size[0] * scale)),
                            max(1, int(working.size[1] * scale)),
                        )
                        candidate = working.resize(new_size, Image.LANCZOS)
                    else:
                        candidate = working

                    buffer = BytesIO()
                    candidate.save(buffer, format="JPEG", quality=quality, optimize=False)
                    data = buffer.getvalue()
                    if len(data) <= max_bytes:
                        return data

            buffer = BytesIO()
            working.save(buffer, format="JPEG", quality=55, optimize=False)
            return buffer.getvalue()

        rendered = None
        if self.current_pil_image is not None:
            previous_enabled = self.manual_blend_enabled
            previous_live = self.manual_blend_live_editing
            try:
                self.manual_blend_enabled = False
                self.manual_blend_live_editing = False
                rendered = self.render_current_image(for_preview=False)
            finally:
                self.manual_blend_enabled = previous_enabled
                self.manual_blend_live_editing = previous_live

        if rendered is not None:
            data = encode_compact_jpeg(rendered)
            if data:
                return data

        if self.current_pil_image is not None:
            data = encode_compact_jpeg(self.current_pil_image)
            if data:
                return data

        return b""

    def _format_manual_blend_bytes(self, data, mode=None):
        """
        Render byte data as editable text based on the selected encoding mode.
        """
        if not data:
            return ""

        if mode is None:
            mode = self.manual_blend_encoding_var.get() if hasattr(self, "manual_blend_encoding_var") else "Hex"

        if mode == "Latin-1 Text":
            return data.decode("latin-1", errors="ignore")

        if mode == "UTF-8 Text":
            return data.decode("utf-8", errors="replace")

        if mode == "Base64":
            import base64
            encoded = base64.b64encode(data).decode("ascii")
            chunk = 76
            return "\n".join(encoded[index:index + chunk] for index in range(0, len(encoded), chunk))

        per_line = 32
        lines = []
        for start in range(0, len(data), per_line):
            chunk = data[start:start + per_line]
            lines.append(" ".join(f"{byte:02x}" for byte in chunk))
        return "\n".join(lines)

    def _parse_manual_blend_text(self, text, mode=None):
        """
        Parse edited text into bytes using the selected encoding mode.
        """
        if mode is None:
            mode = self.manual_blend_encoding_var.get() if hasattr(self, "manual_blend_encoding_var") else "Hex"

        if mode == "Latin-1 Text":
            return text.encode("latin-1", errors="ignore")

        if mode == "UTF-8 Text":
            return text.encode("utf-8")

        if mode == "Base64":
            import base64
            compact = "".join(ch for ch in text if ch not in " \n\t\r")
            if compact == "":
                return b""
            return base64.b64decode(compact, validate=True)

        compact = "".join(ch for ch in text if ch not in " \n\t\r")
        if compact == "":
            return b""
        if len(compact) % 2 != 0:
            raise ValueError("Hex text length must be even.")
        return bytes.fromhex(compact)

    def _decode_image_bytes(self, data):
        """
        Decode image bytes safely and return an RGBA PIL image, or None.
        """
        if not data:
            return None

        try:
            decoded = Image.open(BytesIO(data))
            decoded.load()
            return decoded.convert("RGBA")
        except Exception:
            return None

    def _databend_bytes_with_payload(self, base_bytes, payload_bytes, frame_index=0):
        """
        Apply payload bytes onto encoded image bytes while preserving header safety.
        """
        if not base_bytes:
            return payload_bytes

        output = bytearray(base_bytes)
        if not payload_bytes:
            return bytes(output)

        keep_header = min(1024, max(64, len(output) // 20))
        if len(output) <= keep_header:
            return bytes(output)

        payload = np.frombuffer(payload_bytes, dtype=np.uint8)
        if payload.size == 0:
            return bytes(output)

        body = np.frombuffer(bytes(output[keep_header:]), dtype=np.uint8).copy()
        offset = int((frame_index * 73) % payload.size)
        shifted = np.roll(payload, -offset)
        stream = np.resize(shifted, body.size)
        body = np.bitwise_xor(body, stream)
        output[keep_header:] = body.tobytes()
        return bytes(output)

    def _apply_manual_blending(self, img, frame_index=0):
        """
        Apply text-driven byte blending to image pixels for glitch results.
        """
        if img is None or not self.manual_blend_enabled:
            return img

        arr = np.array(img.convert("RGBA"), copy=True)
        if arr.ndim != 3 or arr.shape[2] < 3:
            return img

        payload = np.frombuffer(self.manual_blend_bytes, dtype=np.uint8)
        if payload.size == 0:
            if self.manual_blend_live_editing:
                arr[..., :3] = 0
                return Image.fromarray(arr, mode="RGBA").convert(img.mode)
            return img

        direct_decode = self._decode_image_bytes(self.manual_blend_bytes)
        strict_reopen = bool(self.manual_blend_direct_reopen_var.get()) if hasattr(self, "manual_blend_direct_reopen_var") else False

        if direct_decode is not None:
            if direct_decode.size != img.size:
                direct_decode = direct_decode.resize(img.size, Image.LANCZOS)
            if arr.shape[2] >= 4:
                alpha = Image.fromarray(arr[..., 3], mode="L")
                direct_decode.putalpha(alpha)
            return direct_decode.convert(img.mode)

        if strict_reopen:
            if self.manual_blend_live_editing:
                arr[..., :3] = np.roll(arr[..., :3], shift=3 + (frame_index % 9), axis=0)
                return Image.fromarray(arr, mode="RGBA").convert(img.mode)
            return img

        base_buffer = BytesIO()
        img.convert("RGB").save(base_buffer, format="JPEG", quality=84, optimize=False)
        base_bytes = base_buffer.getvalue()
        databent_bytes = self._databend_bytes_with_payload(base_bytes, self.manual_blend_bytes, frame_index=frame_index)
        decoded = self._decode_image_bytes(databent_bytes)

        if decoded is None and self.manual_blend_source_bytes:
            from_source = self._databend_bytes_with_payload(
                self.manual_blend_source_bytes,
                self.manual_blend_bytes,
                frame_index=frame_index,
            )
            decoded = self._decode_image_bytes(from_source)

        if decoded is None:
            if self.manual_blend_live_editing:
                arr[..., :3] = np.roll(arr[..., :3], shift=1 + (frame_index % 7), axis=1)
                return Image.fromarray(arr, mode="RGBA").convert(img.mode)
            return img

        if decoded.size != img.size:
            decoded = decoded.resize(img.size, Image.LANCZOS)
        if arr.shape[2] >= 4:
            alpha = Image.fromarray(arr[..., 3], mode="L")
            decoded.putalpha(alpha)
        return decoded.convert(img.mode)

    def disable_manual_blending(self):
        """
        Disable manual blending and refresh preview.
        """
        self.manual_blend_enabled = False
        self.manual_blend_live_editing = False
        self.manual_blend_bytes = b""
        self.manual_blend_source_bytes = b""
        self.manual_blend_status_var.set("Manual blending disabled.")
        self.request_preview_update(immediate=True)

    def apply_manual_blending(self):
        """
        Commit the current moshed preview as the new working source image.
        """
        if self.current_pil_image is None:
            messagebox.showerror("Error", "No media loaded.")
            return

        final_image = self.render_current_image(for_preview=False)
        if final_image is None:
            messagebox.showerror("Error", "Unable to apply manual blending.")
            return

        baked = final_image.convert("RGBA")
        self.current_pil_image = baked
        self.image_source_path = None
        self.image_object = ImageObject(
            name=self.image_object.name if self.image_object is not None else "Manual Blend",
            size=baked.size,
            pixel_array=np.array(baked),
        )

        self.manual_blend_enabled = False
        self.manual_blend_live_editing = False
        self.manual_blend_bytes = b""
        self.manual_blend_source_bytes = b""
        self.manual_blend_status_var.set("Manual blending applied to source.")
        self.pipeline_image = baked.copy()
        self.display_image(baked)

    def _apply_manual_blend_editor_changes(self):
        """
        Parse editor text and apply manual blending payload.
        """
        self._manual_blend_pending_job = None
        if self.manual_blend_text_widget is None:
            return

        mode = self.manual_blend_encoding_var.get() if hasattr(self, "manual_blend_encoding_var") else "Hex"
        raw_text = self.manual_blend_text_widget.get("1.0", "end-1c")
        try:
            parsed = self._parse_manual_blend_text(raw_text, mode=mode)
        except Exception as exc:
            self.manual_blend_status_var.set(f"Manual blending parse error ({mode}): {exc}")
            return

        if len(parsed) > 32768:
            parsed = parsed[:32768]

        self.manual_blend_bytes = parsed
        self.manual_blend_enabled = True
        self.manual_blend_live_editing = True
        self.manual_blend_status_var.set(f"Manual blending active ({mode}) • {len(parsed)} edited bytes")
        self.request_preview_update()

    def _schedule_manual_blend_text_parse(self, _event=None):
        """
        Debounce text parsing for live preview updates.
        """
        if self._manual_blend_pending_job is not None:
            self.root.after_cancel(self._manual_blend_pending_job)
        self._manual_blend_pending_job = self.root.after(120, self._apply_manual_blend_editor_changes)

    def open_manual_blend_editor(self):
        """
        Open the built-in text editor used for manual byte blending.
        """
        seed_bytes = self._get_manual_blend_seed_bytes()
        if not seed_bytes:
            messagebox.showerror("Error", "Load an image or video before opening manual blending.")
            return

        self.manual_blend_source_bytes = seed_bytes

        if self.manual_blend_editor_window is not None and self.manual_blend_editor_window.winfo_exists():
            self.manual_blend_editor_window.lift()
            return

        win = tk.Toplevel(self.root)
        win.title("Manual Blending Editor")
        win.configure(bg=self.theme["panel"])
        win.geometry("860x620")
        self.manual_blend_editor_window = win

        tk.Label(
            win,
            text="Edit data below. Changes are applied live to the preview.",
            fg=self.theme["muted"],
            bg=self.theme["panel"],
            anchor="w",
        ).pack(fill=tk.X, padx=12, pady=(12, 6))

        mode_row = tk.Frame(win, bg=self.theme["panel"])
        mode_row.pack(fill=tk.X, padx=12, pady=(0, 6))
        tk.Label(
            mode_row,
            text="Encoding",
            fg=self.theme["text"],
            bg=self.theme["panel"],
            anchor="w",
        ).pack(side=tk.LEFT)
        encoding_menu = tk.OptionMenu(
            mode_row,
            self.manual_blend_encoding_var,
            "Hex",
            "Latin-1 Text",
            "UTF-8 Text",
            "Base64",
        )
        self._style_option_menu(encoding_menu)
        encoding_menu.pack(side=tk.LEFT, padx=(8, 0))

        strict_toggle = tk.Checkbutton(
            mode_row,
            text="Direct Reopen Only",
            variable=self.manual_blend_direct_reopen_var,
            bg=self.theme["panel"],
            fg=self.theme["text"],
            activebackground=self.theme["panel"],
            activeforeground=self.theme["text"],
            selectcolor=self.theme["field"],
            command=self.request_preview_update,
        )
        strict_toggle.pack(side=tk.LEFT, padx=(12, 0))

        editor_wrap = tk.Frame(win, bg=self.theme["panel"])
        editor_wrap.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        y_scroll = tk.Scrollbar(editor_wrap, orient=tk.VERTICAL)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget = tk.Text(
            editor_wrap,
            wrap=tk.NONE,
            bg=self.theme["field"],
            fg=self.theme["text"],
            insertbackground=self.theme["text"],
            relief=tk.SUNKEN,
            bd=2,
            yscrollcommand=y_scroll.set,
            padx=8,
            pady=8,
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scroll.configure(command=text_widget.yview)

        self.manual_blend_text_widget = text_widget
        self.manual_blend_live_editing = True
        if self.manual_blend_enabled and self.manual_blend_bytes:
            initial_bytes = self.manual_blend_bytes
        else:
            initial_bytes = seed_bytes

        text_widget.insert("1.0", self._format_manual_blend_bytes(initial_bytes))
        text_widget.bind("<KeyRelease>", self._schedule_manual_blend_text_parse)

        if self.manual_blend_encoding_trace_id is not None:
            try:
                self.manual_blend_encoding_var.trace_remove("write", self.manual_blend_encoding_trace_id)
            except Exception:
                pass
            self.manual_blend_encoding_trace_id = None

        last_mode = [self.manual_blend_encoding_var.get()]

        def on_encoding_change(*_args):
            if self.manual_blend_text_widget is None:
                return

            current_text = self.manual_blend_text_widget.get("1.0", "end-1c")
            previous_mode = last_mode[0]
            current_mode = self.manual_blend_encoding_var.get()
            try:
                current_bytes = self._parse_manual_blend_text(current_text, mode=previous_mode)
            except Exception:
                current_bytes = self.manual_blend_bytes if self.manual_blend_bytes else self._get_manual_blend_seed_bytes()

            self.manual_blend_text_widget.delete("1.0", tk.END)
            self.manual_blend_text_widget.insert("1.0", self._format_manual_blend_bytes(current_bytes, mode=current_mode))
            last_mode[0] = current_mode
            self._schedule_manual_blend_text_parse()

        self.manual_blend_encoding_trace_id = self.manual_blend_encoding_var.trace_add("write", on_encoding_change)

        button_row = tk.Frame(win, bg=self.theme["panel"])
        button_row.pack(fill=tk.X, padx=12, pady=(0, 12))

        def reset_to_source():
            source_bytes = self._get_manual_blend_seed_bytes()
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", self._format_manual_blend_bytes(source_bytes))
            self._schedule_manual_blend_text_parse()

        tk.Button(
            button_row,
            text="Reset To Source",
            command=reset_to_source,
            **self._button_style(self.theme["button"])
        ).pack(side=tk.LEFT)

        tk.Button(
            button_row,
            text="Disable",
            command=self.disable_manual_blending,
            **self._button_style(self.theme["button_alt"])
        ).pack(side=tk.LEFT, padx=(8, 0))

        tk.Button(
            button_row,
            text="Apply",
            command=self.apply_manual_blending,
            **self._button_style(self.theme["accent_soft"])
        ).pack(side=tk.LEFT, padx=(8, 0))

        tk.Button(
            button_row,
            text="Close",
            command=lambda: on_close(),
            **self._button_style(self.theme["button"])
        ).pack(side=tk.RIGHT)

        def on_close():
            if self.manual_blend_encoding_trace_id is not None:
                try:
                    self.manual_blend_encoding_var.trace_remove("write", self.manual_blend_encoding_trace_id)
                except Exception:
                    pass
                self.manual_blend_encoding_trace_id = None
            self.manual_blend_live_editing = False
            self.manual_blend_editor_window = None
            self.manual_blend_text_widget = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)
        self._schedule_manual_blend_text_parse()

    def _modulate_video_effect_values(self, frame_index, base_values):
        """
        Return effect values modulated by Intensity controls for a video frame index.
        """
        return render_pipeline_helpers.modulate_video_effect_values(self, frame_index, base_values)

    def _render_frame_with_values(self, source_image, effect_values, for_preview=False, frame_index=0):
        """
        Render a single frame (image or video frame) using supplied effect values.
        """
        return render_pipeline_helpers.render_frame_with_values(
            self,
            source_image,
            effect_values,
            for_preview=for_preview,
            frame_index=frame_index,
        )

    def render_current_image(self, for_preview=False):
        """
        Render the current image using the active controls.
        For preview rendering, CRT effects are applied on a reduced-size copy for speed.
        """
        return render_pipeline_helpers.render_current_image(self, for_preview=for_preview)

    def apply_pipeline(self):
        """
        Applies all effects in a pipeline, ensuring modifications are cumulative.
        """
        render_pipeline_helpers.apply_pipeline(self)

    def _trigger_preview_update(self, _=None):
        self.request_preview_update()

    def _effect_float(self, effect_values, key, default=0.0):
        try:
            return float(effect_values.get(key, default))
        except Exception:
            return float(default)

    def _effect_int(self, effect_values, key, default=0):
        try:
            return int(effect_values.get(key, default))
        except Exception:
            return int(default)

    def update_effects(self, _=None):
        self._trigger_preview_update()

    def update_colorize(self, _=None):
        self._trigger_preview_update()

    def update_confuser(self, _=None):
        """
        Updates the confuser effects (blur and color reduction) based on the sliders.
        """
        # Re-run the full pipeline so confuser effects are applied in sequence
        self._trigger_preview_update()

    def update_crt(self, _=None):
        """
        Updates the CRT effects.
        """
        self._trigger_preview_update()

    def update_bending(self, _=None):
        """
        Updates the databending effect.
        """
        self._trigger_preview_update()

    def update_datamosh(self, _=None):
        """
        Updates the datamoshing effect.
        """
        self._trigger_preview_update()

    def process_effects_on_image(self, pil_img, effect_values=None):
        """
        Apply the current UI-controlled effects to a given PIL image and return the result.
        This mirrors the main pipeline but operates on an arbitrary image (used for blending).
        """
        return render_pipeline_helpers.process_effects_on_image(self, pil_img, effect_values=effect_values)

    def apply_crt_effects(self, img, effect_values=None):
        """
        Apply CRT-style post-processing to the fully composited image.
        """
        return render_pipeline_helpers.apply_crt_effects(self, img, effect_values=effect_values)

    def upload_blend_image(self):
        """
        Uploads an image to be used as the blend overlay.
        """
        path = filedialog.askopenfilename(title="Select an Image to Blend", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if not path:
            return
        try:
            img = Image.open(path).convert("RGBA")
            self.blend_image_pil = img
            self.blend_filename_var.set(os.path.basename(path))
            self.request_preview_update(immediate=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load blend image: {e}")

    def update_blend(self, _=None):
        """
        Re-run pipeline when blend slider changes.
        """
        self._trigger_preview_update()

    def reset_pipeline(self):
        """
        Resets the pipeline to the original image.
        """
        self.pipeline_image = None
        self.request_preview_update(immediate=True)

    def upload_image(self):
        # Use root.after to decouple the dialog from the button event
        self.root.after(50, self._execute_upload)

    def _is_video_path(self, path):
        return media_io_helpers.is_video_path(path)

    def _close_video_preview_window(self):
        media_io_helpers.close_video_preview_window(self)

    def _read_video_source_snapshot(self, file_path):
        return media_io_helpers.read_video_source_snapshot(file_path)

    def _apply_loaded_media(self, file_path, img, is_video_mode, video_fps=12.0, video_frame_count=0, select_intensity_tab=False):
        media_io_helpers.apply_loaded_media(
            self,
            file_path,
            img,
            is_video_mode,
            video_fps=video_fps,
            video_frame_count=video_frame_count,
            select_intensity_tab=select_intensity_tab,
        )

    def _load_image_file(self, file_path):
        self._close_video_preview_window()
        img = Image.open(file_path).convert("RGBA")
        self._apply_loaded_media(file_path, img, is_video_mode=False)

    def _load_video_file(self, file_path):
        self._close_video_preview_window()
        img, fps, frame_count = self._read_video_source_snapshot(file_path)
        self._apply_loaded_media(
            file_path,
            img,
            is_video_mode=True,
            video_fps=fps,
            video_frame_count=frame_count,
            select_intensity_tab=True,
        )

    def _execute_upload(self):
        media_io_helpers.execute_upload(self)

    def _iter_video_frames(self):
        """
        Yield source video frames as RGBA PIL images.
        """
        if not self.video_source_path:
            return

        reader = imageio.get_reader(self.video_source_path)
        try:
            for frame in reader:
                yield Image.fromarray(frame).convert("RGBA")
        finally:
            reader.close()

    def _render_video_preview_frames(self, max_frames=90):
        """
        Render a lightweight processed frame list for in-app video preview playback.
        """
        if not self.is_video_mode or not self.video_source_path:
            return []

        base_values = self._collect_effect_values()
        rendered = []
        for index, frame in enumerate(self._iter_video_frames()):
            if index >= max_frames:
                break
            frame_values = self._modulate_video_effect_values(index, base_values)
            processed = self._render_frame_with_values(frame, frame_values, for_preview=True, frame_index=index)
            if processed is not None:
                rendered.append(processed)

        return rendered

    def _run_video_preview_loop(self):
        """
        Advance preview playback in the video preview window.
        """
        if self.video_preview_window is None or not self.video_preview_window.winfo_exists():
            return
        if not self.video_preview_images:
            return

        self.video_preview_index = (self.video_preview_index + 1) % len(self.video_preview_images)
        self.video_preview_label.configure(image=self.video_preview_images[self.video_preview_index])
        frame_delay = max(16, int(round(1000.0 / max(1.0, min(self.video_fps, 30.0)))))
        self.video_preview_window.after(frame_delay, self._run_video_preview_loop)

    def open_video_preview_window(self):
        """
        Open a window that plays a processed preview of the current video settings.
        """
        if not self.is_video_mode or not self.video_source_path:
            messagebox.showerror("Error", "Load a video before opening video preview.")
            return

        try:
            frames = self._render_video_preview_frames(max_frames=90)
        except Exception as exc:
            messagebox.showerror("Error", f"Unable to render video preview: {exc}")
            return

        if not frames:
            messagebox.showerror("Error", "No preview frames could be rendered.")
            return

        if self.video_preview_window is not None and self.video_preview_window.winfo_exists():
            self.video_preview_window.destroy()

        win = tk.Toplevel(self.root)
        win.title("Video Preview")
        win.configure(bg=self.theme["panel"])
        win.geometry("760x560")
        self.video_preview_window = win

        label = tk.Label(win, bg="#000000")
        label.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 8))
        self.video_preview_label = label

        footer = tk.Label(
            win,
            text=f"Showing first {len(frames)} rendered frame(s) at up to 30 fps.",
            fg=self.theme["muted"],
            bg=self.theme["panel"],
            anchor="w",
        )
        footer.pack(fill=tk.X, padx=12, pady=(0, 12))

        self.video_preview_images = [ImageTk.PhotoImage(frame) for frame in frames]
        self.video_preview_index = 0
        self.video_preview_label.configure(image=self.video_preview_images[0])
        self._run_video_preview_loop()

    def export_video_from_dialog(self):
        """
        Open save dialog and export the processed video.
        """
        if not self.is_video_mode or not self.video_source_path:
            messagebox.showerror("Error", "Load a video before exporting.")
            return

        file_path = self._ask_save_file(
            title="Export Video",
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4")],
            initialfile="Weird_Pixelator_Video.mp4",
        )
        if not file_path:
            return

        self._run_export_with_feedback(
            export_callable=lambda: self.export_video(file_path),
            failure_message="Failed to export video",
            success_message=f"Video exported to {file_path}",
        )

    def export_video(self, file_path):
        """
        Process and export the full source video with current controls.
        """
        if not self.is_video_mode or not self.video_source_path:
            raise ValueError("No video loaded.")

        base_values = self._collect_effect_values()
        fps = max(1.0, float(self.video_fps))
        writer = None
        try:
            for index, frame in enumerate(self._iter_video_frames()):
                frame_values = self._modulate_video_effect_values(index, base_values)
                processed = self._render_frame_with_values(frame, frame_values, for_preview=False, frame_index=index)
                if processed is None:
                    continue

                rgb = processed.convert("RGB")
                width, height = rgb.size
                even_size = (width + (width % 2), height + (height % 2))
                if rgb.size != even_size:
                    rgb = rgb.resize(even_size, Image.LANCZOS)

                if writer is None:
                    writer = imageio.get_writer(
                        file_path,
                        fps=fps,
                        codec="libx264",
                        quality=8,
                        pixelformat="yuv420p",
                        macro_block_size=1,
                    )

                writer.append_data(np.array(rgb))
        finally:
            if writer is not None:
                writer.close()

    def display_image(self, img):
        if img is None:
            self.tk_img = None
            self._render_empty_preview()
            self._update_preview_metadata()
            return

        self.canvas.update_idletasks() # Ensure canvas dimensions are updated
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        img_width, img_height = img.size
        ratio = min(canvas_width / img_width, canvas_height / img_height, 1.0)
        new_width = max(1, int(img_width * ratio))
        new_height = max(1, int(img_height * ratio))
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)

        self.tk_img = ImageTk.PhotoImage(resized_img)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width/2, canvas_height/2, anchor=tk.CENTER, image=self.tk_img)
        self._update_preview_metadata(rendered_size=img.size)

    def randomize_effects(self):
        """
        Randomizes all effect sliders to create a unique combination of effects.
        """
        import random
        # Randomize only the parameters enabled in settings
        get = lambda key, default=True: self.randomize_settings.get(key, tk.BooleanVar(value=default)).get()

        self.begin_bulk_update()
        try:
            # Pixelate group
            if get('pixel_scale'):
                self.pixel_slider.set(random.uniform(0.01, 1.0))
            if get('jitter'):
                self.jitter_slider.set(random.randint(0, 100))
            if get('block'):
                self.block_slider.set(random.randint(0, 100))
            if get('sort'):
                self.sort_slider.set(random.randint(0, 100))

            # Colorize group
            if get('hue'):
                self.hue_slider.set(random.randint(-180, 180))
            if get('saturation'):
                self.saturation_slider.set(random.uniform(0.0, 2.0))
            if get('contrast'):
                self.contrast_slider.set(random.uniform(0.5, 2.0))
            if get('invert'):
                self.invert_state.set(random.choice([True, False]))

            # Random pixels
            if get('random_pixels'):
                self.random_pixel_slider.set(random.uniform(0.0, 1.0))

            # Confuser group
            if get('blur'):
                self.blur_slider.set(random.randint(0, 10))
            if get('color_reducer'):
                self.color_reducer_slider.set(random.randint(2, 256))
            if get('legacy_collapse'):
                self.legacy_color_slider.set(random.randint(2, 256))
            if get('bending'):
                self.bend_slider.set(random.randint(0, 75))
                self.bend_mode_var.set(random.choice(["Byte Shift", "Byte Swap", "Repeat Burst"]))
            if get('datamosh'):
                self.datamosh_slider.set(random.randint(0, 80))
                self.datamosh_mode_var.set(random.choice(["AVI Style", "P-Frame Smear", "Block Echo", "Reverse"]))

            # CRT group
            if get('curvature'):
                self.curvature_slider.set(random.randint(0, 65))
            if get('distortion'):
                self.distortion_slider.set(random.randint(0, 55))
            if get('glow'):
                self.glow_slider.set(random.randint(0, 60))
            if get('noise'):
                self.noise_slider.set(random.randint(0, 35))
            if get('scanlines'):
                self.scanline_slider.set(random.randint(0, 85))
            if get('rgb_shift'):
                self.rgb_shift_slider.set(random.randint(0, 6))
            if get('vignette'):
                self.vignette_slider.set(random.randint(0, 65))

            # Blend
            if get('blend') and hasattr(self, 'blend_slider'):
                self.blend_slider.set(random.uniform(0.0, 1.0))

            # Export compression
            if get('compression') and hasattr(self, 'export_compression_var'):
                self.export_compression_var.set(random.choice([
                    "No Compression",
                    "Soft CCD",
                    "Compact Camera",
                    "Memory Saver",
                    "Harsh Artifacts",
                ]))
        finally:
            self.end_bulk_update(refresh=True)

    def update_random_pixels(self, _=None):
        """
        Gradually randomizes the color of random pixels based on the slider value.
        """
        # Re-run the full pipeline so randomization is persistent and composes with other effects
        self.request_preview_update()

    def open_randomize_settings(self):
        """
        Open a modal window where the user can toggle which parameters are affected by Randomize.
        """
        win = tk.Toplevel(self.root)
        win.title("Randomize Settings")
        win.configure(bg=self.theme["panel"])
        win.transient(self.root)
        win.grab_set()

        # Layout checkboxes in two columns, alphabetically
        sorted_keys = sorted(self.randomize_settings.keys(), key=lambda key: key.replace('_', ' '))
        left_keys = sorted_keys[::2]
        right_keys = sorted_keys[1::2]

        row = 0
        for k in left_keys:
            cb = tk.Checkbutton(
                win,
                text=k.replace('_',' ').title(),
                variable=self.randomize_settings[k],
                bg=self.theme["panel"],
                fg=self.theme["text"],
                activebackground=self.theme["panel"],
                activeforeground=self.theme["text"],
                selectcolor=self.theme["field"],
            )
            cb.grid(row=row, column=0, sticky='w', padx=10, pady=2)
            row += 1

        row = 0
        for k in right_keys:
            if k not in self.randomize_settings:
                self.randomize_settings[k] = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(
                win,
                text=k.replace('_',' ').title(),
                variable=self.randomize_settings[k],
                bg=self.theme["panel"],
                fg=self.theme["text"],
                activebackground=self.theme["panel"],
                activeforeground=self.theme["text"],
                selectcolor=self.theme["field"],
            )
            cb.grid(row=row, column=1, sticky='w', padx=10, pady=2)
            row += 1

        # Buttons
        btn_frame = tk.Frame(win, bg=self.theme["panel"])
        btn_frame.grid(row=max(len(left_keys), len(right_keys))+1, column=0, columnspan=2, pady=10)

        def select_all():
            for v in self.randomize_settings.values():
                v.set(True)

        def deselect_all():
            for v in self.randomize_settings.values():
                v.set(False)

        tk.Button(btn_frame, text="Select All", command=select_all, **self._button_style(self.theme["button"])).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Deselect All", command=deselect_all, **self._button_style(self.theme["button"])).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=win.destroy, **self._button_style(self.theme["button_alt"])).pack(side=tk.LEFT, padx=5)

    def toggle_invert(self):
        """
        Toggles the invert effect on the image.
        """
        # Variable is already updated by the Checkbutton; just re-run the pipeline
        self.request_preview_update()

    def select_folder(self):
        """
        Opens a dialog to select a folder and updates the folder path.
        """
        folder_selected = filedialog.askdirectory(title="Select Folder")
        if folder_selected:
            self.folder_path.set(folder_selected)

    def _resolve_output_folder(self):
        return export_helpers.resolve_output_folder(self)

    def _next_available_png_path(self, folder, base_name):
        return export_helpers.next_available_png_path(folder, base_name)

    def save_image(self):
        """
        Saves the current image to the selected folder.
        """
        if self.image_object is None:
            messagebox.showerror("Error", "No image to save.")
            return

        folder = self._resolve_output_folder()
        if not folder:
            messagebox.showerror("Error", "No folder selected.")
            return

        # Prompt for filename (without extension)
        default_name = "Weird_Pixellator_Output"
        name = simpledialog.askstring("Save As", "Enter file name (without extension):", initialvalue=default_name)
        if not name:
            return
        name = name.strip()
        if name == "":
            messagebox.showerror("Error", "Invalid file name.")
            return

        file_path = self._next_available_png_path(folder, name)

        try:
            final_image = self.render_current_image(for_preview=False)
            if final_image is None:
                messagebox.showerror("Error", "No image to save.")
                return
            self.full_resolution_image = final_image
            final_image.save(file_path)
            messagebox.showinfo("Success", f"Image saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")

    def save_as(self):
        """
        Save the current media: image as PNG or video as MP4.
        """
        if self.is_video_mode:
            self.export_video_from_dialog()
            return

        self.save_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()