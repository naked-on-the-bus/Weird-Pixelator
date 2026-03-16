import tkinter as tk
from tkinter import ttk


def build_ui_shell(app):
    app.root.configure(bg=app.theme["bg"])
    configure_notebook_style(app)

    if hasattr(app, "app_shell") and app.app_shell is not None:
        app.app_shell.destroy()

    app.app_shell = tk.Frame(app.root, bg=app.theme["bg"])
    app.app_shell.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
    app.app_shell.grid_columnconfigure(0, weight=3)
    app.app_shell.grid_columnconfigure(1, weight=2, minsize=360)
    app.app_shell.grid_rowconfigure(1, weight=1)

    build_header(app)
    build_preview_panel(app)
    build_control_sidebar(app)


def configure_notebook_style(app):
    style = ttk.Style(app.root)
    try:
        style.theme_use("classic")
    except tk.TclError:
        pass

    style.configure(
        "Weird.TNotebook",
        background=app.theme["bg"],
        borderwidth=1,
        tabmargins=(2, 2, 2, 0),
    )
    style.configure(
        "Weird.TNotebook.Tab",
        background=app.theme["panel"],
        foreground=app.theme["text"],
        padding=(12, 6),
        borderwidth=1,
        relief="raised",
        focuscolor=app.theme["panel"],
    )
    style.map(
        "Weird.TNotebook.Tab",
        background=[("selected", app.theme["panel_alt"]), ("active", app.theme["panel_soft"])],
        foreground=[("selected", app.theme["text"]), ("active", app.theme["text"])],
    )


def build_header(app):
    app.header_frame = tk.Frame(app.app_shell, bg=app.theme["bg"])
    app.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
    app.header_frame.grid_columnconfigure(0, weight=1)

    title_block = tk.Frame(app.header_frame, bg=app.theme["bg"])
    title_block.grid(row=0, column=0, sticky="w")

    tk.Label(
        title_block,
        text="Weird Pixelator",
        fg=app.theme["text"],
        bg=app.theme["bg"],
        font=("Helvetica", 20, "bold"),
    ).pack(anchor="w")
    tk.Label(
        title_block,
        text="Compact glitch controls with a cleaner preview workflow.",
        fg=app.theme["muted"],
        bg=app.theme["bg"],
        font=("Helvetica", 10),
    ).pack(anchor="w", pady=(2, 0))

    actions = tk.Frame(app.header_frame, bg=app.theme["bg"])
    actions.grid(row=0, column=1, sticky="e")

    app.upload_button = tk.Button(
        actions,
        text="Upload",
        command=app.upload_image,
        **app._button_style(app.theme["button"]),
    )
    app.upload_button.pack(side=tk.LEFT, padx=(0, 8))

    app.save_button = tk.Button(
        actions,
        text="Save As",
        command=app.save_as,
        **app._button_style(app.theme["accent_soft"]),
    )
    app.save_button.pack(side=tk.LEFT, padx=(0, 8))

    app.randomize_settings_button = tk.Button(
        actions,
        text="Randomize Settings",
        command=app.open_randomize_settings,
        **app._button_style(app.theme["button_alt"]),
    )
    app.randomize_settings_button.pack(side=tk.LEFT, padx=(0, 8))

    app.settings_button = tk.Button(
        actions,
        text="Settings",
        command=app.open_app_settings,
        **app._button_style(app.theme["button"]),
    )
    app.settings_button.pack(side=tk.LEFT)


