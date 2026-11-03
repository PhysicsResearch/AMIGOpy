# -*- coding: utf-8 -*-
"""
isodose.py - isodose lines on the 2D views (Evaluation > Isodoses)
==================================================================
Up to N_SLOTS doses (RTDOSE / MCNP series of the patient shown) drawn at once with the same
levels and colours, each with its own line style (solid, dashed, dotted, dash-dot) and width, so
doses can be compared on the axial, coronal and sagittal views.

Levels come from templates, as the HU LUTs of the Material Assignment tab: one CSV per template in
%LOCALAPPDATA%\\AMIGOpy\\Isodose_templates (file name = template name), every edit saved to the
template shown, a Default template created when there is none, the last used one (settings.json)
shown at start. A template has its unit, % of a reference dose or Gy, and its reference dose:

    #unit,%
    #reference,7
    Value,Color,Show
    200,#ff00ff,1
    ...

Placement: a dose is drawn where it is as an image layer (Data_tree_general: Im_Offset over layer
0, rows stored flipped), at its slice nearest to the plane shown, so the lines lie on the dose
image itself.

NOTE: must not import fcn_display.display_images at module level (it imports this module).
"""
import csv
import json
import os
import re

import contourpy
import numpy as np
import vtk
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QColorDialog, QInputDialog, QLineEdit, QMessageBox, QPushButton,
                               QTableWidgetItem)
from vtkmodules.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray

from fcn_3DPrinting.safe_io import atomic_write_csv, atomic_write_json, read_json_safe
from fcn_processing.mc_grid import DOSE_MODALITIES, series_grid

N_SLOTS = 4
LINE_STYLES = ("Solid", "Dashed", "Dotted", "Dash-dot")
UNITS = ("%", "Gy")
TEMPLATE_HEADER = ["Value", "Color", "Show"]
DEFAULT_TEMPLATE_NAME = "Default"
DEFAULT_TEMPLATE = {"unit": "%", "reference": 7.0,
                    "levels": ((200.0, "#ff00ff", True), (150.0, "#ff8000", True), (100.0, "#ff0000", True),
                               (90.0, "#ffff00", True), (75.0, "#00ff00", True), (50.0, "#00c8ff", True),
                               (25.0, "#3c64ff", True))}
LEVEL_COLORS = ("#ff0000", "#ffff00", "#00ff00", "#00c8ff", "#ff00ff", "#ff8000", "#ffffff", "#3c64ff")
Z_LINES = 0.4               # above the images (0) and the cross lines (0.05), below the brachy overlays (0.5)
# dash patterns in screen pixels per unit of line width: (on, off) pairs
PATTERNS = {"Dashed": ((6.0, 4.0),), "Dash-dot": ((6.0, 3.0), (1.0, 3.0))}
DOT_SPACING_PX = 3.0        # dotted: a dot every 3 pixels per unit of line width
VIEWS = ("ax", "co", "sa")
_VIEW_WIDGETS = {"ax": "vtkWidgetAxial", "co": "vtkWidgetCoronal", "sa": "vtkWidgetSagittal"}

_BAD_NAME_CHARS = set('<>:"/\\|?*')
_RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL"} | {f"{d}{i}" for d in ("COM", "LPT") for i in range(1, 10)}


# ----------------------------------------------------------------------------
# Templates: one CSV per template in the AppData folder
# ----------------------------------------------------------------------------
def _template_dir():
    from fcn_materialassignment.material_assignment_properties import get_appdata_path
    d = os.path.join(get_appdata_path(), "Isodose_templates")
    os.makedirs(d, exist_ok=True)
    return d


def _template_path(name):
    return os.path.join(_template_dir(), name + ".csv")


def _settings_path():
    """settings.json in %LOCALAPPDATA%\\AMIGOpy (last used template, slot styles)."""
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
        print(f"[Isodoses] could not save {_settings_path()}: {e}")


def list_templates():
    """Names of the saved isodose templates (CSV file names without extension), sorted."""
    return sorted((f[:-4] for f in os.listdir(_template_dir()) if f.lower().endswith(".csv")), key=str.lower)


