"""
Text of the 2D views (fcn_display.mouse_move_slicechanges): the slice labels and the voxel / position under
the mouse in the user's axes, as the MCNP input: X = DICOM x, Y = DICOM z, Z = -DICOM y (anterior +); voxel
(column, slice, row as stored), the X, Y, Z of the MonteCarlo grids.
"""
from types import SimpleNamespace

import numpy as np
import vtk

from fcn_display import mouse_move_slicechanges as mm
from fcn_mcnp.mcnp_input import to_mcnp_axes

IPP = (-10.0, 20.0, 30.0)
PS_ROW, PS_COL, ST = 0.9, 0.8, 2.0
NS, NR, NC = 4, 5, 6


class _Text:
    def SetInput(self, text):
        self.text = text


class _Picker:
    """vtkPointPicker stand-in: picks the world point WORLD wherever the mouse is."""
    WORLD = (0.0, 0.0, 0.0)

    def Pick(self, *args):
        pass

    def GetPickPosition(self):
        return self.WORLD


def _view_app(coronal_index):
    """The coronal view of a CT whose voxel values are their numbers."""
    vol = np.arange(NS * NR * NC, dtype=float).reshape(NS, NR, NC)
    image = vtk.vtkImageData()                      # the coronal slice: columns along x, slices along y
    image.SetDimensions(NC, NS, 1)
    image.SetSpacing(PS_COL, ST, 1.0)
    actor = SimpleNamespace(GetPosition=lambda: (0.0, 0.0, 0.0), GetInput=lambda: image)
    window = SimpleNamespace(Render=lambda: None)
    return SimpleNamespace(display_data=[vol], layer_selected=SimpleNamespace(currentIndex=lambda: 0),
                           current_axial_slice_index=[1], current_coronal_slice_index=[coronal_index],
                           current_sagittal_slice_index=[2], LeftButtonCoronalDown=False, LeftButtonRuler=False,
                           _text_dragging=False, renCoronal=None, imageActorCoronal=[actor],
                           pixel_spac=np.array([[PS_ROW, PS_COL]]), slice_thick=np.array([ST]),
                           Im_PatPosition=np.array([IPP]), Im_Offset=np.zeros((1, 3)), DataType="DICOM",
                           textActorCoronal=_Text(), vtkWidgetCoronal=SimpleNamespace(GetRenderWindow=lambda: window),
                           CoronalSlider=SimpleNamespace(setValue=lambda v: None))


def test_coronal_view_text_in_the_users_axes(monkeypatch):
    monkeypatch.setattr(mm.vtk, "vtkPointPicker", _Picker)
    monkeypatch.setattr(mm, "displaycoronal", lambda self: None)
    app = _view_app(coronal_index=1)                # row 1 as stored = DICOM row 3 (rows stored flipped)
    y = IPP[1] + (NR - 1 - 1) * PS_ROW              # its DICOM y
    _Picker.WORLD = (2 * PS_COL, 3 * ST, 0.0)       # column 2, slice 3
    mm.onMouseMoveCoronal(app, SimpleNamespace(GetEventPosition=lambda: (0, 0), GetLastEventPosition=lambda: (0, 0)), None)
    x, z = IPP[0] + 2 * PS_COL, IPP[2] + 3 * ST
    X, Y, Z = to_mcnp_axes(x, y, z)
    value = app.display_data[0][3, 1, 2]
    assert app.textActorCoronal.text == f"Slice (Z): {-y:.2f} mm (2, 3, 1) Vox. ({X:.2f}, {Y:.2f}, {Z:.2f}) mm {value:.4f}"
    assert Z == -y < 0                              # the label and the triple: the same Z, as MCNP

    mm.change_sliceCoronal(app, 1)                  # the next row up: more anterior, Z grows
    assert app.textActorCoronal.text == f"Slice (Z): 2 : {-(y - PS_ROW):.2f} mm"