def build_preview_panel(app):
    app.preview_frame, preview_body = app._create_card(
        app.app_shell,
        "Preview",
        app.preview_hint_var,
        stretch=True,
    )
    app.preview_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
    app.preview_frame.grid_rowconfigure(1, weight=1)
    app.preview_frame.grid_columnconfigure(0, weight=1)

    tk.Label(
        preview_body,
        textvariable=app.preview_title_var,
        fg=app.theme["text"],
        bg=app.theme["panel"],
        font=("Helvetica", 13, "bold"),
        anchor="w",
    ).pack(anchor="w")

    app.canvas_wrap = tk.Frame(
        preview_body,
        bg=app.theme["canvas"],
        relief=tk.SUNKEN,
        bd=2,
        highlightthickness=0,
    )
    app.canvas_wrap.configure(width=430, height=430)
    app.canvas_wrap.pack_propagate(False)
    app.canvas_wrap.pack(pady=(10, 0), anchor="center")

    app.canvas = tk.Canvas(
        app.canvas_wrap,
        width=400,
        height=400,
        bg="#000000",
        bd=0,
        highlightthickness=0,
    )
    app.canvas.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    tk.Label(
        preview_body,
        text="Live preview updates automatically while you tweak controls.",
        fg=app.theme["muted"],
        bg=app.theme["panel"],
        font=("Helvetica", 10),
    ).pack(anchor="w", pady=(10, 0))

    app.fullsize_preview_button = tk.Button(
        preview_body,
        text="Full Size Preview",
        command=app.open_fullsize_preview,
        bg=app.theme["button"],
        fg=app.theme["text"],
        relief=tk.FLAT,
        padx=10,
        pady=4,
        cursor="hand2",
    )
    app.fullsize_preview_button.pack(anchor="center", pady=(8, 0))


def build_control_sidebar(app):
    app.sidebar_frame = tk.Frame(app.app_shell, bg=app.theme["bg"])
    app.sidebar_frame.grid(row=1, column=1, sticky="nsew")
    app.sidebar_frame.grid_rowconfigure(0, weight=1)
    app.sidebar_frame.grid_columnconfigure(0, weight=1)

    app.controls_notebook = ttk.Notebook(app.sidebar_frame, style="Weird.TNotebook")
    app.controls_notebook.grid(row=0, column=0, sticky="nsew")

    app.edit_tab = tk.Frame(app.controls_notebook, bg=app.theme["bg"])
    app.glitch_tab = tk.Frame(app.controls_notebook, bg=app.theme["bg"])
    app.finish_tab = tk.Frame(app.controls_notebook, bg=app.theme["bg"])
    app.crop_tab = tk.Frame(app.controls_notebook, bg=app.theme["bg"])
    app.animate_tab = tk.Frame(app.controls_notebook, bg=app.theme["bg"])
    app.intensity_tab = tk.Frame(app.controls_notebook, bg=app.theme["bg"])
    app.palette_tab = tk.Frame(app.controls_notebook, bg=app.theme["bg"])
    app.batch_tab = tk.Frame(app.controls_notebook, bg=app.theme["bg"])

    app.controls_notebook.add(app.edit_tab, text="Adjust")
    app.controls_notebook.add(app.glitch_tab, text="Glitch")
    app.controls_notebook.add(app.finish_tab, text="Finish")
    app.controls_notebook.add(app.crop_tab, text="Crop")
    app.controls_notebook.add(app.animate_tab, text="Animate")
    app.controls_notebook.add(app.intensity_tab, text="Intensity")
    app.controls_notebook.add(app.palette_tab, text="Palette")
    app.controls_notebook.add(app.batch_tab, text="Batch")

    build_adjust_tab(app)
    build_glitch_tab(app)
    build_finish_tab(app)
    build_crop_tab(app)
    build_animation_tab(app)
    build_intensity_tab(app)
    build_palette_tab(app)
    build_batch_tab(app)
    app._sync_media_tabs()