def _float(text):
    try:
        return float(str(text).strip())
    except (TypeError, ValueError):
        return None


_HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}")


def _color(text):
    text = str(text).strip()
    return text.lower() if _HEX_COLOR.fullmatch(text) else None


def read_template(path):
    """A template file as {'unit': '%' or 'Gy', 'reference': Gy, 'levels': ((value, '#rrggbb', show), ...)}."""
    unit, reference, levels = "%", DEFAULT_TEMPLATE["reference"], []
    with open(path, "r", newline="", encoding="utf-8-sig", errors="replace") as f:
        for row in csv.reader(f):
            cells = [c.strip() for c in row] + ["", "", ""]
            key = cells[0].lower()
            if key.startswith("#"):
                if key == "#unit" and cells[1] in UNITS:
                    unit = cells[1]
                elif key == "#reference" and (_float(cells[1]) or 0) > 0:
                    reference = _float(cells[1])
                continue
            value = _float(cells[0])
            if value is None:
                continue        # header, empty line
            levels.append((value, _color(cells[1]) or LEVEL_COLORS[len(levels) % len(LEVEL_COLORS)],
                           cells[2].lower() not in ("0", "false", "no")))
    return {"unit": unit, "reference": float(reference), "levels": tuple(levels)}


def write_template(path, template):
    """Write a template (as read_template returns it); crash-safe (temporary file + replace)."""
    rows = [["#unit", template["unit"]], ["#reference", f"{template['reference']:g}"], TEMPLATE_HEADER]
    rows += [[f"{v:g}", color, 1 if show else 0] for v, color, show in template["levels"]]
    atomic_write_csv(path, None, rows)


def _ensure_templates():
    """Names of the saved templates; the Default template is created first when there is none."""
    names = list_templates()
    if names:
        return names
    try:
        write_template(_template_path(DEFAULT_TEMPLATE_NAME), DEFAULT_TEMPLATE)
    except OSError as e:
        print(f"[Isodoses] could not create the {DEFAULT_TEMPLATE_NAME} template: {e}")
        return []
    return [DEFAULT_TEMPLATE_NAME]


def _preferred_template(names):
    last = _get_setting("isodose_template")
    if last in names:
        return last
    return DEFAULT_TEMPLATE_NAME if DEFAULT_TEMPLATE_NAME in names else names[0]


def level_doses(template):
    """(dose in Gy, colour) of the levels shown, highest first."""
    scale = template["reference"] / 100.0 if template["unit"] == "%" else 1.0
    return sorted(((v * scale, color) for v, color, show in template["levels"] if show and v > 0), reverse=True)


# ----------------------------------------------------------------------------
# Geometry: where a dose is drawn on the views
# ----------------------------------------------------------------------------
def layer_offset(geom0, geom):
    """
    Im_Offset (world mm of the views) of a series shown as a layer over layer 0, as Data_tree_general
    sets it: geom = (ImagePositionPatient, (ps_col, ps_row, st), (n_slices, n_rows, n_cols)).
    """
    ipp0, (_, psr0, _), (_, nr0, _) = geom0
    ipp, (_, psr, _), (_, nr, _) = geom
    return ipp[0] - ipp0[0], (nr0 * psr0 - nr * psr) - (ipp[1] - ipp0[1]), ipp[2] - ipp0[2]


def dose_slice(volume, geom, offset, view, plane):
    """
    Slice of a dose nearest to the plane shown (world mm along the view normal, as the layers pick
    theirs): (slice2d, (x0, dx), (y0, dy)) with world x = x0 + i * dx, y = y0 + j * dy of its column /
    row contour coordinates (i, j); None if the plane misses the dose.
    """
    _, (psc, psr, st), (ns, nr, nc) = geom
    ox, oy, oz = offset
    if view == "ax":
        k = int(np.round((plane - oz) / st))
        return (volume[k], (ox, psc), (oy, psr)) if 0 <= k < ns else None
    if view == "co":
        k = int(np.round((plane - oy) / psr))
        return (volume[:, k, :], (ox, psc), (oz, st)) if 0 <= k < nr else None
    k = int(np.round((plane - ox) / psc))
    return (volume[:, :, k], (oy, psr), (oz, st)) if 0 <= k < nc else None


