"""
3D view coordinates (fcn_3Dview): volumes, catheters, structures and spots are all placed in patient mm with
patient_to_view (X = x, Y = z, Z = -y), so a plan shown before its CT does not move when the CT comes, and the
catheters are inside the CT where the 2D views show them. Stored matrices have their rows flipped (load_dcm):
voxel [s, r, c] = patient (IPPx + c dx, IPPy + (rows - 1 - r) dy, IPPz + s dz).
"""
import numpy as np
import pytest
import vtk

from fcn_3Dview.volume_3d_viewer import VTK3DViewerMixin, patient_to_view

IPP = np.array([-100.0, -80.0, -30.0])
SPACING = (2.0, 1.5, 3.0)            # cols (x), rows (y), slices (z)
SHAPE = (6, 8, 10)                   # slices, rows, cols


def test_patient_to_view_is_a_rotation():
    p = np.array([[1.0, 2.0, 3.0], [-4.0, 5.0, -6.0]])
    assert np.allclose(patient_to_view(p), [[1.0, 3.0, -2.0], [-4.0, -6.0, -5.0]])
    basis = patient_to_view(np.eye(3))
    assert np.isclose(np.linalg.det(basis), 1.0)            # not mirrored


class _Stub:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _viewer(qapp, medical_image=None, plan=None):
    """What display_numpy_volume and the brachy table use of the main window."""
    from PySide6.QtWidgets import QWidget

    class Viewer(VTK3DViewerMixin):
        pass

    v = Viewer()
    render_window = _Stub(Render=lambda: None)
    v.VTK3D_renderer = vtk.vtkRenderer()
    v.VTK3D_interactor = _Stub(GetRenderWindow=lambda: render_window)
    v.layer_selected = _Stub(currentIndex=lambda: 0)
    v.View3D_colormap = _Stub(currentText=lambda: "Gray")
    v.Layer_0_alpha_sli = _Stub(setValue=lambda value: None)
    v._volumes, v._imgs, v._ctfs, v._otfs, v._vol_props = {}, {}, {}, {}, {}
    v._full_ranges, v._crops, v._colormaps, v._isovalues, v._clouds = {}, {}, {}, {}, {}
    v._thresholds, v._dims = {0: (0.0, 1.0)}, {0: (1, 1, 1)}     # no slider / crop widgets here
    v._opacities = [1.0] * 4
    v._render_controls_initialized = False
    v.tab_41 = QWidget()
    v.medical_image = medical_image or {}
    if plan:
        v.patientID_plan, v.studyID_plan, v.modality_plan, v.series_index_plan = plan
    return v


def test_volume_voxels_at_their_patient_position(qapp):
    v = _viewer(qapp)
    volume = np.arange(np.prod(SHAPE), dtype=np.float32).reshape(SHAPE)
    v.display_numpy_volume(volume, voxel_spacing=SPACING, layer_idx=0, position=IPP)
    matrix = v._volumes[0].GetMatrix()
    ny = SHAPE[1]
    for s, r, c in ((0, 0, 0), (5, 7, 9), (2, 3, 4)):
        local = (c * SPACING[0], (ny - 1 - r) * SPACING[1], s * SPACING[2], 1.0)     # the image rows flipped back
        patient = IPP + np.array([c * SPACING[0], (ny - 1 - r) * SPACING[1], s * SPACING[2]])
        assert np.allclose(matrix.MultiplyPoint(local)[:3], patient_to_view(patient)[0])
    # the VTK image holds the stored voxel there
    image = v._imgs[0]
    assert image.GetScalarComponentAsDouble(4, ny - 1 - 3, 2, 0) == volume[2, 3, 4]


def test_catheters_do_not_move_when_the_ct_comes(qapp):
    from PySide6.QtWidgets import QCheckBox
    from fcn_3Dview import brachy_3D_table as bt
    # inside the image: x -100..-82, y -80..-69.5, z -30..-15
    ch_pos = np.array([[-95.0, -78.0, -28.0], [-90.0, -75.0, -22.0], [-85.0, -71.0, -17.0]], dtype=np.float32)
    dwells = np.zeros((2, 9), dtype=np.float32)
    dwells[:, 3:6] = ch_pos[:2]
    plan_meta = {"Plan_Brachy_Channels": [{"ChPos": ch_pos, "DwellInfo": dwells}], "Plan_Dose_References": []}
    medical_image = {"P": {"S": {"RTPLAN": [{"metadata": plan_meta}]}}}
    v = _viewer(qapp, medical_image, ("P", "S", "RTPLAN", 0))

    def points(name):
        """The catheter's line points (the input of its tube)."""
        mapper = v._3D_brachy_actors[name][0].GetMapper()
        tube = mapper.GetInputAlgorithm()
        poly = tube.GetInput() if isinstance(tube, vtk.vtkTubeFilter) else mapper.GetInput()
        return np.array([poly.GetPoint(i) for i in range(poly.GetNumberOfPoints())])

    bt.init_3D_brachy_table(v)                          # the plan first: no image in the 3D view
    first = points("Catheter - Ch 1")
    assert np.allclose(first, patient_to_view(ch_pos))
    v.display_numpy_volume(np.zeros(SHAPE, np.float32), voxel_spacing=SPACING, layer_idx=0, position=IPP)
    for row in range(v._3D_brachy_table.rowCount()):    # visibility off and on
        check = v._3D_brachy_table.cellWidget(row, 5).findChild(QCheckBox)
        check.setChecked(False)
        check.setChecked(True)
    assert np.allclose(points("Catheter - Ch 1"), first)
    low, high = np.array(v._volumes[0].GetBounds()).reshape(3, 2).T
    assert np.all((first >= low) & (first <= high))      # inside the image


def test_orientation_axes_bottom_right(qapp):
    from PySide6.QtWidgets import QCheckBox
    from fcn_3Dview.render_controls import apply_3d_axes_visibility
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.AddRenderer(vtk.vtkRenderer())
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)
    v = _Stub(VTK3D_interactor=interactor, View3D_shoiw_axes_checkBox=QCheckBox())
    v.View3D_shoiw_axes_checkBox.setChecked(True)
    apply_3d_axes_visibility(v)
    marker = v._3d_axes_widget
    assert marker.GetViewport() == pytest.approx((0.8, 0.0, 1.0, 0.2))
    assert marker.GetEnabled() == 1 and marker.GetInteractive() == 0
    axes = marker.GetOrientationMarker()
    assert (axes.GetXAxisLabelText(), axes.GetYAxisLabelText(), axes.GetZAxisLabelText()) == ("X (L)", "Y (S)", "Z (A)")
    v.View3D_shoiw_axes_checkBox.setChecked(False)
    apply_3d_axes_visibility(v)
    assert marker.GetEnabled() == 0
