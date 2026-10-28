# -*- coding: utf-8 -*-
"""
mat_overlay.py - live material-assignment overlay
=================================================

While View > MonteCarlo > Material Assignment is the selected tab, the
material assignment is painted as a coloured, semi-transparent mask on the
axial / coronal / sagittal views:

  * rows of the "Materials to HU ranges" table   (HU thresholds of layer 0)
  * rows of the "Materials to structures" table  (structure masks)

Only rows whose "Show" checkbox is ticked are drawn, each with its own
colour. As in generate_mat_map(), later HU rows override earlier ones and
structures override HU ranges.

NOTE: must NOT import fcn_display.display_images at module level
(display_images imports this module).
"""

import numpy as np
import vtk

_ALPHA = 0.45          # overlay opacity of each assigned voxel
_VIEWS = ("ax", "co", "sa")


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def mat_overlay_active(self):
    """True only when View > MonteCarlo > Material Assignment is selected."""
    tabs = getattr(self, "tabView01", None)
    mc = getattr(self, "tab_montecarlo", None)
    sub = getattr(self, "mc_tabs", None)
    mat_tab = getattr(self, "tab_mat_assignment", None)
    if tabs is None or mc is None or sub is None or mat_tab is None:
        return False
    if tabs.currentWidget() is not mc or sub.currentWidget() is not mat_tab:
        return False
    mods = getattr(self, "tabModules", None)
    if mods is not None and mods.tabText(mods.currentIndex()) != "View":
        return False
    return True


def hex_to_rgb255(h):
    try:
        s = str(h).strip().lstrip("#")
        if len(s) == 3:
            s = "".join(c * 2 for c in s)
        return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    except Exception:
        return 255, 0, 0


def _volume(self):
    dd = getattr(self, "display_data", None)
    try:
        v = dd[0]
        return v if isinstance(v, np.ndarray) and v.ndim == 3 else None
    except Exception:
        return None


def _structure_masks(self, shape):
    """{structure name: Mask3D} of the current series (only matching shape)."""
    try:
        series = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]
    except Exception:
        return {}
    out = {}
    for sdat in (series.get("structures") or {}).values():
        name = sdat.get("Name")
        m = sdat.get("Mask3D")
        if name and isinstance(m, np.ndarray) and m.shape == shape:
            out[name] = m
    return out


def _layers(self):
    """Ordered list of ('hu', (lo, hi), rgb) / ('struct', name, rgb) to paint."""
    layers = []
    for d in getattr(self, "mat_HU_list", None) or []:
        if (d.get("visible", True) and d.get("key") is not None
                and d.get("min") is not None and d.get("max") is not None
                and d["min"] < d["max"]):
            layers.append(("hu", (d["min"], d["max"]), hex_to_rgb255(d.get("color"))))
    view = getattr(self, "mat_struct_view", {}) or {}
    for s_name, d in (getattr(self, "mat_struct", None) or {}).items():
        v = view.get(s_name, {})
        if v.get("visible", True):
            layers.append(("struct", s_name, hex_to_rgb255(v.get("color"))))
    return layers


def _build_rgba(self, view):
    vol = _volume(self)
    if vol is None:
        return None
    try:
        if view == "ax":
            i = int(self.current_axial_slice_index[0])
            if not 0 <= i < vol.shape[0]:
                return None
            sl = lambda a: a[i, :, :]
        elif view == "co":
            i = int(self.current_coronal_slice_index[0])
            if not 0 <= i < vol.shape[1]:
                return None
            sl = lambda a: a[:, i, :]
        else:
            i = int(self.current_sagittal_slice_index[0])
            if not 0 <= i < vol.shape[2]:
                return None
            sl = lambda a: a[:, :, i]
    except Exception:
        return None

    layers = _layers(self)
    hu = sl(vol)
    rgba = np.zeros(hu.shape + (4,), dtype=np.uint8)
    if not layers:
        return rgba
    masks = None
    a = int(_ALPHA * 255)
    for kind, arg, (r, g, b) in layers:
        if kind == "hu":
            m = (hu >= arg[0]) & (hu < arg[1])
        else:
            if masks is None:
                masks = _structure_masks(self, vol.shape)
            m3 = masks.get(arg)
            if m3 is None:
                continue
            m = sl(m3) != 0
        if m.any():
            rgba[m] = (r, g, b, a)      # later layers override
    return rgba


