# segmentator_api.spec
# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# --- Hidden imports for TS stack ---
_pkgs = [
    "totalsegmentator",
    "nnunet",
    "monai",
    "torch",
    "torchvision",
    "nibabel",
    "SimpleITK",
    "scipy",
    "skimage",
    "tqdm",
    "einops",
    "packaging",
]
hiddenimports = []
for p in _pkgs:
    try:
        hiddenimports += collect_submodules(p)
    except Exception:
        pass

# --- Data files (non-code assets) ---
datas = []
for p in ["totalsegmentator", "nnunet", "monai", "torch", "torchvision", "skimage", "SimpleITK"]:
    try:
        datas += collect_data_files(p, include_py_files=False)
    except Exception:
        pass

# If you ship pre-downloaded models, uncomment:
# models_dir = r"C:\Models\TotalSegmentator"
# if os.path.isdir(models_dir):
#     datas += [(models_dir, "models/TotalSegmentator")]

a = Analysis(
    ['segmentator_api/segmentator_api.py'],   # <-- adjust if your path is different
    pathex=['segmentator_api'],               # <-- folder containing the script
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],     # default hooks include torch/monai
    hooksconfig={},
    runtime_hooks=[],
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
    console=True,  # set False if you want no console window
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
