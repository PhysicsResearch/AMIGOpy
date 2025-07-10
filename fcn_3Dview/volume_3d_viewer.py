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

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, Qt
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

    # initialize to full range
    self.View3D_Threshold_slider_01.setValue(0)
    self.View3D_Threshold_spin_01.setValue(self.slider3D_LOW)
    self.View3D_Threshold_slider_02.setValue(self.slider3D_RES)
    self.View3D_Threshold_spin_02.setValue(self.slider3D_HIGH)

    for w in widgets:
        w.blockSignals(False)

    # record both the absolute data range and current threshold for this layer
    layer = self.layer_selection_box.currentIndex()
    self._full_ranges[layer] = (self.slider3D_LOW, self.slider3D_HIGH)
    self._thresholds[layer]  = (self.slider3D_LOW, self.slider3D_HIGH)

    # apply the lower‐slider once to fire off the initial transfer function
    _from_slider(self, 1, 0)


def _from_slider(self, idx: int, sval: int):
    """Handler for threshold sliders: updates only the active layer."""
    v = self._s_to_v(sval)
    if idx == 1:
        # lower handle: clamp to upper spin value
        v = min(v, self.View3D_Threshold_spin_02.value())
        sval = self._v_to_s(v)
        self.View3D_Threshold_slider_01.blockSignals(True)
        self.View3D_Threshold_slider_01.setValue(sval)
        self.View3D_Threshold_slider_01.blockSignals(False)
        self.View3D_Threshold_spin_01.setValue(v)
    else:
        # upper handle: clamp to lower spin value
        v = max(v, self.View3D_Threshold_spin_01.value())
        sval = self._v_to_s(v)
        self.View3D_Threshold_slider_02.blockSignals(True)
        self.View3D_Threshold_slider_02.setValue(sval)
        self.View3D_Threshold_slider_02.blockSignals(False)
        self.View3D_Threshold_spin_02.setValue(v)

    layer = self.layer_selection_box.currentIndex()
    # print(f"[DEBUG] _from_slider: layer={layer}, idx={idx}, sval={sval}")  
    # store the new threshold for this layer
    tmin = self.View3D_Threshold_spin_01.value()
    tmax = self.View3D_Threshold_spin_02.value()
    self._thresholds[layer] = (tmin, tmax)
    # print(f"[DEBUG] stored thresholds[{layer}] = {self._thresholds[layer]}") 
    # apply only this layer’s transfer functions
    opacity = self._opacities[layer] 
    otf = self._otfs[layer]
    otf.RemoveAllPoints()
    otf.AddPoint(tmin, 0.0)
    otf.AddPoint(tmax, opacity)

    ctf = self._ctfs[layer]
    cmap = self._colormaps.get(
        layer,
        self.findChild(QtWidgets.QComboBox, 'View3D_colormap').currentText()
    )
    self.update_color_transfer(layer, ctf, cmap, tmin, tmax)
    self.VTK3D_interactor.GetRenderWindow().Render()


