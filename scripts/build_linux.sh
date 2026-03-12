#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python_bin="${PYTHON_BIN:-./.venv/bin/python}"

if [[ ! -x "$python_bin" ]]; then
  echo "Python executable not found: $python_bin" >&2
  exit 1
fi

"$python_bin" -m PyInstaller --noconfirm --windowed --name "Weird Pixelator" main.py

cd dist
tar -czf "Weird Pixelator Linux.tar.gz" "Weird Pixelator"

echo
echo "Build complete: dist/Weird Pixelator Linux.tar.gz"
