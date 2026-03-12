# Weird Pixelator Build and Release Guide

This document reflects the current repository setup for local builds and GitHub releases.

## Build Rule

Build each platform on that platform.

- Windows build on Windows
- macOS build on macOS
- Linux build on Linux

## Dependencies

Runtime dependencies are pinned in `requirements.txt`:

- `numpy`
- `Pillow`
- `imageio`
- `imageio-ffmpeg`

Build dependencies are in `requirements-build.txt` (includes runtime + `pyinstaller`).

On Linux CI, `python3-tk` is installed at OS level for Tkinter.

## Build Scripts

All scripts:

- install from `requirements-build.txt`
- run a Python import smoke check before packaging

### Windows

Command:

```powershell
.\scripts\build_windows.ps1
```

Uses spec:

- `Weird Pixelator Windows.spec`

Output:

- `dist\Weird Pixelator Windows.zip`

### macOS

Command:

```bash
./scripts/build_macos.sh
```

Uses spec:

- `Weird Pixellator.spec`

Output:

- `dist/Weird Pixelator.app`

### Linux

Command:

```bash
./scripts/build_linux.sh
```

Uses spec:

- `Weird Pixelator Linux.spec`

Output:

- `dist/Weird Pixelator Linux.tar.gz`

## Why Spec Files Exist

PyInstaller spec files are explicit build recipes used to make packaging deterministic.

They define:

- entry script
- app name/icon
- metadata copied into the bundle
- hidden imports that auto-discovery may miss

This project uses them to ensure `imageio` metadata and Pillow/Tk modules are bundled correctly.

## GitHub Actions Release Flow

Workflow file:

- `.github/workflows/build-release.yml`

Trigger:

- manual `workflow_dispatch` with required `version` input (for example `v1.2`)

Jobs:

- build-windows
- build-macos
- build-linux
- release

Published release assets:

- `Weird Pixelator Windows.zip`
- `Weird Pixelator macOS.zip`
- `Weird Pixelator Linux.tar.gz`

Assets are gathered from downloaded workflow artifacts under:

- `artifacts/weird-pixelator-windows/`
- `artifacts/weird-pixelator-macos/`
- `artifacts/weird-pixelator-linux/`

## Suggested Release Checklist

- Build all three platforms from clean environments.
- Smoke-test upload/open/save on each artifact.
- Verify animation export on each artifact.
- Run the Actions release workflow with the target version.
- Validate the three release assets before publishing externally.