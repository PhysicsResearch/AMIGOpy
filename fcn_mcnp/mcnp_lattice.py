# -*- coding: utf-8 -*-
"""
mcnp_lattice.py - MCNP universe (lattice) map from material + density maps
==========================================================================

Builds a voxel map with the same shape as the material map, where each voxel
holds an MCNP universe number instead of a material ID.

Universe numbering
------------------
* The materials present in the material map are ordered as in the material
  list of the map ('Material_used', i.e. the order of the HU table followed by
  the structures).
* Densities are rounded to 3 decimals (0.001 g/cm3 steps).
* Each material owns a block of ``UNIVERSE_BLOCK`` universes:
      material 1 -> 1    ... 1999
      material 2 -> 2000 ... 3999
      material 3 -> 4000 ... 5999   (and so on)
  (Universe 0 is reserved by MCNP, so the first block starts at 1.)
* Within a material, the smallest density present gets the first universe of
  the block, the next (larger) distinct density the next universe, etc.
"""

from datetime import datetime

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox, QProgressDialog

from fcn_load.populate_med_image_list import populate_medical_image_tree

UNIVERSE_BLOCK = 2000      # universes reserved per material
DENSITY_DECIMALS = 3       # density rounding (g/cm3)


AIR_MATERIAL_INDEX = 1   # Air is always standard material ID 1
AIR_DENSITY = 0.001205     # Standard air fixed density (g/cm3)
AIR_UNIVERSE = 1           # Default universe for standard air


def _is_air(name):
    """Return True if the material name denotes Air."""
    s = str(name).strip().lower()
    return s == "air" or s.startswith("air-") or s.startswith("air_")


def _block_range(mat_index):
    """Return (first, last) universe for the 0-based material index.

    mat_index=0 (Material 1 / Air)     -> 1    ... 1999
    mat_index=1 (Material 2 / 1st non-air) -> 2000 ... 3999
    mat_index=2 (Material 3 / 2nd non-air) -> 4000 ... 5999
    """
    first = max(1, mat_index * UNIVERSE_BLOCK)
    last = (mat_index + 1) * UNIVERSE_BLOCK - 1
    return first, last


def _pick_map(self, maps, title, label):
    """Return the key of the chosen map (auto-select if only one), or None."""
    keys = list(maps.keys())
    if len(keys) == 1:
        return keys[0]
    item, ok = QInputDialog.getItem(self, title, label, keys, len(keys) - 1, False)
    return item if ok and item else None


def _get_mat_name(mat_used, key):
    if not mat_used:
        return f"ID {key}"
    for k in (key, str(key), int(key), np.int16(key)):
        if k in mat_used:
            return mat_used[k]
    return f"ID {key}"


def build_universe_map(mat_map, den_map, mat_used, progress_cb=None):
    """Pure-numpy core: return (universe_map, universe_table, errors).

    Universe & Material rules:
      * Standard Material ID 1 is Air (fixed density 0.001205 g/cm3, universe 1).
      * Other materials start from Material ID 2, each owning a 2000-universe block:
            Material 2 -> 2000 ... 3999
            Material 3 -> 4000 ... 5999
            ...

    universe_table: list of dicts {universe, material_index, material_key,
                    material, density}
    errors: list of strings (materials exceeding their universe block)
    """
    mat_map = np.asarray(mat_map)
    den_map = np.asarray(den_map, dtype=np.float64)
    present = [int(v) for v in np.unique(mat_map)]

    # Material order: as listed in the map, then any present-but-unlisted IDs
    order = []
    for k in (mat_used or {}).keys():
        try:
            k = int(k)
        except (TypeError, ValueError):
            continue
        if k in present and k not in order:
            order.append(k)
    order += [k for k in present if k not in order]

    # Separate Air (Material 1) from other materials (Material 2, 3, ...)
    air_keys = []
    non_air_keys = []
    for k in order:
        name = _get_mat_name(mat_used, k)
        if _is_air(name):
            air_keys.append(k)
        else:
            non_air_keys.append(k)

    uni_map = np.zeros(mat_map.shape, dtype=np.int32)
    table, errors = [], []
    scale = 10 ** DENSITY_DECIMALS

    total_steps = len(air_keys) + len(non_air_keys)
    step = 0

    # 1. Process Air (Material ID 1) with fixed density
    air_added = False
    for key in air_keys:
        step += 1
        name = _get_mat_name(mat_used, key)
        if progress_cb is not None and total_steps > 0:
            pct = int(10 + (step / total_steps) * 75)
            progress_cb(pct, f"Processing Air (Material 1): {name}...")
        mask = mat_map == key
        uni_map[mask] = AIR_UNIVERSE
        if not air_added:
            table.append({
                'universe': AIR_UNIVERSE,
                'material_index': AIR_MATERIAL_INDEX,
                'material_key': key,
                'material': 'Air',
                'density': AIR_DENSITY,
            })
            air_added = True

    # 2. Process non-air materials starting from Material ID 2
    for idx, key in enumerate(non_air_keys, start=2):
        step += 1
        name = _get_mat_name(mat_used, key)
        if progress_cb is not None and total_steps > 0:
            pct = int(10 + (step / total_steps) * 75)
            progress_cb(pct, f"Processing material {idx} (ID {idx}): {name}...")
        first, last = _block_range(idx - 1)
        mask = mat_map == key
        d_arr = np.nan_to_num(den_map[mask], nan=0.0, posinf=0.0, neginf=0.0)
        d_int = np.rint(d_arr * scale).astype(np.int64)
        uniq, inv = np.unique(d_int, return_inverse=True)
        capacity = last - first + 1
        if len(uniq) > capacity:
            errors.append(f"{name}: {len(uniq)} densities (max {capacity}), "
                          f"range {uniq[0] / scale:.3f}-{uniq[-1] / scale:.3f} g/cm3")
            continue
        uni_map[mask] = first + inv.astype(np.int32)
        for j, d in enumerate(uniq):
            table.append({
                'universe': int(first + j),
                'material_index': idx,
                'material_key': key,
                'material': str(name),
                'density': round(float(d) / scale, DENSITY_DECIMALS),
            })
    return uni_map, table, errors


