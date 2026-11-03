# -*- coding: utf-8 -*-
"""
mc_grid.py - Monte Carlo grid overlays
======================================

Draws rectangular boxes (similar to an ROI) on the axial, coronal and
sagittal VTK views for the Monte Carlo grids defined in the "MonteCarlo"
tab (bottom panel):

    * Calculation grid   (prefix "mc_grid") -> yellow
    * Voxelization grid  (prefix "mc_vox")  -> red

Each grid is defined by 6 values typed by the user, in voxel indices of
layer 0 (inclusive bounds):

    X min / X max  -> image column  (sagittal slice index)
    Y min / Y max  -> image slice   (axial slice index)
    Z min / Z max  -> image row     (coronal slice index)

(This follows the AMIGOpy view convention: axial plane = X-Z,
sagittal = Z-Y, coronal = X-Y.)

Each grid has its own "Display" checkbox, and the boxes are only shown
while the MonteCarlo tab is the selected tab. There the boxes can be dragged
on the views: an edge or a corner resizes, the inside moves the box.

In mm mode the calculation grid boxes hold mm of the first / last voxel
centres in the user's (MCNP) axes: X = DICOM x, Y = DICOM z, Z = -DICOM y
(anterior +). The layer 0 rows are stored flipped (row r is DICOM row
n_rows - 1 - r), so Z runs with them, as in voxel mode.
"Import from dose" sets the calculation grid to the voxels of a dose.

NOTE: this module must NOT import fcn_display.display_images at module
level (display_images imports this module -> circular import).
"""

import time

import numpy as np
import vtk
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QDoubleSpinBox, QMenu

# prefix -> appearance
GRIDS = {
    "mc_grid": {"color": (1.0, 0.85, 0.0), "z": 1.00, "name": "Calculation grid"},
    "mc_vox":  {"color": (1.0, 0.15, 0.15), "z": 1.05, "name": "Voxelization grid"},
}

_LINE_WIDTH = 2.0
_VIEWS = ("ax", "co", "sa")
MM_DECIMALS = 4     # mm mode boxes: 0.1 um, so a grid taken from a dose keeps its voxels


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def _fields(prefix):
    return tuple(f"{prefix}_{a}{k}" for a in "xyz" for k in ("min", "max"))


def _ref_origin_and_spacing(self):
    """
    Return (ox, oy, oz), (ps_col, ps_row, st) for reference image: the one shown in layer 0, which
    the boxes are drawn on; without one, the series selected in the data tree.
    """
    if _has_image(self):
        try:
            ipp = self.Im_PatPosition[0]
            ps_row, ps_col, st = float(self.pixel_spac[0, 0]), float(self.pixel_spac[0, 1]), float(self.slice_thick[0])
            if ps_col > 0 and ps_row > 0 and st > 0:
                return (float(ipp[0]), float(ipp[1]), float(ipp[2])), (ps_col, ps_row, st)
        except Exception:
            pass
    ox, oy, oz = 0.0, 0.0, 0.0
    ps_col, ps_row, st = 1.0, 1.0, 1.0

    # Try from current series metadata first
    try:
        meta = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']
        if 'PixelSpacing' in meta:
            ps_row = float(meta['PixelSpacing'][0])
            ps_col = float(meta['PixelSpacing'][1])
        if 'SliceThickness' in meta:
            st = float(meta['SliceThickness'])
        if 'ImagePositionPatient' in meta:
            ox = float(meta['ImagePositionPatient'][0])
            oy = float(meta['ImagePositionPatient'][1])
            oz = float(meta['ImagePositionPatient'][2])
        if ps_col > 0 and ps_row > 0 and st > 0:
            return (ox, oy, oz), (ps_col, ps_row, st)
    except Exception:
        pass

    if hasattr(self, "Im_PatPosition"):
        try:
            ipp = self.Im_PatPosition[0]
            ox = float(ipp[0])
            oy = float(ipp[1])
            oz = float(ipp[2])
        except Exception:
            pass

    if hasattr(self, "pixel_spac"):
        try:
            r = float(self.pixel_spac[0, 0])
            c = float(self.pixel_spac[0, 1])
            if r > 0:
                ps_row = r
            if c > 0:
                ps_col = c
        except Exception:
            pass

    if hasattr(self, "slice_thick"):
        try:
            t = float(self.slice_thick[0])
            if t > 0:
                st = t
        except Exception:
            pass

    return (ox, oy, oz), (ps_col, ps_row, st)


def is_grid_mm_mode(self, prefix):
    if prefix != "mc_grid":
        return False
    combo = getattr(self, f"{prefix}_mode_combo", None)
    return combo is not None and combo.currentText() == "mm"


def _has_image(self):
    dd = getattr(self, "display_data", None)
    if dd is None:
        return False
    try:
        d0 = dd[0]
        return isinstance(d0, np.ndarray) and d0.ndim == 3
    except Exception:
        return False


def _row_of_y(self, y, oy, ps_row):
    """Row of layer 0 as stored and shown (UI Z, voxel mode) of a DICOM y (mm): rows are stored flipped."""
    r = (y - oy) / (ps_row if ps_row > 0 else 1.0)
    return (self.display_data[0].shape[1] - 1) - r if _has_image(self) else r


def _y_of_row(self, r, oy, ps_row):
    """DICOM y (mm) of a row of layer 0 as stored and shown (inverse of _row_of_y)."""
    return oy + ((self.display_data[0].shape[1] - 1) - r if _has_image(self) else r) * ps_row


