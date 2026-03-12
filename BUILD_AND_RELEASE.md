# Weird Pixelator – Build and itch.io Release Guide

It is a small desktop Python app with only a few dependencies:

- `tkinter`
- `Pillow`
- `numpy`

That makes native packaging realistic with `PyInstaller`.

---

## Current state of the app

### What is already good

- The app starts successfully.
- The codebase is small and easy to package.
- There are no current Python analysis errors.
- A `PyInstaller` spec file already exists.

### What needed attention

- Windows path handling used `/` splitting instead of `os.path.basename()`.
- There was no dependency manifest for reproducible builds.
- There was no release guide for platform builds and itch.io upload.

These have now been addressed.

---

## Important packaging rule

Build each platform on that platform.

In practice:

- build Windows on Windows
- build macOS on macOS
- build Linux on Linux

Do not rely on cross-compiling desktop Python apps from one OS to another.

---

## Recommended distribution format for itch.io

### Windows

Recommended:

- zipped folder containing `Weird Pixelator.exe`

Optional later:

- installer made with Inno Setup or NSIS

### macOS

Recommended:

- zipped `Weird Pixelator.app`

Best user experience:

- sign and notarize the app before release

### Linux

Recommended:

- tar.gz containing the packaged app folder

Nice upgrade later:

- AppImage

---

## Build setup

Create a clean virtual environment on each target OS, then install build dependencies:

```bash
pip install -r requirements-build.txt
```

For local app runtime (not packaging), install runtime dependencies with:

```bash
pip install -r requirements.txt
```

---

## GitHub release pipeline (all platforms)

The repository includes a GitHub Actions workflow at `.github/workflows/build-release.yml`.

It supports:

- tag-triggered releases on push of tags matching `v*` (for example `v1.2`)
- manual releases via `workflow_dispatch` with `version` input (default `1.2`)

### CI artifact layout

Each platform job normalizes outputs into platform folders and versioned filenames:

- `dist/Windows/Weird Pixelator Windows v1.2.zip`
- `dist/Mac/Weird Pixelator Mac v1.2.zip`
- `dist/Linux/Weird Pixelator Linux v1.2.tar.gz`

The `release` job publishes those files as GitHub Release assets.

---

## Example PyInstaller commands

Use these from the project root. Prefer the build scripts below — these are shown for reference only.

### Windows

```powershell
pyinstaller --noconfirm --windowed --icon icon.ico --name "Weird Pixelator" main.py
```

Use the build script instead:

```powershell
.\scripts\build_windows.ps1
```

Output to upload:

- local script output: `dist\Weird Pixelator Windows.zip`
- CI/release output: `dist/Windows/Weird Pixelator Windows v<version>.zip`

### macOS

Use the build script:

```bash
./scripts/build_macos.sh
```

Output to upload:

- local script output: `dist/Weird Pixelator.app` (zip manually if needed)
- CI/release output: `dist/Mac/Weird Pixelator Mac v<version>.zip`

If you want lower Gatekeeper friction, sign and notarize it.

### Linux

```bash
pyinstaller --noconfirm --windowed --name "Weird Pixelator" --copy-metadata imageio --copy-metadata imageio-ffmpeg main.py
```

Output to upload:

- local script output: `dist/Weird Pixelator Linux.tar.gz`
- CI/release output: `dist/Linux/Weird Pixelator Linux v<version>.tar.gz`

---

## itch.io upload workflow

For the best install experience, use the itch.io app with platform-specific uploads.

### Option A: manual upload in browser

Upload separate files for:

- Windows
- macOS
- Linux

Mark each upload for its platform.

### Option B: Butler CLI

Recommended for updates.

Typical channels:

- `yourname/weird-pixelator:windows`
- `yourname/weird-pixelator:mac`
- `yourname/weird-pixelator:linux`

Example:

```bash
butler push "dist/Weird Pixelator" yourname/weird-pixelator:windows
```

On macOS, push the zipped `.app` or a prepared release artifact.

---

## Release checklist

Before publishing:

- verify image upload works
- verify save works
- verify randomize works
- verify blend image works
- verify one export on each OS
- include a small README for players
- include an icon for the executable/app
- keep the checked-in source icon as icon.png
- keep the visible app name consistent: `Weird Pixelator`

Recommended next improvements:

- add an application icon
- standardize the spelling of `Pixelator` vs `Pixellator`
- add version metadata
- sign/notarize the macOS app
- optionally create a real Windows installer
- optionally build an AppImage for Linux

---

## Practical recommendation

For the first public itch.io release, use this approach:

1. Package with `PyInstaller`.
2. Build separately on Windows, macOS, and Linux.
3. Upload one artifact per platform to itch.io.
4. Use Butler for future updates.

That is the fastest reliable path.