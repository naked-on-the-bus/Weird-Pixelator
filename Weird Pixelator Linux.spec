# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import copy_metadata


APP_NAME = 'Weird Pixelator'
METADATA_DATAS = copy_metadata('imageio') + copy_metadata('imageio-ffmpeg') + copy_metadata('Pillow') + copy_metadata('imageconvert')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=METADATA_DATAS,
    hiddenimports=['PIL._tkinter_finder', 'PIL.ImageTk'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)
