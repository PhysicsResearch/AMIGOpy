import numpy as np
import pytest

from fcn_display import brachy_channel_edit as bce


def _dwells(xyz, orient=(1.0, 0.0, 0.0)):
    """DwellInfo-like (M, 9) float32 array: IDX, RelPos, Time, X, Y, Z, Ux, Uy, Uz."""
    xyz = np.asarray(xyz, dtype=float)
    out = np.zeros((len(xyz), 9), dtype=np.float32)
    out[:, 0] = np.arange(1, len(xyz) + 1)
    out[:, 2] = 1.0
    out[:, 3:6] = xyz
    out[:, 6:9] = orient
    return out


def test_project_on_polyline():
    poly = [(0, 0, 0), (10, 0, 0), (10, 10, 0)]
    seg, t, proj, dist = bce.project_on_polyline([(5, 1, 0), (10, 5, 0), (-3, 0, 0)], poly)
    assert seg.tolist() == [0, 1, 0]
    np.testing.assert_allclose(t, [0.5, 0.5, 0.0])
    np.testing.assert_allclose(proj, [(5, 0, 0), (10, 5, 0), (0, 0, 0)])
    np.testing.assert_allclose(dist, [1, 0, 3])


def test_project_on_polyline_zero_length_segment():
    seg, t, _, dist = bce.project_on_polyline([(5, 0, 0)], [(0, 0, 0), (0, 0, 0), (10, 0, 0)])
    assert seg[0] == 1 and t[0] == pytest.approx(0.5) and dist[0] == pytest.approx(0.0)


def test_follow_path_moves_dwells_on_adjacent_segments_only():
    poly0 = np.array([(0, 0, 0), (10, 0, 0), (20, 0, 0), (30, 0, 0)], dtype=float)
    dwell = _dwells([(0, 0, 0), (5, 0, 0), (10, 0, 0), (15, 0, 0), (20, 0, 0), (25, 0, 0), (5, 8, 0)])
    seg, t, attached = bce.attach_dwells(dwell, poly0)
    assert attached.tolist() == [True] * 6 + [False]   # last dwell is 8 mm off the path

    poly1 = poly0.copy()
    poly1[1] = (10, 4, 0)                               # drag vertex 1 up by 4 mm
    out = bce.follow_path(dwell, poly0, poly1, seg, t, attached)

    assert out.dtype == np.float32
    # far vertex 0, the dragged vertex, half-way points, far vertex 2, other segment, off-path dwell
    np.testing.assert_allclose(out[:, 4], [0, 2, 4, 2, 0, 0, 8], atol=1e-6)
    np.testing.assert_allclose(out[:, [3, 5]], dwell[:, [3, 5]])


def test_follow_path_rotates_orientation_with_segment():
    poly0 = np.array([(0, 0, 0), (10, 0, 0)], dtype=float)
    dwell = _dwells([(5, 0, 0), (2, 0, 0)])
    dwell[1, 6:9] = np.nan                              # no orientation in the plan
    seg, t, attached = bce.attach_dwells(dwell, poly0)
    poly1 = np.array([(0, 0, 0), (0, 10, 0)], dtype=float)
    out = bce.follow_path(dwell, poly0, poly1, seg, t, attached)
    np.testing.assert_allclose(out[0, 3:9], [0, 5, 0, 0, 1, 0], atol=1e-6)
    assert np.all(np.isnan(out[1, 6:9]))


def test_follow_path_without_displacement_is_identity():
    poly = np.array([(0, 0, 0), (10, 3, 1), (20, 0, 4)], dtype=float)
    dwell = _dwells([(2, 1, 0), (12, 2, 2), (19, 0, 4)], orient=(0.6, 0.8, 0.0))
    seg, t, attached = bce.attach_dwells(dwell, poly)
    np.testing.assert_allclose(bce.follow_path(dwell, poly, poly.copy(), seg, t, attached), dwell, atol=1e-6)