def contour_lines(slice2d, doses):
    """Contour polylines of each dose level: [[(N, 2) arrays of (column, row) coordinates], ...]."""
    z = np.asarray(slice2d, dtype=np.float64)
    if z.ndim != 2 or min(z.shape) < 2 or not len(doses):
        return [[] for _ in doses]
    top = np.nanmax(z)
    gen = contourpy.contour_generator(z=z)
    return [gen.lines(d) if d <= top else [] for d in doses]


def pattern_pieces(points, pattern):
    """
    Pieces of a polyline (N, 2) that are drawn with a dash pattern: (on, off) lengths (world mm)
    repeated along it from its start; returns a list of (M, 2) polylines.
    """
    points = np.asarray(points, float)
    if len(points) < 2:
        return []
    seg = np.linalg.norm(np.diff(points, axis=0), axis=1)
    s = np.concatenate(([0.0], np.cumsum(seg)))
    period = sum(on + off for on, off in pattern)
    if s[-1] <= 0 or period <= 0:
        return []
    pieces, start = [], 0.0
    while start < s[-1]:
        for on, off in pattern:
            a, b = start, min(start + on, s[-1])
            if b > a:
                inner = (s > a) & (s < b)
                piece = np.vstack(([_point_at(points, s, a)], points[inner], [_point_at(points, s, b)]))
                pieces.append(piece)
            start += on + off
            if start >= s[-1]:
                break
    return pieces


def _point_at(points, s, length):
    """Point at arc length 'length' along a polyline with cumulative lengths s."""
    i = int(np.clip(np.searchsorted(s, length, side="right") - 1, 0, len(points) - 2))
    t = 0.0 if s[i + 1] == s[i] else (length - s[i]) / (s[i + 1] - s[i])
    return points[i] + t * (points[i + 1] - points[i])


def dots_along(points, spacing):
    """Points every 'spacing' (world mm) along a polyline (N, 2), from its start."""
    points = np.asarray(points, float)
    if len(points) < 2 or spacing <= 0:
        return np.empty((0, 2))
    s = np.concatenate(([0.0], np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))))
    return np.array([_point_at(points, s, d) for d in np.arange(0.0, s[-1], spacing)]).reshape(-1, 2)


def styled(world_lines, style, width, mm_per_px):
    """(polylines, dots) drawing world polylines in a line style; lengths in screen pixels x line width."""
    unit = mm_per_px * max(1.0, width)
    if style == "Dotted":
        dots = [dots_along(p, DOT_SPACING_PX * unit) for p in world_lines]
        return [], np.vstack(dots) if dots else np.empty((0, 2))
    if style in PATTERNS:
        pattern = tuple((on * unit, off * unit) for on, off in PATTERNS[style])
        return [piece for p in world_lines for piece in pattern_pieces(p, pattern)], np.empty((0, 2))
    return list(world_lines), np.empty((0, 2))


# ----------------------------------------------------------------------------
# Drawing on the views
# ----------------------------------------------------------------------------
def _layer0_geometry(self):
    dd = getattr(self, "display_data", None)
    try:
        d0 = dd[0]
        if not isinstance(d0, np.ndarray) or d0.ndim != 3:
            return None
        ipp = tuple(float(v) for v in self.Im_PatPosition[0][:3])
        psr, psc, st = float(self.pixel_spac[0, 0]), float(self.pixel_spac[0, 1]), float(self.slice_thick[0])
    except Exception:
        return None
    return ipp, (psc, psr, st), d0.shape