def _row_of_ui_z(self, z, oy, ps_row):
    """Row of layer 0 as stored and shown of a mm mode Z (= -DICOM y, the user's / MCNP axes)."""
    return _row_of_y(self, 0.0 - z, oy, ps_row)


def _ui_z_of_row(self, r, oy, ps_row):
    """mm mode Z (= -DICOM y) of a row of layer 0 as stored and shown (inverse of _row_of_ui_z)."""
    return 0.0 - _y_of_row(self, r, oy, ps_row)


def _mc_tab_active(self):
    """True only when the MonteCarlo tab AND its GRID sub-tab are selected."""
    tabs = getattr(self, "tabView01", None)
    tab = getattr(self, "tab_montecarlo", None)
    if tabs is None or tab is None or tabs.currentWidget() is not tab:
        return False
    sub = getattr(self, "mc_tabs", None)
    grid_tab = getattr(self, "mc_tab_grid", None)
    if sub is None or grid_tab is None:
        return True
    return sub.currentWidget() is grid_tab


def get_grid_bounds(self, prefix):
    """Return (col_min, col_max, row_min, row_max, slice_min, slice_max)
    in voxel indices (or effective floating-point voxels if in mm mode), or None.

    UI mapping: X -> column, Y -> slice, Z -> row.
    """
    names = _fields(prefix)
    if not all(hasattr(self, f) for f in names):
        return None
    xmin, xmax, ymin, ymax, zmin, zmax = (float(getattr(self, f).value()) for f in names)

    if is_grid_mm_mode(self, prefix):
        (ox, oy, oz), (ps_col, ps_row, st) = _ref_origin_and_spacing(self)
        cmin = (xmin - ox) / (ps_col if ps_col > 0 else 1.0)
        cmax = (xmax - ox) / (ps_col if ps_col > 0 else 1.0)
        smin = (ymin - oz) / (st if st > 0 else 1.0)
        smax = (ymax - oz) / (st if st > 0 else 1.0)
        rmin = _row_of_ui_z(self, zmin, oy, ps_row)   # UI Z = -DICOM y: with the rows as stored
        rmax = _row_of_ui_z(self, zmax, oy, ps_row)
    else:
        cmin, cmax = xmin, xmax
        smin, smax = ymin, ymax
        rmin, rmax = zmin, zmax

    cmin, cmax = sorted((cmin, cmax))   # X -> columns
    smin, smax = sorted((smin, smax))   # Y -> slices
    rmin, rmax = sorted((rmin, rmax))   # Z -> rows
    return cmin, cmax, rmin, rmax, smin, smax


def get_grid_origin_abs(self, prefix):
    """
    Return the first voxel centre (X, Y, Z) of a grid in absolute mm, the user's (MCNP) axes:
    X = DICOM x, Y = DICOM z, Z = -DICOM y; or None.
    """
    names = _fields(prefix)
    if not all(hasattr(self, f) for f in names):
        return None
    (ox, oy, oz), (ps_col, ps_row, st) = _ref_origin_and_spacing(self)
    xmin = float(getattr(self, f"{prefix}_xmin").value())
    xmax = float(getattr(self, f"{prefix}_xmax").value())
    ymin = float(getattr(self, f"{prefix}_ymin").value())
    ymax = float(getattr(self, f"{prefix}_ymax").value())
    zmin = float(getattr(self, f"{prefix}_zmin").value())
    zmax = float(getattr(self, f"{prefix}_zmax").value())

    if is_grid_mm_mode(self, prefix):
        return min(xmin, xmax), min(ymin, ymax), min(zmin, zmax)
    orig_x = ox + min(xmin, xmax) * ps_col
    orig_y = oz + min(ymin, ymax) * st          # UI Y is slice -> DICOM z
    orig_z = min(_ui_z_of_row(self, zmin, oy, ps_row), _ui_z_of_row(self, zmax, oy, ps_row))   # UI Z: rows
    return orig_x, orig_y, orig_z


def get_mc_grid_bounds(self):
    """Backward-compatible accessor for the calculation grid."""
    return get_grid_bounds(self, "mc_grid")


def get_grid_resolution(self, prefix):
    """Return (res_x, res_y, res_z) in mm (UI order), or None."""
    names = [f"{prefix}_{a}res" for a in "xyz"]
    if not all(hasattr(self, n) for n in names):
        return None
    return tuple(float(getattr(self, n).value()) for n in names)


def _is_enabled(self, prefix):
    cb = getattr(self, f"{prefix}_display", None)
    return cb is not None and cb.isChecked() and _mc_tab_active(self)


def _widget(self, view):
    return {"ax": self.vtkWidgetAxial,
            "co": self.vtkWidgetCoronal,
            "sa": self.vtkWidgetSagittal}[view]


def _renderer(widget):
    return widget.GetRenderWindow().GetRenderers().GetFirstRenderer()


def _get_actor(self, prefix, view):
    """Create (once) and return the outline actor for a grid/view."""
    attr = f"{prefix}_actor_{view}"
    renderer = _renderer(_widget(self, view))

    actor = getattr(self, attr, None)
    if actor is not None:
        if not renderer.HasViewProp(actor):
            renderer.AddActor(actor)
        return actor

    poly = vtk.vtkPolyData()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*GRIDS[prefix]["color"])
    actor.GetProperty().SetLineWidth(_LINE_WIDTH)
    actor.SetPickable(False)
    actor.SetVisibility(0)
    renderer.AddActor(actor)

    setattr(self, attr, actor)
    setattr(self, f"{prefix}_poly_{view}", poly)
    return actor