def test_new_point_for_insert():
    poly = [(0, 0, 0), (10, 0, 0), (10, 10, 0)]
    np.testing.assert_allclose(bce.new_point_for_insert(poly, 0), (5, 0, 0))
    np.testing.assert_allclose(bce.new_point_for_insert(poly, 1), (10, 5, 0))
    np.testing.assert_allclose(bce.new_point_for_insert(poly, 2), (10, 20, 0))     # extends the path
    np.testing.assert_allclose(bce.new_point_for_insert(poly, -1), (10, 20, 0))    # no selection: after last
    np.testing.assert_allclose(bce.new_point_for_insert([(1, 2, 3)], 0), (1, 2, 3))
    np.testing.assert_allclose(bce.new_point_for_insert(np.zeros((0, 3)), -1, (7, 8, 9)), (7, 8, 9))


def test_remap_dwells_after_delete_interior_point():
    poly = np.array([(0, 0, 0), (10, 10, 0), (20, 0, 0)], dtype=float)
    diag = (np.sqrt(0.5), np.sqrt(0.5), 0)
    dwell = _dwells([(0, 0, 0), (5, 5, 0), (10, 10, 0), (15, 5, 0), (20, 0, 0), (5, 5, 1), (5, 20, 0)], orient=diag)
    out = bce.remap_dwells_after_delete(dwell, poly, 1)
    # equal-length segments: arc fractions 0, .25, .5, .75, 1 along the new straight segment
    np.testing.assert_allclose(out[:5, 3:6], [(0, 0, 0), (5, 0, 0), (10, 0, 0), (15, 0, 0), (20, 0, 0)], atol=1e-5)
    np.testing.assert_allclose(out[5, 3:6], (5, 0, 1), atol=1e-5)          # keeps its offset from the path
    np.testing.assert_allclose(out[6], dwell[6])                           # ~11 mm off the path: unchanged
    np.testing.assert_allclose(out[1, 6:9], (1, 0, 0), atol=1e-6)          # orientation follows the segment


@pytest.mark.parametrize("j", [0, 2])
def test_remap_dwells_after_delete_end_point_keeps_dwells(j):
    poly = np.array([(0, 0, 0), (10, 10, 0), (20, 0, 0)], dtype=float)
    dwell = _dwells([(2, 2, 0), (18, 2, 0)])
    np.testing.assert_array_equal(bce.remap_dwells_after_delete(dwell, poly, j), dwell)


def test_rotate_vectors():
    v = np.array([(1, 0, 0), (0, 0, 1), (1, 2, 3)], dtype=float)
    out = bce.rotate_vectors(v, (1, 0, 0), (0, 2, 0))           # 90 degrees about +z
    np.testing.assert_allclose(out, [(0, 1, 0), (0, 0, 1), (-2, 1, 3)], atol=1e-12)
    np.testing.assert_allclose(bce.rotate_vectors(v, (1, 1, 0), (2, 2, 0)), v)    # parallel: unchanged
    np.testing.assert_allclose(bce.rotate_vectors(v, (0, 0, 0), (1, 0, 0)), v)    # degenerate: unchanged


@pytest.mark.parametrize("view, kept", [("axial", 2), ("coronal", 1), ("sagittal", 0)])
def test_view_xy_round_trip(view, kept):
    ipp, height = np.array([-250.0, -200.0, -100.0]), 512 * 0.97
    pt = np.array([10.0, 20.0, 30.0])
    xy = bce.view_xy(view, pt, ipp, height)[0]
    np.testing.assert_allclose(bce.point_from_view_xy(view, xy, pt, ipp, height), pt)
    # only the in-plane coordinates come from the view; the normal one is kept
    other = np.array([99.0, 99.0, 99.0])
    new = bce.point_from_view_xy(view, xy, other, ipp, height)
    assert new[kept] == 99.0
    np.testing.assert_allclose(np.delete(new, kept), np.delete(pt, kept))


