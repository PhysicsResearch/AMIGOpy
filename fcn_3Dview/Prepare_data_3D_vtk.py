# Diplay dicom 3D - VTK

# Imports for VTK 9.x
from vtkmodules.vtkRenderingVolumeOpenGL2 import vtkSmartVolumeMapper
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtkmodules.all as vtk
from vtkmodules.util.numpy_support import numpy_to_vtk, get_vtk_array_type


# Standard imports
import numpy as np
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import QTimer

def display_numpy_volume(self, volume_np: np.ndarray,
                         voxel_spacing=(1.0, 1.0, 1.0)):
    """
    Render a NumPy volume in 3D with GPU cropping and dynamic sliders,
    with the coronal axis flipped.
    """
    # --- 0) flip coronal direction: reverse Y axis ---
    volume_np = np.flip(volume_np, axis=1)

    # --- rest is unchanged ---
    renderer   = self.VTK3D_renderer
    interactor = self.VTK3D_interactor

    # remember spacing for cropping
    self._voxel_spacing = voxel_spacing

    # 1) NumPy → vtkImageData
    nz, ny, nx = volume_np.shape
    flat = numpy_to_vtk(volume_np.ravel(order='C'),
                        deep=True,
                        array_type=get_vtk_array_type(volume_np.dtype))

    img = vtk.vtkImageData()
    img.SetDimensions(nx, ny, nz)
    img.SetSpacing(*voxel_spacing)
    img.GetPointData().SetScalars(flat)
    self._img = img 

    # 2) transfer functions…
    vmin, vmax = float(volume_np.min()), float(volume_np.max())
    ctf = vtk.vtkColorTransferFunction()
    ctf.AddRGBPoint(vmin, 0, 0, 0)
    ctf.AddRGBPoint(vmax, 1, 1, 1)

    otf = vtk.vtkPiecewiseFunction()
    otf.AddPoint(vmin, 0)
    otf.AddPoint(vmax, 1)

    vol_prop = vtk.vtkVolumeProperty()
    vol_prop.SetColor(ctf)
    vol_prop.SetScalarOpacity(otf)
    vol_prop.ShadeOff()
    vol_prop.SetInterpolationTypeToLinear()

    self._ctf = ctf
    self._otf = otf
    self._volume_prop = vol_prop

    # 3) GPU mapper + composite blending + cropping
    mapper = vtkSmartVolumeMapper()
    mapper.SetInputData(img)
    mapper.SetBlendModeToComposite()
    mapper.CroppingOn()

    sx, sy, sz = voxel_spacing
    mapper.SetCroppingRegionPlanes(
        0 * sx, (nx - 1) * sx,
        0 * sy, (ny - 1) * sy,
        0 * sz, (nz - 1) * sz
    )
    mapper.SetCroppingRegionFlagsToSubVolume()

    # 4) assemble & add
    self._volume = vtk.vtkVolume()
    self._volume.SetMapper(mapper)
    self._volume.SetProperty(vol_prop)
    renderer.RemoveAllViewProps()
    renderer.AddVolume(self._volume)
    renderer.ResetCamera()

    # 5) interactor
    interactor.Initialize()
    interactor.Start()

    # 6) widgets
    initialize_crop_widgets(self, (nx, ny, nz))
    initialize_3Dsliders(self, vmin, vmax, n_steps=100)

    # 7) initial render
    _apply_threshold(self, vmin, vmax)
    interactor.GetRenderWindow().Render()

def _apply_threshold(self, tmin: float, tmax: float) -> None:
    """Rewrite the transfer functions and re-render."""
    self._ctf.RemoveAllPoints()
    self._ctf.AddRGBPoint(tmin, 0.0, 0.0, 0.0)
    self._ctf.AddRGBPoint(tmax, 1.0, 1.0, 1.0)

    self._otf.RemoveAllPoints()
    self._otf.AddPoint(tmin, 0.0)
    self._otf.AddPoint(tmax, 1.0)

    self.VTK3D_interactor.GetRenderWindow().Render()


