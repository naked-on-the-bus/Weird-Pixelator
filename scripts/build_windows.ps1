#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Set-Location (Join-Path $PSScriptRoot '..')

$pythonBin  = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { '.\.venv\Scripts\python.exe' }
$iconPng    = 'icon.png'
$assetsDir  = 'assets'
$iconIco    = "$assetsDir\icon.ico"
$specFile   = 'Weird Pixelator Windows.spec'

if (-not (Test-Path $pythonBin)) {
    Write-Error "Python executable not found: $pythonBin"
    exit 1
}

& $pythonBin -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $pythonBin -c "import tkinter; import numpy; import imageio; import imageio_ffmpeg; from PIL import Image, ImageTk"
if ($LASTEXITCODE -ne 0) {
    Write-Error 'Missing required Python modules in the selected environment.'
    exit $LASTEXITCODE
}

if (-not (Test-Path $iconPng)) {
    Write-Error "Missing icon source: $iconPng"
    exit 1
}

New-Item -ItemType Directory -Force -Path $assetsDir | Out-Null

& $pythonBin -c "from PIL import Image; sizes=[16,32,48,64,128,256]; img=Image.open('icon.png').convert('RGBA'); imgs=[img.resize((s,s),Image.LANCZOS) for s in sizes]; imgs[0].save('assets/icon.ico',format='ICO',sizes=[(s,s) for s in sizes],append_images=imgs[1:])"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $pythonBin -m PyInstaller --noconfirm "$specFile"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$distFolder = 'dist\Weird Pixelator'
$zipPath    = 'dist\Weird Pixelator Windows.zip'

if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path $distFolder -DestinationPath $zipPath

Write-Host ''
Write-Host "Build complete: $zipPath"
