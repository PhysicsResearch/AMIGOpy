# -*- mode: python ; coding: utf-8 -*-

import os
block_cipher = None

# ─── Base directory: where the spec is run ────────────────────────────────────
BASE_DIR = os.getcwd()
os.chdir(BASE_DIR)

# ─── Data files (icons) ───────────────────────────────────────────────────────
datas = [
    (os.path.join(BASE_DIR, 'icons', 'ruler.png'),    'icons'),
    (os.path.join(BASE_DIR, 'icons', 'ruler_remove.png'),    'icons'),
    (os.path.join(BASE_DIR, 'icons', 'dcm_insp.png'), 'icons'),
]

# ─── Entry script & pathex ────────────────────────────────────────────────────
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

# ─── Bundle into a PYZ ────────────────────────────────────────────────────────
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ─── Create the EXE (onedir mode) ─────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=False,      # <— keep your binaries external
    name='Launch_ImGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

# ─── Collect everything into dist/Launch_ImGUI ───────────────────────────────
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
)