def plane_position(self, view):
    """Plane shown on a view, world mm along its normal (as displayaxial / coronal / sagittal use it)."""
    idx = self.layer_selected.currentIndex() if hasattr(self, "layer_selected") else 0
    if view == "ax":
        return float(self.Im_Offset[idx, 2] + self.current_axial_slice_index[idx] * self.slice_thick[idx])
    if view == "co":
        return float(self.Im_Offset[idx, 1] + self.current_coronal_slice_index[idx] * self.pixel_spac[idx, 0])
    return float(self.Im_Offset[idx, 0] + self.current_sagittal_slice_index[idx] * self.pixel_spac[idx, 1])


def _renderer(self, view):
    widget = getattr(self, _VIEW_WIDGETS[view], None)
    return None if widget is None else widget.GetRenderWindow().GetRenderers().GetFirstRenderer()


def _mm_per_px(renderer, fallback=0.5):
    try:
        height = renderer.GetSize()[1]
        scale = renderer.GetActiveCamera().GetParallelScale()
        return 2.0 * scale / height if height > 0 and scale > 0 else fallback
    except Exception:
        return fallback


def _hex_rgb(color):
    c = QColor(color)
    return c.redF(), c.greenF(), c.blueF()


def _lines_actor(pieces, color, width):
    pts = [np.asarray(p, float) for p in pieces if len(p) >= 2]
    if not pts:
        return None
    xyz = np.column_stack((np.vstack(pts), np.full(sum(len(p) for p in pts), Z_LINES)))
    offsets = np.concatenate(([0], np.cumsum([len(p) for p in pts]))).astype(np.int64)
    cells = vtk.vtkCellArray()
    cells.SetData(numpy_to_vtkIdTypeArray(offsets, deep=True),
                  numpy_to_vtkIdTypeArray(np.arange(offsets[-1], dtype=np.int64), deep=True))
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(xyz, deep=True))
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetLines(cells)
    return _actor(poly, color, lambda p: p.SetLineWidth(width))


def _dots_actor(dots, color, width):
    if len(dots) == 0:
        return None
    xyz = np.column_stack((dots, np.full(len(dots), Z_LINES)))
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(xyz, deep=True))
    cells = vtk.vtkCellArray()
    n = len(dots)
    cells.SetData(numpy_to_vtkIdTypeArray(np.arange(n + 1, dtype=np.int64), deep=True),
                  numpy_to_vtkIdTypeArray(np.arange(n, dtype=np.int64), deep=True))
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetVerts(cells)

    def style(prop):
        prop.SetPointSize(max(2.0, 1.6 * width))
        prop.SetRenderPointsAsSpheres(True)
    return _actor(poly, color, style)


def _actor(poly, color, style):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    prop = actor.GetProperty()
    prop.SetColor(*_hex_rgb(color))
    prop.SetLighting(False)
    style(prop)
    actor.SetPickable(False)
    return actor


def view_isodose_lines(self, view, series, doses):
    """World polylines of each dose level of a series on a view at the plane shown ([] if none)."""
    geom0, geom = _layer0_geometry(self), series_grid(series)
    if geom0 is None or geom is None:
        return [[] for _ in doses]
    cut = dose_slice(series["3DMatrix"], geom, layer_offset(geom0, geom), view, plane_position(self, view))
    if cut is None:
        return [[] for _ in doses]
    slice2d, (x0, dx), (y0, dy) = cut
    return [[np.column_stack((x0 + line[:, 0] * dx, y0 + line[:, 1] * dy)) for line in lines]
            for lines in contour_lines(slice2d, doses)]