def build_adjust_tab(app):
    app.edit_tab.grid_columnconfigure(0, weight=1)
    app.edit_tab.grid_columnconfigure(1, weight=1)

    app.pixelate_frame, pixelate_body = app._create_card(app.edit_tab, "Pixelate")
    app.pixelate_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 8))
    app.jitter_slider = app._create_compact_slider(pixelate_body, "Row Jitter", 0, 100, app.update_effects, initial=0)
    app.block_slider = app._create_compact_slider(pixelate_body, "Block Shift", 0, 100, app.update_effects, initial=0)
    app.sort_slider = app._create_compact_slider(pixelate_body, "Pixel Sort", 0, 100, app.update_effects, initial=0)
    app.pixel_slider = app._create_compact_slider(
        pixelate_body,
        "Pixelate",
        1.0,
        0.01,
        app.update_effects,
        resolution=0.01,
        initial=1.0,
        formatter=lambda value: f"{float(value):.2f}"
    )

    app.colorize_frame, colorize_body = app._create_card(app.edit_tab, "Colorize")
    app.colorize_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 8))
    app.hue_slider = app._create_compact_slider(colorize_body, "Hue Shift", -180, 180, app.update_colorize, initial=0)
    app.saturation_slider = app._create_compact_slider(
        colorize_body,
        "Saturation",
        0.0,
        2.0,
        app.update_colorize,
        resolution=0.1,
        initial=1.0,
        formatter=lambda value: f"{float(value):.1f}"
    )
    app.contrast_slider = app._create_compact_slider(
        colorize_body,
        "Contrast",
        0.5,
        2.0,
        app.update_colorize,
        resolution=0.1,
        initial=1.0,
        formatter=lambda value: f"{float(value):.1f}"
    )
    app.invert_button = tk.Checkbutton(
        colorize_body,
        text="Invert Colors",
        variable=app.invert_state,
        command=app.toggle_invert,
        bg=app.theme["panel"],
        fg=app.theme["text"],
        activebackground=app.theme["panel"],
        activeforeground=app.theme["text"],
        selectcolor=app.theme["field"],
        highlightthickness=0,
        bd=0,
        anchor="w"
    )
    app.invert_button.pack(fill=tk.X, pady=(4, 0))

    app.randomize_frame, randomize_body = app._create_card(app.edit_tab, "Randomize")
    app.randomize_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=(0, 8))
    app.randomize_button = tk.Button(
        randomize_body,
        text="Randomize Effects",
        command=app.randomize_effects,
        **app._button_style(app.theme["button"])
    )
    app.randomize_button.pack(fill=tk.X)
    app.random_pixel_slider = app._create_compact_slider(
        randomize_body,
        "Random Pixels",
        0.0,
        1.0,
        app.update_random_pixels,
        resolution=0.01,
        initial=0.0,
        formatter=lambda value: f"{float(value):.2f}"
    )
    app.randomize_settings_inline = tk.Button(
        randomize_body,
        text="Choose Randomized Controls",
        command=app.open_randomize_settings,
        **app._button_style(app.theme["button_alt"])
    )
    app.randomize_settings_inline.pack(fill=tk.X, pady=(6, 0))

    app.confuser_frame, confuser_body = app._create_card(app.edit_tab, "Confuser")
    app.confuser_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 0), pady=(0, 8))
    app.blur_slider = app._create_compact_slider(confuser_body, "Blur", 0, 10, app.update_confuser, initial=0)
    app.color_reducer_slider = app._create_compact_slider(confuser_body, "Color Reducer", 2, 256, app.update_confuser, initial=256)
    app.legacy_color_slider = app._create_compact_slider(confuser_body, "Color Collapse", 2, 256, app.update_confuser, initial=256)

    app.blend_frame, blend_body = app._create_card(app.edit_tab, "Blend")
    app.blend_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
    app.upload_blend_button = tk.Button(
        blend_body,
        text="Upload Blend Image",
        command=app.upload_blend_image,
        **app._button_style(app.theme["button"])
    )
    app.upload_blend_button.pack(fill=tk.X)
    tk.Label(
        blend_body,
        textvariable=app.blend_filename_var,
        fg=app.theme["muted"],
        bg=app.theme["panel"],
        anchor="w"
    ).pack(fill=tk.X, pady=(6, 2))
    app.blend_slider = app._create_compact_slider(
        blend_body,
        "Blend Factor",
        0.0,
        1.0,
        app.update_blend,
        resolution=0.01,
        initial=0.0,
        formatter=lambda value: f"{float(value):.2f}"
    )


