# Weird Pixelator

NOTE!!
For some reason the mac build doesn't work via github action, download the mac version from the itch.io page : https://naked-on-the-bus.itch.io/weird-pixellator

Weird Pixelator is a desktop glitch-art editor built with Tkinter.
It supports live preview controls for pixel effects, color work, blend overlays,
crop tools, and animation export workflows.

## Features

- Pixelate and glitch controls (row jitter, block shift, pixel sort, etc.)
- Color controls (hue shift, saturation, contrast, invert)
- Confuser controls (blur and color reducers)
- Blend image overlay workflow
- Crop tab with presets and live dimensions
- Animation workflow with frame capture and GIF / MP4 / animated WebP export
- Randomized control generation for rapid exploration

## Requirements

- Python 3.10+
- Tkinter available in the Python installation
- Runtime dependencies in `requirements.txt`
- Build dependencies in `requirements-build.txt`

## Run Locally

1. Create or activate a virtual environment.
2. Install runtime dependencies:
	- `pip install -r requirements.txt`
3. Start the app:
	- `python main.py`

## Build Artifacts

Build each platform on that platform.

- Build Windows on Windows
- Build macOS on macOS
- Build Linux on Linux

### Windows

Run:

- `./scripts/build_windows.ps1`

This script:

- installs build dependencies
- validates required imports
- generates `assets/icon.ico` from `icon.png`
- builds using `Weird Pixelator Windows.spec`
- creates `dist/Weird Pixelator Windows.zip`

### macOS

Run:

- `./scripts/build_macos.sh`

This script:

- installs build dependencies
- validates required imports
- generates `assets/icon.icns` from `icon.png`
- builds using `Weird Pixellator.spec`
- outputs `dist/Weird Pixelator.app`

### Linux

Run:

- `./scripts/build_linux.sh`

This script:

- installs build dependencies
- validates required imports
- builds using `Weird Pixelator Linux.spec`
- creates `dist/Weird Pixelator Linux.tar.gz`

## PyInstaller Spec Files

PyInstaller `.spec` files are build recipes that make packaging deterministic.
They define the entry script, artifact settings, hidden imports, and extra metadata.

This repository includes:

- `Weird Pixelator Windows.spec`
- `Weird Pixellator.spec` (macOS)
- `Weird Pixelator Linux.spec`

## GitHub Release Workflow

Workflow file:

- `.github/workflows/build-release.yml`

Current trigger:

- manual run (`workflow_dispatch`) with a required `version` input (for example `v1.2`)

Published release assets:

- `Weird Pixelator Windows.zip`
- `Weird Pixelator macOS.zip`
- `Weird Pixelator Linux.tar.gz`

## License

This project is source-available under the custom non-commercial license in `LICENSE`.
Commercial use and resale are not allowed without prior written permission.
