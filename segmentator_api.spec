# -*- mode: python ; coding: utf-8 -*-

import os, sys, sysconfig
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

block_cipher = None

# --- site-packages path for this env ---
SITE_PKGS = []
try:
    p = sysconfig.get_paths().get("purelib")
    if p and os.path.isdir(p): SITE_PKGS.append(p)
except Exception:
    pass
cp = os.environ.get("CONDA_PREFIX")
if cp:
    sp = os.path.join(cp, "Lib", "site-packages")
    if os.path.isdir(sp) and sp not in SITE_PKGS:
        SITE_PKGS.append(sp)

# --- packages to sweep ---
BASE_PKGS = [
    # API
    "fastapi","starlette","uvicorn","h11","anyio","sniffio","pydantic",
    "typing_extensions","python_multipart",
    # Segmentation stack
    "totalsegmentator","nnunet","nnunetv2","monai","torch","torchvision",
    # Imaging
    "nibabel","SimpleITK","scipy","skimage","tqdm","einops","packaging",
    # DICOM/NIfTI
    "pydicom","dicom2nifti",
    # misc
    "filelock","requests","yaml","numpy",
]

hiddenimports, datas, binaries = [], [], []

for pkg in BASE_PKGS:
    try: hiddenimports += collect_submodules(pkg)
    except Exception: pass

# pydicom dynamic bits
for extra in ["pydicom.encaps","pydicom.pixels","pydicom.pixels.decoders"]:
    try: hiddenimports += collect_submodules(extra)
    except Exception: pass

# data files (non-.py) for big libs
for pkg in ["totalsegmentator","nnunet","nnunetv2","monai","torch","torchvision",
            "skimage","SimpleITK","nibabel"]:
    try: datas += collect_data_files(pkg, include_py_files=False)
    except Exception: pass

# explicit native libraries (helps PyTorch/SimpleITK)
for pkg in ["torch","torchvision","SimpleITK"]:
    try: binaries += collect_dynamic_libs(pkg)
    except Exception: pass

a = Analysis(
    ['segmentator_api/segmentator_api.py'],
    pathex=['segmentator_api'] + SITE_PKGS,
    binaries=binaries,              # <— include DLLs
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas,
    name='segmentator_api',
    debug=False, bootloader_ignore_signals=False,
    strip=False, upx=False, console=True,
    disable_windowed_traceback=False, target_arch=None,
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=False, upx_exclude=[],
    name='segmentator_api',
)
