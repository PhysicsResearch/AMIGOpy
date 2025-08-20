# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import sysconfig
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# ----- find site-packages of the current conda/venv (so PyInstaller sees libs) -----
SITE_PKGS = []
try:
    p = sysconfig.get_paths().get("purelib")
    if p and os.path.isdir(p):
        SITE_PKGS.append(p)
except Exception:
    pass

# also consider CONDA_PREFIX fallback
cp = os.environ.get("CONDA_PREFIX")
if cp:
    sp = os.path.join(cp, "Lib", "site-packages")
    if os.path.isdir(sp) and sp not in SITE_PKGS:
        SITE_PKGS.append(sp)

# -------------------------------
# Hidden imports for your stack
# -------------------------------
BASE_PKGS = [
    # API stack
    "fastapi", "starlette", "uvicorn", "h11", "anyio", "sniffio", "pydantic",
    "typing_extensions", "python_multipart",

    # TS + nnUNet/Monai + friends
    "totalsegmentator", "nnunet", "nnunetv2", "monai",
    "torch", "torchvision",

    "nibabel", "SimpleITK", "scipy", "skimage", "tqdm", "einops", "packaging",

    # DICOM/NIfTI toolchain
    "pydicom", "dicom2nifti",

    # sometimes needed
    "filelock", "requests", "yaml", "numpy",
]

hiddenimports = []
for pkg in BASE_PKGS:
    try:
        hiddenimports += collect_submodules(pkg)
    except Exception:
        pass

# pydicom pixel/encaps pipeline often dynamic
for extra in ["pydicom.encaps", "pydicom.pixels", "pydicom.pixels.decoders"]:
    try:
        hiddenimports += collect_submodules(extra)
    except Exception:
        pass

# -------------------------------
# Data files (non-code assets)
# -------------------------------
datas = []
for pkg in ["totalsegmentator", "nnunet", "nnunetv2", "monai", "torch", "torchvision",
            "skimage", "SimpleITK", "nibabel"]:
    try:
        datas += collect_data_files(pkg, include_py_files=False)
    except Exception:
        pass

# If you want to ship pre-downloaded TS models, uncomment and adjust:
# models_dir = r"C:\Models\TotalSegmentator"
# if os.path.isdir(models_dir):
#     datas += [(models_dir, "models/TotalSegmentator")]

a = Analysis(
    ['segmentator_api/segmentator_api.py'],   # adjust if path differs
    pathex=['segmentator_api'] + SITE_PKGS,   # <— key change: include site-packages here
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],     # torch/monai hooks are built-in
    hooksconfig={},
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='segmentator_api',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,  # False if you prefer windowless
    disable_windowed_traceback=False,
    target_arch=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='segmentator_api',
)
