# volume_3d_viewer.py — VTK / PyQt 3-D volume viewer
# -------------------------------------------------
# Bug-fix version: per-layer crop retention, isolated threshold updates,
# and consistent rendering quality when switching layers.

from vtkmodules.vtkRenderingVolumeOpenGL2 import vtkSmartVolumeMapper
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtkmodules.all as vtk
from vtkmodules.util.numpy_support import numpy_to_vtk, get_vtk_array_type

import numpy as np
import matplotlib.cm as cm

from PySide6 import QtWidgets
from PySide6.QtCore import QTimer, Qt
from functools import partial

from fcn_3Dview.surfaces_3D_table import add_stl_to_table

# -------------------------------------------------------------------------
# Suggested colormaps for medical imaging & radiotherapy
# -------------------------------------------------------------------------
CMAPS = [
    "Gray", "Bone", "Hot", "Cool", "Viridis",
    "Plasma", "Jet", "Rainbow", "Spectral", "BlueWhiteRed",
]

# -------------------------------------------------------------------------
# Window/level (threshold) widget helpers
# -------------------------------------------------------------------------
# Window/level (threshold) & transfer function helpers
# -------------------------------------------------------------------------
def _apply_transfer_functions(self, layer: int):
    """Apply updated OTF, CTF, and IsoSurface settings to the given layer."""
    if layer not in self._thresholds or layer not in self._otfs or layer not in self._ctfs:
        return

    low, high = self._full_ranges.get(layer, (self.slider3D_LOW, self.slider3D_HIGH))
    tmin, tmax = self._thresholds.get(layer, (low, high))
    if not hasattr(self, '_isovalues'):
        self._isovalues = {}
    isoval = self._isovalues.get(layer, tmin)

    # Determine opacity
    if hasattr(self, '_opacities') and len(self._opacities) > layer:
        opacity = float(self._opacities[layer])
    else:
        opacity = 1.0

    # IsoSurface contour value
    if layer in self._vol_props:
        volp = self._vol_props[layer]
        volp.GetIsoSurfaceValues().SetValue(0, isoval)

    # Determine blend mode
    mode = "Composite"
    if hasattr(self, 'View3D_render_options') and self.View3D_render_options:
        mode = self.View3D_render_options.currentText()

    # Update OTF
    otf = self._otfs[layer]
    otf.RemoveAllPoints()
    if mode == "IsoSurface":
        otf.AddPoint(isoval - 1e-4, 0.0)
        otf.AddPoint(isoval, opacity)
        otf.AddPoint(high, opacity)
    else:
        safe_tmax = max(tmax, tmin + 1e-4)
        otf.AddPoint(tmin, 0.0)
        otf.AddPoint(safe_tmax, opacity)

    # Update CTF
    ctf = self._ctfs[layer]
    cmap_box = self.findChild(QtWidgets.QComboBox, 'View3D_colormap')
    default_cmap = cmap_box.currentText() if cmap_box else "Gray"
    cmap = self._colormaps.get(layer, default_cmap)
    self.update_color_transfer(layer, ctf, cmap, tmin, max(tmax, tmin + 1e-4))

    if hasattr(self, 'VTK3D_interactor') and self.VTK3D_interactor:
        self.VTK3D_interactor.GetRenderWindow().Render()


def initialize_3Dsliders(self, low: float, high: float, n_steps: int = 100):
    """Configure window/level sliders & spinboxes for the current layer."""
    self.slider3D_LOW, self.slider3D_HIGH = float(low), float(high)
    self.slider3D_SPAN  = max(self.slider3D_HIGH - self.slider3D_LOW, 1e-6)
    self.slider3D_RES   = int(n_steps)

    # mapping lambdas
    self._s_to_v = lambda s: self.slider3D_LOW + (s/self.slider3D_RES)*self.slider3D_SPAN
    self._v_to_s = lambda v: int(round((v-self.slider3D_LOW)/self.slider3D_SPAN*self.slider3D_RES))

    widgets = [
        self.View3D_Threshold_slider_01,
        self.View3D_Threshold_slider_02,
        self.View3D_Threshold_spin_01,
        self.View3D_Threshold_spin_02,
    ]
    if hasattr(self, 'View3D_isovalue_slider'):
        widgets.append(self.View3D_isovalue_slider)
    if hasattr(self, 'View3D_isovalue_spin_01'):
        widgets.append(self.View3D_isovalue_spin_01)
    if hasattr(self, 'View3D_opacity_slider'):
        widgets.append(self.View3D_opacity_slider)
    if hasattr(self, 'View3D_opacity_spin_01'):
        widgets.append(self.View3D_opacity_spin_01)

    for w in widgets:
        w.blockSignals(True)

    # configure ranges & steps
    self.View3D_Threshold_slider_01.setRange(0, self.slider3D_RES)
    self.View3D_Threshold_slider_02.setRange(0, self.slider3D_RES)
    self.View3D_Threshold_spin_01.setRange(self.slider3D_LOW, self.slider3D_HIGH)
    self.View3D_Threshold_spin_02.setRange(self.slider3D_LOW, self.slider3D_HIGH)

    self.View3D_Threshold_slider_01.setSingleStep(1)
    self.View3D_Threshold_slider_02.setSingleStep(1)
    self.View3D_Threshold_spin_01.setDecimals(3)
    self.View3D_Threshold_spin_02.setDecimals(3)
    step = self.slider3D_SPAN / self.slider3D_RES
    self.View3D_Threshold_spin_01.setSingleStep(step)
    self.View3D_Threshold_spin_02.setSingleStep(step)

    # configure isovalue
    if hasattr(self, 'View3D_isovalue_slider'):
        self.View3D_isovalue_slider.setRange(0, self.slider3D_RES)
        self.View3D_isovalue_slider.setSingleStep(1)
    if hasattr(self, 'View3D_isovalue_spin_01'):
        self.View3D_isovalue_spin_01.setRange(self.slider3D_LOW, self.slider3D_HIGH)
        self.View3D_isovalue_spin_01.setDecimals(3)
        self.View3D_isovalue_spin_01.setSingleStep(step)

    # configure opacity
    layer = self.layer_selected.currentIndex()
    current_opacity = 1.0
    if hasattr(self, '_opacities') and len(self._opacities) > layer:
        current_opacity = float(self._opacities[layer])

    if hasattr(self, 'View3D_opacity_slider'):
        self.View3D_opacity_slider.setRange(0, 100)
        self.View3D_opacity_slider.setSingleStep(1)
        self.View3D_opacity_slider.setValue(int(round(current_opacity * 100)))
    if hasattr(self, 'View3D_opacity_spin_01'):
        self.View3D_opacity_spin_01.setRange(0.0, 1.0)
        self.View3D_opacity_spin_01.setDecimals(2)
        self.View3D_opacity_spin_01.setSingleStep(0.05)
        self.View3D_opacity_spin_01.setValue(current_opacity)

    # initialize to full range
    self.View3D_Threshold_slider_01.setValue(0)
    self.View3D_Threshold_spin_01.setValue(self.slider3D_LOW)
    self.View3D_Threshold_slider_02.setValue(self.slider3D_RES)
    self.View3D_Threshold_spin_02.setValue(self.slider3D_HIGH)

    if hasattr(self, 'View3D_isovalue_slider'):
        self.View3D_isovalue_slider.setValue(0)
    if hasattr(self, 'View3D_isovalue_spin_01'):
        self.View3D_isovalue_spin_01.setValue(self.slider3D_LOW)

    for w in widgets:
        w.blockSignals(False)

    # record both the absolute data range and current threshold for this layer
    if not hasattr(self, '_isovalues'):
        self._isovalues = {}
    self._full_ranges[layer] = (self.slider3D_LOW, self.slider3D_HIGH)
    self._thresholds[layer]  = (self.slider3D_LOW, self.slider3D_HIGH)
    self._isovalues[layer]   = self.slider3D_LOW

    # apply the lower‐slider once to fire off the initial transfer function
    _from_slider(self, 1, 0)


