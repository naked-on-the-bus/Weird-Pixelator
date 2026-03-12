#!/usr/bin/env zsh
set -euo pipefail

cd "$(dirname "$0")/.."

python_bin="${PYTHON_BIN:-./.venv/bin/python}"
icon_png="icon.png"
iconset_dir="assets/icon.iconset"
icon_icns="assets/icon.icns"

if [[ ! -x "$python_bin" ]]; then
  echo "Python executable not found: $python_bin" >&2
  exit 1
fi

"$python_bin" -m pip install -r requirements-build.txt
"$python_bin" -c "import tkinter; import numpy; import imageio; import imageio_ffmpeg; from PIL import Image, ImageTk"

if [[ ! -f "$icon_png" ]]; then
  echo "Missing icon source: $icon_png" >&2
  exit 1
fi

if ! command -v sips >/dev/null 2>&1; then
  echo "sips is required to build the macOS icon." >&2
  exit 1
fi

if ! command -v iconutil >/dev/null 2>&1; then
  echo "iconutil is required to build the macOS icon." >&2
  exit 1
fi

rm -rf "$iconset_dir"
mkdir -p "$iconset_dir"

sips -z 16 16     "$icon_png" --out "$iconset_dir/icon_16x16.png" >/dev/null
sips -z 32 32     "$icon_png" --out "$iconset_dir/icon_16x16@2x.png" >/dev/null
sips -z 32 32     "$icon_png" --out "$iconset_dir/icon_32x32.png" >/dev/null
sips -z 64 64     "$icon_png" --out "$iconset_dir/icon_32x32@2x.png" >/dev/null
sips -z 128 128   "$icon_png" --out "$iconset_dir/icon_128x128.png" >/dev/null
sips -z 256 256   "$icon_png" --out "$iconset_dir/icon_128x128@2x.png" >/dev/null
sips -z 256 256   "$icon_png" --out "$iconset_dir/icon_256x256.png" >/dev/null
sips -z 512 512   "$icon_png" --out "$iconset_dir/icon_256x256@2x.png" >/dev/null
sips -z 512 512   "$icon_png" --out "$iconset_dir/icon_512x512.png" >/dev/null
cp "$icon_png" "$iconset_dir/icon_512x512@2x.png"

iconutil -c icns "$iconset_dir" -o "$icon_icns"
"$python_bin" -m PyInstaller --noconfirm "Weird Pixellator.spec"

echo
echo "Build complete: dist/Weird Pixelator.app"
