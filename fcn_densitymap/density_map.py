# -*- coding: utf-8 -*-
"""
density_map.py - density maps of a CT (MonteCarlo > Density Map > Create density map)
====================================================================================
"Create density map" opens a small dialog with every choice: what to create (mass density, RED or
SPR), the HU table of that type (fcn_ctcal.ct_cal; the table shown by default), and a material map
of the CT, used
  * as reference: its materials and structures with a fixed density get the value of the material
    database (Den, RED or SPR), the others the HU table value, and / or
  * to override the non-tissue materials (Tissue = 0 in the material database) with their
    database value.
A database value that is missing or not above 0 (RED and SPR are 0 in the bundled database) is
not used: those voxels keep the HU table value, and the dialog after the creation says which.
The map goes under the CT's density_maps with its type and how it was made, and appears in the
data tree (rename / delete there, right-click).
"""
from datetime import datetime

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel,
                               QLineEdit, QMessageBox)

from fcn_ctcal.ct_cal import TYPES, _table_path, curve, list_tables, read_table, type_label
from fcn_load.populate_med_image_list import populate_medical_image_tree


def compute_density(ct_matrix, ct_cal_curve):
    """
    Values of a CT (HU) from a calibration curve: (HU, value) arrays or a two-column DataFrame.
    Linear between the points, the first value below them, the last segment extended above them;
    then limited to [max(0, first value), max(last value, 2.9)].
    """
    if hasattr(ct_cal_curve, "iloc"):
        HU, values = ct_cal_curve.iloc[:, 0].to_numpy(dtype=np.float32), ct_cal_curve.iloc[:, 1].to_numpy(dtype=np.float32)
    else:
        HU, values = (np.asarray(a, dtype=np.float32) for a in ct_cal_curve)
    order = np.argsort(HU)
    HU, values = HU[order], values[order]

    slopes = np.diff(values) / np.diff(HU)
    intercepts = values[:-1] - slopes * HU[:-1]
    density_map = np.zeros_like(ct_matrix, dtype=np.float32)
    density_map[ct_matrix < HU[0]] = values[0]
    for i in range(len(slopes)):
        mask = (ct_matrix >= HU[i]) & (ct_matrix < HU[i + 1])
        density_map[mask] = ct_matrix[mask] * slopes[i] + intercepts[i]
    mask_last = ct_matrix >= HU[-1]
    density_map[mask_last] = ct_matrix[mask_last] * slopes[-1] + intercepts[-1] if len(slopes) else values[-1]

    np.clip(density_map, max(0.0, float(values[0])), max(float(values[-1]), 2.9), out=density_map)
    return density_map


def material_value(mat_df, material, kind):
    """Value of a material in the material database (Den for mass density); None if missing or not above 0."""
    column = "Den" if kind == "DENSITY" else kind
    if mat_df is None or "Name" not in getattr(mat_df, "columns", ()) or column not in mat_df.columns:
        return None
    row = mat_df[mat_df["Name"] == material]
    try:
        value = float(str(row[column].values[0]).strip())
    except (IndexError, ValueError):
        return None
    return value if value > 0 else None


def _is_tissue(mat_df, material):
    try:
        return float(str(mat_df[mat_df["Name"] == material]["Tissue"].values[0]).strip()) != 0
    except (IndexError, KeyError, TypeError, ValueError):
        return True


def _structure_rows(table):
    """(structure name, row) of a material map's structure table (dict or list)."""
    if isinstance(table, dict):
        return list(table.items())
    return [(s.get("structure"), s) for s in table or []]


def fixed_flags(hu_table, structure_table):
    """Material key / name -> fixed density, from a material map's HU table and structure table."""
    flags = {}
    for row in hu_table or []:
        for k in (row.get("key"), row.get("name")):
            if k is not None:
                flags[k] = row.get("fixed_density", True)
    for _, row in _structure_rows(structure_table):
        for k in (row.get("key"), row.get("material")):
            if k is not None:
                flags[k] = row.get("fixed_density", True)
    return flags


