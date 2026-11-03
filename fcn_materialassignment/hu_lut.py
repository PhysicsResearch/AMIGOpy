# -*- coding: utf-8 -*-
"""
hu_lut.py - Material assignment helpers
=======================================

* Shows the HU range of the currently selected image series in the
  Material assignment tab (info box at the bottom).
* HU look-up tables (HU LUT): lists of (Material, From HU, To HU) picked in
  the dropdown above the HU table, so the HU ranges don't have to be typed
  every time. One CSV per LUT in %LOCALAPPDATA%\\AMIGOpy\\HU_LUTs (file name =
  LUT name); every edit of the table is saved to the LUT shown, a Default LUT
  is created when there is none, and the last used LUT (settings.json) is
  shown at start.

HU LUT file format (CSV, with header; table order, later rows override):

    Material,From,To,Color,Fixed Density
    Air,-1024,-950,,1
    Lung-TG186,-950,-200,#ff0000,1
    ...
"""

import os
import csv

import numpy as np
from PySide6.QtWidgets import QInputDialog, QLineEdit, QMessageBox

from fcn_3DPrinting.safe_io import atomic_write_csv, atomic_write_json, read_json_safe
from fcn_materialassignment.material_map import (NONE_MAT, _fmt, _mat_names, _to_float,
                                                 update_mat2HU_table)

# Above this number of voxels, statistics are computed on a strided sample
_MAX_FULL_VOXELS = 50_000_000


# ----------------------------------------------------------------------------
# HU range of the selected series
# ----------------------------------------------------------------------------
def _selected_series(self):
    try:
        return self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]
    except Exception:
        return None


def _hu_stats(arr):
    """Return (min, max, p1, p99, mean, sampled) for a volume.

    min/max are always exact (one pass, no copy); percentiles and mean are
    computed on a strided sample for very large volumes.
    """
    arr = np.asarray(arr)
    if np.issubdtype(arr.dtype, np.floating):
        vmin, vmax = float(np.nanmin(arr)), float(np.nanmax(arr))
    else:
        vmin, vmax = float(arr.min()), float(arr.max())

    sampled = arr.size > _MAX_FULL_VOXELS
    if sampled:
        step = int(np.ceil((arr.size / _MAX_FULL_VOXELS) ** (1.0 / 3.0)))
        data = arr[::step, ::step, ::step] if arr.ndim == 3 else arr.ravel()[::step ** 3]
    else:
        data = arr
    data = np.asarray(data).ravel()
    if np.issubdtype(data.dtype, np.floating):
        data = data[np.isfinite(data)]
    if data.size == 0 or not np.isfinite(vmin):
        return None
    p1, p99 = np.percentile(data, [1, 99])
    return vmin, vmax, float(p1), float(p99), float(data.mean()), sampled


def update_series_hu_info(self, force=False):
    """Fill the info box with the HU range of the selected series.

    Only computes when the Material assignment tab is visible (or force=True);
    results are cached per series so switching tabs is instant.
    """
    lbl = getattr(self, "mat_series_hu_info", None)
    if lbl is None:
        return
    tab = getattr(self, "tab_mat_assignment", None)
    if not force and tab is not None and not tab.isVisible():
        return

    series = _selected_series(self)
    if not isinstance(series, dict) or series.get("3DMatrix") is None:
        lbl.setText("Selected series: none (select an image series in the data tree)")
        return

    arr = series["3DMatrix"]
    if not isinstance(arr, np.ndarray) or arr.size == 0:
        lbl.setText("Selected series has no image data")
        return

    cache = getattr(self, "_hu_info_cache", None)
    if cache is None:
        cache = self._hu_info_cache = {}
    key = (self.patientID, self.studyID, self.modality, self.series_index, id(arr), arr.shape)
    stats = cache.get(key)
    if stats is None:
        try:
            stats = _hu_stats(arr)
        except Exception as e:
            lbl.setText(f"Could not compute HU range: {e}")
            return
        cache.clear()          # keep only the latest series (volumes can be large)
        cache[key] = stats
    if stats is None:
        lbl.setText("Selected series has no finite values")
        return

    vmin, vmax, p1, p99, mean, sampled = stats
    s_num = series.get("SeriesNumber", self.series_index)
    desc = series.get("metadata", {}).get("SeriesDescription", "") if isinstance(series.get("metadata"), dict) else ""
    shape = " \u00d7 ".join(str(s) for s in arr.shape[::-1])
    txt = (f"Series: {self.modality} #{s_num} {desc}".rstrip() +
           f"   |   size: {shape}"
           f"   |   HU range: {vmin:.0f} \u2192 {vmax:.0f}"
           f"   |   1st\u201399th percentile: {p1:.0f} \u2192 {p99:.0f}"
           f"   |   mean: {mean:.1f}")
    if sampled:
        txt += "   (sampled)"
    if self.modality != "CT":
        txt += "   \u26a0 material map is generated from the CT modality"
    lbl.setText(txt)


