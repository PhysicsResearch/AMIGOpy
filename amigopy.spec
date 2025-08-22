# -*- mode: python ; coding: utf-8 -*-

import os, sys, sysconfig
from PyInstaller.utils.hooks import (
    collect_submodules, collect_data_files, collect_dynamic_libs
)

block_cipher = None

# ── Base dir ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.getcwd())
os.chdir(BASE_DIR)

# ── Shared data files (icons, csv, etc.) for the GUI ──────────────────────────
gui_datas = [
    (os.path.join(BASE_DIR, 'icons', 'ruler.png'),               'icons'),
    (os.path.join(BASE_DIR, 'icons', 'dcm_insp.png'),            'icons'),
    (os.path.join(BASE_DIR, 'icons', 'brush.png'),               'icons'),
    (os.path.join(BASE_DIR, 'icons', 'eraser.png'),              'icons'),
    (os.path.join(BASE_DIR, 'icons', 'layout.png'),              'icons'),
    (os.path.join(BASE_DIR, 'icons', 'roi_point.png'),           'icons'),
    (os.path.join(BASE_DIR, 'icons', 'roi_circle.png'),          'icons'),
    (os.path.join(BASE_DIR, 'icons', 'roi_ellipse.png'),         'icons'),
    (os.path.join(BASE_DIR, 'icons', 'roi_square.png'),          'icons'),
    (os.path.join(BASE_DIR, 'icons', 'undo.png'),                'icons'),
    ('fcn_materialassignment/materials_db.csv',                   'fcn_materialassignment'),
    ('fcn_ctcal/ct_cal_curves',                                  'fcn_ctcal/ct_cal_curves'),
]

# ── Scripts ───────────────────────────────────────────────────────────────────
GUI_SCRIPT = os.path.join(BASE_DIR, 'Launch_ImGUI.py')
WORKER_SCRIPT = os.path.join(BASE_DIR, 'fcn_autocont', 'ts_worker_entry.py')

# ── GUI Analysis (slim: exclude TS stack) ─────────────────────────────────────
a_gui = Analysis(
    [GUI_SCRIPT],
    pathex=[BASE_DIR],
    binaries=[],
    datas=gui_datas,
    hiddenimports=[],
    hookspath=[os.path.join(BASE_DIR, 'hooks')],
    runtime_hooks=[],
    excludes=[
        # Keep GUI lean: exclude segmentation stack & web servers
        'totalsegmentator',
        'torch', 'torchvision',
        'monai',
        'nnunet', 'nnunetv2',
        'einops',
        'tqdm',
        'fastapi', 'starlette', 'uvicorn', 'pydantic',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz_gui = PYZ(a_gui.pure, a_gui.zipped_data, cipher=block_cipher)

exe_gui = EXE(
    pyz_gui,
    a_gui.scripts,
    [],
    exclude_binaries=False,
    name='Launch_ImGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # GUI app
)

# ── Worker Analysis (heavy: include TS stack) ─────────────────────────────────
# Packages to sweep for hidden imports / data / DLLs
BASE_PKGS = [
    # Segmentation stack
    "totalsegmentator","nnunet","nnunetv2","monai","torch","torchvision",
    # Imaging
    "nibabel","SimpleITK","scipy","skimage","tqdm","einops","packaging",
    # DICOM/NIfTI
    "pydicom","dicom2nifti",
    # misc
    "filelock","requests","yaml","numpy",
]

hiddenimports, worker_datas, worker_bins = [], [], []

for pkg in BASE_PKGS:
    try:
        hiddenimports += collect_submodules(pkg)
    except Exception:
        pass

# pydicom dynamic bits
for extra in ["pydicom.encaps","pydicom.pixels","pydicom.pixels.decoders"]:
    try:
        hiddenimports += collect_submodules(extra)
    except Exception:
        pass

# non-.py data
for pkg in ["totalsegmentator","nnunet","nnunetv2","monai","torch","torchvision",
            "skimage","SimpleITK","nibabel"]:
    try:
        worker_datas += collect_data_files(pkg, include_py_files=False)
    except Exception:
        pass

# DLLs (torch, SimpleITK)
for pkg in ["torch","torchvision","SimpleITK"]:
    try:
        worker_bins += collect_dynamic_libs(pkg)
    except Exception:
        pass

a_ts = Analysis(
    [WORKER_SCRIPT],
    pathex=[BASE_DIR],
    binaries=worker_bins,
    datas=worker_datas,
    hiddenimports=hiddenimports,
    hookspath=[os.path.join(BASE_DIR, 'hooks')],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz_ts = PYZ(a_ts.pure, a_ts.zipped_data, cipher=block_cipher)

exe_ts = EXE(
    pyz_ts,
    a_ts.scripts,
    a_ts.binaries,
    a_ts.zipfiles,
    a_ts.datas,
    name='segmentator_worker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,   # console is fine for logs
)

# ── Single output folder containing BOTH executables ──────────────────────────
coll = COLLECT(
    exe_gui, exe_ts,
    a_gui.binaries, a_gui.zipfiles, a_gui.datas,
    a_ts.binaries,  a_ts.zipfiles,  a_ts.datas,
    strip=False, upx=False, upx_exclude=[],
    name='AMIGOpy',       # dist/AMIGOpy with both EXEs + shared libs
)
