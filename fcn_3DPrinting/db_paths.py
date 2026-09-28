"""
Single source of truth for where the 3D-printing (filament / MatMix) databases live.

Every database file is a flat CSV/JSON under %LOCALAPPDATA%/AMIGOpy. All path
lookups in the 3D-printing code go through this module so the file names are
declared exactly once (the old inlined lists drifted: the whole-database export
looked for "filaments_db.csv" while the writer produced "filaments_3d_db.csv").
"""

import os

DB_DIR_NAME = "AMIGOpy"

DB_FILES = {
    "materials": "filaments_3d_db.csv",
    "material_calibration": "filaments_calibration_db.csv",
    "material_notes": "filaments_notes_db.json",
    "mixes": "filaments_mix_db.csv",
    "mix_calibration": "filaments_mix_calibration_db.csv",
    "mix_notes": "filaments_mix_notes_db.json",
    "mix_red": "filaments_mix_red_db.json",
}


def get_3dp_db_dir():
    base = os.getenv("LOCALAPPDATA", os.path.expanduser("~/AppData/Local"))
    path = os.path.join(base, DB_DIR_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def get_3dp_db_file(key):
    return os.path.join(get_3dp_db_dir(), DB_FILES[key])


def get_backup_dir():
    path = os.path.join(get_3dp_db_dir(), "backups")
    os.makedirs(path, exist_ok=True)
    return path


def list_db_files(existing_only=True):
    db_dir = get_3dp_db_dir()
    paths = [os.path.join(db_dir, name) for name in DB_FILES.values()]
    if existing_only:
        return [p for p in paths if os.path.exists(p)]
    return paths
