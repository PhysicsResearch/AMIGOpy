# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

# Force the working directory for PyInstaller
import os
os.chdir("C:/AMIGOpy")  # Change working directory to prevent Z: usage

datas = [
    ('Z:/AMIGOpy/icons/ruler.png', 'icons'),  
	('Z:/AMIGOpy/icons/dcm_insp.png', 'icons')
]

# Specify all paths explicitly
source_script = 'Z:/AMIGOpy/Launch_ImGUI.py'
build_output_dir = 'C:/AMIGOpy'

a = Analysis(
    ['Z:/AMIGOpy/Launch_ImGUI.py'],
    pathex=['Z:/AMIGOpy'],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=['Z:/AMIGOpy/hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
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
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Launch_ImGUI',
	# Specify the output folder for the build
    distpath=os.path.join(build_output_dir, 'dist'),  # Explicit distpath
    workpath=os.path.join(build_output_dir, 'build'),  # Explicit workpath
    tempdir=os.path.join(build_output_dir, 'temp')  # Explicit tempdir
)