def build_glitch_tab(app):
    app.glitch_tab.grid_columnconfigure(0, weight=1)
    app.glitch_tab.grid_columnconfigure(1, weight=1)

    app.bending_frame, bending_body = app._create_card(app.glitch_tab, "Bending")
    app.bending_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 8))
    tk.Label(bending_body, text="Mode", fg=app.theme["text"], bg=app.theme["panel"], anchor="w").pack(fill=tk.X)
    app.bend_mode_menu = tk.OptionMenu(
        bending_body,
        app.bend_mode_var,
        "Byte Shift",
        "Byte Swap",
        "Repeat Burst",
        command=app.update_bending,
    )
    app._style_option_menu(app.bend_mode_menu)
    app.bend_mode_menu.pack(fill=tk.X, pady=(4, 8))
    app.bend_slider = app._create_compact_slider(
        bending_body,
        "Corruption",
        0,
        100,
        app.update_bending,
        initial=0,
    )

    app.datamosh_frame, datamosh_body = app._create_card(app.glitch_tab, "Data Moshing")
    app.datamosh_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 8))
    tk.Label(datamosh_body, text="Mode", fg=app.theme["text"], bg=app.theme["panel"], anchor="w").pack(fill=tk.X)
    app.datamosh_mode_menu = tk.OptionMenu(
        datamosh_body,
        app.datamosh_mode_var,
        "AVI Style",
        "P-Frame Smear",
        "Block Echo",
        "Reverse",
        command=app.update_datamosh,
    )
    app._style_option_menu(app.datamosh_mode_menu)
    app.datamosh_mode_menu.pack(fill=tk.X, pady=(4, 8))
    app.datamosh_slider = app._create_compact_slider(
        datamosh_body,
        "Intensity",
        0,
        100,
        app.update_datamosh,
        initial=0,
    )

    app.converter_frame, converter_body = app._create_card(app.glitch_tab, "Image Converter")
    app.converter_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 8))
    tk.Label(converter_body, text="Convert To", fg=app.theme["text"], bg=app.theme["panel"], anchor="w").pack(fill=tk.X)
    app.convert_format_menu = tk.OptionMenu(
        converter_body,
        app.convert_format_var,
        "PNG", "JPEG", "BMP", "TIFF", "WebP", "HEIF",
    )
    app._style_option_menu(app.convert_format_menu)
    app.convert_format_menu.pack(fill=tk.X, pady=(4, 8))
    app.convert_button = tk.Button(
        converter_body,
        text="Convert Image",
        command=app.convert_image_format,
        **app._button_style(app.theme["button_alt"])
    )
    app.convert_button.pack(fill=tk.X)
    tk.Label(
        converter_body,
        textvariable=app.convert_status_var,
        fg=app.theme["muted"],
        bg=app.theme["panel"],
        anchor="w",
        justify=tk.LEFT,
        wraplength=320,
    ).pack(fill=tk.X, pady=(8, 0))

    app.manual_blend_frame, manual_blend_body = app._create_card(app.glitch_tab, "Databend Editor")
    app.manual_blend_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
    app.manual_blend_button = tk.Button(
        manual_blend_body,
        text="Open Databend Editor",
        command=app.open_manual_blend_editor,
        **app._button_style(app.theme["button_alt"])
    )
    app.manual_blend_button.pack(fill=tk.X)
    app.manual_blend_clear_button = tk.Button(
        manual_blend_body,
        text="Disable Databend",
        command=app.disable_manual_blending,
        **app._button_style(app.theme["button"])
    )
    app.manual_blend_clear_button.pack(fill=tk.X, pady=(6, 0))
    tk.Label(
        manual_blend_body,
        textvariable=app.manual_blend_status_var,
        fg=app.theme["muted"],
        bg=app.theme["panel"],
        anchor="w",
        justify=tk.LEFT,
        wraplength=320,
    ).pack(fill=tk.X, pady=(8, 0))


