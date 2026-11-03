"""
Isodoses (fcn_evaluation.isodose): templates kept like the HU LUTs, contour lines placed on the views
where the dose is shown as a layer (rows stored flipped), dashes and dots along the lines.
"""
from types import SimpleNamespace

import numpy as np
import pytest

from fcn_evaluation import isodose
from fcn_evaluation.isodose import (dots_along, layer_offset, level_doses, pattern_pieces, read_template, styled,
                                    view_isodose_lines, write_template)

IPP0 = (-50.0, -40.0, -30.0)          # layer 0 (CT): centre of the voxel with the lowest x, y, z (mm)
PS_COL0, PS_ROW0, ST0 = 1.0, 1.0, 2.0
NS0, NR0, NC0 = 30, 80, 100
CENTRE = np.array([-12.0, -3.0, 6.0])   # DICOM point of the dose maximum


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(isodose, "_template_dir", lambda: (tmp_path / "Isodose_templates").mkdir(exist_ok=True)
                        or str(tmp_path / "Isodose_templates"))
    monkeypatch.setattr(isodose, "_settings_path", lambda: str(tmp_path / "settings.json"))
    return tmp_path


def test_templates_default_and_round_trip(store):
    assert isodose._ensure_templates() == ["Default"]
    default = read_template(isodose._template_path("Default"))
    assert default == {**isodose.DEFAULT_TEMPLATE, "levels": tuple(isodose.DEFAULT_TEMPLATE["levels"])}
    gy = {"unit": "Gy", "reference": 5.0, "levels": ((10.0, "#ff0000", True), (3.5, "#00ff00", False))}
    write_template(isodose._template_path("Brachy Gy"), gy)
    assert read_template(isodose._template_path("Brachy Gy")) == gy
    assert isodose.list_templates() == ["Brachy Gy", "Default"]
    # levels shown, in Gy, highest first: % of the reference or Gy as they are
    (d1, c1), (d2, c2) = level_doses(default)[:2]
    assert (d1, d2) == pytest.approx((14.0, 10.5)) and (c1, c2) == ("#ff00ff", "#ff8000")
    assert level_doses(gy) == [(10.0, "#ff0000")]
    assert isodose.name_problem("Default") and isodose.name_problem("a/b") and isodose.name_problem("New") is None


def _app(cur_ax, cur_co, cur_sa):
    """Main window stand-in: layer 0 shown, the slices shown in the three views."""
    return SimpleNamespace(display_data={0: np.zeros((NS0, NR0, NC0), np.float32)},
                           Im_PatPosition=np.array([IPP0]), pixel_spac=np.array([[PS_ROW0, PS_COL0]]),
                           slice_thick=np.array([ST0]), Im_Offset=np.zeros((1, 3)),
                           layer_selected=SimpleNamespace(currentIndex=lambda: 0),
                           current_axial_slice_index=[cur_ax], current_coronal_slice_index=[cur_co],
                           current_sagittal_slice_index=[cur_sa])


def _dose(ipp, spacing, shape):
    """A radial dose 10 exp(-r^2 / (2 * 8^2)) Gy around CENTRE, stored as AMIGOpy stores volumes."""
    (x0, y0, z0), (psc, psr, st), (ns, nr, nc) = ipp, spacing, shape
    s, r, c = np.indices(shape)
    pts = np.stack((x0 + c * psc, y0 + (nr - 1 - r) * psr, z0 + s * st), -1)
    vol = 10.0 * np.exp(-np.sum((pts - CENTRE) ** 2, axis=-1) / (2 * 8.0 ** 2))
    return {"3DMatrix": vol.astype(np.float32),
            "metadata": {"ImagePositionPatient": list(ipp), "PixelSpacing": [psr, psc], "SliceThickness": st}}


def test_isodose_lines_on_each_view_at_the_patient_position():
    # same row spacing as the CT: the lines sit at the true DICOM radius of the level
    dose = _dose((-40.0, -30.0, -20.0), (1.0, 1.0, 2.0), (22, 60, 60))
    radius = 8.0 * np.sqrt(2 * np.log(10.0 / 5.0))          # the 5 Gy line around CENTRE
    k_ax = int(round((CENTRE[2] - IPP0[2]) / ST0))
    k_co = int(round((NR0 - 1) - (CENTRE[1] - IPP0[1]) / PS_ROW0))     # row as stored of the centre's y
    k_sa = int(round((CENTRE[0] - IPP0[0]) / PS_COL0))
    app = _app(k_ax, k_co, k_sa)
    top = IPP0[1] + (NR0 - 1) * PS_ROW0                     # DICOM y at world y 0 (rows stored flipped)
    to_dicom = {"ax": lambda p: np.column_stack((IPP0[0] + p[:, 0], top - p[:, 1])),
                "co": lambda p: np.column_stack((IPP0[0] + p[:, 0], IPP0[2] + p[:, 1])),
                "sa": lambda p: np.column_stack((top - p[:, 0], IPP0[2] + p[:, 1]))}
    centre_2d = {"ax": CENTRE[[0, 1]], "co": CENTRE[[0, 2]], "sa": CENTRE[[1, 2]]}
    for view in ("ax", "co", "sa"):
        (lines,) = view_isodose_lines(app, view, dose, [5.0])
        pts = to_dicom[view](np.vstack(lines))
        r = np.linalg.norm(pts - centre_2d[view], axis=1)
        assert len(lines) == 1 and np.abs(r - radius).max() < 0.15, (view, r.min(), r.max(), radius)


