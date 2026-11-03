"""
The tip of a catheter (its first point) on the images: an arrowhead pointing to it in the 2D views
(a ring where the catheter is seen end-on) and a cone pointing to it in the 3D view.
"""
import numpy as np
import pytest


def _points(polydata):
    return np.array([polydata.GetPoint(i) for i in range(polydata.GetNumberOfPoints())])


def _output(actor):
    mapper = actor.GetMapper()
    mapper.GetInputAlgorithm().Update()
    return mapper.GetInput()


def test_arrowhead_points_to_the_tip_along_the_catheter():
    from fcn_display.display_images import catheter_tip_actor
    # tip at (10, 20); the catheter goes away from it towards +x, with a bend after 30 mm
    x, y = [10.0, 12.0, 40.0, 40.0], [20.0, 20.0, 20.0, 60.0]
    actor = catheter_tip_actor(x, y, 0.55, 9.0, (0, 0, 1), 2)
    poly = _output(actor)
    tip, side_1, side_2 = _points(poly)
    assert poly.GetNumberOfPolys() == 1 and tip == pytest.approx([10.0, 20.0, 0.55])   # vtkPoints: float32
    base = (side_1 + side_2) / 2
    assert base[:2].tolist() == pytest.approx([19.0, 20.0])            # 9 mm back along the catheter
    assert np.linalg.norm(side_1 - side_2) == pytest.approx(2 * 0.35 * 9.0)
    assert actor.GetProperty().GetColor() == (0.0, 0.0, 1.0)


def test_arrowhead_direction_from_the_points_half_an_arrow_away():
    from fcn_display.display_images import catheter_tip_actor
    # points closer than half an arrow to the tip are skipped (a dense tip does not turn the arrow)
    x, y = [0.0, 0.5, 3.0, 3.0], [0.0, 0.5, 0.0, 30.0]
    tip, side_1, side_2 = _points(_output(catheter_tip_actor(x, y, 0.55, 9.0, (1, 1, 1), 1)))
    axis = tip[:2] - (side_1 + side_2)[:2] / 2
    # the first point at least 4.5 mm away is (3, 30): the arrow points from it to the tip
    expected = np.array([0.0, 0.0]) - [3.0, 30.0]
    assert axis / np.linalg.norm(axis) == pytest.approx(expected / np.linalg.norm(expected))


def test_ring_where_the_catheter_is_seen_end_on():
    from fcn_display.display_images import catheter_tip_actor
    poly = _output(catheter_tip_actor([5.0, 5.2, 5.1], [7.0, 7.1, 6.9], 0.55, 9.0, (0, 1, 0), 2))
    ring = _points(poly)
    assert poly.GetNumberOfPolys() == 0 and poly.GetNumberOfLines() >= 1
    assert np.hypot(ring[:, 0] - 5.0, ring[:, 1] - 7.0) == pytest.approx(np.full(len(ring), 0.4 * 9.0))


def test_cone_points_to_the_tip_in_3d():
    from fcn_3Dview.brachy_3D_table import catheter_tip_cone
    catheter = np.array([[1.0, 2.0, 3.0], [1.0, 2.0, 13.0], [1.0, 12.0, 13.0]])     # tip first
    points = _points(_output(catheter_tip_cone(catheter, 1.0)))
    apex = points[np.argmin(points[:, 2])]
    assert apex == pytest.approx([1.0, 2.0, 3.0], abs=1e-9)            # the point of the cone at the tip
    assert points[:, 2].max() == pytest.approx(11.0)                    # 8 mm back along the catheter
    assert catheter_tip_cone(catheter[:1], 1.0) is None


def test_tip_shown_by_default():
    from types import SimpleNamespace
    from fcn_display.brachy_panel import DISPLAY_OPTIONS, brachy_display
    assert brachy_display(SimpleNamespace())["ch_tip"] is True
    assert ("ch_tip", "brachy_show_ch_tip", "display_brachy_channel_overlay") in DISPLAY_OPTIONS
