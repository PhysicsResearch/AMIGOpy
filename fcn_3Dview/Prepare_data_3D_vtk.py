# Diplay dicom 3D - VTK

# Imports for VTK 9.x
from vtkmodules.vtkRenderingVolumeOpenGL2 import vtkSmartVolumeMapper
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtkmodules.all as vtk
from vtkmodules.util.numpy_support import numpy_to_vtk, get_vtk_array_type

# Standard imports
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
import matplotlib.cm as cm

# Suggested colormaps
CMAPS = ['Gray', 'Bone', 'Hot', 'Cool', 'Viridis',
         'Plasma', 'Jet', 'Rainbow', 'Spectral', 'BlueWhiteRed']

# -----------------------------------------------------------------------------
# In your widget __init__, initialize storage and wire colormap and threshold
# -----------------------------------------------------------------------------
# self._imgs = {}
# self._ctfs = {}
# self._otfs = {}
# self._vol_props = {}
# self._volumes = {}
# self._play3D_index = 0
# initialize_colormap_menu(self)
# connect threshold sliders/spins:
# self.View3D_Threshold_slider_01.valueChanged.connect(lambda v: _from_slider(self,1,v))
# self.View3D_Threshold_slider_02.valueChanged.connect(lambda v: _from_slider(self,2,v))
# self.View3D_Threshold_spin_01.valueChanged.connect(lambda v: _from_spin(self,1,v))
# self.View3D_Threshold_spin_02.valueChanged.connect(lambda v: _from_spin(self,2,v))

# -----------------------------------------------------------------------------
# Helper: populate colormap combobox and wire signals
# -----------------------------------------------------------------------------
def initialize_colormap_menu(self):
    combo: QtWidgets.QComboBox = self.findChild(
        QtWidgets.QComboBox, 'View3D_colormap'
    )
    combo.addItems(CMAPS)
    combo.currentIndexChanged.connect(lambda _: _on_colormap_changed(self))
    self.View3D_update_all_3D.stateChanged.connect(lambda _: _on_colormap_changed(self))

# -----------------------------------------------------------------------------
# Build a vtkColorTransferFunction from a Matplotlib colormap
# -----------------------------------------------------------------------------
def update_color_transfer(ctf: vtk.vtkColorTransferFunction,
                          cmap_name: str,
                          tmin: float, tmax: float,
                          n_samples: int = 256):
    ctf.RemoveAllPoints()
    name = 'bluewhitered' if cmap_name == 'BlueWhiteRed' else cmap_name.lower()
    try:
        mpl_cmap = cm.get_cmap(name)
    except Exception:
        mpl_cmap = cm.get_cmap('gray')
    for i in range(n_samples):
        frac = i / float(n_samples - 1)
        val = tmin + frac * (tmax - tmin)
        r, g, b, _ = mpl_cmap(frac)
        ctf.AddRGBPoint(val, r, g, b)

# -----------------------------------------------------------------------------
# Slot: update color & opacity for selected or all layers
# -----------------------------------------------------------------------------
def _on_colormap_changed(self):
    tmin = self.View3D_Threshold_spin_01.value()
    tmax = self.View3D_Threshold_spin_02.value()
    cmap = self.findChild(QtWidgets.QComboBox,'View3D_colormap').currentText()
    apply_all = self.View3D_update_all_3D.isChecked()
    sel_layer = self.layer_selection_box.currentIndex()
    for layer_idx in list(self._volumes.keys()):
        if apply_all or layer_idx == sel_layer:
            # opacity
            otf = self._otfs[layer_idx]
            otf.RemoveAllPoints()
            otf.AddPoint(tmin, 0.0)
            otf.AddPoint(tmax, 1.0)
            # color
            ctf = self._ctfs[layer_idx]
            update_color_transfer(ctf, cmap, tmin, tmax)
    self.VTK3D_interactor.GetRenderWindow().Render()

