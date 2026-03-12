# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import copy_metadata


APP_NAME = 'Weird Pixelator'
APP_VERSION = '1.1'
BUNDLE_IDENTIFIER = 'io.itch.weirdpixelator'
ICON_PATH = str(Path(SPECPATH) / 'assets' / 'icon.icns')
INFO_PLIST = {
    'CFBundleDisplayName': APP_NAME,
    'CFBundleName': APP_NAME,
    'CFBundleIdentifier': BUNDLE_IDENTIFIER,
    'CFBundleShortVersionString': APP_VERSION,
    'CFBundleVersion': APP_VERSION,
    'NSHighResolutionCapable': True,
    'LSApplicationCategoryType': 'public.app-category.graphics-design',
}

DIST_METADATA = []
for dist_name in ('imageio', 'imageio-ffmpeg', 'Pillow'):
    try:
        DIST_METADATA += copy_metadata(dist_name)
    except Exception:
        pass


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=DIST_METADATA,
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
    icon=ICON_PATH,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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
app = BUNDLE(
    coll,
    name=f'{APP_NAME}.app',
    icon=ICON_PATH,
    bundle_identifier=BUNDLE_IDENTIFIER,
    info_plist=INFO_PLIST,
)