def test_isodose_lines_lie_on_the_dose_layer():
    # another row spacing: drawn where the dose image is as a layer (Im_Offset of Data_tree_general)
    ipp, spacing, shape = (-41.0, -32.5, -21.0), (2.5, 2.5, 3.0), (15, 25, 25)
    dose = _dose(ipp, spacing, shape)
    geom0 = (IPP0, (PS_COL0, PS_ROW0, ST0), (NS0, NR0, NC0))
    off = layer_offset(geom0, (ipp, spacing, shape))
    assert off == pytest.approx((ipp[0] - IPP0[0], (NR0 * PS_ROW0 - shape[1] * spacing[1]) - (ipp[1] - IPP0[1]),
                                 ipp[2] - IPP0[2]))
    k = 7                                                     # dose slice 7 shown on the axial view
    app = _app(int(round((off[2] + k * spacing[2]) / ST0)), 0, 0)
    (lines,) = view_isodose_lines(app, "ax", dose, [5.0])
    pts = np.vstack(lines)
    # back to the dose's own (column, row) of the layer image: the dose there is the level
    c, r = (pts[:, 0] - off[0]) / spacing[0], (pts[:, 1] - off[1]) / spacing[1]
    from scipy.ndimage import map_coordinates
    values = map_coordinates(dose["3DMatrix"][k].astype(float), [r, c], order=1)
    assert np.abs(values - 5.0).max() < 1e-6


def test_dashes_and_dots_along_a_line():
    line = np.array([[0.0, 0.0], [10.0, 0.0]])
    pieces = pattern_pieces(line, ((2.0, 1.0),))
    assert [tuple(p[[0, -1], 0]) for p in pieces] == [(0, 2), (3, 5), (6, 8), (9, 10)]
    dash_dot = pattern_pieces(line, ((4.0, 1.0), (1.0, 1.0)))
    assert [tuple(p[[0, -1], 0]) for p in dash_dot] == [(0, 4), (5, 6), (7, 10)]
    assert dots_along(line, 2.5)[:, 0].tolist() == [0.0, 2.5, 5.0, 7.5]
    # a corner inside a dash keeps the corner point
    corner = pattern_pieces(np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 3.0]]), ((2.0, 5.0),))
    assert corner[0].tolist() == [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]]
    lines, dots = styled([line], "Dotted", 2.0, 0.5)             # dots every 3 px x width
    assert lines == [] and dots[:, 0].tolist() == [0.0, 3.0, 6.0, 9.0]
    assert styled([line], "Solid", 2.0, 0.5)[0][0] is line


def test_vtk_actors_of_lines_and_dots():
    from vtkmodules.util.numpy_support import vtk_to_numpy
    pieces = [np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]]), np.array([[5.0, 5.0], [6.0, 6.0]])]
    actor = isodose._lines_actor(pieces, "#ff0000", 2.5)
    poly = actor.GetMapper().GetInput()
    pts = vtk_to_numpy(poly.GetPoints().GetData())
    assert pts.shape == (5, 3) and np.allclose(pts[:, 2], isodose.Z_LINES) and np.allclose(pts[:3, :2], pieces[0])
    assert poly.GetNumberOfLines() == 2 and actor.GetProperty().GetColor() == (1.0, 0.0, 0.0)
    assert actor.GetProperty().GetLineWidth() == 2.5
    dots = isodose._dots_actor(np.array([[1.0, 2.0], [3.0, 4.0]]), "#00ff00", 2.0)
    assert dots.GetMapper().GetInput().GetNumberOfVerts() == 2 and dots.GetProperty().GetRenderPointsAsSpheres()
    assert isodose._lines_actor([], "#ff0000", 1.0) is None and isodose._dots_actor(np.empty((0, 2)), "#ff0000", 1.0) is None
