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

    app.controls_notebook.add(app.edit_tab, text="Adjust")
    app.controls_notebook.add(app.glitch_tab, text="Glitch")
    app.controls_notebook.add(app.finish_tab, text="Finish")
    app.controls_notebook.add(app.crop_tab, text="Crop")
    app.controls_notebook.add(app.animate_tab, text="Animate")
    app.controls_notebook.add(app.intensity_tab, text="Intensity")
    app.controls_notebook.add(app.palette_tab, text="Palette")

    app._build_adjust_tab()
    app._build_glitch_tab()
    app._build_finish_tab()
    app._build_crop_tab()
    app._build_animation_tab()
    app._build_intensity_tab()
    app._build_palette_tab()
    app._sync_media_tabs()
