"""
TR cards of the dwell positions (fcn_mcnp/mcnp_transform.py): the 9 rotation values as the MCNP manual
defines them, the source axis towards the cable (away from the catheter tip) whichever way the plan
stores it, and the check of written cards back against the plan.
"""
import numpy as np
import pytest

from fcn_mcnp import mcnp_transform as mt
from fcn_mcnp.mcnp_input import build_source_cards, to_mcnp_axes


def _random_axes(n=50, seed=3):
    v = np.random.default_rng(seed).normal(size=(n, 3))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def test_smallest_rotation_is_a_proper_rotation_onto_the_axis():
    for axis in _random_axes():
        rot = mt.smallest_rotation(axis)
        assert rot.T @ rot == pytest.approx(np.eye(3), abs=1e-12) and np.linalg.det(rot) == pytest.approx(1.0)
        assert rot[:, 0] == pytest.approx(axis)                         # x' = the source axis
        # the smallest rotation: its angle is the angle between X and the axis
        angle = np.degrees(np.arccos(np.clip((np.trace(rot) - 1) / 2, -1, 1)))
        assert angle == pytest.approx(np.degrees(np.arccos(axis[0])), abs=1e-6)
    assert np.array_equal(mt.smallest_rotation([1, 0, 0]), np.eye(3))
    assert np.array_equal(mt.smallest_rotation([-1, 0, 0]), np.diag([-1.0, -1.0, 1.0]))
    assert np.array_equal(mt.smallest_rotation([0, 0, 0]), np.eye(3))


def test_card_values_as_the_manual_defines_them():
    rot = mt.smallest_rotation([0.6, 0.0, 0.8])
    lines = mt.tr_card_lines(7, (1.0, -2.0, 3.5), rot)
    assert lines[0] == "tr7 1.00000 -2.00000 3.50000 &" and len(lines) == 4
    assert all(line.endswith(" &") for line in lines[:3]) and not lines[3].endswith("&")    # one card
    values = mt.parse_tr_cards(lines)[7]
    assert values[:3] == [1.0, -2.0, 3.5]
    b = np.array(values[3:]).reshape(3, 3)
    # xx' yx' zx' = cosines of x' with x, y, z: row k of the 9 values is axis k' in the main axes
    x, y, z = np.eye(3)
    assert b[0] == pytest.approx([np.dot(x, rot[:, 0]), np.dot(y, rot[:, 0]), np.dot(z, rot[:, 0])], abs=1e-7)
    # a recorded particle at r' (source frame) starts at O + R r'
    r_source = np.array([0.2, -0.1, 0.05])
    assert np.array(values[:3]) + b.T @ r_source == pytest.approx(np.array([1.0, -2.0, 3.5]) + rot @ r_source, abs=1e-6)


def test_axes_mapping_matches_the_input():
    for v in _random_axes(5):
        assert mt.mcnp_vector(v) == pytest.approx(to_mcnp_axes(*v))
        assert mt.dicom_vector(mt.mcnp_vector(v)) == pytest.approx(v)


def _catheter(n=4, plan_sign=None):
    """A straight catheter from its tip at the origin towards +x (mm), dwells every 5 mm."""
    xyz = np.array([[5.0 * (k + 1), 0.0, 0.0] for k in range(n)])
    plan = np.full((n, 3), np.nan) if plan_sign is None else np.tile([plan_sign, 0.0, 0.0], (n, 1))
    return xyz, plan, np.array([[0.0, 0.0, 0.0], [40.0, 0.0, 0.0]])


def test_source_axis_faces_the_cable_whatever_the_plan_stores():
    varian, kept, path_only = mt.cable_directions([_catheter(plan_sign=-1.0), _catheter(plan_sign=1.0), _catheter()])
    for dirs, bases, checked, tangents in (varian, kept, path_only):
        assert dirs == pytest.approx(np.tile([1.0, 0.0, 0.0], (4, 1)))            # away from the tip
        assert tangents == pytest.approx(np.tile([1.0, 0.0, 0.0], (4, 1)))
    assert set(varian[1]) == {mt.PLAN_REVERSED} and varian[2]
    assert set(kept[1]) == {mt.PLAN} and set(path_only[1]) == {mt.PATH}