def _from_spin(self, idx: int, val: float):
    """Mirror spin‐box changes into the slider and reuse the slider logic."""
    sval = self._v_to_s(val)
    if idx == 1:
        self.View3D_Threshold_spin_01.blockSignals(True)
        self.View3D_Threshold_spin_01.setValue(val)
        self.View3D_Threshold_spin_01.blockSignals(False)
        self.View3D_Threshold_slider_01.blockSignals(True)
        self.View3D_Threshold_slider_01.setValue(sval)
        self.View3D_Threshold_slider_01.blockSignals(False)
    else:
        self.View3D_Threshold_spin_02.blockSignals(True)
        self.View3D_Threshold_spin_02.setValue(val)
        self.View3D_Threshold_spin_02.blockSignals(False)
        self.View3D_Threshold_slider_02.blockSignals(True)
        self.View3D_Threshold_slider_02.setValue(sval)
        self.View3D_Threshold_slider_02.blockSignals(False)

    _from_slider(self, idx, sval)


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
    layer = self.layer_selection_box.currentIndex()
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
    sel = self.layer_selection_box.currentIndex()
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
            vol   = self.dicom_data[self.patientID][self.studyID][self.modality][t_idx]['3DMatrix']
            apply_all = self.View3D_update_all_3D.isChecked()
            sel       = self.layer_selection_box.currentIndex()
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
        self._crops       = {}
        self._dims        = {}
        self._colormaps   = {}
        self._full_ranges = {}
        self._clouds      = {}
        self._play3D_index = 0

        # colormap menu
        combo = self.findChild(QtWidgets.QComboBox, 'View3D_colormap')
        combo.addItems(CMAPS)
        combo.currentIndexChanged.connect(self._on_colormap_changed)
        self.View3D_update_all_3D.stateChanged.connect(self._on_colormap_changed)

        # layer change restores state
        self.layer_selection_box.currentIndexChanged.connect(self._on_layer_changed)

        # threshold callbacks
        self.View3D_Threshold_slider_01.valueChanged.connect(partial(_from_slider, self, 1))
        self.View3D_Threshold_slider_02.valueChanged.connect(partial(_from_slider, self, 2))
        self.View3D_Threshold_spin_01.valueChanged.connect(partial(_from_spin,   self, 1))
        self.View3D_Threshold_spin_02.valueChanged.connect(partial(_from_spin,   self, 2))

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
        for pt in points:
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
        sel   = self.layer_selection_box.currentIndex()
        cmap  = self.findChild(QtWidgets.QComboBox, 'View3D_colormap').currentText()
        for li, ctf in self._ctfs.items():
            if apply_all or li==sel:
                tmin,tmax = self._thresholds.get(li, (self.slider3D_LOW, self.slider3D_HIGH))
                otf = self._otfs[li]
                otf.RemoveAllPoints()
                otf.AddPoint(tmin,0.0)
                layer = self.layer_selection_box.currentIndex()
                opacity = self._opacities[layer] 
                otf.AddPoint(tmax, opacity)
                self.update_color_transfer(li, ctf, cmap, tmin, tmax)
        self.VTK3D_interactor.GetRenderWindow().Render()

    def _on_layer_changed(self, new_idx: int):
        if new_idx not in self._imgs:
            return

        # 1) restore that layer’s full [low,high]
        low, high = self._full_ranges[new_idx]
        self.slider3D_LOW, self.slider3D_HIGH = low, high
        self.slider3D_SPAN = max(high - low, 1e-6)
        self._s_to_v = lambda s: self.slider3D_LOW + (s/self.slider3D_RES)*self.slider3D_SPAN
        self._v_to_s = lambda v: int(round((v-self.slider3D_LOW)/self.slider3D_SPAN*self.slider3D_RES))

        # grab references to the four widgets
        spin_lo = self.View3D_Threshold_spin_01
        spin_hi = self.View3D_Threshold_spin_02
        slid_lo = self.View3D_Threshold_slider_01
        slid_hi = self.View3D_Threshold_slider_02

        # block *all* signals from them before touching ranges *or* values
        for w in (spin_lo, spin_hi, slid_lo, slid_hi):
            w.blockSignals(True)

        # reconfigure ranges
        slid_lo.setRange(0, self.slider3D_RES)
        slid_hi.setRange(0, self.slider3D_RES)
        spin_lo.setRange(low, high)
        spin_hi.setRange(low, high)

        # restore your *stored* thresholds for this layer
        tmin, tmax = self._thresholds.get(new_idx, (low, high))
        spin_lo.setValue(tmin)
        slid_lo.setValue(self._v_to_s(tmin))
        spin_hi.setValue(tmax)
        slid_hi.setValue(self._v_to_s(tmax))

        # unblock signals now that everything is in place
        for w in (spin_lo, spin_hi, slid_lo, slid_hi):
            w.blockSignals(False)

        # re-apply exactly those two end‐points
        otf = self._otfs[new_idx]
        otf.RemoveAllPoints()
        otf.AddPoint(tmin, 0.0)
        layer = self.layer_selection_box.currentIndex()
        opacity = self._opacities[layer] 
        otf.AddPoint(tmax, opacity)


        ctf = self._ctfs[new_idx]
        cmap = self._colormaps.get(new_idx,
            self.findChild(QtWidgets.QComboBox, 'View3D_colormap').currentText()
        )
        self.update_color_transfer(new_idx, ctf, cmap, tmin, tmax)

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
            layer_idx = self.layer_selection_box.currentIndex()

        # remove old volume if any
        if layer_idx in self._volumes:
            self.VTK3D_renderer.RemoveVolume(self._volumes[layer_idx])

        # flip Y axis to match VTK’s coordinate system
        vol = np.flip(volume_np, axis=1)
        nz, ny, nx = vol.shape
        arr = numpy_to_vtk(vol.ravel(order='C'), deep=True,
                           array_type=get_vtk_array_type(vol.dtype))

        img = vtk.vtkImageData()
        img.SetDimensions(nx, ny, nz)
        img.SetSpacing(*voxel_spacing)
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
        cmap = self.findChild(QtWidgets.QComboBox, 'View3D_colormap').currentText()
        self.update_color_transfer(layer_idx, ctf, cmap, vmin, vmax)

        # setup volume property
        volp = vtk.vtkVolumeProperty()
        volp.SetColor(ctf)
        volp.SetScalarOpacity(otf)
        volp.ShadeOff()
        volp.SetInterpolationTypeToLinear()
        self._vol_props[layer_idx] = volp

        # mapper
        mapper = vtkSmartVolumeMapper()
        mapper.SetInputData(img)
        mapper.SetBlendModeToComposite()
        mapper.CroppingOn()
        sx, sy, sz = voxel_spacing
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
        if layer is None or layer not in self._thresholds:
            return
        opacity = max(0.0, min(1.0, val))
        self._opacities[layer] = opacity
        # Update OTF
        tmin, tmax = self._thresholds[layer]
        otf = self._otfs[layer]
        otf.RemoveAllPoints()
        otf.AddPoint(tmin, 0.0)
        otf.AddPoint(tmax, opacity)
        self.VTK3D_interactor.GetRenderWindow().Render()


    def update_3d_volume(self, volume_np, layer_idx=None):
        """Update just the scalar data of an existing volume."""
        if layer_idx is None:
            layer_idx = self.layer_selection_box.currentIndex()
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
        self._crops.clear()
        self._dims.clear()
        self._full_ranges.clear()

        # Remove all point cloud actors
        for cloud in self._clouds.values():
            self.VTK3D_renderer.RemoveActor(cloud['actor'])
        self._clouds.clear()

        # Remove all surface actors if you use them
        if hasattr(self, '_surfaces'):
            for actor in self._surfaces.values():
                self.VTK3D_renderer.RemoveActor(actor)
            self._surfaces.clear()

        # Remove all rows from the clouds table
        self._3D_Struct_table.setRowCount(0)

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