def update_isodose_view(self, view):
    """Isodose lines of the doses switched on, on one view at the plane shown."""
    try:
        renderer = _renderer(self, view)
        if renderer is None:
            return
        actors = getattr(self, "_iso_actors", None)
        if actors is None:
            actors = self._iso_actors = {v: [] for v in VIEWS}
        for actor in actors[view]:
            renderer.RemoveActor(actor)
        actors[view].clear()
        show = getattr(self, "iso_show_chk", None)
        template = getattr(self, "_iso_template", None)
        if show is None or not show.isChecked() or not template:
            return
        doses = level_doses(template)
        if not doses:
            return
        mm_per_px = _mm_per_px(renderer)
        for i in range(N_SLOTS):
            slot = _slot(self, i)
            series = slot_series(self, i)
            if slot is None or series is None or not slot[0].isChecked():
                continue
            style, width = slot[2].currentText(), float(slot[3].value())
            lines = view_isodose_lines(self, view, series, [d for d, _ in doses])
            for (_, color), level_lines in zip(doses, lines):
                pieces, dots = styled(level_lines, style, width, mm_per_px)
                for actor in (_lines_actor(pieces, color, width), _dots_actor(dots, color, width)):
                    if actor is not None:
                        renderer.AddActor(actor)
                        actors[view].append(actor)
    except Exception as e:
        print(f"[Isodoses] {view} update failed: {e}")


def update_isodose_axial(self):
    update_isodose_view(self, "ax")


def update_isodose_coronal(self):
    update_isodose_view(self, "co")


def update_isodose_sagittal(self):
    update_isodose_view(self, "sa")


def refresh_isodoses(self):
    """Redraw the isodose lines on the three views (the settings changed)."""
    for view in VIEWS:
        update_isodose_view(self, view)
        widget = getattr(self, _VIEW_WIDGETS[view], None)
        if widget is not None:
            try:
                widget.GetRenderWindow().Render()
            except Exception:
                pass


# ----------------------------------------------------------------------------
# Dose series of the patient shown (slot combos)
# ----------------------------------------------------------------------------
def dose_items(self):
    """[(key, label, series)] of the RTDOSE and MCNP series of the patient shown (series_key)."""
    pid = getattr(self, "patientID", None)
    studies = (getattr(self, "medical_image", None) or {}).get(pid) or {}
    several = len(studies) > 1
    out = []
    for sid, study in studies.items():
        if not isinstance(study, dict):
            continue
        for modality in DOSE_MODALITIES:
            for k, series in enumerate(study.get(modality) or []):
                grid = series_grid(series)
                if grid is None:
                    continue
                meta = series.get("metadata") or {}
                name = meta.get("SeriesDescription") or f"Series {series.get('SeriesNumber', k + 1)}"
                label = f"{modality}: {name}"
                out.append((series_key(pid, sid, modality, k), f"Study {sid} / {label}" if several else label, series))
    return out


def series_key(pid, sid, modality, k):
    """Key of a series in combo item data (a string: Qt keeps it as it is)."""
    return json.dumps([pid, sid, modality, int(k)])


def resolve_series(self, key):
    """Series of a key (series_key), None if it is gone."""
    try:
        pid, sid, modality, k = json.loads(key)
        series = self.medical_image[pid][sid][modality][k]
    except (KeyError, IndexError, TypeError, ValueError):
        return None
    return series if series_grid(series) is not None else None


def fill_series_combo(self, combo, items=None, none_label="(none)"):
    """Refill a series combo with the doses of the patient shown, keeping its choice when it is still there."""
    items = dose_items(self) if items is None else items
    current = combo.currentData()
    combo.blockSignals(True)
    combo.clear()
    combo.addItem(none_label, None)
    for key, label, _ in items:
        combo.addItem(label, key)
    i = combo.findData(current) if current is not None else 0
    combo.setCurrentIndex(max(0, i))
    combo.blockSignals(False)
    return combo.currentData() != current


def _slot(self, i):
    widgets = tuple(getattr(self, f"iso_slot{i}_{part}", None) for part in ("show", "series", "style", "width"))
    return None if any(w is None for w in widgets) else widgets


def slot_series(self, i):
    slot = _slot(self, i)
    return None if slot is None else resolve_series(self, slot[1].currentData())


def refresh_slot_combos(self):
    """Refill the series combos of the slots (when the panel is shown or a combo is opened)."""
    items = dose_items(self)
    changed = False
    for i in range(N_SLOTS):
        slot = _slot(self, i)
        if slot is not None:
            changed |= fill_series_combo(self, slot[1], items)
    if changed:
        refresh_isodoses(self)