def test_view_xy_matches_overlay_formulas():
    ipp, height = np.array([-250.0, -200.0, -100.0]), 400.0
    pt = np.array([[10.0, 20.0, 30.0]])
    np.testing.assert_allclose(bce.view_xy("axial", pt, ipp, height), [[260.0, 400.0 - 220.0]])
    np.testing.assert_allclose(bce.view_xy("coronal", pt, ipp, height), [[260.0, 130.0]])
    np.testing.assert_allclose(bce.view_xy("sagittal", pt, ipp, height), [[400.0 - 220.0, 130.0]])


def test_dwell_directions_order_of_preference():
    poly = np.array([(0, 0, 0), (0, 0, 10), (10, 0, 10)], dtype=float)
    dwell = _dwells([(0, 0, 2), (0, 0, 5), (5, 0, 10), (40, 40, 40)], orient=(0.0, 1.0, 0.0))
    dwell[1:, 6:9] = np.nan                             # only the first dwell has a plan orientation
    dirs = bce.dwell_directions(dwell, poly)
    np.testing.assert_allclose(dirs[0], (0, 1, 0))                # plan orientation
    np.testing.assert_allclose(dirs[1], (0, 0, 1))                # channel segment 0
    np.testing.assert_allclose(dirs[2], (1, 0, 0))                # channel segment 1
    np.testing.assert_allclose(dirs[3], np.array((35, 40, 30)) / np.linalg.norm((35, 40, 30)))  # off path: previous dwell


def test_dwell_directions_without_channel_or_orientation():
    dwell = _dwells([(0, 0, 0), (0, 3, 0), (4, 3, 0)])
    dwell[:, 6:9] = np.nan
    dirs = bce.dwell_directions(dwell, None)
    np.testing.assert_allclose(dirs, [(0, 1, 0), (0.8, 0.6, 0), (1, 0, 0)])
    single = _dwells([(1, 2, 3)])
    single[:, 6:9] = np.nan
    assert np.all(np.isnan(bce.dwell_directions(single, None)))


@pytest.mark.parametrize("view", ["axial", "coronal", "sagittal"])
def test_view_dir_matches_view_xy_and_is_right_handed(view):
    ipp, height = np.array([-250.0, -200.0, -100.0]), 400.0
    p, d = np.array([10.0, 20.0, 30.0]), np.array([0.3, -0.5, 0.8])
    moved = bce.view_xy(view, p + d, ipp, height)[0] - bce.view_xy(view, p, ipp, height)[0]
    np.testing.assert_allclose(bce.view_dir(view, d)[0, :2], moved)
    assert np.linalg.det(bce.view_dir(view, np.eye(3))) == pytest.approx(1.0)


def test_dwell_glyph_size():
    assert bce.dwell_glyph_size([(0, 0, 0), (0, 0, 5)], 3) == pytest.approx((3.6, 0.9))      # 1.2 x point size
    assert bce.dwell_glyph_size([(0, 0, 0), (0, 0, 2.5), (0, 0, 2.5)], 3) == pytest.approx((2.25, 0.5625))  # 90 % of the step
    assert bce.dwell_glyph_size([(1, 2, 3)], 2) == pytest.approx((2.4, 0.6))


def test_dwell_outline():
    dirs = [(1, 0, 0), (0, 0, 1), (np.nan,) * 3, (np.sqrt(0.5), 0, np.sqrt(0.5))]
    out = bce.dwell_outline([(10.0, 20.0)] * 4, dirs, 4.0, 1.0)
    assert out.shape == (4, 18, 2)
    lo, hi = out.min(axis=1), out.max(axis=1)
    np.testing.assert_allclose([lo[0], hi[0]], [(8, 19), (12, 21)], atol=1e-12)      # in the plane: 4 x 2 rectangle
    for i in (1, 2):                                                                   # end-on / unknown: circle
        np.testing.assert_allclose(np.linalg.norm(out[i] - (10, 20), axis=1), 1.0)
    half = 2 * np.sqrt(0.5) + np.sqrt(0.5)          # projected half axis + projected cap (ellipse)
    np.testing.assert_allclose([lo[3], hi[3]], [(10 - half, 19), (10 + half, 21)], atol=1e-12)