def build_density_map(ct_matrix, rows, kind, mat_df=None, mat_map=None, material_used=None, flags=None,
                      structure_table=None, structure_masks=None, reference=False, non_tissue=False):
    """
    A density map (float32, the CT shape) from an HU table (rows (HU, value)) of type kind, and the
    materials whose database value is missing (their voxels keep the HU table value).
    mat_map / material_used: a material map (material keys) and {key: material name};
    reference: fixed materials (flags: key or name -> fixed, fixed_flags) and the structures of
    structure_table with a fixed density (masks: structure_masks {name: bool array}) get their
    database value, the others the HU table value; non_tissue: materials with Tissue = 0 get theirs.
    """
    base = compute_density(ct_matrix, curve(rows))
    out = base.copy()
    missing = set()
    if mat_map is None or not (reference or non_tissue):
        return out, []
    used, flags = material_used or {}, flags or {}

    def value_of(material):
        v = material_value(mat_df, material, kind)
        if v is None:
            missing.add(material)
        return v

    if reference:
        for key, material in used.items():
            if flags.get(key, flags.get(material, True)):
                v = value_of(material)
                if v is not None:
                    out[mat_map == key] = v
        for name, row in _structure_rows(structure_table):
            mask = (structure_masks or {}).get(name)
            if mask is None:
                continue
            if row.get("fixed_density", True):
                v = value_of(row.get("material"))
                if v is not None:
                    out[mask] = v
            else:
                out[mask] = base[mask]
    if non_tissue:
        for key, material in used.items():
            if not _is_tissue(mat_df, material):
                v = value_of(material)
                if v is not None:
                    out[mat_map == key] = v
    return out, sorted(m for m in missing if m)


# ----------------------------------------------------------------------------
# Dialog and creation
# ----------------------------------------------------------------------------
def _unique_map_name(existing, kind):
    n = 0
    while f"map_{kind}_{n}" in existing:
        n += 1
    return f"map_{kind}_{n}"


def _table_kinds():
    """{table name: type key} of the saved HU tables."""
    kinds = {}
    for name in list_tables():
        try:
            kinds[name] = read_table(_table_path(name))[0]
        except (OSError, ValueError):
            continue
    return kinds


def ask_density_map(self, target):
    """
    The choices of a new density map of the CT 'target' (dialog): {'kind', 'table', 'mat_map',
    'reference', 'non_tissue', 'name'}; None if cancelled.
    """
    tables = _table_kinds()
    mat_maps = list((target.get("mat_maps") or {}).keys())
    existing = target.get("density_maps") or {}
    dlg = QDialog(self)
    dlg.setWindowTitle("Create density map")
    form = QFormLayout(dlg)
    meta = target.get("metadata") or {}
    form.addRow(QLabel(f"CT: {meta.get('SeriesDescription') or 'Series ' + str(target.get('SeriesNumber', ''))}  "
                       f"({' x '.join(str(n) for n in target['3DMatrix'].shape[::-1])} voxels)", dlg))

    kind_combo = QComboBox(dlg)
    for key, (label, _) in TYPES.items():
        kind_combo.addItem(label, key)
    form.addRow("Create:", kind_combo)
    table_combo = QComboBox(dlg)
    form.addRow("HU table:", table_combo)
    mat_combo = QComboBox(dlg)
    mat_combo.addItem("None", None)
    for name in mat_maps:
        mat_combo.addItem(name, name)
    form.addRow("Material map:", mat_combo)
    reference = QCheckBox("Use the material map as reference", dlg)
    reference.setToolTip("Materials and structures with a fixed density in the material map get their value from\n"
                         "the material database (Den, RED or SPR); the others the HU table value.")
    form.addRow("", reference)
    non_tissue = QCheckBox("Override non-tissue materials", dlg)
    non_tissue.setToolTip("Materials that are not tissue (Tissue = 0 in the material database, e.g. Air) get their\n"
                          "value from the material database.")
    form.addRow("", non_tissue)
    name_edit = QLineEdit(dlg)
    form.addRow("Name:", name_edit)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dlg)
    create = buttons.button(QDialogButtonBox.StandardButton.Ok)
    create.setText("Create")
    form.addRow(buttons)
    edited = {"name": False}

    def on_kind():
        kind = kind_combo.currentData()
        names = [n for n, k in tables.items() if k == kind]
        table_combo.clear()
        table_combo.addItems(names)
        current = getattr(self, "ct_cal_name", None)
        if current in names:
            table_combo.setCurrentText(current)
        table_combo.setToolTip("" if names else f"No {type_label(kind)} HU table: make one in the Density Map tab (New).")
        create.setEnabled(bool(names))
        if not edited["name"]:
            name_edit.blockSignals(True)
            name_edit.setText(_unique_map_name(existing, kind))
            name_edit.blockSignals(False)

    def on_mat():
        has = mat_combo.currentData() is not None
        reference.setEnabled(has)
        non_tissue.setEnabled(has)

    def on_ok():
        name = name_edit.text().strip()
        if not name:
            QMessageBox.warning(dlg, "Create density map", "Please type a name.")
        elif name in existing:
            QMessageBox.warning(dlg, "Create density map", f"The CT has already a density map named '{name}'.")
        else:
            dlg.accept()

    kind_combo.currentIndexChanged.connect(lambda _i: on_kind())
    mat_combo.currentIndexChanged.connect(lambda _i: on_mat())
    name_edit.textEdited.connect(lambda _t: edited.update(name=True))
    buttons.accepted.connect(on_ok)
    buttons.rejected.connect(dlg.reject)
    kind_combo.setCurrentIndex(max(0, kind_combo.findData(getattr(self, "ct_cal_kind", None) or "DENSITY")))
    last = getattr(self, "last_selected_mat_map", None)
    mat_combo.setCurrentIndex(max(0, mat_combo.findData(last if last in mat_maps else (mat_maps[-1] if mat_maps else None))))
    on_kind()
    on_mat()
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return None
    mat = mat_combo.currentData()
    return {"kind": kind_combo.currentData(), "table": table_combo.currentText(), "mat_map": mat,
            "reference": bool(mat) and reference.isChecked(), "non_tissue": bool(mat) and non_tissue.isChecked(),
            "name": name_edit.text().strip()}