def _set_rect(self, prefix, view, x0, x1, y0, y1, inside=True):
    """Update a grid/view actor to a closed rectangle.

    inside=True  -> current slice crosses the grid: solid, opaque outline
    inside=False -> current slice is outside the grid: faded outline
    """
    actor = _get_actor(self, prefix, view)
    poly = getattr(self, f"{prefix}_poly_{view}")
    z = GRIDS[prefix]["z"]

    pts = vtk.vtkPoints()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        pts.InsertNextPoint(x, y, z)

    lines = vtk.vtkCellArray()
    lines.InsertNextCell(5)
    for pid in (0, 1, 2, 3, 0):
        lines.InsertCellPoint(pid)

    poly.SetPoints(pts)
    poly.SetLines(lines)
    poly.Modified()

    prop = actor.GetProperty()
    prop.SetOpacity(1.0 if inside else 0.35)
    prop.SetLineWidth(_LINE_WIDTH if inside else 1.0)
    actor.SetVisibility(1)

    _renderer(_widget(self, view)).ResetCameraClippingRange()


def _hide(self, prefix, view):
    actor = getattr(self, f"{prefix}_actor_{view}", None)
    if actor is not None:
        actor.SetVisibility(0)


def _current_index(self, attr, slider_name):
    lst = getattr(self, attr, None)
    if isinstance(lst, list) and len(lst) > 0 and lst[0] != -1:
        return lst[0]
    slider = getattr(self, slider_name, None)
    return slider.value() if slider is not None else 0


# ----------------------------------------------------------------------------
# Per-view drawing
# ----------------------------------------------------------------------------
def _view_rect(self, prefix, view):
    """
    Box of a grid on a view: (x0, x1, y0, y1) in world mm (voxel edges, as drawn) and whether the
    slice shown crosses it; None without bounds.
    """
    b = get_grid_bounds(self, prefix)
    if b is None:
        return None
    # internal order: columns, rows, slices (see get_grid_bounds)
    cmin, cmax, rmin, rmax, smin, smax = b
    ps_row, ps_col = self.pixel_spac[0, 0], self.pixel_spac[0, 1]
    st = self.slice_thick[0]
    ox, oy, oz = self.Im_Offset[0, 0], self.Im_Offset[0, 1], self.Im_Offset[0, 2]

    if view == "ax":
        curr = _current_index(self, "current_axial_slice_index", "AxialSlider")
        inside = smin - 0.5 <= curr <= smax + 0.5
        rect = (ox + (cmin - 0.5) * ps_col, ox + (cmax + 0.5) * ps_col,
                oy + (rmin - 0.5) * ps_row, oy + (rmax + 0.5) * ps_row)
    elif view == "co":
        curr = _current_index(self, "current_coronal_slice_index", "CoronalSlider")
        inside = rmin - 0.5 <= curr <= rmax + 0.5
        rect = (ox + (cmin - 0.5) * ps_col, ox + (cmax + 0.5) * ps_col,
                oz + (smin - 0.5) * st,     oz + (smax + 0.5) * st)
    else:  # "sa"
        curr = _current_index(self, "current_sagittal_slice_index", "SagittalSlider")
        inside = cmin - 0.5 <= curr <= cmax + 0.5
        rect = (oy + (rmin - 0.5) * ps_row, oy + (rmax + 0.5) * ps_row,
                oz + (smin - 0.5) * st,     oz + (smax + 0.5) * st)
    return rect, inside


def _update_view(self, prefix, view):
    try:
        if not _is_enabled(self, prefix) or not _has_image(self):
            _hide(self, prefix, view)
            return
        box = _view_rect(self, prefix, view)
        if box is None:
            _hide(self, prefix, view)
            return
        _set_rect(self, prefix, view, *box[0], inside=box[1])
    except Exception as e:
        print(f"[MC grid] {prefix}/{view} update failed: {e}")


# Called from displayaxial / displaycoronal / displaysagittal
def update_mc_grid_axial(self):
    sync_grid_limits(self)  # picks up newly loaded images (no-op if unchanged)
    for p in GRIDS:
        _update_view(self, p, "ax")


def update_mc_grid_coronal(self):
    for p in GRIDS:
        _update_view(self, p, "co")


def update_mc_grid_sagittal(self):
    for p in GRIDS:
        _update_view(self, p, "sa")


# ----------------------------------------------------------------------------
# UI callbacks
# ----------------------------------------------------------------------------
def update_grid_info(self, prefix):
    """Refresh the size label (voxels and mm) and absolute origin of one grid."""
    lbl = getattr(self, f"{prefix}_info", None)
    b = get_grid_bounds(self, prefix)
    if lbl is None or b is None:
        return
    cmin, cmax, rmin, rmax, smin, smax = b
    # UI order: X = columns, Y = slices, Z = rows
    nx, ny, nz = cmax - cmin + 1, smax - smin + 1, rmax - rmin + 1

    (ox, oy, oz), (ps_col, ps_row, st) = _ref_origin_and_spacing(self)
    sx = nx * ps_col
    sy = ny * st
    sz = nz * ps_row

    if abs(nx - round(nx)) < 1e-4 and abs(ny - round(ny)) < 1e-4 and abs(nz - round(nz)) < 1e-4:
        txt = f"{int(round(nx))} \u00d7 {int(round(ny))} \u00d7 {int(round(nz))} voxels   |   {sx:.1f} \u00d7 {sy:.1f} \u00d7 {sz:.1f} mm"
    else:
        txt = f"{nx:.1f} \u00d7 {ny:.1f} \u00d7 {nz:.1f} voxels   |   {sx:.1f} \u00d7 {sy:.1f} \u00d7 {sz:.1f} mm"

    res = get_grid_resolution(self, prefix)
    if res is not None and all(r > 0 for r in res):
        bx, by, bz = (max(1, int(np.ceil(s / r - 1e-9))) for s, r in zip((sx, sy, sz), res))
        txt += f"\nBins @ resolution: {bx} \u00d7 {by} \u00d7 {bz}  ({bx * by * bz:,} total)"

    orig = get_grid_origin_abs(self, prefix)
    if orig is not None:
        txt += f"\nOrigin (abs): X = {orig[0]:.2f}, Y = {orig[1]:.2f}, Z = {orig[2]:.2f} mm"

    lbl.setText(txt)


