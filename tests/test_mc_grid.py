"""
MonteCarlo tab grids (fcn_processing.mc_grid): the box drawn on the views is the MCNP mesh (mm mode holds
the MCNP axes, Z = -DICOM y running with the rows as stored), the calculation grid taken from a dose gets
the dose's voxels, and dragging a box edge, corner or inside changes its values.
"""
import re
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from fcn_mcnp.mcnp_input import build_mcnp_cards
from fcn_processing import mc_grid
from fcn_processing.mc_grid import (_fields, _view_rect, dose_series, dragged_values, get_grid_bounds, grid_handle,
                                    mc_grid_from_dose, on_grid_mode_changed, on_mc_grid_move, on_mc_grid_press,
                                    on_mc_grid_release)

IPP = (-10.0, 20.0, 30.0)            # CT: centre of the voxel with the lowest x, y, z (mm)
PS_COL, PS_ROW, ST = 0.8, 0.9, 2.0
NS, NR, NC = 4, 5, 6


class _Text:
    def __init__(self, t):
        self._t = t

    def currentText(self):
        return self._t


@pytest.fixture
def app(qapp):
    """Main window stand-in: a CT shown in layer 0 with its lattice map, a TPS dose, the grid boxes."""
    from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QSpinBox
    uni = (1000 + np.arange(NS * NR * NC)).reshape(NS, NR, NC).astype(np.int32)
    universes = [{'universe': int(u), 'material_index': 2, 'material_key': 2, 'material': 'Water', 'density': 1.0}
                 for u in uni.ravel()]
    ct = {'3DMatrix': np.zeros((NS, NR, NC), np.float32), 'SeriesNumber': 7,
          'metadata': {'ImagePositionPatient': list(IPP), 'PixelSpacing': [PS_ROW, PS_COL], 'SliceThickness': ST},
          'mcnp_lattice_maps': {'lat': {'3DMatrix': uni, 'universes': universes}}}
    dose = {'3DMatrix': np.zeros((3, 4, 7), np.float32), 'SeriesNumber': 9,
            'metadata': {'SeriesDescription': 'TPS dose', 'ImagePositionPatient': [-11.0, 19.5, 29.0],
                         'PixelSpacing': [1.25, 1.5], 'SliceThickness': 2.5}}
    w = SimpleNamespace(medical_image={'P': {'S': {'CT': [ct], 'RTDOSE': [dose]}}}, patientID='P', studyID='S',
                        modality='CT', series_index=0, Mat_df=pd.DataFrame(),
                        mcnp_source_combo=_Text("None (External beam / custom)"),
                        display_data=[ct['3DMatrix']], Im_PatPosition=np.array([IPP]),
                        pixel_spac=np.array([[PS_ROW, PS_COL]]), slice_thick=np.array([ST]), Im_Offset=np.zeros((1, 3)))
    for prefix, values in (("mc_grid", (1, 4, 1, 2, 1, 3)), ("mc_vox", (0, NC - 1, 0, NS - 1, 0, NR - 1))):
        for name, v in zip(_fields(prefix), values):
            sb = QDoubleSpinBox() if prefix == "mc_grid" else QSpinBox()
            if prefix == "mc_grid":
                sb.setDecimals(0)
                sb.setRange(-99999.0, 99999.0)
            else:
                sb.setRange(0, {"x": NC, "y": NS, "z": NR}[name[len(prefix) + 1]] - 1)
            sb.setValue(v)
            setattr(w, name, sb)
        for a, r in zip("xyz", (PS_COL, ST, PS_ROW)):
            sb = QDoubleSpinBox()
            sb.setDecimals(8)
            sb.setRange(1e-8, 1000.0)
            sb.setValue(r)
            setattr(w, f"{prefix}_{a}res", sb)
    w.mc_grid_mode_combo = QComboBox()
    w.mc_grid_mode_combo.addItems(["voxel", "mm"])
    return w, ct, dose


def _fmesh(lines):
    """ORIGIN, upper corner (IMESH, JMESH, KMESH) and bins (IINTS, JINTS, KINTS) of the first FMESH tally (cm)."""
    k = next(i for i, line in enumerate(lines) if "FMESH" in line and "ORIGIN" in line)
    text = " ".join(lines[k:k + 4]).replace("&", " ")
    origin = [float(v) for v in re.search(r"ORIGIN=\s*(\S+)\s+(\S+)\s+(\S+)", text).groups()]
    get = lambda key: re.search(key + r"=\s*(\S+)", text).group(1)
    return (origin, [float(get(k)) for k in ("IMESH", "JMESH", "KMESH")], [int(get(k)) for k in ("IINTS", "JINTS", "KINTS")])


