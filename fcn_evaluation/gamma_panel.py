# -*- coding: utf-8 -*-
"""
gamma_panel.py - Evaluation > Gamma: gamma analysis of two doses of the patient shown
=====================================================================================
Reference and evaluated dose (RTDOSE / MCNP series), 3D (volume) or 2D (the plane shown in a
view), a table of criteria (DD %, DTA mm, threshold %, global / local) filled with pass rate, mean,
95th percentile and maximum gamma and the number of points (fcn_evaluation.gamma). The gamma of the
selected criterion is saved as a new series of modality "Gamma" in the reference's study, with
the criteria, grid and reference positions, doses compared and statistics in its metadata.
The criteria and parameters are remembered (settings.json, key "gamma_panel").
"""
import time
from datetime import datetime

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QMessageBox, QProgressDialog, QTableWidgetItem

from fcn_evaluation.gamma import NOT_EVALUATED, GammaCancelled, gamma_analysis
from fcn_evaluation.isodose import (_get_setting, _layer0_geometry, _set_setting, dose_items, fill_series_combo,
                                    plane_position, resolve_series)
from fcn_processing.mc_grid import series_grid

DEFAULT_CRITERIA = ({"dd": 3.0, "dta": 3.0, "threshold": 10.0, "local": False},
                    {"dd": 2.0, "dta": 2.0, "threshold": 10.0, "local": False},
                    {"dd": 1.0, "dta": 1.0, "threshold": 10.0, "local": False})
NORMALIZATIONS = ("Global", "Local")
RESULT_COLS = (4, 5, 6, 7, 8)
PLANE_VIEWS = {"axial": "ax", "coronal": "co", "sagittal": "sa"}