def update_mc_grid_all(self):
    """Redraw all MC grids on all three views and refresh info labels."""
    sync_grid_limits(self)
    for p in GRIDS:
        update_grid_info(self, p)
    if not hasattr(self, "vtkWidgetAxial"):
        return
    update_mc_grid_axial(self)
    update_mc_grid_coronal(self)
    update_mc_grid_sagittal(self)
    for view in _VIEWS:
        _widget(self, view).GetRenderWindow().Render()


# ----------------------------------------------------------------------------
# Min/Max boxes <-> range slider synchronisation and image-size clamping
# ----------------------------------------------------------------------------
def _axis_widgets(self, prefix, ax):
    return (getattr(self, f"{prefix}_{ax}min", None),
            getattr(self, f"{prefix}_{ax}max", None),
            getattr(self, f"{prefix}_{ax}slider", None))


def _sync_slider_from_spins(self, prefix, ax):
    smin, smax, sl = _axis_widgets(self, prefix, ax)
    if smin is None or smax is None or sl is None:
        return
    if is_grid_mm_mode(self, prefix):
        return
    sl.blockSignals(True)
    sl.setValues(int(round(smin.value())), int(round(smax.value())))
    sl.blockSignals(False)


def _image_extent(self):
    """Number of voxels along UI axes (X=columns, Y=slices, Z=rows), or None."""
    if not _has_image(self):
        return None
    n_slices, n_rows, n_cols = self.display_data[0].shape
    return {"x": n_cols, "y": n_slices, "z": n_rows}


def sync_mc_vox_resolution(self):
    """Ensure the voxelization grid resolution matches the voxel size of the image."""
    try:
        (ox, oy, oz), (ps_col, ps_row, st) = _ref_origin_and_spacing(self)
        # UI order: X = columns (sagittal), Y = slices (axial), Z = rows (coronal)
        spacing = {"x": ps_col, "y": st, "z": ps_row}
        for ax, s in spacing.items():
            sb = getattr(self, f"mc_vox_{ax}res", None)
            if sb is not None and s > 0:
                if abs(sb.value() - s) > 1e-9:
                    sb.blockSignals(True)
                    sb.setValue(s)
                    sb.blockSignals(False)
    except Exception:
        pass


def sync_grid_limits(self):
    """Clamp boxes and sliders to the current image size.

    Cheap to call often: only does work when the image size changes.
    When a new image appears and a grid is still untouched (all zeros),
    it is initialised to cover the whole image.
    """
    sync_mc_vox_resolution(self)
    ext = _image_extent(self)
    key = None if ext is None else (ext["x"], ext["y"], ext["z"])
    if key == getattr(self, "_mc_grid_extent_key", "unset"):
        return
    self._mc_grid_extent_key = key
    if ext is None:
        return  # no image: keep current limits

    for prefix in GRIDS:
        untouched = all(getattr(self, f, None) is not None and getattr(self, f).value() == 0
                        for f in _fields(prefix))
        for ax in "xyz":
            smin, smax, sl = _axis_widgets(self, prefix, ax)
            if smin is None or smax is None:
                continue
            top = max(0, ext[ax] - 1)
            if prefix == "mc_vox":
                # Voxelization grid is strictly voxels within the image
                for w in (smin, smax):
                    w.blockSignals(True)
                    w.setRange(0, top)
                if untouched:
                    smin.setValue(0)
                    smax.setValue(top)
                for w in (smin, smax):
                    w.blockSignals(False)
            else:
                # Calculation grid does not have to overlap with image
                for w in (smin, smax):
                    w.setRange(-99999.0, 99999.0)
                if untouched:
                    if is_grid_mm_mode(self, prefix):
                        (ox, oy, oz), (ps_col, ps_row, st) = _ref_origin_and_spacing(self)
                        orig = {"x": ox, "y": oz, "z": 0.0 - oy - top * ps_row}[ax]   # Z = -DICOM y
                        sp = {"x": ps_col, "y": st, "z": ps_row}[ax]
                        smin.setValue(orig)
                        smax.setValue(orig + top * sp)
                    else:
                        smin.setValue(0)
                        smax.setValue(top)

            if sl is not None:
                sl.blockSignals(True)
                sl.setRange(0, top)
                sl.blockSignals(False)
            _sync_slider_from_spins(self, prefix, ax)
        update_grid_info(self, prefix)