def _set_mm(w, values):
    w.mc_grid_mode_combo.setCurrentText("mm")
    on_grid_mode_changed(w, "mm")
    for name, v in zip(_fields("mc_grid"), values):
        getattr(w, name).setValue(v)


def test_mm_box_on_the_views_is_the_mcnp_mesh(app):
    # mm mode: X = DICOM x, Y = DICOM z, Z = -DICOM y of the first / last voxel centres (MCNP axes); DICOM
    # rows 1..0 (y 20.9, 20.0) are the rows 3..4 as stored (shown bottom to top), not rows 0..1
    w, ct, _ = app
    _set_mm(w, (-9.2, -6.8, 32.0, 34.0, -20.9, -20.0))
    assert get_grid_bounds(w, "mc_grid")[2:4] == pytest.approx((3.0, 4.0))
    origin, far, ints = _fmesh(build_mcnp_cards(w, ct, 'lat')[0])
    # the same numbers as MCNP: the mesh is the typed voxel centres plus half a CT voxel
    assert (10 * origin[2], 10 * far[2]) == pytest.approx((-20.9 - PS_ROW / 2, -20.0 + PS_ROW / 2))
    (x0, x1, y0, y1), _ = _view_rect(w, "mc_grid", "ax")
    top = IPP[1] + (NR - 1) * PS_ROW        # DICOM y of the row stored first (world y 0)
    # axial view: world x = DICOM x - IPP x, world y = top - DICOM y; MCNP X = x, Z = -y (cm)
    assert (IPP[0] + x0, IPP[0] + x1) == pytest.approx((10 * origin[0], 10 * far[0]))
    assert (top - y1, top - y0) == pytest.approx((-10 * far[2], -10 * origin[2]))
    (_, _, s0, s1), _ = _view_rect(w, "mc_grid", "co")
    assert (IPP[2] + s0, IPP[2] + s1) == pytest.approx((10 * origin[1], 10 * far[1]))

    # the switch to voxels and back keeps the box
    on_grid_mode_changed(w, "voxel")
    assert [getattr(w, f).value() for f in _fields("mc_grid")[4:]] == [3, 4]
    on_grid_mode_changed(w, "mm")
    assert [getattr(w, f).value() for f in _fields("mc_grid")[4:]] == pytest.approx([-20.9, -20.0])


def test_origin_shown_is_the_first_voxel_centre_in_mcnp_axes(app):
    # calculation grid columns 1..4, slices 1..2, rows as stored 1..3 (DICOM rows 3..1): the "Origin (abs)"
    # of the info label in X, Y, Z as the boxes, in both modes, half a CT voxel inside the MCNP mesh
    w, ct, _ = app
    voxel = mc_grid.get_grid_origin_abs(w, "mc_grid")
    assert voxel == pytest.approx((IPP[0] + PS_COL, IPP[2] + ST, -(IPP[1] + (NR - 2) * PS_ROW)))
    w.mc_grid_mode_combo.setCurrentText("mm")
    on_grid_mode_changed(w, "mm")
    assert mc_grid.get_grid_origin_abs(w, "mc_grid") == pytest.approx(voxel)
    origin, _, _ = _fmesh(build_mcnp_cards(w, ct, 'lat')[0])
    assert [10 * o for o in origin] == pytest.approx(np.array(voxel) - np.array([PS_COL, ST, PS_ROW]) / 2, abs=1e-4)


def test_calculation_grid_from_a_dose_has_its_voxels(app):
    w, ct, dose = app
    (label, series), = dose_series(w)
    assert series is dose and label == "RTDOSE: TPS dose  (7 x 3 x 4 voxels of 1.5 x 2.5 x 1.25 mm)"
    assert mc_grid_from_dose(w, dose) and w.mc_grid_mode_combo.currentText() == "mm"
    # boxes: dose voxel centres -+ half a dose voxel +- half a CT voxel, Z = -DICOM y
    assert [w.mc_grid_zmin.value(), w.mc_grid_zmax.value()] == pytest.approx([-23.875 + PS_ROW / 2, -18.875 - PS_ROW / 2])
    origin, far, ints = _fmesh(build_mcnp_cards(w, ct, 'lat')[0])
    # dose voxel edges (mm): x -11.75 .. -1.25, y 18.875 .. 23.875, z 27.75 .. 35.25; MCNP X = x, Y = z, Z = -y
    assert origin == pytest.approx([-1.175, 2.775, -2.3875], abs=1e-6)
    assert far == pytest.approx([-0.125, 3.525, -1.8875], abs=1e-6)
    assert ints == [7, 3, 4]