def create_density_map(self):
    """'Create density map': the dialog, then the map of the CT (the CT selected in the data tree, else the first)."""
    from fcn_mcnp.mcnp_input import input_ct
    target = input_ct(self) if getattr(self, "patientID", None) else None
    if target is None or not isinstance(target.get("3DMatrix"), np.ndarray):
        QMessageBox.warning(self, "Create density map", "No CT in the study shown.")
        return
    opts = ask_density_map(self, target)
    if opts is None:
        return
    try:
        kind, rows = read_table(_table_path(opts["table"]))
    except (OSError, ValueError) as e:
        QMessageBox.warning(self, "Create density map", f"Could not read the HU table '{opts['table']}':\n{e}")
        return
    if len(rows) < 2:
        QMessageBox.warning(self, "Create density map", f"The HU table '{opts['table']}' needs at least two rows.")
        return
    mat_entry = (target.get("mat_maps") or {}).get(opts["mat_map"]) if opts["mat_map"] else None
    hu_table = structure_table = None
    if mat_entry is not None:
        hu_table = mat_entry.get("HU_table") or (mat_entry.get("metadata") or {}).get("HU_table")
        structure_table = mat_entry.get("structures") or (mat_entry.get("metadata") or {}).get("structures")
        if not hu_table and not structure_table:     # maps made before they kept their tables
            hu_table, structure_table = getattr(self, "mat_HU_list", None), getattr(self, "mat_struct", None)
    masks = {}
    for s in (target.get("structures") or {}).values():
        if isinstance(s, dict) and "Mask3D" in s:
            masks[s.get("Name")] = s["Mask3D"] != 0

    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
    try:
        matrix, missing = build_density_map(
            target["3DMatrix"], rows, kind, getattr(self, "Mat_df", None),
            None if mat_entry is None else mat_entry["3DMatrix"],
            None if mat_entry is None else mat_entry.get("Material_used", {}),
            fixed_flags(hu_table, structure_table), structure_table, masks, opts["reference"], opts["non_tissue"])
    finally:
        QApplication.restoreOverrideCursor()
    target.setdefault("density_maps", {})[opts["name"]] = {
        "3DMatrix": matrix, "type": kind,
        "metadata": {"created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "hu_table": opts["table"],
                     "hu_table_rows": [list(r) for r in rows], "material_map": opts["mat_map"],
                     "material_map_reference": opts["reference"], "override_non_tissue": opts["non_tissue"],
                     "units": "g/cm3" if kind == "DENSITY" else "relative to water"}}
    populate_medical_image_tree(self)
    if missing:
        QMessageBox.information(self, "Create density map",
                                f"No {type_label(kind)} in the material database (missing or 0) for: "
                                f"{', '.join(missing)}.\nTheir voxels have the value of the HU table.")