def _from_slider(self, idx: int, sval: int):
    """Handler for threshold & isovalue sliders: updates only the active layer."""
    if not hasattr(self, '_s_to_v') or not hasattr(self, '_v_to_s'):
        low = getattr(self, 'slider3D_LOW', 0.0)
        high = getattr(self, 'slider3D_HIGH', 100.0)
        res = getattr(self, 'slider3D_RES', 100)
        span = max(high - low, 1e-6)
        self.slider3D_LOW = low
        self.slider3D_HIGH = high
        self.slider3D_RES = res
        self.slider3D_SPAN = span
        self._s_to_v = lambda s: low + (s / res) * span
        self._v_to_s = lambda v: int(round((v - low) / span * res))

    v = self._s_to_v(sval)
    if idx == 1:
        # lower handle: clamp to upper spin value
        max_val = self.View3D_Threshold_spin_02.value() if hasattr(self, 'View3D_Threshold_spin_02') else v
        v = min(v, max_val)
        sval = self._v_to_s(v)
        if hasattr(self, 'View3D_Threshold_slider_01'):
            self.View3D_Threshold_slider_01.blockSignals(True)
            self.View3D_Threshold_slider_01.setValue(sval)
            self.View3D_Threshold_slider_01.blockSignals(False)
        if hasattr(self, 'View3D_Threshold_spin_01'):
            self.View3D_Threshold_spin_01.blockSignals(True)
            self.View3D_Threshold_spin_01.setValue(v)
            self.View3D_Threshold_spin_01.blockSignals(False)
    else:
        # upper handle: clamp to lower spin value
        min_val = self.View3D_Threshold_spin_01.value() if hasattr(self, 'View3D_Threshold_spin_01') else v
        v = max(v, min_val)
        sval = self._v_to_s(v)
        if hasattr(self, 'View3D_Threshold_slider_02'):
            self.View3D_Threshold_slider_02.blockSignals(True)
            self.View3D_Threshold_slider_02.setValue(sval)
            self.View3D_Threshold_slider_02.blockSignals(False)
        if hasattr(self, 'View3D_Threshold_spin_02'):
            self.View3D_Threshold_spin_02.setValue(v)

    layer = self.layer_selected.currentIndex() if hasattr(self, 'layer_selected') else 0
    tmin = self.View3D_Threshold_spin_01.value() if hasattr(self, 'View3D_Threshold_spin_01') else v
    tmax = self.View3D_Threshold_spin_02.value() if hasattr(self, 'View3D_Threshold_spin_02') else v
    if not hasattr(self, '_thresholds'):
        self._thresholds = {}
    self._thresholds[layer] = (tmin, tmax)

    _apply_transfer_functions(self, layer)


def _from_spin(self, idx: int, val: float):
    """Mirror spin‐box changes into the slider and reuse the slider logic."""
    if not hasattr(self, '_s_to_v') or not hasattr(self, '_v_to_s'):
        low = getattr(self, 'slider3D_LOW', 0.0)
        high = getattr(self, 'slider3D_HIGH', 100.0)
        res = getattr(self, 'slider3D_RES', 100)
        span = max(high - low, 1e-6)
        self.slider3D_LOW = low
        self.slider3D_HIGH = high
        self.slider3D_RES = res
        self.slider3D_SPAN = span
        self._s_to_v = lambda s: low + (s / res) * span
        self._v_to_s = lambda v: int(round((v - low) / span * res))

    sval = self._v_to_s(val)
    if idx == 1:
        if hasattr(self, 'View3D_Threshold_spin_01'):
            self.View3D_Threshold_spin_01.blockSignals(True)
            self.View3D_Threshold_spin_01.setValue(val)
            self.View3D_Threshold_spin_01.blockSignals(False)
        if hasattr(self, 'View3D_Threshold_slider_01'):
            self.View3D_Threshold_slider_01.blockSignals(True)
            self.View3D_Threshold_slider_01.setValue(sval)
            self.View3D_Threshold_slider_01.blockSignals(False)

    else:
        if hasattr(self, 'View3D_Threshold_spin_02'):
            self.View3D_Threshold_spin_02.blockSignals(True)
            self.View3D_Threshold_spin_02.setValue(val)
            self.View3D_Threshold_spin_02.blockSignals(False)
        if hasattr(self, 'View3D_Threshold_slider_02'):
            self.View3D_Threshold_slider_02.blockSignals(True)
            self.View3D_Threshold_slider_02.setValue(sval)
            self.View3D_Threshold_slider_02.blockSignals(False)

    _from_slider(self, idx, sval)


