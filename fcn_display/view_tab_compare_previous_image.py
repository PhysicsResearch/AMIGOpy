import numpy as np
from fcn_display.win_level import set_window

def _is_binary_volume(a: np.ndarray) -> bool:
    """True if volume is binary (0/1 or bool), tolerant to float noise."""
    if a.dtype == np.bool_:
        return True
    m = float(np.nanmin(a)); M = float(np.nanmax(a))
    # quick rejects outside [0,1]
    if m < -1e-6 or M > 1 + 1e-6:
        return False
    if np.issubdtype(a.dtype, np.integer):
        return M <= 1.0
    # floats: unique values must be ~0 and/or ~1
    u = np.unique(a[~np.isnan(a)])
    if u.size == 1:
        return np.isclose(u[0], 0.0, atol=1e-6) or np.isclose(u[0], 1.0, atol=1e-6)
    if u.size == 2:
        return np.isclose(u[0], 0.0, atol=1e-6) and np.isclose(u[1], 1.0, atol=1e-6)
    return False


def reset_views_camera(self, idx):
    """
    Reset the 2D view cameras to specifically fit the active layer's image actor,
    preventing empty or different-scale layers (e.g. 100mm placeholders vs 8.5mm microCT)
    from distorting the camera zoom and placement.
    """
    for ren, actors in [
        (getattr(self, 'renAxial', None), getattr(self, 'imageActorAxial', None)),
        (getattr(self, 'renSagittal', None), getattr(self, 'imageActorSagittal', None)),
        (getattr(self, 'renCoronal', None), getattr(self, 'imageActorCoronal', None)),
    ]:
        if ren is None:
            continue
        reset_done = False
        if actors is not None and 0 <= idx < len(actors):
            act = actors[idx]
            if act is not None:
                b = act.GetBounds()
                # Check valid 2D bounds (at least one lateral dimension has non-zero width)
                if b and ((b[1] - b[0]) > 1e-4 or (b[3] - b[2]) > 1e-4):
                    ren.ResetCamera(b)
                    cam = ren.GetActiveCamera()
                    cr = cam.GetClippingRange()
                    cam.SetClippingRange(min(cr[0], 0.01), max(cr[1], 1000.0))
                    reset_done = True
        if not reset_done:
            ren.ResetCamera()
            cam = ren.GetActiveCamera()
            cr = cam.GetClippingRange()
            cam.SetClippingRange(min(cr[0], 0.01), max(cr[1], 1000.0))


def compare_view_previous(self, Window, Level, idx, num_layers=4):
    """
    Per-layer comparison & actions:
      • First time for layer idx: set_window(..), ResetCamera(bounds), Render()
      • If PixelSpacing / IPP / SliceThickness are MISSING or CHANGED: ResetCamera(bounds)
      • If min/max/mean changed >50% or binary volume: set_window(..)
      • Stores per-layer snapshot in self.view_previous_image[idx]
    """
    # ---- guard layer index ----
    if idx is None or idx < 0 or idx >= num_layers:
        return

    # ---- ensure per-layer container ----
    if not hasattr(self, 'view_previous_image') or not isinstance(self.view_previous_image, list):
        self.view_previous_image = [None] * num_layers
    elif len(self.view_previous_image) != num_layers:
        buf = [None] * num_layers
        for i in range(min(num_layers, len(self.view_previous_image))):
            buf[i] = self.view_previous_image[i]
        self.view_previous_image = buf

    # ---- gather current metrics (robust to missing metadata) ----
    meta = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index].get('metadata', {})

    def _safe_tuple(m, key, n):
        v = m.get(key, None)
        if v is None:
            return None
        try:
            return tuple(float(v[i]) for i in range(n))
        except Exception:
            try:
                return tuple(float(x) for x in list(v)[:n])
            except Exception:
                return None

    def _safe_float(m, key):
        v = m.get(key, None)
        try:
            return float(v)
        except Exception:
            return None

    px  = _safe_tuple(meta, 'PixelSpacing', 2)              # (row, col) or None
    ipp = _safe_tuple(meta, 'ImagePositionPatient', 3)      # (x, y, z) or None
    thk = _safe_float(meta, 'SliceThickness')               # float or None

    arr3d = self.display_data[idx]
    # For large volumes (e.g. microCT), subsample in 3D first to avoid freezing UI
    if arr3d.size > 2_000_000:
        step = max(1, int(round((arr3d.size / 500_000) ** (1.0 / 3.0))))
        sample = arr3d[::step, ::step, ::step]
    else:
        sample = arr3d

    cur_min  = float(np.nanmin(sample))
    cur_max  = float(np.nanmax(sample))
    cur_mean = float(np.nanmean(sample))

    current = {
        'pixel_spacing': px,
        'image_position_patient': ipp,
        'slice_thickness': thk,
        'min': cur_min,
        'max': cur_max,
        'mean': cur_mean,
    }

    def _derive_wl():
        # Force WL for binary volumes
        if _is_binary_volume(arr3d):
            return -10.0, -0.1
        # Otherwise use provided W/L or min/max fallback
        W = Window if Window is not None else max(cur_max - cur_min, 1.0)
        L = Level  if Level  is not None else (cur_max + cur_min) / 2.0
        return float(W), float(L)

    def _rel_changed(old_v, new_v, tol=0.5):
        try:
            old_v = float(old_v); new_v = float(new_v)
        except Exception:
            return True
        if old_v == 0.0:
            return abs(new_v) > 0.0
        return abs(new_v - old_v) / abs(old_v) > tol

    prev = self.view_previous_image[idx]

    # ---- first time for this layer: do WL + camera reset + render ----
    if prev is None:
        W, L = _derive_wl()
        set_window(self, W, L)
        reset_views_camera(self, idx)
        self.vtkWidgetAxial.GetRenderWindow().Render()
        self.vtkWidgetSagittal.GetRenderWindow().Render()
        self.vtkWidgetCoronal.GetRenderWindow().Render()
        self.view_previous_image[idx] = current
        return

    # ---- subsequent calls: compare + act ---------------------------
    # If *any* geometry field is missing now -> always reset camera
    missing_any_now = (px is None or ipp is None or thk is None)
    # Or if any geometry field was missing before -> also reset camera
    missing_any_prev = (
        prev.get('pixel_spacing') is None or
        prev.get('image_position_patient') is None or
        prev.get('slice_thickness') is None
    )

    if missing_any_now or missing_any_prev:
        geom_changed = True
    else:
        geom_changed = (
            prev['pixel_spacing'] != px or
            prev['image_position_patient'] != ipp or
            prev['slice_thickness'] != thk
        )

    wl_changed = (
        _rel_changed(prev.get('mean', 0.0), cur_mean, 0.5) or
        _rel_changed(prev.get('min', 0.0),  cur_min,  0.5) or
        _rel_changed(prev.get('max', 0.0),  cur_max,  0.5)
    )

    did_anything = False

    # Always apply WL for binary volumes, or when stats changed greatly
    if wl_changed or _is_binary_volume(arr3d):
        W, L = _derive_wl()
        set_window(self, W, L)
        did_anything = True

    if geom_changed:
        reset_views_camera(self, idx)
        did_anything = True

    if did_anything:
        self.vtkWidgetAxial.GetRenderWindow().Render()
        self.vtkWidgetSagittal.GetRenderWindow().Render()
        self.vtkWidgetCoronal.GetRenderWindow().Render()

    # Update snapshot
    self.view_previous_image[idx] = current