def initialize_3Dsliders(self, low: float, high: float, n_steps: int = 100):
    """
    Prepare the two sliders + two spin-boxes for a new dataset.

    Args:
        low  : real minimum scalar in the volume
        high : real maximum scalar in the volume
        n_steps: slider tick count (granularity). 100 → ≈1 % steps
    """
    # -----------------------------------------------------------------------
    # dataset-dependent constants
    # -----------------------------------------------------------------------
    self.slider3D_LOW        = float(low)
    self.slider3D_HIGH       = float(high)
    self.slider3D_SPAN       = self.slider3D_HIGH - self.slider3D_LOW
    self.slider3D_RESOLUTION = int(n_steps)       # 100 keeps your old feel
    if self.slider3D_SPAN == 0:                   # flat image, avoid /0
        self.slider3D_SPAN = 1e-6

    # helpers – slider<->value conversions
    self._s_to_v = lambda s: self.slider3D_LOW +               \
                             (s / self.slider3D_RESOLUTION) *  \
                             self.slider3D_SPAN
    self._v_to_s = lambda v: int(round((v - self.slider3D_LOW) /
                                       self.slider3D_SPAN *
                                       self.slider3D_RESOLUTION))

    # -----------------------------------------------------------------------
    # configure widgets
    # -----------------------------------------------------------------------
    for slider in (self.View3D_Threshold_slider_01,
                   self.View3D_Threshold_slider_02):
        slider.setRange(0, self.slider3D_RESOLUTION)

    for spin in (self.View3D_Threshold_spin_01,
                 self.View3D_Threshold_spin_02):
        spin.setRange(self.slider3D_LOW, self.slider3D_HIGH)
        spin.setDecimals(3)                          # or 0 if HU integers
        spin.setSingleStep(self.slider3D_SPAN /
                           self.slider3D_RESOLUTION)

    # -----------------------------------------------------------------------
    # initial values (full window)
    # -----------------------------------------------------------------------
    self.View3D_Threshold_slider_01.setValue(0)
    self.View3D_Threshold_slider_02.setValue(self.slider3D_RESOLUTION)
    self.View3D_Threshold_spin_01.setValue(self.slider3D_LOW)
    self.View3D_Threshold_spin_02.setValue(self.slider3D_HIGH)

    # -----------------------------------------------------------------------
    # signal / slot wiring –- unchanged names
    # -----------------------------------------------------------------------
    self.View3D_Threshold_slider_01.valueChanged.connect(
        lambda s: _from_slider(self, 1, s))
    self.View3D_Threshold_slider_02.valueChanged.connect(
        lambda s: _from_slider(self, 2, s))
    self.View3D_Threshold_spin_01.valueChanged.connect(
        lambda v: _from_spin(self, 1, v))
    self.View3D_Threshold_spin_02.valueChanged.connect(
        lambda v: _from_spin(self, 2, v))
    
def _from_slider(self, idx: int, sval: int) -> None:
    """Slider → spin-box, enforcing min ≤ max."""
    v = self._s_to_v(sval)
    if idx == 1:
        if v > self.View3D_Threshold_spin_02.value():
            v = self.View3D_Threshold_spin_02.value()
            sval = self._v_to_s(v)
            self.View3D_Threshold_slider_01.blockSignals(True)
            self.View3D_Threshold_slider_01.setValue(sval)
            self.View3D_Threshold_slider_01.blockSignals(False)
        self.View3D_Threshold_spin_01.setValue(v)
    else:
        if v < self.View3D_Threshold_spin_01.value():
            v = self.View3D_Threshold_spin_01.value()
            sval = self._v_to_s(v)
            self.View3D_Threshold_slider_02.blockSignals(True)
            self.View3D_Threshold_slider_02.setValue(sval)
            self.View3D_Threshold_slider_02.blockSignals(False)
        self.View3D_Threshold_spin_02.setValue(v)

    # refresh the transfer functions
    _apply_threshold(self,self.View3D_Threshold_spin_01.value(),
                          self.View3D_Threshold_spin_02.value())