# ----------------------------------------------------------------------------
# HU LUTs: saved lists of HU ranges, picked in the dropdown above the HU table
# ----------------------------------------------------------------------------
LUT_HEADER = ["Material", "From", "To", "Color", "Fixed Density"]

# Created when there is no LUT (first start); From <= HU < To, in table order
DEFAULT_LUT_NAME = "Default"
DEFAULT_LUT_ROWS = [("Air", -10000, -950),
                    ("Lung-TG186", -950, -200),
                    ("Mean adipose-TG186", -200, -30),
                    ("Water", -30, 200),
                    ("Cortical Bone-TG186", 200, 100000)]

_BAD_NAME_CHARS = set('<>:"/\\|?*')
_RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL"} | {f"{d}{i}" for d in ("COM", "LPT") for i in range(1, 10)}


def _lut_dir():
    from fcn_materialassignment.material_assignment_properties import get_appdata_path
    d = os.path.join(get_appdata_path(), "HU_LUTs")
    os.makedirs(d, exist_ok=True)
    return d


def _lut_path(name):
    return os.path.join(_lut_dir(), name + ".csv")


def _settings_path():
    """settings.json in %LOCALAPPDATA%\\AMIGOpy (last used HU LUT)."""
    from fcn_materialassignment.material_assignment_properties import get_appdata_path
    return os.path.join(get_appdata_path(), "settings.json")


def _get_setting(key, default=None):
    data = read_json_safe(_settings_path(), {})
    return data.get(key, default) if isinstance(data, dict) else default


def _set_setting(key, value):
    data = read_json_safe(_settings_path(), {})
    data = data if isinstance(data, dict) else {}
    data[key] = value
    try:
        atomic_write_json(_settings_path(), data)
    except OSError as e:
        print(f"[HU LUT] could not save {_settings_path()}: {e}")


def list_luts():
    """Names of the saved HU LUTs (CSV file names without extension), sorted."""
    return sorted((f[:-4] for f in os.listdir(_lut_dir()) if f.lower().endswith(".csv")), key=str.lower)


def read_lut(path):
    """
    Rows of an HU LUT file: (material, From, To, colour, fixed density); From / To None if empty,
    colour None = automatic (material colour).
    """
    rows = []
    with open(path, "r", newline="", encoding="utf-8-sig", errors="replace") as f:
        for i, row in enumerate(csv.reader(f)):
            cells = [c.strip() for c in row] + [""] * 5
            if not cells[0] or cells[0].startswith("#") or (i == 0 and cells[0].lower() in ("material", "name")):
                continue
            color = cells[3] if cells[3].startswith("#") and len(cells[3]) in (4, 7) else None
            rows.append((cells[0], _to_float(cells[1]), _to_float(cells[2]), color,
                         cells[4].lower() not in ("0", "false", "no")))
    return tuple(rows)


def write_lut(path, rows):
    """Write HU LUT rows (as read_lut returns them); crash-safe (temporary file + replace)."""
    atomic_write_csv(path, LUT_HEADER, [[name, _fmt(lo), _fmt(hi), color or "", 1 if fixed else 0]
                                        for name, lo, hi, color, fixed in rows])