def test_dwell_glyph_actors_fill_and_edge():
    from vtkmodules.util.numpy_support import vtk_to_numpy
    from fcn_display.display_images import _dwell_glyph_actors
    from fcn_display.brachy_panel import BRACHY_STYLE_DEFAULTS
    style = dict(BRACHY_STYLE_DEFAULTS)
    args = (np.array([(10.0, 20.0), (30.0, 20.0)]), np.array([(1.0, 0, 0), (0, 0, 1.0)]),
            np.array([(4.0, 1.0), (4.0, 1.0)]), np.array([(1.0, 0, 0), (0, 0.5, 0)]), 2.0)
    fill, edge = _dwell_glyph_actors(*args, style)
    assert fill.GetProperty().GetOpacity() == pytest.approx(0.15) and edge.GetProperty().GetOpacity() == 1.0
    assert fill.GetMapper().GetInput().GetNumberOfPolys() == 2 and edge.GetMapper().GetInput().GetNumberOfLines() == 2
    np.testing.assert_allclose(edge.GetBounds()[:4], (8, 31, 19, 21), atol=1e-12)
    assert 2.0 < fill.GetBounds()[4] < edge.GetBounds()[4]      # above the catheter points, edge on top
    np.testing.assert_array_equal(vtk_to_numpy(edge.GetMapper().GetInput().GetCellData().GetScalars()),
                                  [(255, 0, 0), (0, 128, 0)])
    style['dw_fill'] = 0
    assert len(_dwell_glyph_actors(*args, style)) == 1             # outline only


def _point_at(poly, s):
    k, t = bce.locate_arclength(poly, s)
    poly = np.asarray(poly, dtype=float)
    return poly[k] + np.asarray(t)[..., None] * (poly[k + 1] - poly[k])


def test_locate_arclength():
    poly = [(0, 0, 0), (10, 0, 0), (10, 0, 0), (10, 5, 0)]          # zero-length middle segment
    k, t = bce.locate_arclength(poly, [0.0, 4.0, 10.0, 12.5, 20.0])
    assert k.tolist() == [0, 0, 0, 2, 2]                              # on a vertex: end of the segment before it
    np.testing.assert_allclose(t, [0.0, 0.4, 1.0, 0.5, 2.0])          # past the end: along the last segment


def test_keep_idd_keeps_the_distance_along_the_catheter():
    poly0 = np.array([(0, 0, 0), (10, 0, 0), (10, 10, 0)], dtype=float)
    dwell = _dwells([(4, 0, 0), (8, 0, 0), (10, 2, 0), (10, 6, 0), (20, 20, 0)])
    poly1 = np.array([(0, 0, 0), (6, 0, 0), (10, 10, 0)], dtype=float)    # vertex 1 dragged: segment 0 shorter
    out = bce.keep_idd(dwell, poly0, poly1)
    assert out.dtype == np.float32
    np.testing.assert_allclose(out[:4, 3:6], _point_at(poly1, [4.0, 8.0, 12.0, 16.0]), atol=1e-5)
    np.testing.assert_allclose(out[4], dwell[4])                            # off the path: unchanged
    seg1 = np.array([4.0, 10.0, 0.0]) / np.sqrt(116)
    np.testing.assert_allclose(out[1, 6:9], seg1, atol=1e-6)               # moved onto segment 1: turned with it
    np.testing.assert_allclose(out[0, 6:9], (1, 0, 0), atol=1e-6)

    short = np.array([(0, 0, 0), (6, 0, 0), (6, 5, 0)], dtype=float)       # path shorter than the dwells
    np.testing.assert_allclose(bce.keep_idd(dwell, poly0, short)[2:4, 3:6], [(6, 6, 0), (6, 10, 0)], atol=1e-5)