# ----------------------------------------------------------------------------
# VTK actors
# ----------------------------------------------------------------------------
def _widget(self, view):
    return {"ax": self.vtkWidgetAxial, "co": self.vtkWidgetCoronal,
            "sa": self.vtkWidgetSagittal}[view]


def _ensure(self, view):
    attr = f"matOverlayActor_{view}"
    if getattr(self, attr, None) is not None:
        return getattr(self, f"matOverlayImporter_{view}"), getattr(self, attr)
    imp = vtk.vtkImageImport()
    imp.SetDataScalarTypeToUnsignedChar()
    imp.SetNumberOfScalarComponents(4)
    actor = vtk.vtkImageActor()
    actor.GetMapper().SetInputConnection(imp.GetOutputPort())
    actor.InterpolateOff()
    actor.SetPickable(False)
    actor.SetVisibility(0)
    _widget(self, view).GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(actor)
    setattr(self, f"matOverlayImporter_{view}", imp)
    setattr(self, attr, actor)
    return imp, actor


def _z_eps(self):
    try:
        st = float(self.slice_thick[0])
    except Exception:
        st = 1.0
    return max(0.1, 0.05 * (st if st > 0 else 1.0)) * 0.75


def _update_view(self, view):
    if not hasattr(self, "vtkWidgetAxial"):
        return
    try:
        if not mat_overlay_active(self):
            actor = getattr(self, f"matOverlayActor_{view}", None)
            if actor is not None:
                actor.SetVisibility(0)
            return
        rgba = _build_rgba(self, view)
        imp, actor = _ensure(self, view)
        if rgba is None or not rgba[..., 3].any():
            actor.SetVisibility(0)
            return
        rgba = np.ascontiguousarray(rgba)
        h, w, _ = rgba.shape
        if view == "ax":
            sp = (self.pixel_spac[0, 1], self.pixel_spac[0, 0], 1.0)
            pos = (self.Im_Offset[0, 0], self.Im_Offset[0, 1])
        elif view == "co":
            sp = (self.pixel_spac[0, 1], self.slice_thick[0], 1.0)
            pos = (self.Im_Offset[0, 0], self.Im_Offset[0, 2])
        else:
            sp = (self.pixel_spac[0, 0], self.slice_thick[0], 1.0)
            pos = (self.Im_Offset[0, 1], self.Im_Offset[0, 2])
        data = rgba.tobytes()
        imp.SetDataSpacing(*sp)
        imp.SetDataOrigin(0.0, 0.0, 0.0)
        imp.CopyImportVoidPointer(data, len(data))
        imp.SetWholeExtent(0, w - 1, 0, h - 1, 0, 0)
        imp.SetDataExtent(0, w - 1, 0, h - 1, 0, 0)
        imp.Modified()
        actor.SetPosition(pos[0], pos[1], _z_eps(self))
        actor.SetVisibility(1)
    except Exception as e:
        print(f"[Material overlay] {view} update failed: {e}")


# Called from displayaxial / displaycoronal / displaysagittal
def update_mat_overlay_axial(self):
    _update_view(self, "ax")


def update_mat_overlay_coronal(self):
    _update_view(self, "co")


def update_mat_overlay_sagittal(self):
    _update_view(self, "sa")


def update_mat_overlay_all(self):
    """Redraw the overlay on all views (table edits, tab switches...)."""
    if not hasattr(self, "vtkWidgetAxial"):
        return
    for v in _VIEWS:
        _update_view(self, v)
        try:
            _widget(self, v).GetRenderWindow().Render()
        except Exception:
            pass
