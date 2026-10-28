# -*- coding: utf-8 -*-
"""
hu_lut.py - Material assignment helpers
=======================================

* Shows the HU range of the currently selected image series in the
  Plan > Material assignment tab (info box at the bottom).
* Save / load HU look-up tables (HU LUT): lists of
  (Material, From HU, To HU) so the HU ranges don't have to be typed
  every time.

HU LUT file format (CSV, with header):

    Material,From,To
    Air,-1024,-950
    Lung-TG186,-950,-200
    ...
"""

import os
import csv

import numpy as np
from PySide6.QtWidgets import QFileDialog, QMessageBox

from fcn_materialassignment.material_map import update_mat2HU_table, get_mat_HU_ranges

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
# HU LUT save / load
# ----------------------------------------------------------------------------
def _lut_dir():
    from fcn_materialassignment.material_assignment_properties import get_appdata_path
    d = os.path.join(get_appdata_path(), "HU_LUTs")
    os.makedirs(d, exist_ok=True)
    return d


def save_hu_lut(self):
    rows, bad = get_mat_HU_ranges(self)
    if not rows:
        QMessageBox.information(self, "Save HU LUT", "There are no valid HU ranges to save.")
        return
    path, _ = QFileDialog.getSaveFileName(self, "Save HU LUT",
                                          os.path.join(_lut_dir(), "HU_LUT.csv"),
                                          "CSV Files (*.csv)")
    if not path:
        return
    if not path.lower().endswith(".csv"):
        path += ".csv"
    try:
        with open(path, "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["Material", "From", "To", "Color", "Fixed Density"])
            # table order (later rows override); colour only if user-chosen
            for d in getattr(self, "mat_HU_list", []):
                if (d["name"] == "None" or d["key"] is None or d["min"] is None
                        or d["max"] is None or d["min"] >= d["max"]):
                    continue
                color = "" if d.get("color_auto", True) else d.get("color", "")
                fixed = 1 if d.get("fixed_density", True) else 0
                wr.writerow([d["name"], d["min"], d["max"], color, fixed])
    except Exception as e:
        QMessageBox.warning(self, "Save HU LUT", f"Could not write {path}:\n{e}")
        return
    msg = f"Saved {len(rows)} HU ranges to:\n{path}"
    if bad:
        msg += f"\n\nInvalid rows not saved: {', '.join(map(str, bad))}"
    QMessageBox.information(self, "Save HU LUT", msg)


def load_hu_lut(self):
    if getattr(self, "Mat_df", None) is None:
        QMessageBox.critical(self, "Load HU LUT", "Material database is not loaded.")
        return
    path, _ = QFileDialog.getOpenFileName(self, "Load HU LUT", _lut_dir(),
                                          "CSV Files (*.csv);;All Files (*)")
    if not path:
        return

    entries, bad_lines = [], []
    try:
        with open(path, "r", newline="") as f:
            for i, row in enumerate(csv.reader(f), start=1):
                if not row or row[0].strip().startswith("#"):
                    continue
                if i == 1 and row[0].strip().lower() in ("material", "name"):
                    continue  # header
                try:
                    name = row[0].strip()
                    lo, hi = float(row[1]), float(row[2])
                except Exception:
                    bad_lines.append(i)
                    continue
                if lo >= hi:
                    bad_lines.append(i)
                    continue
                color = row[3].strip() if len(row) > 3 else ""
                fixed_den = True
                if len(row) > 4:
                    raw_f = row[4].strip()
                    if raw_f.isdigit():
                        fixed_den = bool(int(raw_f))
                    elif raw_f.lower() in ("false", "0", "no"):
                        fixed_den = False
                entries.append((name, lo, hi, color, fixed_den))
    except Exception as e:
        QMessageBox.warning(self, "Load HU LUT", f"Could not read {path}:\n{e}")
        return

    if not entries:
        QMessageBox.warning(self, "Load HU LUT", "No valid HU ranges found in the file.")
        return

    current = [d for d in (getattr(self, "mat_HU_list", None) or [])]
    if current:
        reply = QMessageBox.question(
            self, "Load HU LUT",
            "The HU table already has rows.\n\nYes = replace them\nNo = append the loaded ranges",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
        if reply == QMessageBox.Cancel:
            return
        if reply == QMessageBox.Yes:
            current = []

    names = self.Mat_df["Name"].tolist()
    missing = []
    for name, lo, hi, color, fixed_den in entries:
        if name not in names:
            missing.append(name)
            continue
        key = self.Mat_df.index[self.Mat_df["Name"] == name][0]
        d = {"name": name, "key": key, "min": lo, "max": hi, "fixed_density": fixed_den, "visible": True}
        if color.startswith("#") and len(color) in (4, 7):
            d.update(color=color, color_auto=False)
        current.append(d)

    self.mat_HU_list = current
    update_mat2HU_table(self)

    msg = f"Loaded {len(entries) - len(missing)} HU ranges from:\n{os.path.basename(path)}"
    if missing:
        msg += ("\n\nThese materials are not in the material database and were skipped:\n"
                + ", ".join(missing))
    if bad_lines:
        msg += f"\n\nInvalid lines skipped: {', '.join(map(str, bad_lines))}"
    QMessageBox.information(self, "Load HU LUT", msg)