def test_keep_idd_after_deleting_a_point():
    poly0 = np.array([(0, 0, 0), (10, 0, 0), (10, 10, 0), (20, 10, 0)], dtype=float)
    dwell = _dwells([(5, 0, 0), (10, 5, 0), (15, 10, 0)])
    poly1 = np.delete(poly0, 2, axis=0)
    out = bce.keep_idd(dwell, poly0, poly1)
    np.testing.assert_allclose(out[:, 3:6], _point_at(poly1, [5.0, 15.0, 25.0]), atol=1e-5)
    np.testing.assert_allclose(out[0], dwell[0])                            # before the change: unchanged


@pytest.mark.parametrize("view, normal", [("axial", 2), ("coronal", 1), ("sagittal", 0)])
def test_view_translation_and_rotation(view, normal):
    ipp, height = np.array([-250.0, -200.0, -100.0]), 400.0
    p = np.array([[10.0, 20.0, 30.0], [-5.0, 7.0, 12.0]])
    shift = bce.view_translation(view, (3.0, -4.0))
    assert shift[normal] == 0
    np.testing.assert_allclose(bce.view_xy(view, p + shift, ipp, height) - bce.view_xy(view, p, ipp, height),
                               [(3, -4), (3, -4)])
    rot = bce.view_rotation(view, np.pi / 2)
    np.testing.assert_allclose(rot @ rot.T, np.eye(3), atol=1e-12)
    pivot = np.array([1.0, 2.0, 3.0])
    q = pivot + (p - pivot) @ rot.T
    np.testing.assert_allclose(q[:, normal], p[:, normal])                  # stays in its slice
    v0 = bce.view_xy(view, p, ipp, height) - bce.view_xy(view, pivot, ipp, height)
    v1 = bce.view_xy(view, q, ipp, height) - bce.view_xy(view, pivot, ipp, height)
    np.testing.assert_allclose(v1, np.column_stack((-v0[:, 1], v0[:, 0])), atol=1e-9)   # quarter turn in the view


def test_distance_to_path_2d():
    assert bce.distance_to_path_2d(np.array([5.0, 3.0]), [(0, 0), (10, 0)]) == pytest.approx(3.0)
    assert bce.distance_to_path_2d(np.array([3.0, 4.0]), [(0, 0)]) == pytest.approx(5.0)


def test_snapshot_and_restore_channels():
    a = {'ChannelNumber': 1, 'ChPos': np.zeros((2, 3), np.float32), 'DwellInfo': _dwells([(0, 0, 0)])}
    b = {'ChannelNumber': 2, 'ChPos': np.ones((2, 3), np.float32), 'DwellInfo': _dwells([(1, 1, 1)])}
    channels = [a, b]
    snap = bce.snapshot_channels(channels)
    a['ChPos'][0] = 5                        # edited in place
    a['DwellInfo'] = np.zeros((0, 9))        # replaced
    channels.pop(1)                          # catheter deleted
    channels.append({'ChannelNumber': 3})    # catheter added
    bce.restore_channels(channels, snap)
    assert len(channels) == 2 and channels[0] is a and channels[1] is b
    np.testing.assert_array_equal(a['ChPos'], np.zeros((2, 3)))
    np.testing.assert_array_equal(a['DwellInfo'], _dwells([(0, 0, 0)]))


def test_new_channel():
    template = {'ChannelNumber': 4, 'ReferencedROINumber': 7, 'ChPos': np.ones((2, 3), np.float32),
                'DwellInfo': _dwells([(0, 0, 5)]), 'SourceApplicatorID': 'Needle', 'ChannelTotalTime': 7.0}
    new = bce.new_channel(template, bce.next_channel_number([template, {'ChannelNumber': 'N/A'}]))
    assert new['ChannelNumber'] == 5 and new['ReferencedROINumber'] == 'N/A' and new['SourceApplicatorID'] == 'Needle'
    assert new['ChPos'].shape == (0, 3) and new['ChPos'].dtype == np.float32 and new['DwellInfo'].shape == (0, 9)
    assert template['ChPos'].shape == (2, 3) and template['ChannelNumber'] == 4      # the template is unchanged


