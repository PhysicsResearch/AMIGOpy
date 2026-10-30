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
while the MonteCarlo tab is the selected tab.

NOTE: this module must NOT import fcn_display.display_images at module
level (display_images imports this module -> circular import).
"""

import numpy as np
import vtk
from PySide6.QtWidgets import QDoubleSpinBox

# prefix -> appearance
GRIDS = {
    "mc_grid": {"color": (1.0, 0.85, 0.0), "z": 1.00, "name": "Calculation grid"},
    "mc_vox":  {"color": (1.0, 0.15, 0.15), "z": 1.05, "name": "Voxelization grid"},
}

_LINE_WIDTH = 2.0
_VIEWS = ("ax", "co", "sa")


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def _fields(prefix):
    return tuple(f"{prefix}_{a}{k}" for a in "xyz" for k in ("min", "max"))


def _ref_origin_and_spacing(self):
    """Return (ox, oy, oz), (ps_col, ps_row, st) for reference image (layer 0)."""
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
        rmin = (zmin - oy) / (ps_row if ps_row > 0 else 1.0)
        rmax = (zmax - oy) / (ps_row if ps_row > 0 else 1.0)
    else:
        cmin, cmax = xmin, xmax
        smin, smax = ymin, ymax
        rmin, rmax = zmin, zmax

    cmin, cmax = sorted((cmin, cmax))   # X -> columns
    smin, smax = sorted((smin, smax))   # Y -> slices
    rmin, rmax = sorted((rmin, rmax))   # Z -> rows
    return cmin, cmax, rmin, rmax, smin, smax


def get_grid_origin_abs(self, prefix):
    """Return (origin_x, origin_y, origin_z) in absolute DICOM mm, or None."""
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
        orig_x = min(xmin, xmax)
        orig_y = min(zmin, zmax)  # UI Z is row -> DICOM Y
        orig_z = min(ymin, ymax)  # UI Y is slice -> DICOM Z
    else:
        cmin = min(xmin, xmax)
        smin = min(ymin, ymax)
        rmin = min(zmin, zmax)
        orig_x = ox + cmin * ps_col
        orig_y = oy + rmin * ps_row
        orig_z = oz + smin * st

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
def _update_view(self, prefix, view):
    try:
        b = get_grid_bounds(self, prefix)
        if b is None or not _is_enabled(self, prefix) or not _has_image(self):
            _hide(self, prefix, view)
            return
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

        _set_rect(self, prefix, view, *rect, inside=inside)
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
                        orig = {"x": ox, "y": oz, "z": oy}[ax]
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
                oy, oy + (n_rows - 1) * ps_row)
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
        if lbl_z is not None: lbl_z.setText(u"Z (DICOM Y):")

        # Read current voxel values
        vx_min = getattr(self, f"{prefix}_xmin").value()
        vx_max = getattr(self, f"{prefix}_xmax").value()
        vy_min = getattr(self, f"{prefix}_ymin").value()
        vy_max = getattr(self, f"{prefix}_ymax").value()
        vz_min = getattr(self, f"{prefix}_zmin").value()
        vz_max = getattr(self, f"{prefix}_zmax").value()

        # Convert to mm
        mm_vals = {
            f"{prefix}_xmin": ox + vx_min * ps_col,
            f"{prefix}_xmax": ox + vx_max * ps_col,
            f"{prefix}_ymin": oz + vy_min * st,
            f"{prefix}_ymax": oz + vy_max * st,
            f"{prefix}_zmin": oy + vz_min * ps_row,
            f"{prefix}_zmax": oy + vz_max * ps_row,
        }

        for f in names:
            sb = getattr(self, f)
            sb.blockSignals(True)
            sb.setDecimals(2)
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

        # Convert to voxels
        vox_vals = {
            f"{prefix}_xmin": round((mmx_min - ox) / (ps_col if ps_col > 0 else 1.0)),
            f"{prefix}_xmax": round((mmx_max - ox) / (ps_col if ps_col > 0 else 1.0)),
            f"{prefix}_ymin": round((mmy_min - oz) / (st if st > 0 else 1.0)),
            f"{prefix}_ymax": round((mmy_max - oz) / (st if st > 0 else 1.0)),
            f"{prefix}_zmin": round((mmz_min - oy) / (ps_row if ps_row > 0 else 1.0)),
            f"{prefix}_zmax": round((mmz_max - oy) / (ps_row if ps_row > 0 else 1.0)),
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