# -------------------------------------------------------------------------
# Independent isovalue handlers (do NOT touch threshold widgets)
# -------------------------------------------------------------------------
def _from_isovalue_slider(self, sval: int):
    """Handler for isovalue slider: updates only isovalue, not threshold."""
    if not hasattr(self, '_s_to_v') or not hasattr(self, '_v_to_s'):
        low = getattr(self, 'slider3D_LOW', 0.0)
        high = getattr(self, 'slider3D_HIGH', 100.0)
        res = getattr(self, 'slider3D_RES', 100)
        span = max(high - low, 1e-6)
        self.slider3D_LOW = low
        self.slider3D_HIGH = high
        self.slider3D_RES = res
        self.slider3D_SPAN = span
        self._s_to_v = lambda s: low + (s / res) * span
        self._v_to_s = lambda v: int(round((v - low) / span * res))

    v = self._s_to_v(sval)
    # Sync the isovalue spinbox
    if hasattr(self, 'View3D_isovalue_spin_01'):
        self.View3D_isovalue_spin_01.blockSignals(True)
        self.View3D_isovalue_spin_01.setValue(v)
        self.View3D_isovalue_spin_01.blockSignals(False)

    layer = self.layer_selected.currentIndex() if hasattr(self, 'layer_selected') else 0
    if not hasattr(self, '_isovalues'):
        self._isovalues = {}
    self._isovalues[layer] = v
    _apply_transfer_functions(self, layer)


def _from_isovalue_spin(self, val: float):
    """Handler for isovalue spinbox: updates only isovalue, not threshold."""
    if not hasattr(self, '_s_to_v') or not hasattr(self, '_v_to_s'):
        low = getattr(self, 'slider3D_LOW', 0.0)
        high = getattr(self, 'slider3D_HIGH', 100.0)
        res = getattr(self, 'slider3D_RES', 100)
        span = max(high - low, 1e-6)
        self.slider3D_LOW = low
        self.slider3D_HIGH = high
        self.slider3D_RES = res
        self.slider3D_SPAN = span
        self._s_to_v = lambda s: low + (s / res) * span
        self._v_to_s = lambda v: int(round((v - low) / span * res))

    sval = self._v_to_s(val)
    # Sync the isovalue slider
    if hasattr(self, 'View3D_isovalue_slider'):
        self.View3D_isovalue_slider.blockSignals(True)
        self.View3D_isovalue_slider.setValue(sval)
        self.View3D_isovalue_slider.blockSignals(False)

    layer = self.layer_selected.currentIndex() if hasattr(self, 'layer_selected') else 0
    if not hasattr(self, '_isovalues'):
        self._isovalues = {}
    self._isovalues[layer] = val
    _apply_transfer_functions(self, layer)


# -------------------------------------------------------------------------
# ROI‐crop widget helpers (per‐layer dims)
# -------------------------------------------------------------------------
def initialize_crop_widgets(self, dims: tuple, layer_idx: int):
    """Initialize six crop widgets to full‐volume for the given layer."""
    nx, ny, nz = dims
    self._dims[layer_idx]  = dims
    self._crops[layer_idx] = (0, nx-1, 0, ny-1, 0, nz-1)

    for axis, size in zip(('sagittal','coronal','axial'), (nx,ny,nz)):
        s1 = getattr(self, f'View3D_{axis}_slider_01')
        s2 = getattr(self, f'View3D_{axis}_slider_02')
        b1 = getattr(self, f'View3D_{axis}_spin_01')
        b2 = getattr(self, f'View3D_{axis}_spin_02')
        for w in (s1,s2,b1,b2):
            w.blockSignals(True)
        s1.setRange(0, size-1); s1.setValue(0)
        s2.setRange(0, size-1); s2.setValue(size-1)
        b1.setRange(0, size-1); b1.setValue(0)
        b2.setRange(0, size-1); b2.setValue(size-1)
        for w in (s1,s2,b1,b2):
            w.blockSignals(False)

    _apply_crop(self)


def _crop_from_slider(self, axis: str, idx_crop: int, sval: int):
    """Handler for crop sliders: updates only that layer’s crop."""
    layer = self.layer_selected.currentIndex()
    if layer not in self._dims:
        initialize_crop_widgets(self, self._imgs[layer].GetDimensions(), layer)
    nx, ny, nz = self._dims[layer]

    s1 = getattr(self, f'View3D_{axis}_slider_01')
    s2 = getattr(self, f'View3D_{axis}_slider_02')
    b1 = getattr(self, f'View3D_{axis}_spin_01')
    b2 = getattr(self, f'View3D_{axis}_spin_02')

    if idx_crop == 1:
        sval = min(sval, s2.value())
        s1.setValue(sval); b1.setValue(sval)
    else:
        sval = max(sval, s1.value())
        s2.setValue(sval); b2.setValue(sval)

    xmin, xmax, ymin, ymax, zmin, zmax = self._crops[layer]
    if axis == 'sagittal':
        xmin, xmax = (sval, xmax) if idx_crop==1 else (xmin, sval)
    elif axis == 'coronal':
        ymin, ymax = (sval, ymax) if idx_crop==1 else (ymin, sval)
    else:
        zmin, zmax = (sval, zmax) if idx_crop==1 else (zmin, sval)

    self._crops[layer] = (xmin, xmax, ymin, ymax, zmin, zmax)
    _apply_crop(self)


def _crop_from_spin(self, axis: str, idx_crop: int, val: int):
    """Mirror spin into slider handler."""
    _crop_from_slider(self, axis, idx_crop, val)