def on_grid_spin_changed(self, prefix, ax, kind):
    """User typed in a Min/Max box: keep min <= max, update slider, redraw."""
    smin, smax, _ = _axis_widgets(self, prefix, ax)
    if smin is None or smax is None:
        return
    if smin.value() > smax.value():
        other = smax if kind == "min" else smin
        other.blockSignals(True)
        other.setValue(smin.value() if kind == "min" else smax.value())
        other.blockSignals(False)
    _sync_slider_from_spins(self, prefix, ax)
    update_mc_grid_all(self)


def on_grid_slider_changed(self, prefix, ax, low, high):
    """User dragged the range slider: update Min/Max boxes, redraw."""
    if is_grid_mm_mode(self, prefix):
        return
    smin, smax, _ = _axis_widgets(self, prefix, ax)
    if smin is None or smax is None:
        return
    for w, v in ((smin, low), (smax, high)):
        w.blockSignals(True)
        w.setValue(float(v) if isinstance(w, QDoubleSpinBox) else int(v))
        w.blockSignals(False)
    update_mc_grid_all(self)


def _set_fields(self, prefix, values):
    for f, v in zip(_fields(prefix), values):
        sb = getattr(self, f)
        sb.blockSignals(True)
        sb.setValue(float(v) if isinstance(sb, QDoubleSpinBox) else int(round(v)))
        sb.blockSignals(False)
    for ax in "xyz":
        _sync_slider_from_spins(self, prefix, ax)
    update_mc_grid_all(self)


def grid_fit_to_image(self, prefix):
    """Set a grid to cover the whole image of layer 0 at the image voxel spacing."""
    if not _has_image(self):
        return
    n_slices, n_rows, n_cols = self.display_data[0].shape
    (ox, oy, oz), (ps_col, ps_row, st) = _ref_origin_and_spacing(self)

    # Resolution
    spacing = (ps_col, st, ps_row)
    for a, s in zip("xyz", spacing):
        sb = getattr(self, f"{prefix}_{a}res", None)
        if sb is not None and s > 0:
            sb.blockSignals(True)
            sb.setValue(s)
            sb.blockSignals(False)

    if is_grid_mm_mode(self, prefix):
        vals = (ox, ox + (n_cols - 1) * ps_col,
                oz, oz + (n_slices - 1) * st,
                0.0 - oy - (n_rows - 1) * ps_row, 0.0 - oy)     # Z = -DICOM y
    else:
        vals = (0, n_cols - 1, 0, n_slices - 1, 0, n_rows - 1)

    _set_fields(self, prefix, vals)


def mc_grid_fit_to_image(self):
    grid_fit_to_image(self, "mc_grid")


def mc_vox_fit_to_image(self):
    grid_fit_to_image(self, "mc_vox")


def mc_grid_set_ref_resolution(self):
    """Set calculation grid resolution to match the reference image voxel size without changing bounds."""
    (ox, oy, oz), (ps_col, ps_row, st) = _ref_origin_and_spacing(self)
    # UI order: x -> cols (ps_col), y -> slices (st), z -> rows (ps_row)
    spacing = {"x": ps_col, "y": st, "z": ps_row}
    for ax, s in spacing.items():
        sb = getattr(self, f"mc_grid_{ax}res", None)
        if sb is not None and s > 0:
            sb.blockSignals(True)
            sb.setValue(s)
            sb.blockSignals(False)
    update_mc_grid_all(self)
    update_grid_info(self, "mc_grid")