# ----------------------------------------------------------------------------
# Criteria table
# ----------------------------------------------------------------------------
def _num(text):
    try:
        return float(str(text).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None


def criteria_rows(self):
    """Criteria of the table: [{'dd', 'dta', 'threshold', 'local'}] (None for a row with a bad value)."""
    table = self.gamma_table
    rows = []
    for r in range(table.rowCount()):
        vals = [_num(table.item(r, c).text()) if table.item(r, c) is not None else None for c in range(3)]
        combo = table.cellWidget(r, 3)
        if any(v is None or v < 0 for v in vals) or vals[0] <= 0 or vals[1] <= 0:
            rows.append(None)
            continue
        rows.append({"dd": vals[0], "dta": vals[1], "threshold": vals[2],
                     "local": combo is not None and combo.currentText() == "Local"})
    return rows


def _set_criteria(self, rows):
    table = self.gamma_table
    table.blockSignals(True)
    table.setRowCount(0)
    for crit in rows:
        r = table.rowCount()
        table.insertRow(r)
        for c, key in enumerate(("dd", "dta", "threshold")):
            table.setItem(r, c, QTableWidgetItem(f"{crit[key]:g}"))
        combo = QComboBox()
        combo.addItems(list(NORMALIZATIONS))
        combo.setCurrentIndex(1 if crit.get("local") else 0)
        combo.currentIndexChanged.connect(lambda _i: on_criteria_edited(self))
        table.setCellWidget(r, 3, combo)
        for c in RESULT_COLS:
            item = QTableWidgetItem("")
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            table.setItem(r, c, item)
    table.blockSignals(False)


def on_criteria_edited(self, *_):
    """Criteria changed: the results shown no longer match them."""
    self._gamma_run = None
    table = self.gamma_table
    table.blockSignals(True)
    for r in range(table.rowCount()):
        for c in RESULT_COLS:
            if table.item(r, c) is not None:
                table.item(r, c).setText("")
    table.blockSignals(False)
    _save_panel(self)


def add_criterion(self):
    rows = [r for r in criteria_rows(self) if r is not None]
    last = rows[-1] if rows else DEFAULT_CRITERIA[0]
    _set_criteria(self, rows + [dict(last)])
    self.gamma_table.selectRow(len(rows))
    on_criteria_edited(self)


def remove_criterion(self):
    r = self.gamma_table.currentRow()
    if r < 0:
        QMessageBox.information(self, "Gamma", "Select the criterion to remove.")
        return
    rows = criteria_rows(self)
    _set_criteria(self, [c for k, c in enumerate(rows) if k != r and c is not None])
    on_criteria_edited(self)


# ----------------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------------
def _panel_settings(self):
    return {"criteria": [c for c in criteria_rows(self) if c is not None],
            "mode": self.gamma_mode_combo.currentIndex(), "plane": self.gamma_plane_combo.currentIndex(),
            "norm": self.gamma_norm_combo.currentIndex(), "norm_dose": float(self.gamma_norm_spin.value()),
            "max_gamma": float(self.gamma_max_spin.value()), "fraction": int(self.gamma_fraction_spin.value()),
            "use_resolution": self.gamma_res_chk.isChecked(), "resolution": float(self.gamma_res_spin.value())}


def _save_panel(self):
    if getattr(self, "_gamma_ready", False):
        _set_setting("gamma_panel", _panel_settings(self))


def _load_panel(self):
    s = _get_setting("gamma_panel") or {}
    rows = s.get("criteria") if isinstance(s, dict) else None
    try:
        rows = [{"dd": float(c["dd"]), "dta": float(c["dta"]), "threshold": float(c["threshold"]),
                 "local": bool(c.get("local"))} for c in rows] if rows else None
    except (KeyError, TypeError, ValueError):
        rows = None
    _set_criteria(self, rows or [dict(c) for c in DEFAULT_CRITERIA])
    if not isinstance(s, dict):
        return
    for widget, key, kind in ((self.gamma_mode_combo, "mode", int), (self.gamma_plane_combo, "plane", int),
                              (self.gamma_norm_combo, "norm", int), (self.gamma_norm_spin, "norm_dose", float),
                              (self.gamma_max_spin, "max_gamma", float), (self.gamma_fraction_spin, "fraction", int),
                              (self.gamma_res_spin, "resolution", float)):
        if key in s:
            try:
                value = kind(s[key])
            except (TypeError, ValueError):
                continue
            if isinstance(widget, QComboBox):
                widget.setCurrentIndex(max(0, min(widget.count() - 1, value)))
            else:
                widget.setValue(value)
    self.gamma_res_chk.setChecked(bool(s.get("use_resolution", False)))


def _update_enabled(self):
    self.gamma_plane_combo.setEnabled(self.gamma_mode_combo.currentIndex() == 1)
    self.gamma_norm_spin.setEnabled(self.gamma_norm_combo.currentIndex() == 1)
    self.gamma_res_spin.setEnabled(self.gamma_res_chk.isChecked())


def refresh_gamma_combos(self):
    items = dose_items(self)
    fill_series_combo(self, self.gamma_ref_combo, items, "(choose the reference dose)")
    fill_series_combo(self, self.gamma_eval_combo, items, "(choose the evaluated dose)")


# ----------------------------------------------------------------------------
# Run and save
# ----------------------------------------------------------------------------
def plane_dicom_position(self, plane):
    """DICOM mm along the normal of the plane shown in a view (z axial, y coronal, x sagittal), None without image."""
    geom0 = _layer0_geometry(self)
    if geom0 is None:
        return None
    (x0, y0, z0), (_, psr0, _), (_, nr0, _) = geom0
    world = plane_position(self, PLANE_VIEWS[plane])
    if plane == "axial":
        return z0 + world
    if plane == "coronal":
        return y0 + (nr0 - 1) * psr0 - world       # layer 0 rows are stored flipped
    return x0 + world


def _series_info(self, key, series):
    import json
    meta = series.get("metadata") or {}
    pid, sid, modality, k = json.loads(key)
    dcm = meta.get("DCM_Info")
    uid = meta.get("SeriesInstanceUID") or getattr(dcm, "SeriesInstanceUID", None)
    return {"description": meta.get("SeriesDescription") or f"{modality} {series.get('SeriesNumber', k + 1)}",
            "modality": modality, "patient": pid, "study": sid, "index": k,
            "SeriesInstanceUID": None if uid is None else str(uid),
            "SeriesNumber": series.get("SeriesNumber"), "DoseUnits": meta.get("DoseUnits")}


def run_gamma(self):
    """'Run': gamma of the evaluated dose against the reference for every criterion of the table."""
    ref_key, eval_key = self.gamma_ref_combo.currentData(), self.gamma_eval_combo.currentData()
    ref, ev = resolve_series(self, ref_key), resolve_series(self, eval_key)
    if ref is None or ev is None:
        QMessageBox.warning(self, "Gamma", "Choose the reference and the evaluated dose.")
        return None
    rows = criteria_rows(self)
    if not rows or any(r is None for r in rows):
        QMessageBox.warning(self, "Gamma", "Every criterion needs DD > 0 %, DTA > 0 mm and a threshold >= 0 %.")
        return None
    plane = None
    position = None
    if self.gamma_mode_combo.currentIndex() == 1:
        plane = self.gamma_plane_combo.currentText().lower()
        position = plane_dicom_position(self, plane)
        if position is None:
            QMessageBox.warning(self, "Gamma", "2D gamma: show an image to choose the plane.")
            return None
    params = {"plane": plane, "plane_position": position,
              "resolution": float(self.gamma_res_spin.value()) if self.gamma_res_chk.isChecked() else None,
              "norm_dose": float(self.gamma_norm_spin.value()) if self.gamma_norm_combo.currentIndex() == 1 else None,
              "max_gamma": float(self.gamma_max_spin.value()), "fraction": int(self.gamma_fraction_spin.value())}
    prog = QProgressDialog("Gamma...", "Cancel", 0, 1000, self)
    prog.setWindowTitle("Gamma analysis")
    prog.setWindowModality(Qt.WindowModality.ApplicationModal)
    prog.setMinimumDuration(0)
    prog.setValue(0)
    QApplication.processEvents()

    def progress(k, fraction):
        c = rows[k]
        prog.setLabelText(f"Criterion {k + 1} of {len(rows)}: {c['dd']:g} % / {c['dta']:g} mm "
                          f"({'local' if c['local'] else 'global'})...")
        prog.setValue(int(1000 * (k + fraction) / len(rows)))
        QApplication.processEvents()
        return not prog.wasCanceled()

    t0 = time.time()
    try:
        out = gamma_analysis(ref["3DMatrix"], series_grid(ref), ev["3DMatrix"], series_grid(ev), rows,
                             progress=progress, **params)
    except GammaCancelled:
        self.gamma_status.setText("Gamma cancelled.")
        return None
    except (ValueError, MemoryError) as e:
        QMessageBox.warning(self, "Gamma", f"Gamma failed:\n{e}")
        return None
    finally:
        prog.close()
    elapsed = time.time() - t0
    self._gamma_run = {"out": out, "rows": rows, "params": params, "ref": _series_info(self, ref_key, ref),
                       "eval": _series_info(self, eval_key, ev), "ref_key": ref_key, "ref_geom": series_grid(ref),
                       "seconds": elapsed}
    _show_results(self, out)
    (_, sp, n) = out["geom"]
    where = "3D" if plane is None else f"2D {plane} at {position:.2f} mm"
    self.gamma_status.setText(
        f"{where}, normalization dose {out['norm_dose']:.4g} Gy, grid {n[2]} x {n[0]} x {n[1]} of {sp[0]:g} x "
        f"{sp[2]:g} x {sp[1]:g} mm (X x Y x Z), {elapsed:.1f} s"
        + (f"; {out['outside']} points outside the evaluated dose not evaluated." if out["outside"] else "."))
    return out


def _show_results(self, out):
    table = self.gamma_table
    table.blockSignals(True)
    for r, res in enumerate(out["results"]):
        s = res["stats"]
        texts = (f"{s['pass_rate']:.2f}", f"{s['mean']:.3f}", f"{s['gamma95']:.3f}",
                 (f">= {s['max']:.2f}" if s["capped"] else f"{s['max']:.3f}"), f"{s['points']}")
        for c, text in zip(RESULT_COLS, texts):
            table.item(r, c).setText(text)
    table.blockSignals(False)


def gamma_series(result, run, series_number):
    """Series (modality Gamma) of one criterion's result of a run (run_gamma): gamma volume and its metadata."""
    (x, y, z), (psc, psr, st), shape = result["geom"]
    crit, stats, params = result["criterion"], result["stats"], run["params"]
    norm = "local" if crit["local"] else "global"
    desc = f"Gamma {crit['dd']:g}%/{crit['dta']:g}mm {norm} ({run['eval']['description']} vs {run['ref']['description']})"
    (gx, gy, gz), gsp, gn = run["out"]["geom"]
    info = {"dd_percent": crit["dd"], "dta_mm": crit["dta"], "threshold_percent": crit["threshold"],
            "normalization": norm, "normalization_dose_gy": run["out"]["norm_dose"],
            "max_gamma": params["max_gamma"], "search_step_mm": crit["dta"] / params["fraction"],
            "mode": "3D" if params["plane"] is None else "2D", "plane": params["plane"],
            "plane_position_mm": params["plane_position"],
            "resolution_mm": [gsp[0], gsp[1], gsp[2]] if params["resolution"] else None,
            "evaluation_grid": {"ImagePositionPatient": [gx, gy, gz], "spacing_mm": list(gsp), "shape": list(gn)},
            "reference_position": list(run["ref_geom"][0]),
            "reference": run["ref"], "evaluated": run["eval"],
            "pass_rate": stats["pass_rate"], "mean": stats["mean"], "gamma95": stats["gamma95"],
            "max": stats["max"], "points": stats["points"], "outside_points": run["out"]["outside"],
            "not_evaluated_value": NOT_EVALUATED, "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    meta = {"SeriesDescription": desc, "Modality": "Gamma", "WindowWidth": 2.0, "WindowCenter": 1.0,
            "AcquisitionNumber": 1, "DCM_Info": {}, "StudyDescription": "AMIGOpy",
            "ImageComments": f"Gamma index (max {params['max_gamma']:g}); {NOT_EVALUATED:g} = not evaluated",
            "SliceThickness": st, "PixelSpacing": [psr, psc], "ImagePositionPatient": [x, y, z],
            "DataType": "Gamma", "Gamma": info}
    return {"3DMatrix": np.ascontiguousarray(result["gamma"], dtype=np.float32), "metadata": meta,
            "SeriesNumber": series_number}


def save_gamma(self):
    """'Save selected': the gamma of the selected criterion as a new Gamma series of the reference's study."""
    run = getattr(self, "_gamma_run", None)
    r = self.gamma_table.currentRow()
    if run is None:
        QMessageBox.information(self, "Gamma", "Run the gamma first.")
        return None
    if not 0 <= r < len(run["out"]["results"]):
        QMessageBox.information(self, "Gamma", "Select the criterion (row) to save.")
        return None
    from fcn_display.brachy_plan_actions import _next_series_number
    from fcn_load.populate_med_image_list import add_series_tree_item
    pid, sid = run["ref"]["patient"], run["ref"]["study"]
    study = self.medical_image[pid][sid]
    series = gamma_series(run["out"]["results"][r], run, _next_series_number(study))
    study.setdefault("Gamma", []).append(series)
    label = f"{series['metadata']['SeriesDescription']}_Series: {series['SeriesNumber']}"
    add_series_tree_item(self, pid, sid, "Gamma", len(study["Gamma"]) - 1, label)
    stats = run["out"]["results"][r]["stats"]
    self.gamma_status.setText(f"Saved '{series['metadata']['SeriesDescription']}' (pass rate {stats['pass_rate']:.2f} %) "
                              f"in Patient {pid}, Study {sid}, modality Gamma.")
    return series


# ----------------------------------------------------------------------------
# Init
# ----------------------------------------------------------------------------
def init_gamma_panel(self):
    """Once, after the Evaluation tab is built: criteria and parameters remembered, signals."""
    if getattr(self, "_gamma_ready", False) or getattr(self, "gamma_table", None) is None:
        return
    self._gamma_run = None
    _load_panel(self)
    self._gamma_ready = True
    _update_enabled(self)
    for combo in (self.gamma_ref_combo, self.gamma_eval_combo):
        combo.on_popup = lambda: refresh_gamma_combos(self)
        combo.currentIndexChanged.connect(lambda _i: on_criteria_edited(self))
    self.gamma_table.itemChanged.connect(lambda _item: on_criteria_edited(self))
    for widget, signal in ((self.gamma_mode_combo, "currentIndexChanged"), (self.gamma_plane_combo, "currentIndexChanged"),
                           (self.gamma_norm_combo, "currentIndexChanged"), (self.gamma_norm_spin, "valueChanged"),
                           (self.gamma_max_spin, "valueChanged"), (self.gamma_fraction_spin, "valueChanged"),
                           (self.gamma_res_chk, "toggled"), (self.gamma_res_spin, "valueChanged")):
        getattr(widget, signal).connect(lambda *_: (_update_enabled(self), on_criteria_edited(self)))
    self.gamma_add_btn.clicked.connect(lambda: add_criterion(self))
    self.gamma_remove_btn.clicked.connect(lambda: remove_criterion(self))
    self.gamma_run_btn.clicked.connect(lambda: run_gamma(self))
    self.gamma_save_btn.clicked.connect(lambda: save_gamma(self))
    tabs = getattr(self, "tabView01", None)
    if tabs is not None:
        tabs.currentChanged.connect(lambda _i: _on_view_tab(self))


def _on_view_tab(self):
    """The Evaluation tab shown: dose lists of the patient shown."""
    if getattr(self, "tabView01", None) is None or self.tabView01.currentWidget() is not getattr(self, "tab_evaluation", None):
        return
    from fcn_evaluation.isodose import refresh_slot_combos
    refresh_slot_combos(self)
    refresh_gamma_combos(self)