# -----------------------------------------------------------------------------
# Display or replace one of up to 4 layers and init sliders
# -----------------------------------------------------------------------------
def display_numpy_volume(self, volume_np: np.ndarray,
                         voxel_spacing=(1.0,1.0,1.0),
                         layer_idx=None):
    # connect threshold sliders/spins:
    self.View3D_Threshold_slider_01.valueChanged.connect(lambda v: _from_slider(self,1,v))
    self.View3D_Threshold_slider_02.valueChanged.connect(lambda v: _from_slider(self,2,v))
    self.View3D_Threshold_spin_01.valueChanged.connect(lambda v: _from_spin(self,1,v))
    self.View3D_Threshold_spin_02.valueChanged.connect(lambda v: _from_spin(self,2,v))
    if layer_idx is None:
        layer_idx = self.layer_selection_box.currentIndex()
    # remove old
    if layer_idx in self._volumes:
        self.VTK3D_renderer.RemoveVolume(self._volumes[layer_idx])
    # flip coronal
    vol = np.flip(volume_np, axis=1)
    nz,ny,nx = vol.shape
    arr = numpy_to_vtk(vol.ravel(order='C'),deep=True,
                       array_type=get_vtk_array_type(vol.dtype))
    img = vtk.vtkImageData()
    img.SetDimensions(nx,ny,nz);
    img.SetSpacing(*voxel_spacing);
    img.GetPointData().SetScalars(arr)
    self._imgs[layer_idx]=img
    # transfer funcs
    vmin,vmax=float(vol.min()),float(vol.max())
    ctf=vtk.vtkColorTransferFunction()
    otf=vtk.vtkPiecewiseFunction(); otf.AddPoint(vmin,0.0); otf.AddPoint(vmax,1.0)
    self._ctfs[layer_idx]=ctf; self._otfs[layer_idx]=otf
    # apply colormap
    cmap=self.findChild(QtWidgets.QComboBox,'View3D_colormap').currentText()
    update_color_transfer(ctf,cmap,vmin,vmax)
    # volume prop
    volp=vtk.vtkVolumeProperty(); volp.SetColor(ctf); volp.SetScalarOpacity(otf)
    volp.ShadeOff(); volp.SetInterpolationTypeToLinear()
    self._vol_props[layer_idx]=volp
    # mapper & volume
    m=vtkSmartVolumeMapper(); m.SetInputData(img); m.SetBlendModeToComposite(); m.CroppingOn()
    sx,sy,sz=voxel_spacing
    m.SetCroppingRegionPlanes(0,(nx-1)*sx,0,(ny-1)*sy,0,(nz-1)*sz)
    m.SetCroppingRegionFlagsToSubVolume()
    volobj=vtk.vtkVolume(); volobj.SetMapper(m); volobj.SetProperty(volp)
    self._volumes[layer_idx]=volobj
    self.VTK3D_renderer.AddVolume(volobj)
    if layer_idx==0: self.VTK3D_renderer.ResetCamera()
    # init sliders for this data range
    initialize_3Dsliders(self,vmin,vmax)
    self.VTK3D_interactor.GetRenderWindow().Render()

# -----------------------------------------------------------------------------
# Threshold widgets setup and callbacks
# -----------------------------------------------------------------------------
def initialize_3Dsliders(self,low,high,n_steps=100):
    self.slider3D_LOW=float(low); self.slider3D_HIGH=float(high)
    self.slider3D_SPAN=self.slider3D_HIGH-self.slider3D_LOW
    self.slider3D_RES=int(n_steps) if self.slider3D_SPAN else 100
    if self.slider3D_SPAN==0: self.slider3D_SPAN=1e-6
    self._s_to_v=lambda s:self.slider3D_LOW+(s/self.slider3D_RES)*self.slider3D_SPAN
    self._v_to_s=lambda v:int(round((v-self.slider3D_LOW)/self.slider3D_SPAN*self.slider3D_RES))
    for sl in (self.View3D_Threshold_slider_01,self.View3D_Threshold_slider_02):
        sl.setRange(0,self.slider3D_RES)
        sl.blockSignals(True)
    for sp in (self.View3D_Threshold_spin_01,self.View3D_Threshold_spin_02):
        sp.setRange(self.slider3D_LOW,self.slider3D_HIGH)
        sp.setDecimals(3)
        sp.setSingleStep(self.slider3D_SPAN/self.slider3D_RES)
        sp.blockSignals(True)
    self.View3D_Threshold_slider_01.setValue(0); self.View3D_Threshold_spin_01.setValue(self.slider3D_LOW)
    self.View3D_Threshold_slider_02.setValue(self.slider3D_RES); self.View3D_Threshold_spin_02.setValue(self.slider3D_HIGH)
    for sl in (self.View3D_Threshold_slider_01,self.View3D_Threshold_slider_02): sl.blockSignals(False)
    for sp in (self.View3D_Threshold_spin_01,self.View3D_Threshold_spin_02): sp.blockSignals(False)