def on_grid_mode_changed(self, mode):
    """Switch the calculation grid between 'voxel' and 'mm' modes."""
    prefix = "mc_grid"
    names = _fields(prefix)
    if not all(hasattr(self, f) for f in names):
        return

    (ox, oy, oz), (ps_col, ps_row, st) = _ref_origin_and_spacing(self)

    h_min = getattr(self, f"{prefix}_header_min", None)
    h_max = getattr(self, f"{prefix}_header_max", None)
    lbl_x = getattr(self, f"{prefix}_lbl_x", None)
    lbl_y = getattr(self, f"{prefix}_lbl_y", None)
    lbl_z = getattr(self, f"{prefix}_lbl_z", None)

    if mode == "mm":
        # Switching from voxel -> mm
        if h_min is not None: h_min.setText(u"Min (mm)")
        if h_max is not None: h_max.setText(u"Max (mm)")
        if lbl_x is not None: lbl_x.setText(u"X (DICOM X):")
        if lbl_y is not None: lbl_y.setText(u"Y (DICOM Z):")
        if lbl_z is not None: lbl_z.setText(u"Z (-DICOM Y):")

        # Read current voxel values
        vx_min = getattr(self, f"{prefix}_xmin").value()
        vx_max = getattr(self, f"{prefix}_xmax").value()
        vy_min = getattr(self, f"{prefix}_ymin").value()
        vy_max = getattr(self, f"{prefix}_ymax").value()
        vz_min = getattr(self, f"{prefix}_zmin").value()
        vz_max = getattr(self, f"{prefix}_zmax").value()

        # Convert to mm (Z: -DICOM y of the rows as stored)
        z_a, z_b = _ui_z_of_row(self, vz_min, oy, ps_row), _ui_z_of_row(self, vz_max, oy, ps_row)
        mm_vals = {
            f"{prefix}_xmin": ox + vx_min * ps_col,
            f"{prefix}_xmax": ox + vx_max * ps_col,
            f"{prefix}_ymin": oz + vy_min * st,
            f"{prefix}_ymax": oz + vy_max * st,
            f"{prefix}_zmin": min(z_a, z_b),
            f"{prefix}_zmax": max(z_a, z_b),
        }

        for f in names:
            sb = getattr(self, f)
            sb.blockSignals(True)
            sb.setDecimals(MM_DECIMALS)
            sb.setSingleStep(1.0)
            sb.setRange(-99999.0, 99999.0)
            sb.setValue(mm_vals[f])
            sb.blockSignals(False)

        # Disable sliders in mm mode
        for ax in "xyz":
            sl = getattr(self, f"{prefix}_{ax}slider", None)
            if sl is not None:
                sl.setEnabled(False)

    else:
        # Switching from mm -> voxel
        if h_min is not None: h_min.setText(u"Min (vox)")
        if h_max is not None: h_max.setText(u"Max (vox)")
        if lbl_x is not None: lbl_x.setText(u"X (columns):")
        if lbl_y is not None: lbl_y.setText(u"Y (slices):")
        if lbl_z is not None: lbl_z.setText(u"Z (rows):")

        # Read current mm values
        mmx_min = getattr(self, f"{prefix}_xmin").value()
        mmx_max = getattr(self, f"{prefix}_xmax").value()
        mmy_min = getattr(self, f"{prefix}_ymin").value()
        mmy_max = getattr(self, f"{prefix}_ymax").value()
        mmz_min = getattr(self, f"{prefix}_zmin").value()
        mmz_max = getattr(self, f"{prefix}_zmax").value()

        # Convert to voxels (Z: rows as stored of the -DICOM y)
        r_a, r_b = _row_of_ui_z(self, mmz_min, oy, ps_row), _row_of_ui_z(self, mmz_max, oy, ps_row)
        vox_vals = {
            f"{prefix}_xmin": round((mmx_min - ox) / (ps_col if ps_col > 0 else 1.0)),
            f"{prefix}_xmax": round((mmx_max - ox) / (ps_col if ps_col > 0 else 1.0)),
            f"{prefix}_ymin": round((mmy_min - oz) / (st if st > 0 else 1.0)),
            f"{prefix}_ymax": round((mmy_max - oz) / (st if st > 0 else 1.0)),
            f"{prefix}_zmin": round(min(r_a, r_b)),
            f"{prefix}_zmax": round(max(r_a, r_b)),
        }

        for f in names:
            sb = getattr(self, f)
            sb.blockSignals(True)
            sb.setDecimals(0)
            sb.setSingleStep(1.0)
            sb.setRange(-99999.0, 99999.0)
            sb.setValue(vox_vals[f])
            sb.blockSignals(False)

        # Re-enable sliders in voxel mode
        for ax in "xyz":
            sl = getattr(self, f"{prefix}_{ax}slider", None)
            if sl is not None:
                sl.setEnabled(True)
            _sync_slider_from_spins(self, prefix, ax)

    update_mc_grid_all(self)


# ----------------------------------------------------------------------------
# Calculation grid from a dose (RTDOSE or MCNP series)
# ----------------------------------------------------------------------------
DOSE_MODALITIES = ("RTDOSE", "MCNP")


def series_grid(series):
    """(ImagePositionPatient, (ps_col, ps_row, st), (n_slices, n_rows, n_cols)) of a series volume; None."""
    if not isinstance(series, dict):
        return None
    meta = series.get("metadata") or {}
    try:
        ns, nr, nc = series["3DMatrix"].shape
        ipp = tuple(float(v) for v in meta["ImagePositionPatient"][:3])
        ps_row, ps_col = (float(v) for v in meta["PixelSpacing"][:2])
        st = float(meta["SliceThickness"])
    except (AttributeError, KeyError, TypeError, ValueError):
        return None
    if min(ps_col, ps_row, st) <= 0 or len(ipp) != 3:
        return None
    return ipp, (ps_col, ps_row, st), (int(ns), int(nr), int(nc))


def dose_series(self):
    """(label, series) of the RTDOSE and MCNP series of the patient shown that hold a volume."""
    studies = (getattr(self, "medical_image", None) or {}).get(getattr(self, "patientID", None)) or {}
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
                _, (sx, sy, sz), (ns, nr, nc) = grid
                name = (series.get("metadata") or {}).get("SeriesDescription") or f"Series {series.get('SeriesNumber', k + 1)}"
                label = f"{modality}: {name}  ({nc} x {ns} x {nr} voxels of {sx:g} x {sz:g} x {sy:g} mm)"
                out.append((f"Study {sid} / {label}" if several else label, series))
    return out


def mc_grid_from_dose(self, series):
    """
    Calculation grid = the voxels of a dose series: mm mode, resolution = its voxel size, and the
    boxes (first / last voxel centres of the CT, the MCNP mesh adding half a CT voxel, mcnp_input) set
    so that the mesh runs from the lower edge of its first voxel to the upper edge of its last one.
    False if the series has no volume geometry.
    """
    grid = series_grid(series)
    if grid is None or not all(hasattr(self, f) for f in _fields("mc_grid")):
        return False
    (x0, y0, z0), (sx, sy, sz), (ns, nr, nc) = grid
    from fcn_mcnp.mcnp_input import ct_origin_and_spacing, input_ct
    ct = input_ct(self)
    _, (ps_col, ps_row, st) = ct_origin_and_spacing(self, ct) if ct is not None else _ref_origin_and_spacing(self)
    combo = getattr(self, "mc_grid_mode_combo", None)
    if combo is not None and combo.currentText() != "mm":
        combo.blockSignals(True)
        combo.setCurrentText("mm")
        combo.blockSignals(False)
        on_grid_mode_changed(self, "mm")     # labels, decimals and sliders of mm mode
    for ax, s in zip("xyz", (sx, sz, sy)):  # UI X = DICOM x, Y = DICOM z (slices), Z = -DICOM y (rows)
        sb = getattr(self, f"mc_grid_{ax}res", None)
        if sb is not None:
            sb.blockSignals(True)
            sb.setValue(s)
            sb.blockSignals(False)
    _set_fields(self, "mc_grid", (x0 - sx / 2 + ps_col / 2, x0 + (nc - 0.5) * sx - ps_col / 2,
                                  z0 - sz / 2 + st / 2, z0 + (ns - 0.5) * sz - st / 2,
                                  ps_row / 2 - y0 - (nr - 0.5) * sy, sy / 2 - y0 - ps_row / 2))
    return True