def _apply_crop(self):
    """Apply recorded crop extents to the selected (or all) layers."""
    apply_all = self.View3D_update_all_3D.isChecked()
    sel = self.layer_selected.currentIndex()
    for li, volobj in self._volumes.items():
        if apply_all or li == sel:
            xmin, xmax, ymin, ymax, zmin, zmax = self._crops.get(
                li, (0,) + self._dims.get(li,(1,1,1)) + (0,)
            )
            sx, sy, sz = self._imgs[li].GetSpacing()
            m = volobj.GetMapper()
            m.SetCroppingRegionPlanes(
                xmin*sx, xmax*sx,
                ymin*sy, ymax*sy,
                zmin*sz, zmax*sz
            )
            m.SetCroppingRegionFlagsToSubVolume()

    self.VTK3D_interactor.GetRenderWindow().Render()


# -------------------------------------------------------------------------
# 4D playback helper
# -------------------------------------------------------------------------
def play_4D_sequence_3D(self, play: bool):
    if play:
        self.View3D_play4D.setStyleSheet("background-color: red; color: white;")
        checked = []
        table   = self.CT4D_table_display
        for row in range(table.rowCount()):
            cb = table.cellWidget(row,0).layout().itemAt(0).widget()
            if cb.isChecked():
                t_idx = int(table.item(row,3).text())
                seq   = int(table.item(row,1).text())
                checked.append((t_idx,seq))
        checked.sort(key=lambda x: x[1])
        if not checked: return
        self._play3D_index = 0
        ms = int(1000/max(1,self.Play_DCT_speed.value()))

        def _advance():
            if not self.View3D_play4D.isChecked(): return
            t_idx = checked[self._play3D_index][0]
            vol   = self.medical_image[self.patientID][self.studyID][self.modality][t_idx]['3DMatrix']
            apply_all = self.View3D_update_all_3D.isChecked()
            sel       = self.layer_selected.currentIndex()
            if apply_all:
                for li in self._volumes:
                    self.update_3d_volume(vol, layer_idx=li)
            else:
                self.update_3d_volume(vol, layer_idx=sel)

            self._play3D_index = (self._play3D_index+1)%len(checked)
            QTimer.singleShot(ms, _advance)

        _advance()
    else:
        self.View3D_play4D.setStyleSheet("")
        self._play3D_index = 0

def find_row_by_name_stl(self, stl_name):
    for row in range(self._STL_Surface_table.rowCount()):
        item = self._STL_Surface_table.item(row, 0)
        if item and item.data(Qt.UserRole) == stl_name:
            return row
    return None