def _from_spin(self, idx: int, v: float) -> None:
    """Spin-box → slider, enforcing min ≤ max."""
    sval = self._v_to_s(v)
    if idx == 1:
        if v > self.View3D_Threshold_spin_02.value():
            v = self.View3D_Threshold_spin_02.value()
            sval = self._v_to_s(v)
            self.View3D_Threshold_spin_01.blockSignals(True)
            self.View3D_Threshold_spin_01.setValue(v)
            self.View3D_Threshold_spin_01.blockSignals(False)
        self.View3D_Threshold_slider_01.setValue(sval)
    else:
        if v < self.View3D_Threshold_spin_01.value():
            v = self.View3D_Threshold_spin_01.value()
            sval = self._v_to_s(v)
            self.View3D_Threshold_spin_02.blockSignals(True)
            self.View3D_Threshold_spin_02.setValue(v)
            self.View3D_Threshold_spin_02.blockSignals(False)
        self.View3D_Threshold_slider_02.setValue(sval)

    # refresh the transfer functions
    _apply_threshold(self,self.View3D_Threshold_spin_01.value(),
                          self.View3D_Threshold_spin_02.value())
    

def initialize_crop_widgets(self, dims):
    """
    Set up 6 sliders + 6 spin-boxes for [min,max] on each axis,
    enforcing min ≤ max and wiring everything to apply_crop().
    """
    nx, ny, nz = dims
    # which axis each plane corresponds to:
    axis_sizes = {
        'sagittal':    nx,   # slice along X
        'coronal':  ny,   # slice along Y
        'axial': nz    # slice along Z
    }

    for axis, size in axis_sizes.items():
        # fetch widgets by name
        s1 = getattr(self, f'View3D_{axis}_slider_01')
        s2 = getattr(self, f'View3D_{axis}_slider_02')
        b1 = getattr(self, f'View3D_{axis}_spin_01')
        b2 = getattr(self, f'View3D_{axis}_spin_02')

        # set ranges
        for w in (s1, s2):
            w.setRange(0, size-1)
        for w in (b1, b2):
            w.setRange(0, size-1)
            w.setSingleStep(1)

        # initialize to full-volume
        s1.setValue(0)
        b1.setValue(0)
        s2.setValue(size-1)
        b2.setValue(size-1)

        # wire signals
        s1.valueChanged.connect(lambda v, ax=axis: _crop_from_slider(self,ax, 1, v))
        s2.valueChanged.connect(lambda v, ax=axis: _crop_from_slider(self, ax, 2, v))
        b1.valueChanged.connect(lambda v, ax=axis: _crop_from_spin(self,ax, 1, v))
        b2.valueChanged.connect(lambda v, ax=axis: _crop_from_spin(self,ax, 2, v))

def _crop_from_slider(self, axis: str, idx: int, sval: int):
    """Slider→spin, enforce 01≤02, then crop."""
    s1 = getattr(self, f'View3D_{axis}_slider_01')
    s2 = getattr(self, f'View3D_{axis}_slider_02')
    b1 = getattr(self, f'View3D_{axis}_spin_01')
    b2 = getattr(self, f'View3D_{axis}_spin_02')

    # enforce
    if idx == 1 and sval > s2.value():
        sval = s2.value()
        s1.blockSignals(True)
        s1.setValue(sval)
        s1.blockSignals(False)
    elif idx == 2 and sval < s1.value():
        sval = s1.value()
        s2.blockSignals(True)
        s2.setValue(sval)
        s2.blockSignals(False)

    # sync spin-box
    if idx == 1:
        b1.setValue(sval)
    else:
        b2.setValue(sval)

    _apply_crop(self)

