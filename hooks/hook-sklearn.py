# hooks/hook-sklearn.py
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Pull in all dynamically imported subpackages (incl. externals/array_api_compat)
hiddenimports = collect_submodules('sklearn')
# Include any non-.py resources scikit-learn needs
datas = collect_data_files('sklearn', include_py_files=False)