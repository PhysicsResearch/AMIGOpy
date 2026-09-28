"""
Crash-safe file helpers for the 3D-printing databases.

All writers stage into a temporary file in the destination directory and then
os.replace() it, so a crash or power loss mid-save can never leave a truncated
CSV/JSON behind. Callers get exceptions (not silent prints) and decide how to
surface them.
"""

import glob
import json
import csv
import logging
import os
import re
import shutil
import tempfile
import zipfile
from datetime import datetime

logger = logging.getLogger("amigopy")


def _atomic_write(path, writer, binary=False, newline=None):
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=directory)
    try:
        if binary:
            handle = os.fdopen(fd, "wb")
        else:
            handle = os.fdopen(fd, "w", encoding="utf-8", newline=newline)
        with handle as f:
            writer(f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def atomic_write_text(path, text):
    _atomic_write(path, lambda f: f.write(text))


def atomic_write_bytes(path, data):
    _atomic_write(path, lambda f: f.write(data), binary=True)


def atomic_write_csv(path, header, rows):
    def _write(f):
        writer = csv.writer(f)
        if header is not None:
            writer.writerow(header)
        for row in rows:
            writer.writerow(row)
    _atomic_write(path, _write, newline="")


def atomic_write_json(path, obj, indent=4):
    _atomic_write(path, lambda f: json.dump(obj, f, indent=indent))


def rotate_backups(path, keep=5):
    """Keep <path>.bak1 (newest) .. <path>.bakN of the current on-disk file before it is overwritten."""
    if keep <= 0 or not os.path.exists(path):
        return
    for i in range(keep, 1, -1):
        older = f"{path}.bak{i - 1}"
        if os.path.exists(older):
            os.replace(older, f"{path}.bak{i}")
    shutil.copy2(path, f"{path}.bak1")


def read_json_safe(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except Exception:
        logger.exception("Could not read JSON file %s", path)
        return default


def safe_extract_zip(zip_path, dest_dir, allowed_names):
    """
    Extract only whitelisted database files from an archive, flattening any folder
    structure and refusing absolute or parent-relative member paths. Each file is
    written atomically. Returns the list of extracted base names.
    """
    allowed = set(allowed_names)
    extracted = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            member = info.filename.replace("\\", "/")
            parts = member.split("/")
            if member.startswith("/") or os.path.isabs(member) or ".." in parts or ":" in member:
                raise ValueError(f"Unsafe path inside archive: {info.filename}")
            base = parts[-1]
            if base not in allowed:
                continue
            atomic_write_bytes(os.path.join(dest_dir, base), zf.read(info))
            extracted.append(base)
    if not extracted:
        raise ValueError("The archive does not contain any recognised AMIGOpy 3DP database files.")
    return extracted


def snapshot_database(reason, keep=10):
    """Zip every existing database file into backups/pre_<reason>_<timestamp>.zip; returns the path or None."""
    from fcn_3DPrinting.db_paths import get_backup_dir, list_db_files

    files = list_db_files(existing_only=True)
    if not files:
        return None
    safe_reason = re.sub(r"[^A-Za-z0-9_-]+", "_", str(reason)).strip("_") or "snapshot"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = get_backup_dir()
    out_path = os.path.join(backup_dir, f"pre_{safe_reason}_{stamp}.zip")
    suffix = 2
    while os.path.exists(out_path):  # two snapshots within the same second must not overwrite each other
        out_path = os.path.join(backup_dir, f"pre_{safe_reason}_{stamp}_{suffix}.zip")
        suffix += 1
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, os.path.basename(path))
    snapshots = sorted(glob.glob(os.path.join(backup_dir, "pre_*.zip")))
    while len(snapshots) > keep:
        oldest = snapshots.pop(0)
        try:
            os.remove(oldest)
        except OSError:
            pass
    logger.info("Database snapshot written: %s", out_path)
    return out_path