# ----------------------------------------------------------------------------
# Levels table <-> template (autosaved to the template shown)
# ----------------------------------------------------------------------------
def _color_button(self, color):
    btn = QPushButton()
    btn.setProperty("iso_color", color)
    btn.setStyleSheet(f"background-color: {color}; border: 1px solid #888;")
    btn.setToolTip("Click to change the colour of this level")
    btn.clicked.connect(lambda _checked=False, b=btn: _pick_color(self, b))
    return btn


def _pick_color(self, btn):
    color = QColorDialog.getColor(QColor(btn.property("iso_color")), self, "Isodose colour")
    if color.isValid():
        btn.setProperty("iso_color", color.name())
        btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #888;")
        on_iso_table_edited(self)


def table_template(self):
    """The template shown in the panel (levels table, unit and reference widgets)."""
    table = self.iso_levels_table
    levels = []
    for r in range(table.rowCount()):
        show, value, btn = table.item(r, 0), table.item(r, 1), table.cellWidget(r, 2)
        v = _float(value.text()) if value is not None else None
        if v is None:
            continue
        levels.append((v, btn.property("iso_color") if btn is not None else LEVEL_COLORS[0],
                       show is None or show.checkState() == Qt.CheckState.Checked))
    return {"unit": "Gy" if self.iso_unit_combo.currentIndex() == 1 else "%",
            "reference": float(self.iso_ref_spin.value()), "levels": tuple(levels)}


def show_template(self, template):
    """Put a template in the panel (no signals, not saved)."""
    table = self.iso_levels_table
    table.blockSignals(True)
    table.setRowCount(0)
    for v, color, show in template["levels"]:
        r = table.rowCount()
        table.insertRow(r)
        item = QTableWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        item.setCheckState(Qt.CheckState.Checked if show else Qt.CheckState.Unchecked)
        table.setItem(r, 0, item)
        table.setItem(r, 1, QTableWidgetItem(f"{v:g}"))
        table.setCellWidget(r, 2, _color_button(self, color))
    table.blockSignals(False)
    for widget, value in ((self.iso_unit_combo, 1 if template["unit"] == "Gy" else 0),
                          (self.iso_ref_spin, template["reference"])):
        widget.blockSignals(True)
        if widget is self.iso_unit_combo:
            widget.setCurrentIndex(value)
        else:
            widget.setValue(value)
        widget.blockSignals(False)
    self.iso_ref_spin.setEnabled(template["unit"] == "%")
    self._iso_template = template


def on_iso_table_edited(self, *_):
    """Any edit of the levels, unit or reference: saved to the template shown, lines redrawn."""
    template = table_template(self)
    self.iso_ref_spin.setEnabled(template["unit"] == "%")
    self._iso_template = template
    name = getattr(self, "iso_template_name", None)
    if name and template != getattr(self, "_iso_saved", None):
        try:
            write_template(_template_path(name), template)
            self._iso_saved = template
        except OSError as e:
            print(f"[Isodoses] could not save '{name}': {e}")
    refresh_isodoses(self)


def add_iso_level(self):
    """'Add level': a level below the selected one (half its value), or 50 % / 1 Gy in an empty table."""
    template = table_template(self)
    levels = list(template["levels"])
    r = self.iso_levels_table.currentRow()
    base = levels[r][0] if 0 <= r < len(levels) else (levels[-1][0] if levels else None)
    value = base / 2.0 if base else (50.0 if template["unit"] == "%" else 1.0)
    used = {c for _, c, _ in levels}
    color = next((c for c in LEVEL_COLORS if c not in used), LEVEL_COLORS[len(levels) % len(LEVEL_COLORS)])
    levels.insert(r + 1 if 0 <= r < len(levels) else len(levels), (value, color, True))
    show_template(self, dict(template, levels=tuple(levels)))
    self.iso_levels_table.setCurrentCell(r + 1 if 0 <= r < len(levels) - 1 else len(levels) - 1, 1)
    on_iso_table_edited(self)


