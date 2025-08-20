# hooks/hook-pydicom.py
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Bring in pixel pipeline pieces that are sometimes imported dynamically
hiddenimports = []
hiddenimports += collect_submodules("pydicom.pixels")
hiddenimports += collect_submodules("pydicom.pixels.decoders")
hiddenimports += collect_submodules("pydicom.encaps")

# Include pydicom's data directory (urls.json etc.)
datas = collect_data_files("pydicom", includes=["data/*"])