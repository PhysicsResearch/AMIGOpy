# segmentator_api.spec
# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# --- Hidden imports: pull in dynamic modules that TS stack uses
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

# --- Data files (be conservative; PyInstaller hooks already grab most torch bits)
datas = []
for p in ["totalsegmentator", "nnunet", "monai", "torch", "torchvision", "skimage", "SimpleITK"]:
    try:
        # Collect non-code assets (configs, resources). Avoid __pycache__.
        datas += collect_data_files(p, include_py_files=False)
    except Exception:
        pass

# If you want to ship pre-downloaded models inside the build, uncomment and point to your cache:
# models_dir = r"C:\Models\TotalSegmentator"  # your prepared model cache
# if os.path.isdir(models_dir):
#     datas += [(models_dir, "models/TotalSegmentator")]

a = Analysis(
    ['segmentator_api.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],   # torch/monai hooks come with PyInstaller
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
    console=True,            # keep console for logs; set False if you prefer windowless
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