def mc_grid_import_dose_menu(self, button=None):
    """'Import from dose': a menu of the dose series of the patient shown; the one picked sets the calculation grid."""
    button = button or getattr(self, "mc_grid_from_dose_btn", None)
    menu = QMenu(button)
    doses = dose_series(self)
    for label, series in doses:
        menu.addAction(label).triggered.connect(lambda checked=False, s=series: mc_grid_from_dose(self, s))
    if not doses:
        menu.addAction("No RTDOSE or MCNP dose for the patient shown").setEnabled(False)
    menu.exec(button.mapToGlobal(button.rect().bottomLeft()) if button is not None else QCursor.pos())


# ----------------------------------------------------------------------------
# Dragging the boxes on the views (MonteCarlo > GRID, Display checked)
# ----------------------------------------------------------------------------
GRAB_TOL_PX = 8                 # an edge grabs the mouse within this many pixels
DRAG_REDRAW_INTERVAL = 0.04     # s between redraws while dragging
# UI axes along the world x and y of each view (X = columns, Y = slices, Z = rows as stored)
VIEW_AXES = {"ax": ("x", "z"), "co": ("x", "y"), "sa": ("z", "y")}
_VIEW_WIDGETS = (("ax", "vtkWidgetAxial"), ("co", "vtkWidgetCoronal"), ("sa", "vtkWidgetSagittal"))
_BUTTON_DOWN = ("LeftButtonAxialDown", "LeftButtonCoronalDown", "LeftButtonSagittalDown")


def grid_handle(rect, mouse, tol):
    """
    What of a box (x0, x1, y0, y1) the mouse (world x, y) grabs: the edges within tol, e.g.
    {'x0'} or {'x1', 'y0'} at a corner, {'move'} inside, None outside.
    """
    x0, x1, y0, y1 = rect
    mx, my = mouse
    if not (x0 - tol <= mx <= x1 + tol and y0 - tol <= my <= y1 + tol):
        return None
    dist = {"x0": abs(mx - x0), "x1": abs(mx - x1), "y0": abs(my - y0), "y1": abs(my - y1)}
    edges = {e for e, d in dist.items() if d <= tol}
    for lo, hi in (("x0", "x1"), ("y0", "y1")):
        if lo in edges and hi in edges:     # a thin box: the nearer edge
            edges.discard(hi if dist[hi] > dist[lo] else lo)
    if edges:
        return frozenset(edges)
    return frozenset({"move"}) if x0 < mx < x1 and y0 < my < y1 else None


def dragged_values(values, view, handle, delta, steps):
    """
    The 6 box values (X min, X max, Y min, Y max, Z min, Z max) after dragging 'handle' (grid_handle)
    of the box on 'view' by delta (world mm along the view's x, y). steps[ax]: world mm per unit of
    the values of an axis (its voxel size in voxel mode, 1 in mm mode); the values of every axis
    grow with the world coordinates (mm mode Z = -DICOM y runs with the rows as stored).
    """
    out = list(values)
    for k, ax in enumerate(VIEW_AXES[view]):
        i = "xyz".index(ax) * 2
        d = delta[k] / steps[ax]
        if "move" in handle:
            out[i] += d
            out[i + 1] += d
        else:
            if f"{'xy'[k]}0" in handle:
                out[i] += d
            if f"{'xy'[k]}1" in handle:
                out[i + 1] += d
    return out


def _event_world_xy(renderer, x, y):
    """Display position -> world (x, y) of a 2D view."""
    renderer.SetDisplayPoint(x, y, 0)
    renderer.DisplayToWorld()
    wp = renderer.GetWorldPoint()
    if wp[3] != 0.0:
        return np.array([wp[0] / wp[3], wp[1] / wp[3]])
    return np.array([wp[0], wp[1]])


def _drag_steps(self, mm_mode):
    """steps of dragged_values for a grid in voxel or mm mode (layer 0 voxels)."""
    if mm_mode:
        return {"x": 1.0, "y": 1.0, "z": 1.0}
    ps_row, ps_col, st = float(self.pixel_spac[0, 0]), float(self.pixel_spac[0, 1]), float(self.slice_thick[0])
    return {"x": ps_col, "y": st, "z": ps_row}


