# -*- mode: python ; coding: utf-8 -*-

import os
block_cipher = None

# ─── 1 ─── Determine the base directory ────────────────────────────────────────
# Use the GitLab checkout dir if set, otherwise the folder containing this spec
BASE_DIR = os.getenv('CI_PROJECT_DIR',
                     os.path.abspath(os.path.dirname(__file__)))
os.chdir(BASE_DIR)

# ─── 2 ─── Data files (icons) ─────────────────────────────────────────────────
# We assume your icons live in <repo_root>/icons/
datas = [
    (os.path.join(BASE_DIR, 'icons', 'ruler.png'), 'icons'),
    (os.path.join(BASE_DIR, 'icons', 'dcm_insp.png'), 'icons'),
]

# ─── 3 ─── Source script & pathex ─────────────────────────────────────────────
script_path = os.path.join(BASE_DIR, 'Launch_ImGUI.py')

a = Analysis(
    [ script_path ],
    pathex=[ BASE_DIR ],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[ os.path.join(BASE_DIR, 'hooks') ],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ─── 4 ─── Build the PYZ and EXE objects ──────────────────────────────────────
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Launch_ImGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

# ─── 5 ─── Collect into a dist folder under the repo ─────────────────────────
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='Launch_ImGUI',
    distpath=os.path.join(BASE_DIR, 'dist'),
    workpath=os.path.join(BASE_DIR, 'build'),
    tempdir=os.path.join(BASE_DIR, 'temp'),
)