# -------------------------------------------------------------------------
# Mixin class
# -------------------------------------------------------------------------
class VTK3DViewerMixin:
    def init_3d_viewer(self):
        """Wire up all UI callbacks; call after setupUi()."""
        # storage
        self._imgs        = {}
        self._ctfs        = {}
        self._otfs        = {}
        self._vol_props   = {}
        self._volumes     = {}
        self._thresholds  = {}
        self._isovalues   = {}
        self._crops       = {}
        self._dims        = {}
        self._colormaps   = {}
        self._full_ranges = {}
        self._clouds      = {}
        self._play3D_index = 0

        # Default mapping helpers before any volume is loaded
        if not hasattr(self, 'slider3D_LOW'):
            self.slider3D_LOW = 0.0
        if not hasattr(self, 'slider3D_HIGH'):
            self.slider3D_HIGH = 100.0
        if not hasattr(self, 'slider3D_RES'):
            self.slider3D_RES = 100
        self.slider3D_SPAN = max(self.slider3D_HIGH - self.slider3D_LOW, 1e-6)
        self._s_to_v = lambda s: self.slider3D_LOW + (s / self.slider3D_RES) * self.slider3D_SPAN
        self._v_to_s = lambda v: int(round((v - self.slider3D_LOW) / self.slider3D_SPAN * self.slider3D_RES))

        # colormap menu
        combo = getattr(self, 'View3D_colormap', None) or self.findChild(QtWidgets.QComboBox, 'View3D_colormap')
        if combo is not None:
            combo.addItems(CMAPS)
            combo.currentIndexChanged.connect(self._on_colormap_changed)
        self.View3D_update_all_3D.stateChanged.connect(self._on_colormap_changed)

        # layer change restores state
        self.layer_selected.currentIndexChanged.connect(self._on_layer_changed)

        # threshold & isovalue callbacks
        self.View3D_Threshold_slider_01.valueChanged.connect(partial(_from_slider, self, 1))
        self.View3D_Threshold_slider_02.valueChanged.connect(partial(_from_slider, self, 2))
        self.View3D_Threshold_spin_01.valueChanged.connect(partial(_from_spin,   self, 1))
        self.View3D_Threshold_spin_02.valueChanged.connect(partial(_from_spin,   self, 2))
        if hasattr(self, 'View3D_isovalue_slider'):
            self.View3D_isovalue_slider.valueChanged.connect(partial(_from_isovalue_slider, self))
        if hasattr(self, 'View3D_isovalue_spin_01'):
            self.View3D_isovalue_spin_01.valueChanged.connect(partial(_from_isovalue_spin, self))

        # opacity callbacks
        if hasattr(self, 'View3D_opacity_slider'):
            self.View3D_opacity_slider.valueChanged.connect(self._from_opacity_slider)
        if hasattr(self, 'View3D_opacity_spin_01'):
            self.View3D_opacity_spin_01.valueChanged.connect(self._from_opacity_spin)

        # crop callbacks
        for axis in ('sagittal','coronal','axial'):
            getattr(self, f'View3D_{axis}_slider_01').valueChanged.connect(
                partial(_crop_from_slider, self, axis, 1))
            getattr(self, f'View3D_{axis}_slider_02').valueChanged.connect(
                partial(_crop_from_slider, self, axis, 2))
            getattr(self, f'View3D_{axis}_spin_01').valueChanged.connect(
                partial(_crop_from_spin, self, axis, 1))
            getattr(self, f'View3D_{axis}_spin_02').valueChanged.connect(
                partial(_crop_from_spin, self, axis, 2))

    
    def add_3d_point_cloud(self, points, color=(1, 0, 0), size=3.0, name=None):
        """
        Add a 3D point cloud (Nx3 numpy array) as VTK actor. Returns a key for later removal.
        - color: (r,g,b)
        - size: point size in pixels
        - name: optional unique string, else uses len(self._clouds)
        """
  
        # Prepare VTK points
        vtk_points = vtk.vtkPoints()
        # Swap Y and Z, then flip Z
        transformed = np.zeros_like(points)
        transformed[:, 0] = points[:, 0]
        transformed[:, 1] = points[:, 2] # new Y is old Z
        transformed[:, 2] = -points[:, 1] # new Z is -old Y
        for pt in transformed:
            vtk_points.InsertNextPoint(float(pt[0]), float(pt[1]), float(pt[2]))

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(vtk_points)

        verts = vtk.vtkVertexGlyphFilter()
        verts.SetInputData(polydata)
        verts.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(verts.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetPointSize(size)

        # Store in clouds dict
        if name is None:
            name = f"cloud_{len(self._clouds)}"
        self._clouds[name] = {
            'actor': actor,
            'color': color,
            'size': size,
            'points': points,
            'transparency': 1.0
        }
        self.VTK3D_renderer.AddActor(actor)
        self.VTK3D_interactor.GetRenderWindow().Render()
        return name

    def remove_3d_point_cloud(self, name):
        """Remove a named 3D point cloud from the renderer."""
        if name in self._clouds:
            actor = self._clouds.pop(name)
            self.VTK3D_renderer.RemoveActor(actor)
            self.VTK3D_interactor.GetRenderWindow().Render()

    def clear_3d_point_clouds(self):
        """Remove all 3D point cloud actors."""
        for actor in self._clouds.values():
            self.VTK3D_renderer.RemoveActor(actor)
        self._clouds.clear()
        self.VTK3D_interactor.GetRenderWindow().Render()


    _apply_transfer_functions = _apply_transfer_functions

    def _from_opacity_slider(self, sval: int):
        val = sval / 100.0
        if hasattr(self, 'View3D_opacity_spin_01'):
            self.View3D_opacity_spin_01.blockSignals(True)
            self.View3D_opacity_spin_01.setValue(val)
            self.View3D_opacity_spin_01.blockSignals(False)
        layer = self.layer_selected.currentIndex()
        self._on_opacity_changed(val, layer)

    def _from_opacity_spin(self, val: float):
        sval = int(round(val * 100))
        if hasattr(self, 'View3D_opacity_slider'):
            self.View3D_opacity_slider.blockSignals(True)
            self.View3D_opacity_slider.setValue(sval)
            self.View3D_opacity_slider.blockSignals(False)
        layer = self.layer_selected.currentIndex()
        self._on_opacity_changed(val, layer)

    def update_color_transfer(self,
                              layer_idx: int,
                              ctf: vtk.vtkColorTransferFunction,
                              cmap_name: str,
                              tmin: float,
                              tmax: float,
                              n_samples: int = 256):
        """Sample matplotlib colormap into the VTK ctf and record it."""
        self._colormaps[layer_idx] = cmap_name
        ctf.RemoveAllPoints()
        cmap = cm.get_cmap(cmap_name.lower())
        for i in range(n_samples):
            frac = i/float(n_samples-1)
            val  = tmin + frac*(tmax-tmin)
            r,g,b,_ = cmap(frac)
            ctf.AddRGBPoint(val, r, g, b)

    def _on_colormap_changed(self, *_):
        apply_all = self.View3D_update_all_3D.isChecked()
        sel = self.layer_selected.currentIndex()
        for li in self._ctfs:
            if apply_all or li == sel:
                _apply_transfer_functions(self, li)

    def _on_layer_changed(self, new_idx: int):
        if new_idx not in self._imgs:
            return

        # 1) restore that layer’s full [low,high]
        low, high = self._full_ranges[new_idx]
        self.slider3D_LOW, self.slider3D_HIGH = low, high
        self.slider3D_SPAN = max(high - low, 1e-6)
        self._s_to_v = lambda s: self.slider3D_LOW + (s/self.slider3D_RES)*self.slider3D_SPAN
        self._v_to_s = lambda v: int(round((v-self.slider3D_LOW)/self.slider3D_SPAN*self.slider3D_RES))

        # grab references to the widgets
        widgets_to_block = [
            self.View3D_Threshold_spin_01,
            self.View3D_Threshold_spin_02,
            self.View3D_Threshold_slider_01,
            self.View3D_Threshold_slider_02,
        ]
        if hasattr(self, 'View3D_isovalue_slider'):
            widgets_to_block.append(self.View3D_isovalue_slider)
        if hasattr(self, 'View3D_isovalue_spin_01'):
            widgets_to_block.append(self.View3D_isovalue_spin_01)
        if hasattr(self, 'View3D_opacity_slider'):
            widgets_to_block.append(self.View3D_opacity_slider)
        if hasattr(self, 'View3D_opacity_spin_01'):
            widgets_to_block.append(self.View3D_opacity_spin_01)

        # block *all* signals from them before touching ranges *or* values
        for w in widgets_to_block:
            w.blockSignals(True)

        # reconfigure ranges
        self.View3D_Threshold_slider_01.setRange(0, self.slider3D_RES)
        self.View3D_Threshold_slider_02.setRange(0, self.slider3D_RES)
        self.View3D_Threshold_spin_01.setRange(low, high)
        self.View3D_Threshold_spin_02.setRange(low, high)

        if hasattr(self, 'View3D_isovalue_slider'):
            self.View3D_isovalue_slider.setRange(0, self.slider3D_RES)
        if hasattr(self, 'View3D_isovalue_spin_01'):
            self.View3D_isovalue_spin_01.setRange(low, high)

        if hasattr(self, 'View3D_opacity_slider'):
            self.View3D_opacity_slider.setRange(0, 100)
        if hasattr(self, 'View3D_opacity_spin_01'):
            self.View3D_opacity_spin_01.setRange(0.0, 1.0)

        # restore stored thresholds & isovalues for this layer
        tmin, tmax = self._thresholds.get(new_idx, (low, high))
        isoval = self._isovalues.get(new_idx, tmin) if hasattr(self, '_isovalues') else tmin
        self.View3D_Threshold_spin_01.setValue(tmin)
        self.View3D_Threshold_slider_01.setValue(self._v_to_s(tmin))
        self.View3D_Threshold_spin_02.setValue(tmax)
        self.View3D_Threshold_slider_02.setValue(self._v_to_s(tmax))

        if hasattr(self, 'View3D_isovalue_spin_01'):
            self.View3D_isovalue_spin_01.setValue(isoval)
        if hasattr(self, 'View3D_isovalue_slider'):
            self.View3D_isovalue_slider.setValue(self._v_to_s(isoval))

        opac = float(self._opacities[new_idx]) if hasattr(self, '_opacities') and len(self._opacities) > new_idx else 1.0
        if hasattr(self, 'View3D_opacity_spin_01'):
            self.View3D_opacity_spin_01.setValue(opac)
        if hasattr(self, 'View3D_opacity_slider'):
            self.View3D_opacity_slider.setValue(int(round(opac * 100)))

        # unblock signals now that everything is in place
        for w in widgets_to_block:
            w.blockSignals(False)

        # re-apply transfer functions
        _apply_transfer_functions(self, new_idx)

        # get dims & stored extents
        nx, ny, nz = self._dims[new_idx]
        xmin, xmax, ymin, ymax, zmin, zmax = self._crops.get(
            new_idx,
            (0, nx-1, 0, ny-1, 0, nz-1)
        )
        # helper to set each axis’s widgets
        for axis, (lo, hi, size) in zip(
            ('sagittal','coronal','axial'),
            [(xmin,xmax,nx), (ymin,ymax,ny), (zmin,zmax,nz)]
        ):
            s1 = getattr(self, f'View3D_{axis}_slider_01')
            s2 = getattr(self, f'View3D_{axis}_slider_02')
            b1 = getattr(self, f'View3D_{axis}_spin_01')
            b2 = getattr(self, f'View3D_{axis}_spin_02')
            # block signals while we set ranges & values
            for w in (s1,s2,b1,b2): w.blockSignals(True)
            s1.setRange(0, size-1); b1.setRange(0, size-1)
            s2.setRange(0, size-1); b2.setRange(0, size-1)
            s1.setValue(lo);          b1.setValue(lo)
            s2.setValue(hi);          b2.setValue(hi)
            for w in (s1,s2,b1,b2): w.blockSignals(False)

        # finally, re‐apply the stored crop to the actual volumes
        _apply_crop(self)

    def display_numpy_volume(self,
                             volume_np: np.ndarray,
                             voxel_spacing=(1.0,1.0,1.0),
                             layer_idx=None,
                             offset=(0.0,0.0,0.0)):
        """Load a new 3D numpy array into a VTK volume and display it."""
        if layer_idx is None:
            layer_idx = self.layer_selected.currentIndex()

        # remove old volume if any
        if layer_idx in self._volumes:
            self.VTK3D_renderer.RemoveVolume(self._volumes[layer_idx])

        # Check if volume exceeds GPU 3D texture limits (OpenGL MAX_3D_TEXTURE_SIZE is 2048)
        # or exceeds 450M voxels, and compute appropriate downsampling steps.
        MAX_3D_DIM = 1024
        MAX_3D_VOXELS = 450_000_000

        orig_nz, orig_ny, orig_nx = volume_np.shape
        step_z = max(1, int(np.ceil(orig_nz / MAX_3D_DIM)))
        step_y = max(1, int(np.ceil(orig_ny / MAX_3D_DIM)))
        step_x = max(1, int(np.ceil(orig_nx / MAX_3D_DIM)))

        while ((orig_nz // step_z) * (orig_ny // step_y) * (orig_nx // step_x)) > MAX_3D_VOXELS:
            step_z += 1
            step_y += 1
            step_x += 1

        if step_z > 1 or step_y > 1 or step_x > 1:
            print(f"[3Dview] Subsampling volume from {volume_np.shape} with steps ({step_z}, {step_y}, {step_x}) "
                  f"to ensure high performance and stay strictly under GPU MAX_3D_TEXTURE_SIZE (2048).")

        # Flip Y axis to match VTK coordinate system and subsample in a single operation
        vol = np.ascontiguousarray(volume_np[::step_z, ::-step_y, ::step_x])
        nz, ny, nx = vol.shape

        effective_spacing = (
            float(voxel_spacing[0] * step_x),
            float(voxel_spacing[1] * step_y),
            float(voxel_spacing[2] * step_z),
        )

        arr = numpy_to_vtk(vol.ravel(order='C'), deep=True,
                           array_type=get_vtk_array_type(vol.dtype))

        img = vtk.vtkImageData()
        img.SetDimensions(nx, ny, nz)
        img.SetSpacing(*effective_spacing)
        img.GetPointData().SetScalars(arr)
        self._imgs[layer_idx] = img

        # compute data range
        vmin, vmax = float(vol.min()), float(vol.max())
        self._full_ranges[layer_idx] = (vmin, vmax)

        ctf = vtk.vtkColorTransferFunction()
        otf = vtk.vtkPiecewiseFunction()
        opacity = self._opacities[layer_idx]
        otf.AddPoint(vmin, 0.0)
        otf.AddPoint(vmax, opacity)
        self._ctfs[layer_idx] = ctf
        self._otfs[layer_idx] = otf

        # initial colormap
        cmap_box = getattr(self, 'View3D_colormap', None) or self.findChild(QtWidgets.QComboBox, 'View3D_colormap')
        cmap = cmap_box.currentText() if cmap_box is not None else "Gray"
        self.update_color_transfer(layer_idx, ctf, cmap, vmin, vmax)

        # setup volume property
        volp = vtk.vtkVolumeProperty()
        volp.SetColor(ctf)
        volp.SetScalarOpacity(otf)
        volp.SetInterpolationTypeToLinear()
        
        # Apply current render panel controls
        if getattr(self, '_render_controls_initialized', False):
            # shading
            if self.View3D_shading_checkBox.isChecked():
                volp.ShadeOn()
            else:
                volp.ShadeOff()
            # brightness (ambient/diffuse)
            brightness_val = self.View3D_brightness_spin_01.value()
            ambient_val = 0.1 + 0.8 * brightness_val if brightness_val >= 0 else 0.1 * (1.0 + brightness_val)
            diffuse_val = 0.7 - 0.5 * brightness_val if brightness_val >= 0 else 0.7 + 0.3 * brightness_val
            volp.SetAmbient(ambient_val)
            volp.SetDiffuse(diffuse_val)
            # specular
            specular_power_val = self.View3D_specular_spin_01.value()
            if specular_power_val > 0:
                volp.SetSpecular(0.5)
                volp.SetSpecularPower(specular_power_val)
            else:
                volp.SetSpecular(0.0)
        else:
            volp.ShadeOff()
            
        self._vol_props[layer_idx] = volp

        # mapper
        mapper = vtkSmartVolumeMapper()
        mapper.SetInputData(img)
        
        # Apply blend mode and quality
        min_sp = min(effective_spacing)
        if getattr(self, '_render_controls_initialized', False):
            mode = self.View3D_render_options.currentText()
            if mode == "MIP":
                mapper.SetBlendModeToMaximumIntensity()
            elif mode == "MinIP":
                mapper.SetBlendModeToMinimumIntensity()
            elif mode == "IsoSurface":
                mapper.SetBlendModeToIsoSurface()
            else:
                mapper.SetBlendModeToComposite()
                
            # Quality (sample distance): adapt to volume's voxel spacing
            quality_val = self.View3D_quality_spin_01.value()
            sample_distance = max(min_sp * (2.5 - 2.0 * quality_val), 1e-4)
            mapper.SetSampleDistance(sample_distance)
            mapper.SetAutoAdjustSampleDistances(1)
        else:
            mapper.SetBlendModeToComposite()
            mapper.SetSampleDistance(min_sp)
            mapper.SetAutoAdjustSampleDistances(1)
            
        mapper.CroppingOn()
        sx, sy, sz = effective_spacing
        mapper.SetCroppingRegionPlanes(0, (nx-1)*sx,
                                       0, (ny-1)*sy,
                                       0, (nz-1)*sz)
        mapper.SetCroppingRegionFlagsToSubVolume()

        volobj = vtk.vtkVolume()
        volobj.SetMapper(mapper)
        volobj.SetProperty(volp)
        volobj.SetPosition(*offset)
        self._volumes[layer_idx] = volobj
        self.VTK3D_renderer.AddVolume(volobj)




        # initialize sliders & crops if first time
        if layer_idx not in self._thresholds:
            initialize_3Dsliders(self, vmin, vmax)
        if layer_idx not in self._dims:
            initialize_crop_widgets(self, (nx, ny, nz), layer_idx)

        self.VTK3D_interactor.GetRenderWindow().Render()

        if layer_idx==0:
            self.VTK3D_renderer.ResetCamera()
            self.Layer_0_alpha_sli.setValue(100)
        elif layer_idx==1:
            self.Layer_1_alpha_sli.setValue(100)
        elif layer_idx==2:
            self.Layer_2_alpha_sli.setValue(100)
        elif layer_idx==3:
            self.Layer_3_alpha_sli.setValue(100)



    def _on_opacity_changed(self, val, layer=None):
        if layer is None:
            layer = self.layer_selected.currentIndex()
        if layer not in self._thresholds and layer not in self._imgs:
            return
        opacity = max(0.0, min(1.0, float(val)))
        if hasattr(self, '_opacities') and len(self._opacities) > layer:
            self._opacities[layer] = opacity
        if hasattr(self, 'LayerAlpha') and len(self.LayerAlpha) > layer:
            self.LayerAlpha[layer] = opacity

        # Sync sidebar sliders/spins for this layer
        sli = getattr(self, f'Layer_{layer}_alpha_sli', None)
        if sli is not None:
            sli.blockSignals(True)
            sli.setValue(int(round(opacity * 100)))
            sli.blockSignals(False)
        spin = getattr(self, f'Layer_{layer}_alpha_spin', None)
        if spin is not None:
            spin.blockSignals(True)
            spin.setValue(opacity)
            spin.blockSignals(False)

        # Sync 3D view opacity widgets if this is the active layer
        if layer == self.layer_selected.currentIndex():
            if hasattr(self, 'View3D_opacity_slider'):
                self.View3D_opacity_slider.blockSignals(True)
                self.View3D_opacity_slider.setValue(int(round(opacity * 100)))
                self.View3D_opacity_slider.blockSignals(False)
            if hasattr(self, 'View3D_opacity_spin_01'):
                self.View3D_opacity_spin_01.blockSignals(True)
                self.View3D_opacity_spin_01.setValue(opacity)
                self.View3D_opacity_spin_01.blockSignals(False)

        _apply_transfer_functions(self, layer)


    def update_3d_volume(self, volume_np, layer_idx=None):
        """Update just the scalar data of an existing volume."""
        if layer_idx is None:
            layer_idx = self.layer_selected.currentIndex()
        vol = np.flip(volume_np, axis=1)
        arr = numpy_to_vtk(vol.ravel(order='C'), deep=True,
                           array_type=get_vtk_array_type(vol.dtype))
        img = self._imgs[layer_idx]
        img.GetPointData().SetScalars(arr)
        img.Modified()
        self.VTK3D_interactor.GetRenderWindow().Render()

    def play_4D_sequence_3D(self, play: bool):
        """Proxy to the 4D playback helper."""
        play_4D_sequence_3D(self, play)

    def clear_3d_axes(self):
        # Remove all volumes
        for vol in self._volumes.values():
            self.VTK3D_renderer.RemoveVolume(vol)
        self._volumes.clear()
        self._imgs.clear()
        self._ctfs.clear()
        self._otfs.clear()
        self._vol_props.clear()
        self._thresholds.clear()
        if hasattr(self, '_isovalues'):
            self._isovalues.clear()
        self._crops.clear()
        self._dims.clear()
        self._full_ranges.clear()

        # Remove all general point cloud actors
        for cloud in self._clouds.values():
            self.VTK3D_renderer.RemoveActor(cloud['actor'])
        self._clouds.clear()

        # Remove all surface actors if you use them
        if hasattr(self, '_surfaces'):
            for actor in self._surfaces.values():
                self.VTK3D_renderer.RemoveActor(actor)
            self._surfaces.clear()

        # Remove all STL surface table rows
        if hasattr(self, "_STL_Surface_table"):
            self._STL_Surface_table.setRowCount(0)

        # Remove all rows from the clouds table
        self._3D_Struct_table.setRowCount(0)

        # ----- NEW: Clear proton spot actors and data -----
        if hasattr(self, '_proton_spots'):
            for actor in self._proton_spots.values():
                self.VTK3D_renderer.RemoveActor(actor)
            self._proton_spots.clear()
        if hasattr(self, '_proton_spot_data'):
            self._proton_spot_data.clear()
        if hasattr(self, '_3D_proton_table'):
            self._3D_proton_table.setRowCount(0)

        # ----- NEW: Clear brachy actors and data -----
        if hasattr(self, '_3D_brachy_actors'):
            for actors in self._3D_brachy_actors.values():
                for actor in actors:
                    self.VTK3D_renderer.RemoveActor(actor)
            self._3D_brachy_actors.clear()
        if hasattr(self, '_3D_brachy_table'):
            self._3D_brachy_table.setRowCount(0)

        self.VTK3D_interactor.GetRenderWindow().Render()


    def reset_3d_camera(self):
        self.VTK3D_renderer.ResetCamera()
        self.VTK3D_interactor.GetRenderWindow().Render()
    
    def display_stl_surface_in_3d_viewer(self, polydata, name="surface", color=(0.8, 0.3, 0.2), opacity=1.0, highlight=False):
        """
        Display a single STL surface in the 3D viewer.
        - polydata: vtkPolyData of the surface
        - name: unique key for surface (use STL_data key)
        - color: tuple, default reddish
        - opacity: 0..1
        - highlight: if True, sets a yellow border

        Caches actors in self._surfaces; replaces actor if already exists.
        """
        # --- Ensure _surfaces dict exists ---
        if not hasattr(self, "_surfaces") or self._surfaces is None:
            self._surfaces = {}

        # --- Remove previous actor if exists ---
        if name in self._surfaces:
            self.VTK3D_renderer.RemoveActor(self._surfaces[name])
            del self._surfaces[name]

        # --- Build new actor ---
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetOpacity(opacity)
        actor.GetProperty().SetInterpolationToPhong()
        if highlight:
            actor.GetProperty().SetEdgeVisibility(1)
            actor.GetProperty().SetEdgeColor(1,1,0)
            actor.GetProperty().SetLineWidth(2)
        else:
            actor.GetProperty().SetEdgeVisibility(0)

        # --- Add to renderer and cache ---
        self.VTK3D_renderer.AddActor(actor)
        self._surfaces[name] = actor

        # --- Render and adjust camera if wanted ---
        self.VTK3D_interactor.GetRenderWindow().Render()
        # Optionally, reset camera on first STL
        if len(self._surfaces) == 1:
            self.VTK3D_renderer.ResetCamera()
            self.VTK3D_interactor.GetRenderWindow().Render()
        
        # --- Add or update row in the STL table ---
        if hasattr(self, "_STL_Surface_table"):
            row = find_row_by_name_stl(self, name)
            if row is not None:
                self._STL_Surface_table.removeRow(row)
            add_stl_to_table(
                self,
                name=name,
                face_color=color,
                line_color=(1,0,0),
                show_faces=True,
                show_lines=False if not highlight else True,
                face_alpha=opacity,
                line_width=1,
                tx=actor.GetPosition()[0],
                ty=actor.GetPosition()[1],
                tz=actor.GetPosition()[2],
                sx=actor.GetScale()[0],
                sy=actor.GetScale()[1],
                sz=actor.GetScale()[2],
        )

    def add_3d_proton_spots(self, points, color=(1,0,0), size=3.0, name=None):
        """
        Add 3D proton spots as VTK crosses (one per spot).
        - points: (N,3) array of spot XYZ positions
        - color: (r,g,b) tuple
        - size: cross length (float, e.g. 3.0)
        - name: unique key to store for later removal
        """
        import vtkmodules.all as vtk

        if not hasattr(self, '_proton_spots'):
            self._proton_spots = {}

        # Remove previous actor for this name if exists
        if name and name in self._proton_spots:
            self.VTK3D_renderer.RemoveActor(self._proton_spots[name])
            del self._proton_spots[name]

        # ---- Subtract the reference from all spots ----
        ref = self.Im_PatPosition3Dview[0, :3] if hasattr(self, "Im_PatPosition3Dview") else np.zeros(3)
        shifted_points = points - ref  # shape (N,3)
        # Swap Y and Z, then flip Z
        transformed = np.zeros_like(shifted_points)
        transformed[:, 0] = shifted_points[:, 0]
        transformed[:, 1] = shifted_points[:, 2] # new Y is old Z
        transformed[:, 2] = -shifted_points[:, 1] # new Z is -old Y
        shifted_points = transformed

        # subtract this image reference from spots: self.Im_PatPosition3Dview[0, :3]

        # Build a single vtkAppendPolyData of all crosses for performance
        append = vtk.vtkAppendPolyData()
        for pt in shifted_points:
            for axis in range(3):
                line = vtk.vtkLineSource()
                start = list(pt)
                end   = list(pt)
                start[axis] -= size/2
                end[axis]   += size/2
                line.SetPoint1(*start)
                line.SetPoint2(*end)
                line.Update()
                append.AddInputData(line.GetOutput())
        append.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(append.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(2.5) # adjust for visibility

        if name is None:
            name = f"proton_spots_{len(self._proton_spots)}"
        self._proton_spots[name] = actor
        self.VTK3D_renderer.AddActor(actor)
        self.VTK3D_interactor.GetRenderWindow().Render()
        return name
    
    def remove_3d_proton_spots(self, name):
        """
        Remove a proton spot actor by name.
        """
        if hasattr(self, '_proton_spots') and name in self._proton_spots:
            self.VTK3D_renderer.RemoveActor(self._proton_spots[name])
            del self._proton_spots[name]
            self.VTK3D_interactor.GetRenderWindow().Render()