def build_finish_tab(app):
    app.finish_tab.grid_columnconfigure(0, weight=1)

    app.crt_frame, crt_body = app._create_card(app.finish_tab, "CRT Finish")
    app.crt_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))

    crt_grid = tk.Frame(crt_body, bg=app.theme["panel"])
    crt_grid.pack(fill=tk.X)
    crt_grid.grid_columnconfigure(0, weight=1)
    crt_grid.grid_columnconfigure(1, weight=1)

    crt_left = tk.Frame(crt_grid, bg=app.theme["panel"])
    crt_left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
    crt_right = tk.Frame(crt_grid, bg=app.theme["panel"])
    crt_right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

    app.curvature_slider = app._create_compact_slider(crt_left, "Curvature", 0, 100, app.update_crt, initial=0)
    app.glow_slider = app._create_compact_slider(crt_left, "Glow", 0, 100, app.update_crt, initial=0)
    app.rgb_shift_slider = app._create_compact_slider(crt_left, "RGB Shift", 0, 20, app.update_crt, initial=0)
    app.vignette_slider = app._create_compact_slider(crt_left, "Vignette", 0, 100, app.update_crt, initial=0)

    app.distortion_slider = app._create_compact_slider(crt_right, "Distortion", 0, 100, app.update_crt, initial=0)
    app.noise_slider = app._create_compact_slider(crt_right, "Noise", 0, 100, app.update_crt, initial=0)
    app.scanline_slider = app._create_compact_slider(crt_right, "Scanlines", 0, 100, app.update_crt, initial=0)

    app.export_frame, export_body = app._create_card(app.finish_tab, "Export")
    app.export_frame.grid(row=1, column=0, sticky="nsew")
    tk.Label(export_body, text="Save Style", fg=app.theme["text"], bg=app.theme["panel"], anchor="w").pack(fill=tk.X)
    app.export_compression_menu = tk.OptionMenu(
        export_body,
        app.export_compression_var,
        "No Compression",
        "Soft CCD",
        "Compact Camera",
        "Memory Saver",
        "Harsh Artifacts",
        command=app.update_export_compression
    )
    app._style_option_menu(app.export_compression_menu)
    app.export_compression_menu.pack(fill=tk.X, pady=(4, 8))

    tk.Label(export_body, text="Save Folder", fg=app.theme["text"], bg=app.theme["panel"], anchor="w").pack(fill=tk.X)
    folder_row = tk.Frame(export_body, bg=app.theme["panel"])
    folder_row.pack(fill=tk.X, pady=(4, 0))
    app.folder_entry = tk.Entry(folder_row, textvariable=app.folder_path, **app._entry_style())
    app.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    app.browse_button = tk.Button(
        folder_row,
        text="Browse",
        command=app.select_folder,
        **app._button_style(app.theme["button_alt"])
    )
    app.browse_button.pack(side=tk.LEFT, padx=(8, 0))

    button_row = tk.Frame(export_body, bg=app.theme["panel"])
    button_row.pack(fill=tk.X, pady=(10, 0))
    app.save_png_button = tk.Button(
        button_row,
        text="Save As",
        command=app.save_as,
        **app._button_style(app.theme["button"])
    )
    app.save_png_button.pack(side=tk.LEFT)
    app.video_preview_button = tk.Button(
        button_row,
        text="See Video Preview",
        command=app.open_video_preview_window,
        **app._button_style(app.theme["button_alt"])
    )
    app.video_preview_button.pack(side=tk.LEFT, padx=(8, 0))
    tk.Label(
        export_body,
        text="Compression affects preview and final export.",
        fg=app.theme["muted"],
        bg=app.theme["panel"],
        anchor="w"
    ).pack(fill=tk.X, pady=(8, 0))
    app._update_video_action_buttons()