def _lut_row(d):
    """LUT row of an HU table entry (self.mat_HU_list, material map metadata)."""
    return (d.get("name") or NONE_MAT, d.get("min"), d.get("max"),
            None if d.get("color_auto", True) else d.get("color"), bool(d.get("fixed_density", True)))


def table_lut_rows(self):
    """The HU table as LUT rows."""
    return tuple(_lut_row(d) for d in getattr(self, "mat_HU_list", None) or [])


def _show_rows(self, rows):
    """Put LUT rows in the HU table (not saved); returns the materials missing from the database (set to None)."""
    names = set(_mat_names(self))
    missing = sorted({r[0] for r in rows if r[0] != NONE_MAT and r[0] not in names})
    self.mat_HU_list = [{"name": n if n in names else NONE_MAT, "key": None, "min": lo, "max": hi,
                         "fixed_density": fixed, "color": color, "color_auto": color is None, "visible": True}
                        for n, lo, hi, color, fixed in rows]
    update_mat2HU_table(self)
    self._hu_lut_saved = table_lut_rows(self)
    return missing


def _warn_missing(self, name, missing):
    if missing:
        QMessageBox.information(self, "HU LUT",
                                f"These materials of '{name}' are not in the material database; "
                                "their rows were set to None:\n" + ", ".join(missing))


def _fill_combo(self, names, current):
    """Dropdown = the saved LUTs, 'current' selected (no signals)."""
    self._hu_lut_temp = None
    combo = getattr(self, "hu_lut_combo", None)
    if combo is None:
        return
    combo.blockSignals(True)
    combo.clear()
    combo.addItems(names)
    combo.setCurrentIndex(max(0, combo.findText(current)))
    combo.blockSignals(False)


def _drop_temp_item(self):
    """Remove the dropdown entry of a material map's table (a saved LUT was chosen)."""
    label, self._hu_lut_temp = getattr(self, "_hu_lut_temp", None), None
    combo = getattr(self, "hu_lut_combo", None)
    i = combo.findText(label) if combo is not None and label else -1
    if i >= 0:
        current = combo.currentText()
        combo.blockSignals(True)
        combo.removeItem(i)
        combo.setCurrentIndex(max(0, combo.findText(current)))
        combo.blockSignals(False)


def _ensure_luts(self):
    """Names of the saved LUTs; the Default LUT is created first when there is none."""
    names = list_luts()
    if names:
        return names
    known = set(_mat_names(self))
    rows = [(n, lo, hi, None, True) for n, lo, hi in DEFAULT_LUT_ROWS if not known or n in known]
    try:
        write_lut(_lut_path(DEFAULT_LUT_NAME), rows)
    except OSError as e:
        print(f"[HU LUT] could not create the {DEFAULT_LUT_NAME} HU LUT: {e}")
        return []
    return [DEFAULT_LUT_NAME]


def _preferred_lut(names):
    """The last used LUT if it still exists, else Default, else the first."""
    last = _get_setting("hu_lut")
    if last in names:
        return last
    return DEFAULT_LUT_NAME if DEFAULT_LUT_NAME in names else names[0]


def _select(self, name):
    """Show the saved LUT 'name' (dropdown and table)."""
    _fill_combo(self, list_luts(), name)
    select_hu_lut(self, name)


def init_hu_lut_selector(self):
    """At start: fill the dropdown (Default LUT if there is none) and show the last used LUT (once)."""
    combo = getattr(self, "hu_lut_combo", None)
    if combo is None or getattr(self, "_hu_lut_ready", False):
        return
    self._hu_lut_ready = True
    combo.setToolTip(f"Saved HU LUTs ({_lut_dir()}).\nChanges in the table are saved to the LUT shown here.")
    names = _ensure_luts(self)
    if names:
        name = _preferred_lut(names)
        _fill_combo(self, names, name)
        select_hu_lut(self, name, remember=False, notify=False)