def test_grab_handles_of_a_box():
    rect, tol = (0.0, 10.0, 0.0, 5.0), 0.5
    assert grid_handle(rect, (10.2, 2.0), tol) == {"x1"}
    assert grid_handle(rect, (-0.3, 4.8), tol) == {"x0", "y1"}
    assert grid_handle(rect, (5.0, 2.5), tol) == {"move"}
    assert grid_handle(rect, (11.0, 2.0), tol) is None
    assert grid_handle((0.0, 0.6, 0.0, 5.0), (0.5, 2.5), tol) == {"x1"}      # thin box: the nearer edge


def test_dragged_values_per_view_and_mode():
    values = [1, 4, 1, 2, 1, 3]                               # X, Y, Z min / max
    voxel_steps = {"x": 0.8, "y": 2.0, "z": 0.9}
    assert dragged_values(values, "ax", {"x1"}, (1.6, 0.0), voxel_steps) == [1, 6, 1, 2, 1, 3]
    assert dragged_values(values, "sa", {"move"}, (0.9, 2.0), voxel_steps) == [1, 4, 2, 3, 2, 4]
    # mm mode: Z = -DICOM y grows up the axial view like the rows, its low y edge is Z min
    mm = [-9.0, -7.0, 32.0, 34.0, -21.0, -20.0]
    out = dragged_values(mm, "ax", {"y0"}, (0.0, 0.5), {"x": 1, "y": 1, "z": 1})
    assert out == pytest.approx([-9.0, -7.0, 32.0, 34.0, -20.5, -20.0])


def test_drag_on_the_views(app, monkeypatch):
    # world mm = pixels / 10 on every view; the calculation grid (columns 1..4, rows 1..3) is shown
    w, _, _ = app
    monkeypatch.setattr(mc_grid, "_mc_tab_active", lambda self: True)
    monkeypatch.setattr(mc_grid, "_is_enabled", lambda self, prefix: prefix == "mc_grid")
    monkeypatch.setattr(mc_grid, "_renderer", lambda widget: None)
    monkeypatch.setattr(mc_grid, "_widget", lambda self, view: None)
    monkeypatch.setattr(mc_grid, "_event_world_xy", lambda renderer, x, y: np.array([x, y]) / 10.0)

    class _Mouse:
        def __init__(self, x, y):
            self.pos = (x, y)

        def GetEventPosition(self):
            return self.pos

    def drag(view, start, end):
        on_mc_grid_press(w, view, _Mouse(*start))
        on_mc_grid_move(w, view, _Mouse(*end))
        on_mc_grid_release(w, view, _Mouse(*end))
        return [getattr(w, f).value() for f in _fields("mc_grid")]

    # axial: the right edge (world x 3.6) two voxels to the right; the window/level flag is reset after
    assert drag("ax", (36, 18), (52, 18)) == [1, 6, 1, 2, 1, 3] and w._text_dragging is False
    # the inside moves the box: one column right, one row up
    assert drag("ax", (20, 18), (28, 27)) == [2, 7, 1, 2, 2, 4]
    # a corner (bottom left: columns min, rows min) on the axial view
    assert drag("ax", (12, 13), (4, 4)) == [1, 7, 1, 2, 1, 4]
    # an edge never crosses the other one
    assert drag("ax", (60, 18), (-100, 18)) == [1, 1, 1, 2, 1, 4]
    # outside every box nothing is dragged (window/level)
    before = [getattr(w, f).value() for f in _fields("mc_grid")]
    assert drag("ax", (300, 300), (400, 400)) == before and w._mc_grid_drag is None
    # mm mode, rows 3..4 (world y 2.25 .. 4.05): the lower edge a row down lowers Z min a row, as in voxels
    _set_mm(w, (-9.2, -6.8, 32.0, 34.0, -20.9, -20.0))
    assert drag("ax", (20, 23), (20, 14))[4:] == pytest.approx([-20.9 - PS_ROW, -20.0])
    assert get_grid_bounds(w, "mc_grid")[2:4] == pytest.approx((2.0, 4.0))
