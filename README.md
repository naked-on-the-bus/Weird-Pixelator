# Weird Pixelator

Weird Pixelator is a desktop image tool for glitch art, color manipulation, blending, CRT effects, crop controls, retro export compression, and simple frame-by-frame animation export.

## Features

- pixelation and glitch effects
- color controls and invert
- CRT-style post-processing
- four-edge crop with live size readout and presets
- blend image overlay
- save/export with retro compression profiles
- frame capture strip with GIF, MP4, and animated WebP export
- randomized effect generation

## Run locally

1. Create or activate a Python environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Start the app:
   - `python main.py`

## Build Windows app

Use the included build script from PowerShell:

- `.\scripts\build_windows.ps1`

The script uses the checked-in source icon:

- `icon.ico`

The packaged app and a ready-to-upload zip are created in `dist/`.

## Build macOS app

Use the included build script:

- `./scripts/build_macos.sh`

The script uses the checked-in source icon:

- `icon.png`

The packaged app is created in `dist/`.

## Cut release v1.2 (GitHub Actions)

Use `.github/workflows/build-release.yml` to build and publish all platforms.

1. Commit and push your changes to `main`.
2. Trigger one of these:
   - push tag `v1.2` (example: `git tag v1.2 && git push origin v1.2`), or
   - run **Build and Release** manually in Actions with `version = 1.2`.
3. Wait for all jobs to finish (`build-windows`, `build-macos`, `build-linux`, `release`).
4. Verify GitHub Release assets include:
   - `Weird Pixelator Windows v1.2.zip`
   - `Weird Pixelator Mac v1.2.zip`
   - `Weird Pixelator Linux v1.2.tar.gz`

In CI, artifacts are normalized under platform folders before release upload:

- `dist/Windows/`
- `dist/Mac/`
- `dist/Linux/`

## Repository hygiene

The project ignores local and generated files such as:

- `.venv/`
- `build/`
- `dist/`

## License

This project is source-available under the custom non-commercial license in
[LICENSE](LICENSE).

Commercial use and resale are not allowed without prior written permission.