def build_crop_tab(app):
    app.crop_tab.grid_columnconfigure(0, weight=1)
    app.crop_frame, crop_body = app._create_card(app.crop_tab, "Crop & Aspect")
    app.crop_frame.grid(row=0, column=0, sticky="nsew")

    crop_grid = tk.Frame(crop_body, bg=app.theme["panel"])
    crop_grid.pack(fill=tk.X)
    crop_grid.grid_columnconfigure(0, weight=1)
    crop_grid.grid_columnconfigure(1, weight=1)

    app.crop_left_slider, app.crop_left_entry = app._create_crop_control(crop_grid, 0, 0, "left", "Left")
    app.crop_right_slider, app.crop_right_entry = app._create_crop_control(crop_grid, 0, 1, "right", "Right")
    app.crop_top_slider, app.crop_top_entry = app._create_crop_control(crop_grid, 1, 0, "top", "Top")
    app.crop_bottom_slider, app.crop_bottom_entry = app._create_crop_control(crop_grid, 1, 1, "bottom", "Bottom")

    footer = tk.Frame(crop_body, bg=app.theme["panel"])
    footer.pack(fill=tk.X, pady=(8, 0))
    footer.grid_columnconfigure(0, weight=1)
    footer.grid_columnconfigure(1, weight=0)

    app.crop_size_label = tk.Label(
        footer,
        textvariable=app.crop_size_var,
        fg=app.theme["muted"],
        bg=app.theme["panel"],
        anchor="w"
    )
    app.crop_size_label.grid(row=0, column=0, sticky="w")

    preset_row = tk.Frame(footer, bg=app.theme["panel"])
    preset_row.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
    preset_row.grid_columnconfigure(1, weight=1)
    tk.Label(preset_row, text="Preset", fg=app.theme["text"], bg=app.theme["panel"]).grid(row=0, column=0, sticky="w", padx=(0, 8))
    app.crop_preset_menu = tk.OptionMenu(
        preset_row,
        app.crop_preset_var,
        "Free",
        "1:1",
        "3:2",
        "4:5",
        "16:9",
        "9:16",
        "21:9",
        command=app.apply_crop_preset
    )
    app._style_option_menu(app.crop_preset_menu)
    app.crop_preset_menu.grid(row=0, column=1, sticky="ew")

    app.reset_crop_button = tk.Button(
        crop_body,
        text="Reset Crop",
        command=app.reset_crop,
        **app._button_style(app.theme["button_alt"])
    )
    app.reset_crop_button.pack(fill=tk.X, pady=(10, 0))


def build_animation_tab(app):
    app.animate_tab.grid_columnconfigure(0, weight=1)
    app.animation_frame, animation_body = app._create_card(app.animate_tab, "Animation Frames")
    app.animation_frame.grid(row=0, column=0, sticky="nsew")

    app.animation_button_row = tk.Frame(animation_body, bg=app.theme["panel"])
    app.animation_button_row.pack(fill=tk.X)
    app.add_frame_button = tk.Button(
        app.animation_button_row,
        text="Add Frame",
        command=app.add_animation_frame,
        **app._button_style(app.theme["button"])
    )
    app.add_frame_button.pack(side=tk.LEFT)

    app.delete_frame_button = tk.Button(
        app.animation_button_row,
        text="Delete Last",
        command=app.delete_last_animation_frame,
        **app._button_style(app.theme["button_alt"])
    )
    app.delete_frame_button.pack(side=tk.LEFT, padx=(8, 0))

    app.export_animation_button = tk.Button(
        app.animation_button_row,
        text="Export",
        command=app.open_animation_export_modal,
        **app._button_style(app.theme["accent_soft"])
    )
    app.export_animation_button.pack(side=tk.RIGHT)

    app.animation_status_label = tk.Label(
        animation_body,
        textvariable=app.animation_status_var,
        fg=app.theme["muted"],
        bg=app.theme["panel"],
        anchor="w",
        justify=tk.LEFT
    )
    app.animation_status_label.pack(fill=tk.X, pady=(8, 6))

    app.animation_preview_inner = tk.Frame(
        animation_body,
        bg=app.theme["panel_soft"],
        highlightbackground=app.theme["border"],
        highlightthickness=1,
        bd=0
    )
    app.animation_preview_inner.pack(fill=tk.BOTH, expand=True)

    tk.Label(
        animation_body,
        text="The panel shows the latest frames so the layout stays compact.",
        fg=app.theme["muted"],
        bg=app.theme["panel"],
        anchor="w"
    ).pack(fill=tk.X, pady=(8, 0))