def test_without_a_path_the_sign_of_the_other_catheters_or_the_tip_convention():
    xyz, plan, _ = _catheter(plan_sign=-1.0)
    with_path, without = mt.cable_directions([_catheter(plan_sign=-1.0), (xyz, plan, None)])
    assert without[0] == pytest.approx(with_path[0]) and not without[2] and set(without[1]) == {mt.PLAN_REVERSED}
    (alone,) = mt.cable_directions([(xyz, plan, None)])           # no path anywhere: towards the tip assumed
    assert alone[0] == pytest.approx(np.tile([1.0, 0.0, 0.0], (4, 1))) and not alone[2]


def test_neighbouring_dwells_away_from_the_tip_and_nothing():
    xyz = np.array([[30.0, 0, 0], [20.0, 0, 0], [10.0, 0, 0]])      # listed from the far end
    far_from_path = np.array([[0.0, 50.0, 0.0], [10.0, 50.0, 0.0]])  # the tip known, the dwells off the path
    (dwells,) = mt.cable_directions([(xyz, None, far_from_path)])
    assert set(dwells[1]) == {mt.DWELLS} and dwells[0][:, 0] == pytest.approx([1.0, 1.0, 1.0])
    (single,) = mt.cable_directions([(xyz[:1], None, None)])
    assert list(single[1]) == [mt.NONE] and single[0] == pytest.approx(np.zeros((1, 3)))


def _dwells(catheter_dirs):
    """Dwell dicts (as mcnp_input.extract_plan_dwells) of _catheter() with these x' directions."""
    xyz, plan, pts = _catheter(plan_sign=-1.0)
    tangents = mt.path_tangents(xyz, pts)
    return [{"x_mm": p[0], "y_mm": p[1], "z_mm": p[2], "x_cm": p[0] / 10, "y_cm": p[1] / 10, "z_cm": p[2] / 10,
             "time_s": 1.0, "dir_x": d[0], "dir_y": d[1], "dir_z": d[2], "dir_basis": mt.PLAN_REVERSED,
             "sign_checked": True, "plan_dir": tuple(o), "path_dir": tuple(t)}
            for p, d, o, t in zip(xyz, catheter_dirs, plan, tangents)]


def _cards_of(dwells):
    lines = []
    for n, d in enumerate(dwells, start=1):
        origin = to_mcnp_axes(d["x_cm"], d["y_cm"], d["z_cm"])
        lines += mt.tr_card_lines(n, origin, mt.smallest_rotation(to_mcnp_axes(d["dir_x"], d["dir_y"], d["dir_z"])))
    return lines


def test_check_of_written_cards_against_the_plan():
    dwells = _dwells(np.tile([1.0, 0.0, 0.0], (4, 1)))
    result, report = mt.check_tr_cards(_cards_of(dwells), dwells)
    assert result["max_position_mm"] < 1e-6 and result["facing_connector"] == result["on_path"] == 4
    assert result["plan_reversed"] == 4 and result["max_orthogonality"] < 1e-6
    assert result["det_min"] == pytest.approx(1.0, abs=1e-6) and not result["missing"]
    assert all(len("c " + line) <= 80 for line in report)
    # a card turned the wrong way and one moved: both found
    lines = _cards_of(_dwells(np.array([[1.0, 0, 0], [-1.0, 0, 0], [1.0, 0, 0], [1.0, 0, 0]])))
    assert lines[8].startswith("tr3 1.50000 ")                       # dwell 3 at 15 mm
    lines[8] = lines[8].replace("tr3 1.50000", "tr3 1.60000")
    result, _ = mt.check_tr_cards(lines, dwells)
    assert result["facing_connector"] == 3 and result["max_position_mm"] == pytest.approx(1.0, abs=1e-6)


def test_old_three_value_cards_can_be_checked_too():
    dwells = _dwells(np.tile([1.0, 0.0, 0.0], (4, 1)))
    old = [f"tr{n} {d['x_cm']:.5f} {d['z_cm']:.5f} {0.0 - d['y_cm']:.5f} -1.00000 0.00000 0.00000"
           for n, d in enumerate(dwells, start=1)]                    # MATLAB-style: x' as the plan stored it
    result, _ = mt.check_tr_cards(old, dwells)
    assert result["facing_connector"] == 0 and result["max_orthogonality"] == 0.0


def test_at_most_999_tr_cards():
    dwells = _dwells(np.tile([1.0, 0.0, 0.0], (4, 1)))
    with pytest.raises(ValueError, match="999"):
        build_source_cards({"source_model": "TG186"}, dwells * 250, 1000.0)
