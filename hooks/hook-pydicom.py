from PyInstaller.utils.hooks import collect_submodules

# Collect all submodules of pydicom
hiddenimports = collect_submodules('pydicom')