def _grab(self, view, interactor):
    """(grid prefix, handle, mouse world xy) of the displayed box under the mouse on a view, or None."""
    if not _mc_tab_active(self) or not _has_image(self):
        return None
    renderer = _renderer(_widget(self, view))
    x, y = interactor.GetEventPosition()
    mouse = _event_world_xy(renderer, x, y)
    tol = abs(_event_world_xy(renderer, x + GRAB_TOL_PX, y)[0] - mouse[0])
    best = None
    for prefix in GRIDS:
        box = _view_rect(self, prefix, view) if _is_enabled(self, prefix) else None
        handle = None if box is None else grid_handle(box[0], mouse, tol)
        if handle is None:
            continue
        x0, x1, y0, y1 = box[0]
        rank = ("move" in handle, (x1 - x0) * (y1 - y0))      # edges first, then the smaller box
        if best is None or rank < best[0]:
            best = (rank, prefix, handle)
    return None if best is None else (best[1], best[2], mouse)


def _cursor_shape(handle):
    if "move" in handle:
        return Qt.CursorShape.SizeAllCursor
    if len(handle) == 2:   # corner; world y runs up on the screen
        return Qt.CursorShape.SizeBDiagCursor if handle in ({"x0", "y0"}, {"x1", "y1"}) else Qt.CursorShape.SizeFDiagCursor
    return Qt.CursorShape.SizeHorCursor if next(iter(handle))[0] == "x" else Qt.CursorShape.SizeVerCursor


def _set_drag_values(self, drag, delta):
    """Box values of a drag: whole voxels in voxel mode, within the ranges of the boxes, min <= max."""
    prefix, v0 = drag["prefix"], drag["values"]
    values = dragged_values(v0, drag["view"], drag["handle"], delta, drag["steps"])
    boxes = [getattr(self, f) for f in _fields(prefix)]
    for i in (0, 2, 4):
        lo, hi = values[i], values[i + 1]
        if not drag["mm"]:
            lo, hi = float(round(lo)), float(round(hi))
        bottom, top = boxes[i].minimum(), boxes[i + 1].maximum()
        if "move" in drag["handle"]:
            shift = min(max(lo, bottom), top - (hi - lo)) - lo      # the box keeps its size
            lo, hi = lo + shift, hi + shift
        else:
            lo, hi = min(max(lo, bottom), top), min(max(hi, bottom), top)
            if lo > hi:     # an edge stops at the other one
                lo, hi = (hi, hi) if lo != v0[i] else (lo, lo)
        for sb, v in ((boxes[i], lo), (boxes[i + 1], hi)):
            sb.blockSignals(True)
            sb.setValue(v if isinstance(sb, QDoubleSpinBox) else int(v))
            sb.blockSignals(False)
    for ax in "xyz":
        _sync_slider_from_spins(self, prefix, ax)


def on_mc_grid_press(self, view, interactor):
    if getattr(self, "_mc_grid_drag", None) is not None:
        return
    grab = _grab(self, view, interactor)
    if grab is None:
        return      # not on a box: left-drag stays window/level
    prefix, handle, mouse = grab
    mm_mode = is_grid_mm_mode(self, prefix)
    self._mc_grid_drag = {"prefix": prefix, "view": view, "handle": handle, "mouse0": mouse, "mm": mm_mode,
                          "values": [float(getattr(self, f).value()) for f in _fields(prefix)],
                          "steps": _drag_steps(self, mm_mode), "last_draw": 0.0}
    self._text_dragging = True      # window/level and the other left-drag handlers skip
    QApplication.setOverrideCursor(_cursor_shape(handle))


def on_mc_grid_move(self, view, interactor):
    drag = getattr(self, "_mc_grid_drag", None)
    if drag is None:
        _hover(self, view, interactor)
        return
    if drag["view"] != view:
        return
    x, y = interactor.GetEventPosition()
    _set_drag_values(self, drag, _event_world_xy(_renderer(_widget(self, view)), x, y) - drag["mouse0"])
    now = time.perf_counter()
    if now - drag["last_draw"] >= DRAG_REDRAW_INTERVAL:
        drag["last_draw"] = now
        update_mc_grid_all(self)


def on_mc_grid_release(self, view, interactor):
    if getattr(self, "_mc_grid_drag", None) is None:
        return
    self._mc_grid_drag = None
    self._text_dragging = False
    QApplication.restoreOverrideCursor()
    update_mc_grid_all(self)


def _hover(self, view, interactor):
    """Cursor over a box: resize arrows on its edges and corners, move arrows inside."""
    cursors = getattr(self, "_mc_grid_cursor", None)
    if cursors is None:
        cursors = self._mc_grid_cursor = {}
    grab = None
    if not getattr(self, "_text_dragging", False) and not any(getattr(self, b, False) for b in _BUTTON_DOWN):
        grab = _grab(self, view, interactor)
    shape = None if grab is None else _cursor_shape(grab[1])
    if shape == cursors.get(view):
        return
    widget = _widget(self, view)
    if shape is None:
        widget.unsetCursor()
    else:
        widget.setCursor(shape)
    cursors[view] = shape


def add_mc_grid_drag_observers(self):
    """
    Mouse observers dragging the grid boxes. Priority 1 runs them before the window/level handlers
    (priority 0), which skip while self._text_dragging is set.
    """
    self._mc_grid_drag = None
    for view, attr in _VIEW_WIDGETS:
        widget = getattr(self, attr, None)
        if widget is None:
            continue
        widget.AddObserver("LeftButtonPressEvent", lambda caller, event, v=view: on_mc_grid_press(self, v, caller), 1.0)
        widget.AddObserver("MouseMoveEvent", lambda caller, event, v=view: on_mc_grid_move(self, v, caller), 1.0)
        widget.AddObserver("LeftButtonReleaseEvent", lambda caller, event, v=view: on_mc_grid_release(self, v, caller), 1.0)
