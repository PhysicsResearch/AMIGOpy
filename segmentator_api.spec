# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# -------------------------------
# Hidden imports for your stack
# -------------------------------
BASE_PKGS = [
    # your app stack
    "fastapi", "starlette", "uvicorn", "h11", "anyio", "sniffio", "pydantic",
    "typing_extensions", "python_multipart",

    # TS + nnUNet/Monai + friends
    "totalsegmentator", "nnunet", "nnunetv2", "monai", "torch", "torchvision",
    "nibabel", "SimpleITK", "scipy", "skimage", "tqdm", "einops", "packaging",

    # DICOM/NIfTI toolchain
    "pydicom", "dicom2nifti",

    # often pulled at runtime by subpackages
    "filelock", "requests", "yaml", "numpy",
]

hiddenimports = []
for pkg in BASE_PKGS:
    try:
        hiddenimports += collect_submodules(pkg)
    except Exception:
        pass

# Pydicom’s pixel pipelines sometimes need explicit submodules
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
        # include package data (e.g., resources, DLLs shipped as data, configs)
        datas += collect_data_files(pkg, include_py_files=False)
    except Exception:
        pass

# If you want to ship pre-downloaded TS models, uncomment and adjust:
# models_dir = r"C:\Models\TotalSegmentator"
# if os.path.isdir(models_dir):
#     # they'll end up under: <dist>/segmentator_api/models/TotalSegmentator
#     datas += [(models_dir, "models/TotalSegmentator")]

a = Analysis(
    ['segmentator_api/segmentator_api.py'],   # adjust path if needed
    pathex=['segmentator_api'],               # folder containing the script
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],     # torch/monai hooks are built-in
    hooksconfig={},
    runtime_hooks=['runtime_hooks/set_env.py'],  # <— see hook below
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
    console=True,  # False if you want a windowless build
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