def test_pick_point():
    d, depth = [5.0, 0.5, 0.6, 9.0], [0.0, 10.0, 0.0, 0.0]
    assert bce.pick_point(d, depth, 0.0, tol=2.0, overlap=0.3) == 2   # overlapping: closest to the slice
    assert bce.pick_point(d, depth, 0.0, tol=2.0, overlap=0.0) == 1   # otherwise the nearest
    assert bce.pick_point(d, depth, 0.0, tol=0.1, overlap=0.3) is None
    assert bce.pick_point([np.nan], [0.0], 0.0, tol=2.0, overlap=0.3) is None


def test_new_channel_is_shown():
    assert bce.new_channel({'ChannelNumber': 1, 'Visible': False}, 2)['Visible'] is True


def test_visibility_flags():
    assert bce.channel_visible({}) and not bce.channel_visible({'Visible': False})
    assert bce.channel_visible({'Visible': np.True_}) and not bce.channel_visible({'Visible': np.False_})
    assert bce.ref_point_visible({}) and not bce.ref_point_visible({'Visible': False})


def test_ref_point_xyz():
    np.testing.assert_allclose(bce.ref_point_xyz({'DoseReferencePointCoordinates': [1, '2.5', 3]}), (1, 2.5, 3))
    for coords in (['N/A', 'N/A', 'N/A'], 'N/A', None, [1, 2], [1, np.nan, 3]):
        assert bce.ref_point_xyz({'DoseReferencePointCoordinates': coords}) is None
    assert bce.ref_point_xyz({}) is None


def test_ref_point_name():
    assert bce.ref_point_name({'DoseReferenceDescription': ' A left '}, 0) == "A left"
    assert bce.ref_point_name({'DoseReferenceDescription': 'N/A', 'DoseReferenceNumber': 4}, 0) == "Point 4"
    assert bce.ref_point_name({'DoseReferenceNumber': 'N/A'}, 2) == "Point 3"


def test_slice_indices():
    origin, spacing, thick, shape = (-50.0, -40.0, -20.0), (0.5, 2.0), 3.0, (10, 81, 51)
    # the image rows are stored flipped: the first row (y = origin) is the last coronal index
    assert bce.slice_indices((-50, -40, -20), origin, spacing, thick, shape) == (0, 80, 0)
    assert bce.slice_indices((0, 0, 7), origin, spacing, thick, shape) == (9, 0, 25)
    assert bce.slice_indices((1.1, -39.6, -18.4), origin, spacing, thick, shape) == (1, 79, 26)   # nearest slice
    assert bce.slice_indices((1e3, -1e3, -1e3), origin, spacing, thick, shape) == (0, 80, 50)     # clipped


def test_catheter_names():
    assert bce.catheter_name({}, 2) == "Catheter 3" and bce.catheter_label({}, 2) == "3"
    ch = {'CatheterName': '  Tandem '}
    assert bce.catheter_name(ch, 0) == "Tandem" and bce.catheter_label(ch, 0) == "Tandem"


from fcn_display import brachy_dwells as bdw  # noqa: E402

L_PATH = [(0, 0, 0), (0, 0, 10), (10, 0, 10)]   # tip first: 10 mm along z, then 10 mm along x


def test_dwell_count():
    assert bdw.dwell_count(5.0, 20.0) == 5
    assert bdw.dwell_count(3.0, 10.0) == 4          # 0, 3, 6, 9
    assert bdw.dwell_count(2.5, 0.0) == 1
    assert bdw.dwell_count(0.1, 0.3) == 4           # no floating point loss
    assert bdw.dwell_count(5.0, -1.0) == 0 and bdw.dwell_count(0.0, 10.0) == 0


