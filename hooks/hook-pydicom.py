from PyInstaller.utils.hooks import (
    collect_submodules,
    collect_data_files,
    collect_dynamic_libs,
)

# --- pydicom: dynamic imports and data ---
hiddenimports = []
# pixel pipeline (dynamic)
hiddenimports += collect_submodules("pydicom.pixels")
hiddenimports += collect_submodules("pydicom.pixels.decoders")
hiddenimports += collect_submodules("pydicom.encaps")

# encoders (NEW) -> this is where pydicom.encoders.gdcm lives
hiddenimports += collect_submodules("pydicom.encoders")
# be explicit too (helps some PyInstaller versions)
hiddenimports += ["pydicom.encoders.gdcm"]

# package data (urls.json etc.)
datas = collect_data_files("pydicom", includes=["data/*"])

# --- python-gdcm package (module name 'gdcm') ---
# bring the package, plus its DLLs
hiddenimports += collect_submodules("gdcm")
binaries = collect_dynamic_libs("gdcm")           # .dll/.pyd
# (package has no extra data files normally, but safe to include)
datas += collect_data_files("gdcm", include_py_files=False)