def build_intensity_tab(app):
    app.intensity_tab.grid_columnconfigure(0, weight=1)
    app.intensity_frame, intensity_body = app._create_card(app.intensity_tab, "Frame Intensity", app.video_status_var)
    app.intensity_frame.grid(row=0, column=0, sticky="nsew")

    app.intensity_scroll_wrap = tk.Frame(
        intensity_body,
        bg=app.theme["panel_soft"],
        highlightbackground=app.theme["border"],
        highlightthickness=1,
        bd=0,
    )
    app.intensity_scroll_wrap.pack(fill=tk.BOTH, expand=True)

    app.intensity_canvas = tk.Canvas(
        app.intensity_scroll_wrap,
        bg=app.theme["panel_soft"],
        highlightthickness=0,
        bd=0,
        relief=tk.FLAT,
    )
    app.intensity_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    app.intensity_scrollbar = tk.Scrollbar(
        app.intensity_scroll_wrap,
        orient=tk.VERTICAL,
        command=app.intensity_canvas.yview,
    )
    app.intensity_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    app.intensity_canvas.configure(yscrollcommand=app.intensity_scrollbar.set)

    app.intensity_inner = tk.Frame(app.intensity_canvas, bg=app.theme["panel_soft"])
    app.intensity_window_id = app.intensity_canvas.create_window((0, 0), window=app.intensity_inner, anchor="nw")

    app.intensity_inner.bind(
        "<Configure>",
        lambda _event: app.intensity_canvas.configure(scrollregion=app.intensity_canvas.bbox("all")),
    )
    app.intensity_canvas.bind(
        "<Configure>",
        lambda event: app.intensity_canvas.itemconfigure(app.intensity_window_id, width=event.width),
    )

    tk.Label(
        intensity_body,
        text="Each active effect can vary over time for video frames.",
        fg=app.theme["muted"],
        bg=app.theme["panel"],
        anchor="w",
    ).pack(fill=tk.X, pady=(8, 0))

    app._refresh_video_intensity_controls(force=True)