def select_hu_lut(self, name, remember=True, notify=True):
    """
    Show the saved LUT 'name' in the HU table (dropdown choice); later edits are saved to it.
    notify=False (start): materials missing from the database are only printed, not in a dialog.
    """
    if not name or name == getattr(self, "_hu_lut_temp", None):
        return
    try:
        rows = read_lut(_lut_path(name))
    except OSError as e:
        QMessageBox.warning(self, "HU LUT", f"Could not read the HU LUT '{name}':\n{e}")
        _fill_combo(self, list_luts(), getattr(self, "hu_lut_name", None) or "")
        return
    _drop_temp_item(self)
    self.hu_lut_name, self._hu_lut_unsaved = name, None
    missing = _show_rows(self, rows)
    if remember:
        _set_setting("hu_lut", name)
    if notify:
        _warn_missing(self, name, missing)
    elif missing:
        print(f"[HU LUT] '{name}': not in the material database, set to None: {', '.join(missing)}")


def autosave_hu_lut(self):
    """Save the HU table to the LUT shown, if it changed (called after every edit of the table)."""
    rows = table_lut_rows(self)
    if rows == getattr(self, "_hu_lut_saved", None):
        return
    name = getattr(self, "hu_lut_name", None)
    if name is None:
        pending = getattr(self, "_hu_lut_unsaved", None)
        if not pending:
            return
        name = _unique_name(_safe_name(pending))   # a material map's table: saved as a new LUT
    try:
        write_lut(_lut_path(name), rows)
    except OSError as e:
        print(f"[HU LUT] could not save '{name}': {e}")
        if not getattr(self, "_hu_lut_write_warned", False):
            self._hu_lut_write_warned = True
            QMessageBox.warning(self, "HU LUT", f"Could not save the HU LUT '{name}':\n{e}")
        return
    self._hu_lut_saved = rows
    if getattr(self, "hu_lut_name", None) is None:
        self.hu_lut_name, self._hu_lut_unsaved = name, None
        _fill_combo(self, list_luts(), name)
        _set_setting("hu_lut", name)


def show_map_hu_table(self, hu_table, map_name, source="material map"):
    """
    HU table of a material map (Retrieve from Map, a map clicked in the data tree) or of a saved
    project (source): the saved LUT with the same rows, else the rows under a temporary dropdown
    entry "<map_name> (<source>)"; they become a LUT named map_name at their first edit (or with
    Duplicate / Rename).
    """
    rows = tuple(_lut_row(d) for d in hu_table)
    if getattr(self, "hu_lut_combo", None) is None or not getattr(self, "_hu_lut_ready", False):
        _show_rows(self, rows)   # no LUT dropdown
        return
    current = getattr(self, "hu_lut_name", None)
    names = list_luts()
    for name in sorted(names, key=lambda n: n != current):
        try:
            same = read_lut(_lut_path(name)) == rows
        except OSError:
            continue
        if same:
            if name != current or table_lut_rows(self) != rows:
                _select(self, name)
            return
    label = f"{map_name} ({source})"
    _fill_combo(self, names, "")
    combo = self.hu_lut_combo
    combo.blockSignals(True)
    combo.insertItem(0, label)
    combo.setCurrentIndex(0)
    combo.blockSignals(False)
    self._hu_lut_temp = label
    self.hu_lut_name, self._hu_lut_unsaved = None, map_name
    _warn_missing(self, label, _show_rows(self, rows))


# ---- New / Duplicate / Rename / Delete --------------------------------------
def _safe_name(text):
    """A usable LUT (file) name made from any text (e.g. a material map name)."""
    name = "".join("_" if c in _BAD_NAME_CHARS or ord(c) < 32 else c for c in str(text))
    name = name.strip().rstrip(".")[:100].strip()
    return name if name and name.upper() not in _RESERVED_NAMES else "Material map"


def _unique_name(base):
    taken = {n.lower() for n in list_luts()}
    name, i = base, 2
    while name.lower() in taken:
        name, i = f"{base} {i}", i + 1
    return name