def remove_iso_level(self):
    rows = sorted({i.row() for i in self.iso_levels_table.selectedIndexes()}, reverse=True)
    if not rows and self.iso_levels_table.currentRow() >= 0:
        rows = [self.iso_levels_table.currentRow()]
    if not rows:
        QMessageBox.information(self, "Isodoses", "Select the level(s) to remove.")
        return
    template = table_template(self)
    levels = [lv for k, lv in enumerate(template["levels"]) if k not in rows]
    show_template(self, dict(template, levels=tuple(levels)))
    on_iso_table_edited(self)


# ---- template dropdown: select / New / Duplicate / Rename / Delete ---------
def _fill_template_combo(self, names, current):
    combo = self.iso_template_combo
    combo.blockSignals(True)
    combo.clear()
    combo.addItems(names)
    combo.setCurrentIndex(max(0, combo.findText(current)))
    combo.blockSignals(False)


def select_iso_template(self, name, remember=True):
    """Show the saved template 'name'; later edits are saved to it."""
    if not name:
        return
    try:
        template = read_template(_template_path(name))
    except OSError as e:
        QMessageBox.warning(self, "Isodoses", f"Could not read the isodose template '{name}':\n{e}")
        _fill_template_combo(self, list_templates(), getattr(self, "iso_template_name", None) or "")
        return
    self.iso_template_name, self._iso_saved = name, template
    show_template(self, template)
    if remember:
        _set_setting("isodose_template", name)
    refresh_isodoses(self)


def _select(self, name):
    _fill_template_combo(self, list_templates(), name)
    select_iso_template(self, name)


def _safe_name(text):
    name = "".join("_" if c in _BAD_NAME_CHARS or ord(c) < 32 else c for c in str(text))
    name = name.strip().rstrip(".")[:100].strip()
    return name if name and name.upper() not in _RESERVED_NAMES else "Isodoses"


def _unique_name(base):
    taken = {n.lower() for n in list_templates()}
    name, i = base, 2
    while name.lower() in taken:
        name, i = f"{base} {i}", i + 1
    return name


def name_problem(name, ignore=None):
    """Why 'name' cannot be used for a template (None if it can); 'ignore': the template being renamed."""
    if not name:
        return "Please type a name."
    if any(c in _BAD_NAME_CHARS or ord(c) < 32 for c in name) or name.endswith(".") \
            or name.upper() in _RESERVED_NAMES:
        return 'A name cannot contain < > : " / \\ | ? * or end with a dot.'
    if len(name) > 100:
        return "Please use a shorter name (up to 100 characters)."
    if name.lower() in {n.lower() for n in list_templates()} - {(ignore or "").lower()}:
        return f"There is already an isodose template named '{name}'."
    return None


def _ask_name(self, title, label, text, ignore=None):
    while True:
        text, ok = QInputDialog.getText(self, title, label, QLineEdit.EchoMode.Normal, text)
        if not ok:
            return None
        name = text.strip()
        problem = name_problem(name, ignore)
        if problem is None:
            return name
        QMessageBox.warning(self, title, problem)


def _create(self, name, template):
    try:
        write_template(_template_path(name), template)
    except OSError as e:
        QMessageBox.warning(self, "Isodoses", f"Could not save the isodose template '{name}':\n{e}")
        return
    _select(self, name)


def new_iso_template(self):
    """'New': a template with one level (100 % of the reference shown)."""
    name = _ask_name(self, "New isodose template", "Name of the new isodose template:", _unique_name("New isodoses"))
    if name:
        _create(self, name, {"unit": "%", "reference": float(self.iso_ref_spin.value()),
                             "levels": ((100.0, LEVEL_COLORS[0], True),)})


def duplicate_iso_template(self):
    base = getattr(self, "iso_template_name", None) or "Isodoses"
    name = _ask_name(self, "Duplicate isodose template", f"Name of the copy of '{base}':", _unique_name(f"{base} copy"))
    if name:
        _create(self, name, table_template(self))


