from PyInstaller.utils.hooks import collect_dynamic_libs

# Collect dynamic libraries for bm4d
binaries = collect_dynamic_libs('bm4d')