def _crop_from_spin(self, axis: str, idx: int, v: int):
    """Spin→slider, enforce 01≤02, then crop."""
    s1 = getattr(self, f'View3D_{axis}_slider_01')
    s2 = getattr(self, f'View3D_{axis}_slider_02')
    b1 = getattr(self, f'View3D_{axis}_spin_01')
    b2 = getattr(self, f'View3D_{axis}_spin_02')

    # enforce
    if idx == 1 and v > b2.value():
        v = b2.value()
        b1.blockSignals(True)
        b1.setValue(v)
        b1.blockSignals(False)
    elif idx == 2 and v < b1.value():
        v = b1.value()
        b2.blockSignals(True)
        b2.setValue(v)
        b2.blockSignals(False)

    # sync slider
    if idx == 1:
        s1.setValue(v)
    else:
        s2.setValue(v)

    _apply_crop(self)

def _apply_crop(self):
    """
    Read slider/spin-box indices, convert to physical coordinates,
    update the mapper’s cropping planes, and re-render.
    """
    # get index‐ranges from widgets
    xmin_i, xmax_i = (self.View3D_sagittal_spin_01.value(),
                      self.View3D_sagittal_spin_02.value())
    ymin_i, ymax_i = (self.View3D_coronal_spin_01.value(),
                      self.View3D_coronal_spin_02.value())
    zmin_i, zmax_i = (self.View3D_axial_spin_01.value(),
                      self.View3D_axial_spin_02.value())

    # convert indices to physical coords
    sx, sy, sz = self._voxel_spacing
    xmin, xmax = xmin_i * sx, xmax_i * sx
    ymin, ymax = ymin_i * sy, ymax_i * sy
    zmin, zmax = zmin_i * sz, zmax_i * sz

    # update the mapper’s crop
    mapper = self._volume.GetMapper()
    mapper.SetCroppingRegionPlanes(
        xmin, xmax,
        ymin, ymax,
        zmin, zmax
    )
    mapper.SetCroppingRegionFlagsToSubVolume()

    # re-render
    self.VTK3D_interactor.GetRenderWindow().Render()

def update_3d_volume(self, volume_np: np.ndarray):
    # print("🔄 update_3d_volume called; incoming shape:", volume_np.shape)
    flat = numpy_to_vtk(
        volume_np.ravel(order='C'),
        deep=True,
        array_type=get_vtk_array_type(volume_np.dtype)
    )
    self._img.GetPointData().SetScalars(flat)
    self._img.Modified()
    self.VTK3D_interactor.GetRenderWindow().Render()

def play_4D_sequence_3D(self, play: bool):
    """
    Start/stop looping 3D playback. 'play' is True when button is checked.
    """
    if play:
        # Turn button red to show “playing”
        self.View3D_play4D.setStyleSheet("background-color: red; color: white;")

        # --- collect & sort frames ---
        checked = []
        table = self.CT4D_table_display
        for row in range(table.rowCount()):
            cb = table.cellWidget(row, 0).layout().itemAt(0).widget()
            if cb.isChecked():
                t_idx = int(table.item(row, 3).text())
                seq   = int(table.item(row, 1).text())
                checked.append((t_idx, seq))
        checked.sort(key=lambda x: x[1])
        if not checked:
            return

        # prepare playback
        self._play3D_index = 0
        interval = max(1, self.Play_DCT_speed.value())
        ms = int(1000 / interval)

        def _advance():
            # stop if button was toggled off
            if not self.View3D_play4D.isChecked():
                return

            # grab and show the next volume
            t_idx = checked[self._play3D_index][0]

            
            vol = (
                self.dicom_data[self.patientID]
                             [self.studyID]
                             [self.modality]
                             [t_idx]['3DMatrix']
            )

            # flip coronal axis to match orientation
            vol = np.flip(vol, axis=1)

            update_3d_volume(self,vol)

            # advance & wrap
            self._play3D_index = (self._play3D_index + 1) % len(checked)
            QTimer.singleShot(ms, _advance)

        # kick off the first frame
        _advance()

    else:
        # stopped: reset button style and index
        self.View3D_play4D.setStyleSheet("")
        self._play3D_index = 0