def rename_iso_template(self):
    old = getattr(self, "iso_template_name", None)
    if not old:
        return duplicate_iso_template(self)
    name = _ask_name(self, "Rename isodose template", f"New name of '{old}':", old, ignore=old)
    if not name or name == old:
        return
    try:
        os.replace(_template_path(old), _template_path(name))
    except OSError as e:
        QMessageBox.warning(self, "Isodoses", f"Could not rename the isodose template '{old}':\n{e}")
        return
    self.iso_template_name = name
    _fill_template_combo(self, list_templates(), name)
    _set_setting("isodose_template", name)


def delete_iso_template(self):
    name = getattr(self, "iso_template_name", None)
    if not name:
        return
    if QMessageBox.question(self, "Delete isodose template", f"Delete the isodose template '{name}'?",
                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
        return
    names = list_templates()
    i = names.index(name) if name in names else 0
    try:
        os.remove(_template_path(name))
    except FileNotFoundError:
        pass
    except OSError as e:
        QMessageBox.warning(self, "Isodoses", f"Could not delete the isodose template '{name}':\n{e}")
        return
    self.iso_template_name = None
    left = _ensure_templates()          # Default again when it was the last one
    if left:
        _select(self, left[min(i, len(left) - 1)])


# ---- slots: style and width remembered ------------------------------------
def _save_slot_styles(self):
    styles = []
    for i in range(N_SLOTS):
        slot = _slot(self, i)
        if slot is not None:
            styles.append({"style": slot[2].currentText(), "width": float(slot[3].value())})
    _set_setting("isodose_slots", styles)


def on_slot_changed(self, *_):
    _save_slot_styles(self)
    refresh_isodoses(self)


def init_isodose_panel(self):
    """Once, after the Evaluation tab is built: templates (Default if none, last used shown), slot styles, signals."""
    if getattr(self, "_iso_ready", False) or getattr(self, "iso_template_combo", None) is None:
        return
    self._iso_ready = True
    self._iso_actors = {v: [] for v in VIEWS}
    self.iso_template_combo.setToolTip(f"Saved isodose templates ({_template_dir()}).\n"
                                       "Changes of the levels, unit and reference are saved to the template shown.")
    names = _ensure_templates()
    if names:
        name = _preferred_template(names)
        _fill_template_combo(self, names, name)
        select_iso_template(self, name, remember=False)
    saved = _get_setting("isodose_slots") or []
    for i in range(N_SLOTS):
        slot = _slot(self, i)
        if slot is None:
            continue
        style = saved[i] if i < len(saved) and isinstance(saved[i], dict) else {}
        slot[2].setCurrentText(style.get("style", LINE_STYLES[i % len(LINE_STYLES)]))
        slot[3].setValue(float(style.get("width", 2.0)))
        slot[1].on_popup = lambda: refresh_slot_combos(self)
        slot[0].toggled.connect(lambda _c: refresh_isodoses(self))
        slot[1].currentIndexChanged.connect(lambda _i: refresh_isodoses(self))
        slot[2].currentTextChanged.connect(lambda _t: on_slot_changed(self))
        slot[3].valueChanged.connect(lambda _v: on_slot_changed(self))
    self.iso_template_combo.currentTextChanged.connect(lambda name: select_iso_template(self, name))
    self.iso_unit_combo.currentIndexChanged.connect(lambda _i: on_iso_table_edited(self))
    self.iso_ref_spin.valueChanged.connect(lambda _v: on_iso_table_edited(self))
    self.iso_levels_table.itemChanged.connect(lambda _item: on_iso_table_edited(self))
    self.iso_show_chk.toggled.connect(lambda _c: refresh_isodoses(self))
    for name, func in (("iso_new_btn", new_iso_template), ("iso_dup_btn", duplicate_iso_template),
                       ("iso_rename_btn", rename_iso_template), ("iso_del_btn", delete_iso_template),
                       ("iso_add_level_btn", add_iso_level), ("iso_del_level_btn", remove_iso_level)):
        getattr(self, name).clicked.connect(lambda _checked=False, f=func: f(self))