def _name_problem(name, ignore=None):
    """Why 'name' cannot be used for a new LUT (None if it can); 'ignore': the LUT being renamed."""
    if not name:
        return "Please type a name."
    if any(c in _BAD_NAME_CHARS or ord(c) < 32 for c in name) or name.endswith(".") \
            or name.upper() in _RESERVED_NAMES:
        return 'A name cannot contain < > : " / \\ | ? * or end with a dot.'
    if len(name) > 100:
        return "Please use a shorter name (up to 100 characters)."
    taken = {n.lower() for n in list_luts()} - {(ignore or "").lower()}
    if name.lower() in taken:
        return f"There is already an HU LUT named '{name}'."
    return None


def _ask_name(self, title, label, text, ignore=None):
    """A LUT name typed by the user (None if cancelled); asks again while it cannot be used."""
    while True:
        text, ok = QInputDialog.getText(self, title, label, QLineEdit.EchoMode.Normal, text)
        if not ok:
            return None
        name = text.strip()
        problem = _name_problem(name, ignore)
        if problem is None:
            return name
        QMessageBox.warning(self, title, problem)


def _create(self, name, rows):
    try:
        write_lut(_lut_path(name), rows)
    except OSError as e:
        QMessageBox.warning(self, "HU LUT", f"Could not save the HU LUT '{name}':\n{e}")
        return
    _select(self, name)


def new_hu_lut(self):
    """'New': an empty HU LUT, shown in the table."""
    name = _ask_name(self, "New HU LUT", "Name of the new (empty) HU LUT:", _unique_name("New LUT"))
    if name:
        _create(self, name, ())


def duplicate_hu_lut(self):
    """'Duplicate': the table shown saved as a new HU LUT (a material map's table: under the map name)."""
    pending = getattr(self, "_hu_lut_unsaved", None)
    if getattr(self, "hu_lut_name", None) is None and pending:
        title, label, text = "Save HU LUT", f"Save the HU ranges of '{pending}' as the HU LUT:", \
            _unique_name(_safe_name(pending))
    else:
        base = getattr(self, "hu_lut_name", None) or "HU LUT"
        title, label, text = "Duplicate HU LUT", f"Name of the copy of '{base}':", _unique_name(f"{base} copy")
    name = _ask_name(self, title, label, text)
    if name:
        _create(self, name, table_lut_rows(self))


def rename_hu_lut(self):
    """'Rename': rename the LUT shown (a material map's table: save it under the new name)."""
    old = getattr(self, "hu_lut_name", None)
    if old is None:
        return duplicate_hu_lut(self)
    name = _ask_name(self, "Rename HU LUT", f"New name of '{old}':", old, ignore=old)
    if not name or name == old:
        return
    try:
        if os.path.exists(_lut_path(old)):
            os.replace(_lut_path(old), _lut_path(name))
        else:
            write_lut(_lut_path(name), table_lut_rows(self))
    except OSError as e:
        QMessageBox.warning(self, "HU LUT", f"Could not rename the HU LUT '{old}':\n{e}")
        return
    self.hu_lut_name = name
    _fill_combo(self, list_luts(), name)
    _set_setting("hu_lut", name)


def delete_hu_lut(self):
    """'Delete': delete the LUT shown and show the next one (a material map's table: back to the last used LUT)."""
    name = getattr(self, "hu_lut_name", None)
    if name is None:
        names = _ensure_luts(self)
        if names:
            _select(self, _preferred_lut(names))
        return
    if QMessageBox.question(self, "Delete HU LUT", f"Delete the HU LUT '{name}'?",
                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
        return
    names = list_luts()
    i = names.index(name) if name in names else 0
    try:
        os.remove(_lut_path(name))
    except FileNotFoundError:
        pass
    except OSError as e:
        QMessageBox.warning(self, "HU LUT", f"Could not delete the HU LUT '{name}':\n{e}")
        return
    self.hu_lut_name = None          # nothing more is saved to it
    left = _ensure_luts(self)        # Default again when it was the last one
    if left:
        _select(self, left[min(i, len(left) - 1)])
    else:
        _fill_combo(self, [], "")