def build_palette_tab(app):
    app.palette_tab.grid_columnconfigure(0, weight=1)
    app.palette_frame, palette_body = app._create_card(app.palette_tab, "Palette", app.palette_status_var)
    app.palette_frame.grid(row=0, column=0, sticky="nsew")

    app.palette_count_slider = app._create_compact_slider(
        palette_body,
        "Color Count",
        2,
        24,
        app.update_palette_count,
        initial=8,
    )

    format_row = tk.Frame(palette_body, bg=app.theme["panel"])
    format_row.pack(fill=tk.X, pady=(0, 6))
    tk.Label(format_row, text="Format", fg=app.theme["text"], bg=app.theme["panel"], anchor="w").pack(anchor="w")
    app.palette_format_menu = tk.OptionMenu(
        format_row,
        app.palette_format_var,
        "PNG Image (1x)",
        "PNG Image (8x)",
        "PNG Image (32x)",
        "PAL File (JASC)",
        "Photoshop ASE",
        "Paint.net TXT",
        "GIMP GPL",
        "HEX File",
    )
    app._style_option_menu(app.palette_format_menu)
    app.palette_format_menu.pack(fill=tk.X, pady=(4, 0))

    sort_row = tk.Frame(palette_body, bg=app.theme["panel"])
    sort_row.pack(fill=tk.X, pady=(0, 8))
    tk.Label(sort_row, text="Sort Colors", fg=app.theme["text"], bg=app.theme["panel"], anchor="w").pack(anchor="w")
    app.palette_sort_menu = tk.OptionMenu(
        sort_row,
        app.palette_sort_var,
        "Frequency",
        "Hue",
        "Brightness",
        command=app.update_palette_display,
    )
    app._style_option_menu(app.palette_sort_menu)
    app.palette_sort_menu.pack(fill=tk.X, pady=(4, 0))

    app.extract_palette_button = tk.Button(
        palette_body,
        text="Extract Palette",
        command=app.extract_palette_from_preview,
        **app._button_style(app.theme["accent_soft"])
    )
    app.extract_palette_button.pack(fill=tk.X, pady=(0, 6))

    app.save_palette_button = tk.Button(
        palette_body,
        text="Save Palette As",
        command=app.save_palette_as,
        **app._button_style(app.theme["button_alt"])
    )
    app.save_palette_button.pack(fill=tk.X, pady=(0, 10))

    preview_label = tk.Label(
        palette_body,
        text="Preview (click a swatch to copy HEX)",
        fg=app.theme["text"],
        bg=app.theme["panel"],
        anchor="w"
    )
    preview_label.pack(fill=tk.X)

    app.palette_preview_inner = tk.Frame(
        palette_body,
        bg=app.theme["panel_soft"],
        highlightbackground=app.theme["panel_soft"],
        highlightthickness=0,
        bd=0
    )
    app.palette_preview_inner.pack(fill=tk.X, pady=(4, 10))

    values_label = tk.Label(
        palette_body,
        text="Palette Values",
        fg=app.theme["text"],
        bg=app.theme["panel"],
        anchor="w"
    )
    values_label.pack(fill=tk.X)

    app.palette_values_text = tk.Text(
        palette_body,
        height=12,
        wrap=tk.WORD,
        bg=app.theme["field"],
        fg=app.theme["text"],
        insertbackground=app.theme["text"],
        relief=tk.FLAT,
        highlightthickness=1,
        highlightbackground=app.theme["field_border"],
        highlightcolor=app.theme["accent"],
        bd=0,
        padx=10,
        pady=10,
    )
    app.palette_values_text.pack(fill=tk.BOTH, expand=True)
    app.palette_values_text.configure(state=tk.DISABLED)
    app._reset_palette_output()


def build_batch_tab(app):
    app.batch_tab.grid_columnconfigure(0, weight=1)

    app.batch_frame, batch_body = app._create_card(app.batch_tab, "Batch Processing")
    app.batch_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))

    tk.Label(
        batch_body,
        text="Apply current glitch settings to every image in a folder.",
        fg=app.theme["muted"],
        bg=app.theme["panel"],
        anchor="w",
        wraplength=320,
        justify=tk.LEFT,
    ).pack(fill=tk.X, pady=(0, 8))

    folder_row = tk.Frame(batch_body, bg=app.theme["panel"])
    folder_row.pack(fill=tk.X, pady=(0, 6))
    folder_row.grid_columnconfigure(1, weight=1)

    app.batch_browse_button = tk.Button(
        folder_row,
        text="Browse",
        command=app.batch_browse_folder,
        **app._button_style(app.theme["button"]),
    )
    app.batch_browse_button.grid(row=0, column=0, padx=(0, 6))

    tk.Label(
        folder_row,
        textvariable=app.batch_folder_var,
        fg=app.theme["muted"],
        bg=app.theme["panel"],
        anchor="w",
    ).grid(row=0, column=1, sticky="ew")

    app.batch_run_button = tk.Button(
        batch_body,
        text="Run Batch",
        command=app.run_batch_processing,
        **app._button_style(app.theme["accent_soft"]),
    )
    app.batch_run_button.pack(fill=tk.X, pady=(4, 6))

    app.batch_progress_bar = ttk.Progressbar(
        batch_body,
        variable=app.batch_progress_var,
        maximum=100,
        mode="determinate",
    )
    app.batch_progress_bar.pack(fill=tk.X, pady=(0, 6))

    tk.Label(
        batch_body,
        textvariable=app.batch_status_var,
        fg=app.theme["muted"],
        bg=app.theme["panel"],
        anchor="w",
        justify=tk.LEFT,
        wraplength=320,
    ).pack(fill=tk.X)