def create_mcnp_lattice_map(self):
    """Button callback: build and store an MCNP universe map for the current CT."""
    if not getattr(self, 'patientID', None):
        QMessageBox.critical(self, 'Error', 'No patient selected')
        return
    try:
        target = self.medical_image[self.patientID][self.studyID]['CT'][self.series_index]
    except Exception:
        QMessageBox.critical(self, 'Error', 'No CT found')
        return

    mat_maps = target.get('mat_maps', {}) or {}
    den_maps = target.get('density_maps', {}) or {}
    if not mat_maps:
        QMessageBox.critical(self, 'Error', 'No material maps found for this CT.')
        return
    if not den_maps:
        QMessageBox.critical(self, 'Error', 'No density maps found for this CT.')
        return

    mat_key = _pick_map(self, mat_maps, 'Material map', 'Select the material map:')
    if mat_key is None:
        return
    den_key = _pick_map(self, den_maps, 'Density map', 'Select the density map:')
    if den_key is None:
        return

    mat_entry, den_entry = mat_maps[mat_key], den_maps[den_key]
    mat_map, den_map = mat_entry['3DMatrix'], den_entry['3DMatrix']
    if mat_map.shape != den_map.shape:
        QMessageBox.critical(self, 'Error',
                             f'Material map {mat_map.shape} and density map {den_map.shape} '
                             'have different sizes.')
        return
    if str(den_entry.get('type', 'Density')).upper() != 'DENSITY':
        reply = QMessageBox.question(
            self, 'Map type',
            f"'{den_key}' is of type {den_entry.get('type')} (not mass density). Continue?",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

    pb = getattr(self, 'progressBar', None)
    prog = QProgressDialog("Creating MCNP lattice map...", None, 0, 100, self)
    prog.setWindowTitle("MCNP Lattice")
    prog.setWindowModality(Qt.WindowModality.ApplicationModal)
    prog.setMinimumDuration(0)
    prog.setValue(5)
    QApplication.processEvents()

    def update_prog(pct, text=None):
        if prog is not None:
            if text:
                prog.setLabelText(text)
            prog.setValue(pct)
        if pb is not None:
            pb.setValue(pct)
        QApplication.processEvents()

    try:
        update_prog(10, "Quantizing densities and building universe map...")
        uni_map, table, errors = build_universe_map(
            mat_map, den_map, mat_entry.get('Material_used', {}), progress_cb=update_prog
        )
        if errors:
            prog.close()
            if pb is not None:
                pb.setValue(0)
            QMessageBox.critical(self, 'Too many densities',
                                 'The following materials exceed the universe block of '
                                 f'{UNIVERSE_BLOCK}:\n\n' + '\n'.join(errors))
            return

        update_prog(88, "Saving MCNP lattice map metadata...")
        existing = target.setdefault('mcnp_lattice_maps', {})
        map_name = f'mcnp_lattice_{len(existing)}'
        existing[map_name] = {
            '3DMatrix': uni_map,
            'universes': table,
            'metadata': {
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'series_index': self.series_index,
                'material_map': mat_key,
                'density_map': den_key,
                'universe_block': UNIVERSE_BLOCK,
                'density_decimals': DENSITY_DECIMALS,
            },
        }

        update_prog(95, "Updating medical image tree...")
        populate_medical_image_tree(self)
        update_prog(100, "Done")
    finally:
        prog.close()
        if pb is not None:
            pb.setValue(0)

    # Summary per material
    summary = {}
    for row in table:
        s = summary.setdefault(row['material'], [row['universe'], row['universe'], row['density'], row['density'], 0])
        s[1], s[3], s[4] = row['universe'], row['density'], s[4] + 1
    lines = [f"{m}: universes {a}-{b} ({n} densities, {da:.3f}-{db:.3f} g/cm3)"
             for m, (a, b, da, db, n) in summary.items()]
    QMessageBox.information(self, 'MCNP lattice map',
                            f"'{map_name}' created ({len(table)} universes, "
                            f"{len(summary)} materials).\n\n" + '\n'.join(lines))