def _from_slider(self,idx,sval):
    v=self._s_to_v(sval)
    if idx==1:
        if v>self.View3D_Threshold_spin_02.value(): v=self.View3D_Threshold_spin_02.value(); sval=self._v_to_s(v)
        self.View3D_Threshold_spin_01.blockSignals(True); self.View3D_Threshold_spin_01.setValue(v); self.View3D_Threshold_spin_01.blockSignals(False)
    else:
        if v<self.View3D_Threshold_spin_01.value(): v=self.View3D_Threshold_spin_01.value(); sval=self._v_to_s(v)
        self.View3D_Threshold_spin_02.blockSignals(True); self.View3D_Threshold_spin_02.setValue(v); self.View3D_Threshold_spin_02.blockSignals(False)
    _on_colormap_changed(self)


def _from_spin(self,idx,v):
    sval=self._v_to_s(v)
    if idx==1:
        self.View3D_Threshold_slider_01.blockSignals(True); self.View3D_Threshold_slider_01.setValue(sval); self.View3D_Threshold_slider_01.blockSignals(False)
    else:
        self.View3D_Threshold_slider_02.blockSignals(True); self.View3D_Threshold_slider_02.setValue(sval); self.View3D_Threshold_slider_02.blockSignals(False)
    _on_colormap_changed(self)

# -----------------------------------------------------------------------------
# Update raw volume data for an existing layer
# -----------------------------------------------------------------------------
def update_3d_volume(self,volume_np,layer_idx=None):
    if layer_idx is None: layer_idx=self.layer_selection_box.currentIndex()
    vol=np.flip(volume_np,axis=1)
    flat=numpy_to_vtk(vol.ravel(order='C'),deep=True,array_type=get_vtk_array_type(vol.dtype))
    img=self._imgs[layer_idx]; img.GetPointData().SetScalars(flat); img.Modified()
    self.VTK3D_interactor.GetRenderWindow().Render()

# -----------------------------------------------------------------------------
# 4D playback: only updates the selected (or all) layer
# -----------------------------------------------------------------------------
def play_4D_sequence_3D(self,play):
    if play:
        self.View3D_play4D.setStyleSheet("background-color: red; color: white;")
        checked=[]; table=self.CT4D_table_display
        for row in range(table.rowCount()):
            cb=table.cellWidget(row,0).layout().itemAt(0).widget()
            if cb.isChecked(): checked.append((int(table.item(row,3).text()),int(table.item(row,1).text())))
        checked.sort(key=lambda x:x[1]);
        if not checked: return
        self._play3D_index=0; ms=int(1000/max(1,self.Play_DCT_speed.value()))
        def _advance():
            if not self.View3D_play4D.isChecked(): return
            t_idx=checked[self._play3D_index][0]
            vol=self.dicom_data[self.patientID][self.studyID][self.modality][t_idx]['3DMatrix']
            sel=self.layer_selection_box.currentIndex(); all_=self.View3D_update_all_3D.isChecked()
            if all_: [self.update_3d_volume(vol,li) for li in range(4)]
            else: self.update_3d_volume(vol,sel)
            self._play3D_index=(self._play3D_index+1)%len(checked)
            QTimer.singleShot(ms,_advance)
        _advance()
    else:
        self.View3D_play4D.setStyleSheet(""); self._play3D_index=0