def test_dwells_on_path():
    dw = bdw.dwells_on_path(L_PATH, offset=2.0, idd=5.0, length=100.0)     # cut at the end (20 mm)
    assert dw.shape == (4, 9) and dw.dtype == np.float32
    np.testing.assert_array_equal(dw[:, 0], [1, 2, 3, 4])
    np.testing.assert_allclose(dw[:, 1], [2, 7, 12, 17])                   # distance from the tip
    assert np.all(dw[:, 2] == 0)                                            # 0 s
    np.testing.assert_allclose(dw[:, 3:6], [(0, 0, 2), (0, 0, 7), (2, 0, 10), (7, 0, 10)], atol=1e-6)
    np.testing.assert_allclose(dw[:, 6:9], [(0, 0, 1), (0, 0, 1), (1, 0, 0), (1, 0, 0)])
    # the tip, a vertex (end of the segment before it) and the end of the catheter; towards the tip
    dw = bdw.dwells_on_path(L_PATH, 0.0, 10.0, 20.0, sign=-1.0)
    np.testing.assert_allclose(dw[:, 3:6], [(0, 0, 0), (0, 0, 10), (10, 0, 10)], atol=1e-6)
    np.testing.assert_allclose(dw[:, 6:9], [(0, 0, -1), (0, 0, -1), (-1, 0, 0)])


def test_current_layout_and_tip_distances():
    dw = bdw.dwells_on_path(L_PATH, 3.0, 2.5, 10.0)
    np.testing.assert_allclose(bdw.tip_distances(dw, L_PATH), [3, 5.5, 8, 10.5, 13], atol=1e-5)
    assert bdw.current_layout(dw, L_PATH) == pytest.approx((3.0, 2.5, 10.0))
    off_path = dw.copy()
    off_path[0, 3:6] = (50, 50, 50)                                         # not on the catheter: ignored
    assert bdw.current_layout(off_path, L_PATH) == pytest.approx((5.5, 2.5, 7.5))
    assert bdw.current_layout(dw[:1], L_PATH) == (pytest.approx(3.0), None, pytest.approx(0.0))
    assert bdw.current_layout(np.zeros((0, 9)), L_PATH) is None


def test_orientation_sign():
    assert bdw.orientation_sign(bdw.dwells_on_path(L_PATH, 0, 5, 20), L_PATH) == 1.0
    assert bdw.orientation_sign(bdw.dwells_on_path(L_PATH, 0, 5, 20, sign=-1.0), L_PATH) == -1.0
    no_direction = bdw.dwells_on_path(L_PATH, 0, 5, 20)
    no_direction[:, 6:9] = np.nan
    assert bdw.orientation_sign(no_direction, L_PATH) == 1.0
    assert bdw.orientation_sign(np.zeros((0, 9)), L_PATH) == 1.0


def test_slice_position_is_the_inverse_of_slice_indices():
    origin, spacing, thick, shape = (-50.0, -40.0, -20.0), (0.5, 2.0), 3.0, (10, 81, 51)
    np.testing.assert_allclose(bce.slice_position((0, 80, 0), origin, spacing, thick, shape), (-50, -40, -20))
    for indices in ((0, 0, 0), (9, 80, 50), (4, 17, 33)):
        p = bce.slice_position(indices, origin, spacing, thick, shape)
        assert bce.slice_indices(p, origin, spacing, thick, shape) == indices


def test_snapshot_copies_lists():
    pt = {'DoseReferenceDescription': 'A', 'DoseReferencePointCoordinates': [1.0, 2.0, 3.0]}
    refs = [pt]
    snap = bce.snapshot_channels(refs)
    pt['DoseReferencePointCoordinates'][0] = 9.0     # changed in place
    refs.append({'DoseReferenceDescription': 'B'})
    bce.restore_channels(refs, snap)
    assert refs == [pt] and pt['DoseReferencePointCoordinates'] == [1.0, 2.0, 3.0]
