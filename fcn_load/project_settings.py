# -*- coding: utf-8 -*-
"""
project_settings.py - settings saved in an AMIGOpy bundle (File > Save) and restored with it
===========================================================================================
Besides the images and their maps (self.medical_image: material, density and MCNP lattice maps
are kept in their series), a bundle keeps the MonteCarlo tab:

  * grids: calculation and voxelization grid bounds, resolution, shown or not, and the mode of the
    calculation grid (voxel / mm);
  * material assignment: the HU table and the structure materials;
  * MCNP: source, nps, tallies and standard cards.
"""
from PySide6.QtWidgets import QDoubleSpinBox

GRID_PREFIXES = ("mc_grid", "mc_vox")
TALLIES = ("mcnp_chk_dwater_water", "mcnp_chk_dwater_med", "mcnp_chk_dmed_med_tl", "mcnp_chk_dmed_med_ed")
# Axes of the mm mode boxes: 2 = the user's (MCNP) axes, Z = -DICOM y; 1 (bundles without the key): Z = DICOM y
GRID_AXES = 2


def _bounds_names(prefix):
    return [f"{prefix}_{a}{k}" for a in "xyz" for k in ("min", "max")]


def collect_project_settings(self):
    """Settings of the MonteCarlo tab to save with the data (widgets that do not exist are left out)."""
    grids = {}
    for prefix in GRID_PREFIXES:
        names = _bounds_names(prefix)
        if not all(hasattr(self, n) for n in names):
            continue
        display = getattr(self, f"{prefix}_display", None)
        grids[prefix] = {
            "bounds": [float(getattr(self, n).value()) for n in names],
            # (the voxelization grid takes the voxel size of the image)
            "resolution": [float(getattr(self, f"{prefix}_{a}res").value()) for a in "xyz"
                           if prefix != "mc_vox" and hasattr(self, f"{prefix}_{a}res")],
            "display": bool(display.isChecked()) if display is not None else None,
        }
    mode = getattr(self, "mc_grid_mode_combo", None)
    src = getattr(self, "mcnp_source_combo", None)
    nps = getattr(self, "mcnp_nps_input", None)
    std = getattr(self, "mcnp_chk_std_cards", None)
    return {
        "grids": grids,
        "grid_mode": mode.currentText() if mode is not None else None,
        "grid_axes": GRID_AXES,
        "material_assignment": {
            "hu_table": [dict(d) for d in getattr(self, "mat_HU_list", None) or []],
            "structures": {s: dict(d) for s, d in (getattr(self, "mat_struct", None) or {}).items()},
            "structures_view": {s: dict(d) for s, d in (getattr(self, "mat_struct_view", None) or {}).items()},
        },
        "mcnp": {
            "source": src.currentText() if src is not None else None,
            "nps": nps.text() if nps is not None else None,
            "tallies": {n: bool(getattr(self, n).isChecked()) for n in TALLIES if hasattr(self, n)},
            "std_cards": bool(std.isChecked()) if std is not None else None,
        },
    }


def apply_project_settings(self, settings, name="AMIGOpy project"):
    """
    Restore saved settings (after the data and the data tree, so the grids know the image). The HU
    table goes through the HU LUT dropdown (a saved LUT with the same rows, else a temporary
    "<name> (project)" entry). Returns notes for the user.
    """
    _apply_grids(self, settings)
    notes = _apply_material_assignment(self, settings.get("material_assignment") or {}, name)
    _apply_mcnp(self, settings.get("mcnp") or {})
    return notes


def _set_spin(sb, value):
    """Value without signals; the range grows to hold it (the voxelization grid follows the image shown)."""
    value = float(value)
    sb.blockSignals(True)
    sb.setRange(min(sb.minimum(), value), max(sb.maximum(), value))
    sb.setValue(value if isinstance(sb, QDoubleSpinBox) else int(round(value)))
    sb.blockSignals(False)


def _apply_grids(self, settings):
    from fcn_processing.mc_grid import _sync_slider_from_spins, update_grid_info, update_mc_grid_all
    mode, combo = settings.get("grid_mode"), getattr(self, "mc_grid_mode_combo", None)
    if combo is not None and mode and combo.findText(mode) >= 0 and combo.currentText() != mode:
        combo.setCurrentText(mode)          # labels, decimals and sliders of the mode (the values are set below)
    dicom_y = mode == "mm" and (settings.get("grid_axes") or 1) < GRID_AXES
    for prefix, grid in (settings.get("grids") or {}).items():
        names = _bounds_names(prefix)
        if not all(hasattr(self, n) for n in names):
            continue
        bounds = [float(v) for v in grid.get("bounds") or []]
        if prefix == "mc_grid" and dicom_y and len(bounds) == 6:
            bounds[4], bounds[5] = 0.0 - bounds[5], 0.0 - bounds[4]     # an older bundle: Z was DICOM y
        for n, v in zip(names, bounds):
            _set_spin(getattr(self, n), v)
        for a, v in zip("xyz", grid.get("resolution") or []):
            if hasattr(self, f"{prefix}_{a}res"):
                _set_spin(getattr(self, f"{prefix}_{a}res"), v)
        display = getattr(self, f"{prefix}_display", None)
        if display is not None and grid.get("display") is not None:
            display.blockSignals(True)
            display.setChecked(bool(grid["display"]))
            display.blockSignals(False)
        for ax in "xyz":
            _sync_slider_from_spins(self, prefix, ax)
        update_grid_info(self, prefix)
    update_mc_grid_all(self)


def _apply_material_assignment(self, assignment, name):
    from fcn_materialassignment.hu_lut import show_map_hu_table
    from fcn_materialassignment.material_map import _current_structure_names, _mat_key, update_struct2mat_table
    notes = []
    hu_table = assignment.get("hu_table") or []
    if hu_table and getattr(self, "tableMatToHU", None) is not None:
        show_map_hu_table(self, hu_table, name, source="project")
    structures, view = assignment.get("structures") or {}, assignment.get("structures_view") or {}
    if structures or view:
        kept, missing = {}, []
        for s, d in structures.items():
            key = _mat_key(self, d.get("material"))      # the material IDs of this material database
            if key is None:
                missing.append(f"{s} ({d.get('material')})")
            else:
                kept[s] = {**d, "key": key}
        self.mat_struct, self.mat_struct_view = kept, dict(view)
        table = getattr(self, "mat_to_struct_tab", None)
        if table is not None:
            if _current_structure_names(self):
                update_struct2mat_table(self)       # the series shown has structures: their rows, choices by name
            else:
                table.setRowCount(0)                # kept for the series with these structures (Refresh structures)
        if missing:
            notes.append("Structure materials not in the material database (not restored): " + ", ".join(missing))
    return notes


def _apply_mcnp(self, mcnp):
    src = getattr(self, "mcnp_source_combo", None)
    if src is not None and mcnp.get("source") and src.findText(mcnp["source"]) >= 0:
        src.setCurrentText(mcnp["source"])
    nps = getattr(self, "mcnp_nps_input", None)
    if nps is not None and mcnp.get("nps"):
        nps.setText(str(mcnp["nps"]))
    tallies = mcnp.get("tallies") or {}
    for n in TALLIES:
        if n in tallies and hasattr(self, n):
            getattr(self, n).setChecked(bool(tallies[n]))
    std = getattr(self, "mcnp_chk_std_cards", None)
    if std is not None and mcnp.get("std_cards") is not None:
        std.setChecked(bool(mcnp["std_cards"]))
