"""
Editing of brachytherapy catheters (plan channels) in View > PLAN > Brachy.

- Edit tools for the axial, coronal and sagittal views (toggle buttons): move single
  points of the selected catheter, or translate / rotate the whole catheter in the
  image plane. Dwell positions ('DwellInfo' cols 3-5) follow the catheter and their
  source directions (cols 6-8) are rotated with it.
- "Hold IDD": the dwells keep their arc length along the catheter, so the
  inter-dwell distance is kept when a segment changes length.
- Add / delete points ('ChPos' rows), delete catheters, and undo.
- New catheter: after "New", each click on the images adds a point (tip first)
  until "Stop".
- Visibility of catheters and dose reference points on the images ('Visible', the
  check boxes of the catheter list), and "go to": the slices through a point.

The edits are made on the plan metadata in place, so the overlays, tables, plots,
CSV export, TG43 and MCNP all see the edited catheters.

The geometry helpers are also used by the 2D brachy overlays (display_images.py).
"""
import time
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox


# Dwells farther than this (mm) from the channel path do not follow it
DWELL_PATH_TOL_MM = 5.0
# Minimum time (s) between overlay redraws while dragging
DRAG_REDRAW_INTERVAL = 0.04
# Grab tolerance in screen pixels (used when larger than 1.5x the sphere radius)
GRAB_TOL_PX = 8
# Number of edits that can be undone
UNDO_LIMIT = 50
# New catheter button: (text, style, tooltip) before New is pressed and while points are clicked
NEW_CATHETER_BUTTON = ("New", "background-color: #28a745; color: white;",
                       "New catheter: after pressing New, click on the images to add its points, starting from the tip.\n"
                       "Each click adds a point on the current slice (keep the mouse button down to adjust it).\n"
                       "Press Stop when done.")
STOP_CATHETER_BUTTON = ("Stop", "background-color: #dc3545; color: white; font-weight: bold;",
                        "Stop adding points: the new catheter is done (without points it is discarded).")

# View name -> VTK widget attribute, and the patient axis normal to the view
VIEW_WIDGETS = (('axial', 'vtkWidgetAxial'), ('coronal', 'vtkWidgetCoronal'), ('sagittal', 'vtkWidgetSagittal'))
NORMAL_AXIS = {'axial': 2, 'coronal': 1, 'sagittal': 0}
# Patient direction d -> view direction M @ d: x, y in the image plane (as in view_xy),
# z out of the plane (towards the viewer, right-handed)
VIEW_MATRIX = {
    'axial': np.array([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]]),
    'coronal': np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0]]),
    'sagittal': np.array([[0.0, -1.0, 0.0], [0.0, 0.0, 1.0], [-1.0, 0.0, 0.0]]),
}
# Edit tools, their toggle buttons and the cursor while dragging
TOOL_BUTTONS = (('move', 'brachy_tool_move'), ('translate', 'brachy_tool_translate'), ('rotate', 'brachy_tool_rotate'))
TOOL_CURSORS = {'move': Qt.ClosedHandCursor, 'translate': Qt.SizeAllCursor, 'rotate': Qt.ClosedHandCursor}
# Channel / reference point dict keys set in the catheter list (shown, name): not part of the undo history
LIST_KEYS = ('Visible', 'CatheterName')
REF_LIST_KEYS = ('Visible', 'DoseReferenceDescription', 'DoseReference Description', 'DoseReferenceDescription ')
# Brachy overlays: (drawing function in display_images.py, actor list), both + view suffix
OVERLAYS = (('display_brachy_channel_overlay_', 'channel_actors_'),
            ('display_dwell_positions_', 'dwell_actors_'),
            ('display_ref_points_', 'ref_point_actors_'))
VIEW_SUFFIX = {'axial': 'ax', 'coronal': 'co', 'sagittal': 'sa'}


# ---------------------------------------------------------------------------
# Geometry (pure numpy)
# ---------------------------------------------------------------------------
def project_on_polyline(pts, poly):
    """
    Project points onto a polyline.

    :param pts: (M, 3) points
    :param poly: (N, 3) polyline vertices, N >= 2
    :return: seg (M,) index of the closest segment, t (M,) position along it
             in [0, 1], proj (M, 3) closest point, dist (M,) distance to it
    """
    pts = np.asarray(pts, dtype=float).reshape(-1, 3)
    poly = np.asarray(poly, dtype=float).reshape(-1, 3)
    a = poly[:-1]
    ab = poly[1:] - a
    len2 = np.einsum('ij,ij->i', ab, ab)
    ap = pts[:, None, :] - a[None, :, :]
    with np.errstate(invalid='ignore', divide='ignore'):
        t = np.einsum('msk,sk->ms', ap, ab) / len2[None, :]
    # zero-length segments project onto their start point
    t = np.where(len2[None, :] > 0, np.clip(t, 0.0, 1.0), 0.0)
    proj = a[None, :, :] + t[..., None] * ab[None, :, :]
    d = np.linalg.norm(pts[:, None, :] - proj, axis=2)
    seg = np.argmin(d, axis=1)
    rows = np.arange(len(pts))
    return seg, t[rows, seg], proj[rows, seg], d[rows, seg]


def rotate_vectors(v, a, b):
    """
    Rotate each v[i] by the rotation taking direction a[i] onto b[i] (Rodrigues).
    Rows where a or b is degenerate or a, b are (anti)parallel are left as they are;
    NaN vectors stay NaN.
    """
    v = np.asarray(v, dtype=float).reshape(-1, 3)
    a = np.broadcast_to(np.asarray(a, dtype=float), v.shape)
    b = np.broadcast_to(np.asarray(b, dtype=float), v.shape)
    with np.errstate(invalid='ignore', divide='ignore'):
        a = a / np.linalg.norm(a, axis=1, keepdims=True)
        b = b / np.linalg.norm(b, axis=1, keepdims=True)
    k = np.cross(a, b)
    s = np.linalg.norm(k, axis=1)
    c = np.einsum('ij,ij->i', a, b)
    out = v.copy()
    ok = s > 1e-12
    if np.any(ok):
        kh = k[ok] / s[ok, None]
        vv = v[ok]
        out[ok] = (vv * c[ok, None]
                   + np.cross(kh, vv) * s[ok, None]
                   + kh * np.einsum('ij,ij->i', kh, vv)[:, None] * (1.0 - c[ok, None]))
    return out


def valid_dwells(dwell_info):
    """True if dwell_info is a (M, >=6) array with at least one row."""
    return (isinstance(dwell_info, np.ndarray) and dwell_info.ndim == 2
            and dwell_info.shape[0] > 0 and dwell_info.shape[1] >= 6)


def attach_dwells(dwell_info, poly, tol=DWELL_PATH_TOL_MM):
    """
    Locate each dwell (cols 3-5) on the channel path.

    :return: seg (M,) segment index, t (M,) position along it, attached (M,) bool,
             True if the dwell lies within tol (mm) of the path
    """
    seg, t, _, dist = project_on_polyline(np.asarray(dwell_info, dtype=float)[:, 3:6], poly)
    return seg, t, dist <= tol


def follow_path(dwell_info, poly0, poly1, seg, t, attached):
    """
    Return a copy of dwell_info with the attached dwells moved from path poly0 to
    path poly1 (same vertex count). Each dwell keeps its position t along its
    segment: it moves by (1 - t) x the shift of the segment start plus t x the
    shift of the segment end, and its orientation (cols 6-8) is rotated with
    the segment.
    """
    out = np.array(dwell_info, copy=True)
    if not np.any(attached):
        return out
    src = np.asarray(dwell_info, dtype=float)
    poly0 = np.asarray(poly0, dtype=float)
    poly1 = np.asarray(poly1, dtype=float)
    s = np.asarray(seg)[attached]
    tt = np.asarray(t, dtype=float)[attached][:, None]
    shift = (1.0 - tt) * (poly1[s] - poly0[s]) + tt * (poly1[s + 1] - poly0[s + 1])
    out[attached, 3:6] = src[attached, 3:6] + shift
    if out.shape[1] >= 9:
        out[attached, 6:9] = rotate_vectors(src[attached, 6:9],
                                            poly0[s + 1] - poly0[s],
                                            poly1[s + 1] - poly1[s])
    return out


def arc_lengths(poly):
    """Segment lengths (N - 1,) and arc length at each vertex (N,) of a polyline."""
    poly = np.asarray(poly, dtype=float).reshape(-1, 3)
    seg_len = np.linalg.norm(np.diff(poly, axis=0), axis=1)
    return seg_len, np.concatenate(([0.0], np.cumsum(seg_len)))


def locate_arclength(poly, s):
    """
    Segment index k and position t along it of the points at arc length s from
    the first vertex of a polyline (N >= 2). A point on a vertex lies at the end of
    the segment before it (as in project_on_polyline). Past the end, t > 1 on the
    last segment.
    """
    seg_len, cum = arc_lengths(poly)
    s = np.asarray(s, dtype=float)
    k = np.clip(np.searchsorted(cum, s, side='left') - 1, 0, len(seg_len) - 1)
    length = seg_len[k]
    t = np.where(length > 0, (s - cum[k]) / np.where(length > 0, length, 1.0), 0.0)
    return k, t


def keep_idd(dwell_info, poly0, poly1, tol=DWELL_PATH_TOL_MM):
    """
    Return a copy of dwell_info with the dwells on path poly0 moved to path poly1
    (any number of vertices) at the same arc length from the first vertex, so the
    distances between them along the path (inter-dwell distance) are kept. A dwell
    keeps its offset from the path; the offset and the orientation (cols 6-8) are
    rotated with the segment it lies on. Dwells past the end of poly1 continue along
    its last segment; dwells farther than tol from poly0 are unchanged.
    """
    out = np.array(dwell_info, copy=True)
    poly0 = np.asarray(poly0, dtype=float).reshape(-1, 3)
    poly1 = np.asarray(poly1, dtype=float).reshape(-1, 3)
    if not valid_dwells(out) or len(poly0) < 2 or len(poly1) < 2:
        return out
    seg, t, attached = attach_dwells(out, poly0, tol)
    if not np.any(attached):
        return out
    src = np.asarray(dwell_info, dtype=float)[attached]
    seg, t = seg[attached], t[attached]
    len0, cum0 = arc_lengths(poly0)
    k, t1 = locate_arclength(poly1, cum0[seg] + t * len0[seg])
    d0 = poly0[seg + 1] - poly0[seg]
    d1 = poly1[k + 1] - poly1[k]
    old_proj = poly0[seg] + t[:, None] * d0
    new_proj = poly1[k] + t1[:, None] * d1
    out[attached, 3:6] = new_proj + rotate_vectors(src[:, 3:6] - old_proj, d0, d1)
    if out.shape[1] >= 9:
        out[attached, 6:9] = rotate_vectors(src[:, 6:9], d0, d1)
    return out


def remap_dwells_after_delete(dwell_info, poly, j, tol=DWELL_PATH_TOL_MM):
    """
    Return a copy of dwell_info for the path 'poly' with vertex j removed.

    For an interior vertex the two segments around it merge into one straight
    segment: dwells on them keep their arc-length fraction over the merged span
    and their offset from the path, and their orientation is rotated with the
    segment. Other dwells, and all dwells when an end point is removed, are unchanged.
    """
    out = np.array(dwell_info, copy=True)
    poly = np.asarray(poly, dtype=float).reshape(-1, 3)
    n = len(poly)
    if not valid_dwells(out) or n < 3 or not (0 < j < n - 1):
        return out
    seg, t, attached = attach_dwells(out, poly, tol)
    on_span = attached & ((seg == j - 1) | (seg == j))
    if not np.any(on_span):
        return out
    src = np.asarray(dwell_info, dtype=float)
    a, m, b = poly[j - 1], poly[j], poly[j + 1]
    l1, l2 = np.linalg.norm(m - a), np.linalg.norm(b - m)
    s, tt = seg[on_span], t[on_span]
    arc = np.where(s == j - 1, tt * l1, l1 + tt * l2)
    f = arc / (l1 + l2) if (l1 + l2) > 0 else np.zeros_like(arc)
    old_proj = poly[s] + tt[:, None] * (poly[s + 1] - poly[s])
    new_proj = a + f[:, None] * (b - a)
    out[on_span, 3:6] = src[on_span, 3:6] - old_proj + new_proj
    if out.shape[1] >= 9:
        out[on_span, 6:9] = rotate_vectors(src[on_span, 6:9], poly[s + 1] - poly[s], b - a)
    return out


def new_point_for_insert(poly, r, fallback=None):
    """
    Coordinates of a point inserted after row r of the channel points: the
    midpoint to the next point, or one more segment of the same length and
    direction after the last point. A single point is duplicated; an empty
    channel uses 'fallback'. r outside the rows means after the last row.
    """
    poly = np.asarray(poly, dtype=float).reshape(-1, 3)
    n = len(poly)
    if n == 0:
        return np.asarray(fallback, dtype=float)
    if not 0 <= r < n:
        r = n - 1
    if r < n - 1:
        return (poly[r] + poly[r + 1]) / 2.0
    if n >= 2:
        return poly[r] + (poly[r] - poly[r - 1])
    return poly[r].copy()


def view_xy(view, pts, ipp, height):
    """
    Patient coordinates (N, 3) -> world (x, y) in a 2D view, as drawn by the
    brachy overlays in display_images.py (layer 0, height = rows * row spacing).
    """
    pts = np.asarray(pts, dtype=float).reshape(-1, 3)
    if view == 'axial':
        return np.column_stack((pts[:, 0] - ipp[0], height - (pts[:, 1] - ipp[1])))
    if view == 'coronal':
        return np.column_stack((pts[:, 0] - ipp[0], pts[:, 2] - ipp[2]))
    return np.column_stack((height - (pts[:, 1] - ipp[1]), pts[:, 2] - ipp[2]))


def point_from_view_xy(view, xy, pt, ipp, height):
    """Inverse of view_xy: pt with its two in-plane coordinates set from xy."""
    new = np.array(pt, dtype=float)
    if view == 'axial':
        new[0] = ipp[0] + xy[0]
        new[1] = ipp[1] + height - xy[1]
    elif view == 'coronal':
        new[0] = ipp[0] + xy[0]
        new[2] = ipp[2] + xy[1]
    else:
        new[1] = ipp[1] + height - xy[0]
        new[2] = ipp[2] + xy[1]
    return new


def slice_position(indices, origin, pixel_spacing, slice_thickness, shape):
    """
    Patient point (x, y, z) where the (axial, coronal, sagittal) slices of a volume of
    shape (Z, Y, X) intersect, as the "Get Plane" button of the reference point table
    computes it: the inverse of slice_indices.
    """
    axial, coronal, sagittal = indices
    return np.array([origin[0] + sagittal * pixel_spacing[1],
                     origin[1] + (shape[1] - 1 - coronal) * pixel_spacing[0],
                     origin[2] + axial * slice_thickness], dtype=float)


def slice_indices(pt, origin, pixel_spacing, slice_thickness, shape):
    """
    (axial, coronal, sagittal) indices of the image slices through the patient point pt
    (as the "Go" button of the reference point table computes them), clipped to a
    volume of shape (Z, Y, X) with its first voxel at 'origin'. The rows are stored
    flipped, so the coronal index counts from the last image row.
    """
    x, y, z = (float(v) for v in np.asarray(pt, dtype=float).reshape(-1)[:3])
    idx = np.rint(((z - origin[2]) / slice_thickness,
                   (shape[1] - 1) - (y - origin[1]) / pixel_spacing[0],
                   (x - origin[0]) / pixel_spacing[1]))
    return tuple(int(np.clip(i, 0, n - 1)) for i, n in zip(idx, shape[:3]))


def view_dir(view, dirs):
    """
    Patient directions (N, 3) -> view coordinates: x, y in the image plane as in
    view_xy, z out of the plane (towards the viewer, right-handed).
    """
    return np.asarray(dirs, dtype=float).reshape(-1, 3) @ VIEW_MATRIX[view].T


def view_translation(view, dxy):
    """Patient displacement that moves points by dxy (world x, y) in a 2D view."""
    return VIEW_MATRIX[view].T @ np.array([dxy[0], dxy[1], 0.0])


def view_rotation(view, angle):
    """
    Patient rotation matrix that turns points by 'angle' (radians, counter-clockwise
    in the world x, y of a 2D view) about the view normal.
    """
    c, s = np.cos(angle), np.sin(angle)
    m = VIEW_MATRIX[view]
    return m.T @ np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]) @ m


def distance_to_path_2d(p, xy):
    """Distance from the 2D point p to the polyline through xy (N, 2), or to its point if N == 1."""
    xy = np.asarray(xy, dtype=float).reshape(-1, 2)
    if len(xy) == 1:
        return float(np.linalg.norm(xy[0] - p))
    flat = np.column_stack((xy, np.zeros(len(xy))))
    return float(project_on_polyline((p[0], p[1], 0.0), flat)[3][0])


def pick_point(d, depth, slice_pos, tol, overlap):
    """
    Index of the point to grab: the nearest one within tol of the cursor (d are
    in-plane distances). When several are within 'overlap' of that nearest
    distance (overlapping in this projection), the one whose out-of-plane
    coordinate (depth) is closest to the current slice wins. None if nothing is in reach.
    """
    d = np.asarray(d, dtype=float)
    finite = np.isfinite(d)
    if not np.any(finite):
        return None
    d_min = d[finite].min()
    if d_min > tol:
        return None
    near = np.where(finite & (d <= d_min + overlap))[0]
    return int(near[np.argmin(np.abs(np.asarray(depth, dtype=float)[near] - slice_pos))])


def dwell_directions(dwell_info, ch_pos=None, tol=DWELL_PATH_TOL_MM):
    """
    Unit source direction at each dwell (patient coordinates), in the same order
    of preference as the MCNP export: the plan's orientation (cols 6-8), the
    nearest channel segment (dwells within tol of the path), the neighbouring
    dwells. Rows without a usable direction are NaN.
    """
    dw = np.asarray(dwell_info, dtype=float)
    xyz = dw[:, 3:6]
    dirs = np.full((len(dw), 3), np.nan)

    def fill(candidates):
        n = np.linalg.norm(candidates, axis=1)
        ok = np.isnan(dirs[:, 0]) & np.isfinite(n) & (n > 1e-9)
        dirs[ok] = candidates[ok] / n[ok, None]

    if dw.shape[1] >= 9:
        fill(dw[:, 6:9])
    pts = np.asarray(ch_pos, dtype=float) if ch_pos is not None else None
    if pts is not None and pts.ndim == 2 and pts.shape[1] >= 3 and len(pts) >= 2 and np.isnan(dirs[:, 0]).any():
        seg, _, _, dist = project_on_polyline(xyz, pts[:, :3])
        seg_dirs = pts[seg + 1, :3] - pts[seg, :3]
        seg_dirs[~(dist <= tol)] = np.nan
        fill(seg_dirs)
    if len(xyz) >= 2 and np.isnan(dirs[:, 0]).any():
        # central difference, one-sided at the first / last dwell
        fill(np.vstack((xyz[1:], xyz[-1:])) - np.vstack((xyz[:1], xyz[:-1])))
    return dirs


def dwell_glyph_size(xyz, point_size):
    """
    (length, radius) in mm of the dwell cylinders of one channel: 1.2 x the point
    size long, but at most 90 % of the smallest dwell spacing so neighbours stay
    apart; the radius is a quarter of the length.
    """
    length = 1.2 * point_size
    xyz = np.asarray(xyz, dtype=float).reshape(-1, 3)
    if len(xyz) >= 2:
        step = np.linalg.norm(np.diff(xyz, axis=0), axis=1)
        step = step[np.isfinite(step) & (step > 1e-3)]
        if step.size:
            length = min(length, 0.9 * step.min())
    return length, length / 4.0


def dwell_outline(xy, dirs, length, radius, n=8):
    """
    Outline (M, 2n + 2, 2) of cylinders centred at xy (M, 2) along dirs (M, 3, view
    coordinates, z out of the plane) as seen in the 2D view: the projected end caps
    (half ellipses) joined by the sides. length and radius are scalars or (M,).
    A cylinder without a usable direction is seen end-on (a circle).
    """
    xy = np.asarray(xy, dtype=float).reshape(-1, 2)
    d = np.asarray(dirs, dtype=float).reshape(-1, 3)
    m = len(xy)
    length = np.broadcast_to(np.asarray(length, dtype=float), (m,))
    radius = np.broadcast_to(np.asarray(radius, dtype=float), (m,))
    norm = np.linalg.norm(d, axis=1)
    ok = np.isfinite(norm) & (norm > 1e-9)
    d = np.where(ok[:, None], d / np.where(ok, norm, 1.0)[:, None], (0.0, 0.0, 1.0))
    s = np.linalg.norm(d[:, :2], axis=1)                       # in-plane part of the axis
    u = np.where((s > 1e-9)[:, None], d[:, :2] / np.maximum(s, 1e-12)[:, None], (1.0, 0.0))
    p = np.column_stack((-u[:, 1], u[:, 0]))
    end = (0.5 * length * s)[:, None, None] * u[:, None, :]    # cap centres at xy +- end
    theta = np.linspace(0.0, np.pi, n + 1)[None, :, None]
    across = radius[:, None, None] * np.cos(theta) * p[:, None, :]
    # a cap of radius r is seen as an ellipse with semi-axes r and r * |dz|
    along = (radius * np.abs(d[:, 2]))[:, None, None] * np.sin(theta) * u[:, None, :]
    c = xy[:, None, :]
    return np.concatenate((c + end + across + along, c - end - across - along), axis=1)


def snapshot_channels(channels):
    """
    Copy of a list of dicts (catheters, reference points) for undo: each dict with a
    copy of its items (arrays and lists copied).
    """
    return [(ch, {key: (val.copy() if isinstance(val, (np.ndarray, list)) else val) for key, val in ch.items()})
            for ch in channels]


def restore_channels(channels, snap):
    """Put the catheter list back as it was at snapshot_channels (in place, same dict objects)."""
    for ch, items in snap:
        ch.clear()
        ch.update(items)
    channels[:] = [ch for ch, _ in snap]


def new_channel(template, number):
    """
    Empty catheter (no points, no dwells, shown) with channel number 'number' and the
    other fields (applicator, source, times) of the channel dict 'template'.
    """
    new = {key: val for key, val in template.items() if not isinstance(val, np.ndarray)}
    new.update({'ChannelNumber': number, 'ReferencedROINumber': 'N/A', 'NumberofControlPoints': 0,
                'ChPos': np.empty((0, 3), dtype=np.float32), 'DwellInfo': np.empty((0, 9), dtype=np.float32),
                'Visible': True})
    return new


def next_channel_number(channels):
    """Channel number for a new catheter: one more than the largest number in use."""
    numbers = []
    for ch in channels:
        try:
            numbers.append(int(ch.get('ChannelNumber')))
        except (TypeError, ValueError):
            pass
    return max(numbers, default=len(channels)) + 1


def channel_visible(ch):
    """True if a catheter is shown on the images (ticked in the catheter list; shown by default)."""
    return bool(ch.get('Visible', True))


def catheter_name(ch, k):
    """Name of catheter k (0-based): the one given in the catheter list, else "Catheter <k + 1>"."""
    return str(ch.get('CatheterName') or '').strip() or f"Catheter {k + 1}"


def catheter_label(ch, k):
    """Label of catheter k on the images: its name, or its number if it was not renamed."""
    return str(ch.get('CatheterName') or '').strip() or str(k + 1)


def ref_point_visible(pt):
    """True if a dose reference point is shown on the images (ticked in the list; shown by default)."""
    return bool(pt.get('Visible', True))


def ref_point_xyz(pt):
    """Coordinates (3,) of a dose reference point, or None if it has none ('N/A')."""
    try:
        xyz = np.asarray(pt.get('DoseReferencePointCoordinates'), dtype=float).reshape(-1)
    except (TypeError, ValueError):
        return None
    return xyz[:3] if xyz.size >= 3 and np.all(np.isfinite(xyz[:3])) else None


def ref_point_name(pt, k):
    """Name of dose reference point k (0-based): its description, else "Point <number>"."""
    name = str(pt.get('DoseReferenceDescription', '') or '').strip()
    if name and name != 'N/A':
        return name
    number = pt.get('DoseReferenceNumber')
    return f"Point {number if number not in (None, '', 'N/A') else k + 1}"


# ---------------------------------------------------------------------------
# App state helpers
# ---------------------------------------------------------------------------
def _has_image(self):
    try:
        return isinstance(self.display_data[0], np.ndarray) and self.display_data[0].ndim == 3
    except Exception:
        return False


def _overlay_channels(self):
    """Channels of the displayed series (what the 2D overlays draw), or None."""
    try:
        meta = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']
    except (AttributeError, KeyError, IndexError, TypeError):
        return None
    channels = meta.get('Plan_Brachy_Channels')
    return channels if isinstance(channels, list) and channels else None


def _plan_metadata(self):
    """Metadata of the loaded plan (what the brachy tables show), or None."""
    try:
        return self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']
    except (AttributeError, KeyError, IndexError, TypeError):
        return None


def _plan_channels(self):
    """Channels of the loaded plan (what the brachy tables show; empty for a new plan), or None."""
    meta = _plan_metadata(self)
    channels = meta.get('Plan_Brachy_Channels') if meta is not None else None
    return channels if isinstance(channels, list) else None


def plan_ref_points(self):
    """Dose reference points of the loaded plan (list of dicts, empty if none)."""
    meta = _plan_metadata(self)
    refs = meta.get('Plan_Dose_References') if meta is not None else None
    return refs if isinstance(refs, list) else []


def _selected_channel(self, channels):
    """Channel dict picked by brachy_spinBox_01, or None."""
    idx = self.brachy_spinBox_01.value() - 1
    if channels and 0 <= idx < len(channels):
        return channels[idx]
    return None


def selected_catheter(self, channels):
    """The catheter selected in the catheter list (None while the table lists the reference points)."""
    combo = getattr(self, 'brachy_combobox_01', None)
    if combo is not None and combo.currentText() == "Ref. Points":
        return None
    return _selected_channel(self, channels)


def _channel_points(ch):
    """The channel's (N, 3) 'ChPos' array, or None if missing / invalid."""
    pts = ch.get('ChPos') if ch is not None else None
    if isinstance(pts, np.ndarray) and pts.ndim == 2 and pts.shape[1] >= 3:
        return pts
    return None


def _view_geometry(self):
    """(Image position, height) of layer 0, as used by the brachy overlays."""
    return self.Im_PatPosition[0], self.display_data[0].shape[1] * self.pixel_spac[0, 0]


def _slice_point(self):
    """Patient coordinates where the three current slices (layer 0) intersect."""
    ipp, height = _view_geometry(self)
    return np.array([
        ipp[0] + self.current_sagittal_slice_index[0] * self.pixel_spac[0, 1],
        ipp[1] + height - self.current_coronal_slice_index[0] * self.pixel_spac[0, 0],
        ipp[2] + self.current_axial_slice_index[0] * self.slice_thick[0],
    ])


def _renderer(self, view):
    widget = getattr(self, dict(VIEW_WIDGETS)[view])
    return widget.GetRenderWindow().GetRenderers().GetFirstRenderer()


def _event_world_xy(renderer, x, y):
    """Display position -> world (x, y) of a 2D view."""
    renderer.SetDisplayPoint(x, y, 0)
    renderer.DisplayToWorld()
    wp = renderer.GetWorldPoint()
    if wp[3] != 0.0:
        return np.array([wp[0] / wp[3], wp[1] / wp[3]])
    return np.array([wp[0], wp[1]])


def _angle(v):
    return np.arctan2(v[1], v[0])


def _checked(self, name):
    box = getattr(self, name, None)
    return box is not None and box.isChecked()


def _hold_idd(self):
    return _checked(self, 'brachy_hold_idd')


def _set_checked(btn, checked):
    """Check / uncheck a button without emitting its signals."""
    if btn is not None and btn.isChecked() != checked:
        btn.blockSignals(True)
        btn.setChecked(checked)
        btn.blockSignals(False)


def brachy_tab_active(self):
    """True when View > PLAN > Brachy is the visible tab."""
    for tabs_name, tab_name in (('tabModules', 'im_display_tab'), ('tabView01', 'tab_14'), ('tabWidget_3', 'tab_37')):
        tabs = getattr(self, tabs_name, None)
        tab = getattr(self, tab_name, None)
        if tabs is None or tab is None or tabs.currentWidget() is not tab:
            return False
    return True


def brachy_tool(self):
    """Name of the active edit tool ('move', 'translate' or 'rotate'), or None."""
    for name, attr in TOOL_BUTTONS:
        btn = getattr(self, attr, None)
        if btn is not None and btn.isChecked():
            return name
    return None


def catheter_being_drawn(self):
    """The new catheter whose points are being clicked on the images (after New), or None."""
    ch = getattr(self, '_brachy_new_ch', None)
    channels = _plan_channels(self)
    if ch is None or channels is None or not any(c is ch for c in channels):
        return None
    return ch


def brachy_edit_active(self):
    """True when an edit tool is on and the selected catheter (shown) can be edited in the 2D views."""
    if brachy_tool(self) is None:
        return False
    if not brachy_tab_active(self) or not self.display_brachy_channel_overlay.isChecked():
        return False
    if self.brachy_combobox_01.currentText() == "Ref. Points":
        return False
    ch = _selected_channel(self, _overlay_channels(self))
    return _has_image(self) and ch is not None and channel_visible(ch)


def brachy_highlight(self, channels):
    """
    (channel dict, point index) to highlight in the channel overlays while a new
    catheter is clicked (its last point) or an edit tool is active, else (None, None).
    With the "move" tool the point is the one being dragged, or the selected table
    row in "Channels" mode.
    """
    new = catheter_being_drawn(self)
    if new is not None:
        n = len(new['ChPos'])
        return new, (n - 1 if n else None)
    if not brachy_edit_active(self):
        return None, None
    ch = _selected_channel(self, channels)
    if brachy_tool(self) != 'move':
        return ch, None
    drag = getattr(self, '_brachy_drag', None)
    if drag is not None:
        return ch, drag['j']
    if self.brachy_combobox_01.currentText() == "Channels":
        row = self.brachy_table_01.currentRow()
        return ch, (row if row >= 0 else None)
    return ch, None


def refresh_brachy_overlays(self):
    """
    Redraw only the brachy overlays (catheters, dwells, reference points) of the three
    views; the ones switched off under Display are removed.
    """
    if not hasattr(self, 'channel_actors_ax') or not _has_image(self):
        return
    from fcn_display import display_images
    shown = (self.display_brachy_channel_overlay.isChecked(), self.display_dw_overlay.isChecked(),
             _checked(self, 'brachy_show_ref_points'))
    for (draw, actors), show in zip(OVERLAYS, shown):
        for view, widget in VIEW_WIDGETS:
            suffix = VIEW_SUFFIX[view]
            if show:
                getattr(display_images, draw + suffix)(self)
            elif getattr(self, actors + suffix, None):
                renderer = _renderer(self, view)
                for actor in getattr(self, actors + suffix):
                    renderer.RemoveActor(actor)
                getattr(self, actors + suffix).clear()
                getattr(self, widget).GetRenderWindow().Render()


def _selected_layer(self):
    """(index, volume) of the selected image layer; layer 0 if that one has no volume."""
    idx = self.layer_selected.currentIndex()
    data = self.display_data.get(idx) if isinstance(self.display_data, dict) else None
    if not isinstance(data, np.ndarray) or data.ndim != 3:
        idx, data = 0, self.display_data[0]
    return idx, data


def current_slice_position(self):
    """Patient point (mm) where the axial, coronal and sagittal slices shown intersect, or None without an image."""
    if not _has_image(self):
        return None
    idx, data = _selected_layer(self)
    indices = (self.current_axial_slice_index[idx], self.current_coronal_slice_index[idx],
               self.current_sagittal_slice_index[idx])
    return slice_position(indices, self.Im_PatPosition[idx] + self.Im_Offset[idx], self.pixel_spac[idx],
                          self.slice_thick[idx], data.shape)


def go_to_point(self, xyz):
    """
    Show the axial, coronal and sagittal slices through a patient point (mm). False if
    there is no image or the point has no coordinates.
    """
    p = np.asarray(xyz, dtype=float).reshape(-1)
    if not _has_image(self) or p.size < 3 or not np.all(np.isfinite(p[:3])):
        return False
    # indices of the selected layer (the slice changes start from it), with its own geometry
    idx, data = _selected_layer(self)
    axial, coronal, sagittal = slice_indices(p, self.Im_PatPosition[idx] + self.Im_Offset[idx], self.pixel_spac[idx],
                                             self.slice_thick[idx], data.shape)
    self.current_axial_slice_index[idx] = axial
    self.current_coronal_slice_index[idx] = coronal
    self.current_sagittal_slice_index[idx] = sagittal
    from fcn_display.mouse_move_slicechanges import change_sliceAxial, change_sliceCoronal, change_sliceSagittal
    change_sliceAxial(self, 0)
    change_sliceCoronal(self, 0)
    change_sliceSagittal(self, 0)
    return True


def commit_channel_edit(self, select_row=None):
    """Refresh tables, plots and views after the channel geometry changed."""
    from fcn_display.disp_plan_data import update_disp_brachy_plan
    update_disp_brachy_plan(self)
    if (select_row is not None and self.brachy_combobox_01.currentText() == "Channels"
            and 0 <= select_row < self.brachy_table_01.rowCount()):
        self.brachy_table_01.selectRow(select_row)


def _set_channel_count(self, n, current):
    """Catheter spin boxes (View and Plan modules) and count after catheters were added or removed."""
    current = int(min(max(current, 1), max(n, 1)))
    changed = self.brachy_spinBox_01.maximum() != n
    for name in ('brachy_spinBox_01', 'brachy_spinBox_02'):
        spin = getattr(self, name, None)
        if spin is None:
            continue
        spin.blockSignals(True)
        spin.setMinimum(1)
        spin.setMaximum(max(n, 1))
        spin.setValue(current)
        spin.blockSignals(False)
    count = getattr(self, 'brachy_N_channels', None)
    if count is not None:
        count.setText(f"{n:.0f}")
    if changed and hasattr(self, '_3D_brachy_table'):
        from fcn_3Dview.brachy_3D_table import repopulate_3D_brachy_table
        repopulate_3D_brachy_table(self)


# ---------------------------------------------------------------------------
# Undo
# ---------------------------------------------------------------------------
def _undo_available(self):
    """True if the last undo step belongs to the plan shown now."""
    stack = getattr(self, '_brachy_undo', None)
    return bool(stack) and any(stack[-1][0] is channels for channels in (_plan_channels(self), _overlay_channels(self))
                               if channels is not None)


def push_undo(self, channels, snap=None, refs=None, sk=False):
    """
    Remember the catheters (before an edit) for undo; 'snap' is taken now if not given.
    For an edit of the reference points, 'refs' (their list) is remembered as well; with
    'sk', the plan's air kerma strength.
    """
    stack = getattr(self, '_brachy_undo', None) or []
    if stack and stack[-1][0] is not channels:
        stack = []  # another plan: its history is dropped
    meta = _plan_metadata(self) if sk else None
    stack.append((channels, snap if snap is not None else snapshot_channels(channels), self.brachy_spinBox_01.value(),
                  (refs, snapshot_channels(refs)) if refs is not None else None,
                  ('ReferenceAirKermaRate' in meta, meta.get('ReferenceAirKermaRate')) if meta is not None else None))
    del stack[:-UNDO_LIMIT]
    self._brachy_undo = stack
    update_undo_button(self)


def update_undo_button(self):
    btn = getattr(self, 'brachy_undo_btn', None)
    if btn is not None:
        btn.setEnabled(_undo_available(self))


def _restore_keeping(elements, snap, keys):
    """restore_channels, keeping the current values of 'keys' (set in the catheter list, not edits)."""
    kept = [(el, {key: el[key] for key in keys if key in el}) for el in elements]
    restore_channels(elements, snap)
    for el, items in kept:
        for key in keys:
            el.pop(key, None)
        el.update(items)


def brachy_undo(self):
    """Undo the last catheter edit (points, dwells, new / deleted catheters) or reference point edit."""
    _end_drag(self)
    if not _undo_available(self):
        self._brachy_undo = []
        update_undo_button(self)
        return
    channels, snap, current, refs_entry, sk_entry = self._brachy_undo.pop()
    # showing / hiding and renaming are not edits: undo keeps them
    _restore_keeping(channels, snap, LIST_KEYS)
    _set_channel_count(self, len(channels), current)
    if refs_entry is not None:
        _restore_keeping(*refs_entry, REF_LIST_KEYS)
    meta = _plan_metadata(self)
    if sk_entry is not None and meta is not None and meta.get('Plan_Brachy_Channels') is channels:
        had_sk, sk = sk_entry
        if had_sk:
            meta['ReferenceAirKermaRate'] = sk
        else:
            meta.pop('ReferenceAirKermaRate', None)
    if refs_entry is not None or self.brachy_combobox_01.currentText() == "Ref. Points":
        from fcn_display.brachy_tree import refresh_ref_points
        refresh_ref_points(self)  # (without asking for the RTDOSE again)
    else:
        commit_channel_edit(self)
    update_undo_button(self)


def on_brachy_undo_key(self):
    """Ctrl+Z in the View module: undo a catheter edit while the Brachy tab is shown."""
    if brachy_tab_active(self):
        brachy_undo(self)


# ---------------------------------------------------------------------------
# Points and catheters (buttons)
# ---------------------------------------------------------------------------
def _plan_selected_channel(self):
    channels = _plan_channels(self)
    if channels is None:
        QMessageBox.warning(self, "Warning", "No brachy plan loaded.")
        return None
    ch = _selected_channel(self, channels)
    if ch is None:
        QMessageBox.warning(self, "Warning", "Invalid channel selected.")
    return ch


def brachy_add_channel_point(self):
    """Insert a channel point below the selected table row (midpoint to the next point)."""
    ch = _plan_selected_channel(self)
    if ch is None:
        return
    pts = _channel_points(ch)
    if pts is None:
        pts = np.zeros((0, 3), dtype=np.float32)
    row = self.brachy_table_01.currentRow()
    r = row if 0 <= row < len(pts) else len(pts) - 1
    fallback = _slice_point(self) if _has_image(self) else np.zeros(3)
    new_pt = new_point_for_insert(pts[:, :3], r, fallback)
    push_undo(self, _plan_channels(self))
    ch['ChPos'] = np.insert(pts[:, :3], r + 1, new_pt, axis=0)
    commit_channel_edit(self, select_row=r + 1)


def brachy_delete_channel_point(self):
    """Delete the channel point of the selected table row; dwells on its segments are re-placed."""
    ch = _plan_selected_channel(self)
    if ch is None:
        return
    pts = _channel_points(ch)
    row = self.brachy_table_01.currentRow()
    if pts is None or not 0 <= row < len(pts):
        QMessageBox.information(self, "Delete point", "Select a channel point (table row) first.")
        return
    push_undo(self, _plan_channels(self))
    dwell_info = ch.get('DwellInfo')
    if valid_dwells(dwell_info) and 0 < row < len(pts) - 1:
        if _hold_idd(self):
            dwell_info[:] = keep_idd(dwell_info, pts[:, :3], np.delete(pts[:, :3], row, axis=0))
        else:
            dwell_info[:] = remap_dwells_after_delete(dwell_info, pts[:, :3], row)
    ch['ChPos'] = np.delete(pts, row, axis=0)
    commit_channel_edit(self, select_row=min(row, len(pts) - 2))


def on_brachy_new_catheter_toggled(self, checked):
    """New / Stop button: start a catheter whose points are clicked on the images, or finish it."""
    if checked:
        if not _start_new_catheter(self):
            _set_checked(getattr(self, 'brachy_new_catheter_btn', None), False)
    else:
        _stop_new_catheter(self)
    update_new_catheter_button(self)


def _start_new_catheter(self):
    """New: an empty catheter (selected, listed in the table); clicks on the images add its points."""
    channels = _plan_channels(self)
    if channels is None:
        QMessageBox.warning(self, "Warning", "No brachy plan loaded.")
        return False
    _end_drag(self)
    for _name, attr in TOOL_BUTTONS:  # a left click now adds points
        _set_checked(getattr(self, attr, None), False)
    # applicator fields of the selected catheter (none in a new plan)
    template = _selected_channel(self, channels) or (channels[-1] if channels else {})
    push_undo(self, channels)
    self._brachy_new_snap = self._brachy_undo[-1][1]
    self._brachy_new_ch = new_channel(template, next_channel_number(channels))
    channels.append(self._brachy_new_ch)
    _set_channel_count(self, len(channels), len(channels))
    _show_for_editing(self, None, points=True)
    if self.brachy_combobox_01.currentText() != "Channels":
        self.brachy_combobox_01.setCurrentText("Channels")  # refreshes the table and views
    else:
        commit_channel_edit(self)
    return True


def _stop_new_catheter(self):
    """Stop: the new catheter is done; without points it is dropped again."""
    ch = catheter_being_drawn(self)
    snap = getattr(self, '_brachy_new_snap', None)
    self._brachy_new_ch = None
    self._brachy_new_snap = None
    _end_drag(self)
    if ch is None:
        return
    if len(ch['ChPos']):
        commit_channel_edit(self)  # redraw without the new-catheter highlight
        return
    stack = getattr(self, '_brachy_undo', None) or []
    if stack and stack[-1][1] is snap:
        brachy_undo(self)  # nothing was clicked: back to before New
        return
    channels = _plan_channels(self)
    idx = next(i for i, c in enumerate(channels) if c is ch)
    channels.pop(idx)
    _set_channel_count(self, len(channels), min(idx + 1, len(channels)))
    commit_channel_edit(self)


def update_new_catheter_button(self):
    """New / Stop text, color and tooltip; back to New when the new catheter is gone (undo, delete)."""
    btn = getattr(self, 'brachy_new_catheter_btn', None)
    if btn is None:
        return
    active = catheter_being_drawn(self) is not None
    if not active:
        self._brachy_new_ch = None
    _set_checked(btn, active)
    text, style, tip = STOP_CATHETER_BUTTON if active else NEW_CATHETER_BUTTON
    btn.setText(text)
    from fcn_create_gui.brachy_widgets import colored_button_style
    btn.setStyleSheet(colored_button_style(style))
    btn.setToolTip(tip)


def _add_clicked_point(self, view, interactor, ch):
    """
    New catheter: add a point where the image was clicked (on the current slice of
    that view). It follows the mouse until the button is released.
    """
    channels = _plan_channels(self)
    x, y = interactor.GetEventPosition()
    mouse = _event_world_xy(_renderer(self, view), x, y)
    ipp, height = _view_geometry(self)
    push_undo(self, channels)
    ch['ChPos'] = np.vstack((ch['ChPos'][:, :3], point_from_view_xy(view, mouse, _slice_point(self), ipp, height))).astype(np.float32)
    j = len(ch['ChPos']) - 1
    self._brachy_drag = {'tool': 'move', 'view': view, 'channels': channels, 'ch': ch, 'j': j,
                         'P0': ch['ChPos'].astype(float), 'mouse0': mouse, 'grab': np.zeros(2),
                         'undo': None, 'dwell0': None, 'moved': True, 'last_draw': 0.0}
    self._text_dragging = True
    QApplication.setOverrideCursor(Qt.CrossCursor)
    refresh_brachy_overlays(self)


def brachy_delete_catheter(self):
    """Delete the selected catheter (the last one too: a plan can have none, as a new plan)."""
    channels = _plan_channels(self)
    if channels is None:
        QMessageBox.warning(self, "Warning", "No brachy plan loaded.")
        return
    idx = self.brachy_spinBox_01.value() - 1
    if not 0 <= idx < len(channels):
        QMessageBox.warning(self, "Warning", "Invalid channel selected.")
        return
    _end_drag(self)
    push_undo(self, channels)
    channels.pop(idx)
    _set_channel_count(self, len(channels), min(idx + 1, len(channels)))
    commit_channel_edit(self)


def brachy_duplicate_catheter(self):
    """Copy the selected catheter (points, dwell positions, times) to a new catheter, which is selected."""
    _end_drag(self)
    if catheter_being_drawn(self) is not None:
        self.brachy_new_catheter_btn.setChecked(False)  # Stop adding points first
    ch = _plan_selected_channel(self)
    if ch is None:
        return
    channels = _plan_channels(self)
    k = next(i for i, c in enumerate(channels) if c is ch)
    push_undo(self, channels)
    copy = {key: (val.copy() if isinstance(val, np.ndarray) else val) for key, val in ch.items()}
    copy.update({'ChannelNumber': next_channel_number(channels), 'ReferencedROINumber': 'N/A', 'Visible': True})
    if str(ch.get('CatheterName') or '').strip():
        copy['CatheterName'] = f"{catheter_name(ch, k)} copy"
    channels.append(copy)
    _set_channel_count(self, len(channels), len(channels))
    commit_channel_edit(self)


def brachy_zero_catheter_times(self):
    """Set the dwell times of the selected catheter to 0 s."""
    ch = _plan_selected_channel(self)
    if ch is None:
        return
    if not valid_dwells(ch.get('DwellInfo')):
        QMessageBox.information(self, "Dwell times", "The selected catheter has no dwell positions.")
        return
    push_undo(self, _plan_channels(self))
    ch['DwellInfo'][:, 2] = 0.0
    commit_channel_edit(self)


def brachy_zero_all_times(self):
    """Set the dwell times of all catheters to 0 s."""
    channels = _plan_channels(self)
    if channels is None:
        QMessageBox.warning(self, "Warning", "No brachy plan loaded.")
        return
    with_dwells = [ch for ch in channels if valid_dwells(ch.get('DwellInfo'))]
    if not with_dwells:
        QMessageBox.information(self, "Dwell times", "No catheter has dwell positions.")
        return
    push_undo(self, channels)
    for ch in with_dwells:
        ch['DwellInfo'][:, 2] = 0.0
    commit_channel_edit(self)


def update_brachy_edit_buttons(self):
    """
    The edit tools and the buttons acting on the selected catheter need one (none in a new
    plan, none while the table lists the reference points); Add / Delete point need the
    channel points in the table; New needs a plan.
    """
    combo = getattr(self, 'brachy_combobox_01', None)
    if combo is None:
        return
    mode = combo.currentText()
    channels = _plan_channels(self)
    catheter = mode != "Ref. Points" and _selected_channel(self, channels) is not None
    for _name, attr in TOOL_BUTTONS:
        btn = getattr(self, attr, None)
        if btn is not None:
            btn.setEnabled(catheter)
    for name in ('brachy_add_point_btn', 'brachy_del_point_btn'):
        btn = getattr(self, name, None)
        if btn is not None:
            btn.setEnabled(catheter and mode == "Channels")
    for name in ('brachy_dup_catheter_btn', 'brachy_del_catheter_btn', 'brachy_set_dwells_btn', 'brachy_zero_catheter_btn'):
        btn = getattr(self, name, None)
        if btn is not None:
            btn.setEnabled(catheter)
    for name in ('brachy_new_catheter_btn', 'brachy_zero_all_btn'):
        btn = getattr(self, name, None)
        if btn is not None:
            btn.setEnabled(channels is not None and (name == 'brachy_new_catheter_btn' or bool(channels)))
    update_undo_button(self)
    update_new_catheter_button(self)


def _show_for_editing(self, ch, points):
    """
    Show what is edited: the Catheters overlay, catheter 'ch' (ticked in the list) and,
    when 'points' or with the path hidden too, the catheter points.
    """
    if _overlay_channels(self) is None:
        return  # no plan on the images (switching the overlay on would only warn)
    if ch is not None and not channel_visible(ch):
        ch['Visible'] = True
        from fcn_display.brachy_tree import refresh_brachy_tree
        refresh_brachy_tree(self)
    names = ['display_brachy_channel_overlay']
    if points or not _checked(self, 'brachy_show_ch_path'):
        names.append('brachy_show_ch_points')
    for name in names:
        box = getattr(self, name, None)
        if box is not None and not box.isChecked():
            box.setChecked(True)


def on_brachy_tool_toggled(self, name, checked):
    """The edit tools work like radio buttons that can all be off (left-drag is then window/level)."""
    if checked:
        if catheter_being_drawn(self) is not None:
            self.brachy_new_catheter_btn.setChecked(False)  # Stop: clicks no longer add points
        for other, attr in TOOL_BUTTONS:
            if other != name:
                _set_checked(getattr(self, attr, None), False)
        # the tools act on the selected catheter: show it
        _show_for_editing(self, _selected_channel(self, _overlay_channels(self)), points=(name == 'move'))
    _end_drag(self)
    refresh_brachy_overlays(self)


def on_brachy_edit_context_changed(self):
    """Tab or table selection changed: update the edit highlight."""
    if brachy_tool(self) is not None:
        refresh_brachy_overlays(self)


# ---------------------------------------------------------------------------
# Mouse dragging
# ---------------------------------------------------------------------------
def add_brachy_edit_observers(self):
    """
    Mouse observers for the edit tools. Priority 1 runs them before the
    window/level handlers (priority 0), which skip while self._text_dragging is set.
    """
    self._brachy_drag = None
    for view, attr in VIEW_WIDGETS:
        widget = getattr(self, attr, None)
        if widget is None:
            continue
        widget.AddObserver("LeftButtonPressEvent", lambda caller, event, v=view: on_brachy_edit_press(self, v, caller), 1.0)
        widget.AddObserver("MouseMoveEvent", lambda caller, event, v=view: on_brachy_edit_move(self, v, caller), 1.0)
        widget.AddObserver("LeftButtonReleaseEvent", lambda caller, event, v=view: on_brachy_edit_release(self, v, caller), 1.0)


def on_brachy_edit_press(self, view, interactor):
    if getattr(self, '_brachy_drag', None) is not None:
        return
    new = catheter_being_drawn(self)
    if new is not None:
        if brachy_tab_active(self) and _has_image(self):
            _add_clicked_point(self, view, interactor, new)
        return
    if not brachy_edit_active(self):
        return
    tool = brachy_tool(self)
    channels = _overlay_channels(self)
    ch = _selected_channel(self, channels)
    pts = _channel_points(ch)
    if pts is None or len(pts) == 0:
        return

    renderer = _renderer(self, view)
    x, y = interactor.GetEventPosition()
    mouse = _event_world_xy(renderer, x, y)
    ipp, height = _view_geometry(self)
    xy = view_xy(view, pts[:, :3], ipp, height)
    radius = self.dw_ch_point_size.value() / 2
    tol = max(1.5 * radius, np.linalg.norm(_event_world_xy(renderer, x + GRAB_TOL_PX, y) - mouse))
    j = None
    if tool == 'move':
        axis = NORMAL_AXIS[view]
        j = pick_point(np.linalg.norm(xy - mouse, axis=1), pts[:, axis], _slice_point(self)[axis], tol, radius)
        if j is None:
            return  # not on a point: left-drag stays window/level
    elif distance_to_path_2d(mouse, xy) > tol:
        return  # not on the catheter

    P0 = pts[:, :3].astype(float)
    drag = {'tool': tool, 'view': view, 'channels': channels, 'ch': ch, 'j': j, 'P0': P0, 'mouse0': mouse,
            'undo': snapshot_channels(channels), 'dwell0': None, 'moved': False, 'last_draw': 0.0}
    dwell_info = ch.get('DwellInfo')
    if valid_dwells(dwell_info):
        drag['dwell0'] = dwell_info.copy()
        if tool == 'move' and len(pts) >= 2:
            drag['seg'], drag['t'], drag['attached'] = attach_dwells(dwell_info, P0)
    if tool == 'move':
        drag['grab'] = xy[j] - mouse
    elif tool == 'rotate':
        drag['pivot'] = (P0.min(axis=0) + P0.max(axis=0)) / 2  # centre of the catheter
        drag['pivot_xy'] = view_xy(view, drag['pivot'], ipp, height)[0]
        drag['angle0'] = _angle(mouse - drag['pivot_xy'])
    self._brachy_drag = drag
    self._text_dragging = True
    QApplication.setOverrideCursor(TOOL_CURSORS[tool])
    if j is not None and self.brachy_combobox_01.currentText() == "Channels":
        # the redraw below already shows the new highlight
        self.brachy_table_01.blockSignals(True)
        self.brachy_table_01.selectRow(j)
        self.brachy_table_01.blockSignals(False)
    refresh_brachy_overlays(self)


def on_brachy_edit_move(self, view, interactor):
    drag = getattr(self, '_brachy_drag', None)
    if drag is None or drag['view'] != view:
        return
    pts = drag['ch'].get('ChPos')
    P0, dwell0 = drag['P0'], drag['dwell0']
    if not isinstance(pts, np.ndarray) or pts.shape[0] != len(P0):
        _end_drag(self)  # channel replaced while dragging
        return

    x, y = interactor.GetEventPosition()
    mouse = _event_world_xy(_renderer(self, view), x, y)
    if not drag['moved']:
        if np.allclose(mouse, drag['mouse0']):
            return
        push_undo(self, drag['channels'], drag['undo'])
        drag['moved'] = True

    dwells = None
    if drag['tool'] == 'move':
        ipp, height = _view_geometry(self)
        j = drag['j']
        pts[j, :3] = point_from_view_xy(view, mouse + drag['grab'], P0[j], ipp, height)
        if dwell0 is not None and len(P0) >= 2:
            if _hold_idd(self):
                dwells = keep_idd(dwell0, P0, pts[:, :3])
            else:
                dwells = follow_path(dwell0, P0, pts[:, :3], drag['seg'], drag['t'], drag['attached'])
    elif drag['tool'] == 'translate':
        shift = view_translation(view, mouse - drag['mouse0'])
        pts[:, :3] = P0 + shift
        if dwell0 is not None:
            dwells = dwell0.copy()
            dwells[:, 3:6] = dwell0[:, 3:6] + shift
    else:
        rot = view_rotation(view, _angle(mouse - drag['pivot_xy']) - drag['angle0'])
        pivot = drag['pivot']
        pts[:, :3] = pivot + (P0 - pivot) @ rot.T
        if dwell0 is not None:
            dwells = dwell0.copy()
            dwells[:, 3:6] = pivot + (dwell0[:, 3:6] - pivot) @ rot.T
            if dwells.shape[1] >= 9:
                dwells[:, 6:9] = dwell0[:, 6:9] @ rot.T
    dwell_info = drag['ch'].get('DwellInfo')
    if dwells is not None and isinstance(dwell_info, np.ndarray) and dwell_info.shape == dwells.shape:
        dwell_info[:] = dwells

    now = time.perf_counter()
    if now - drag['last_draw'] >= DRAG_REDRAW_INTERVAL:
        drag['last_draw'] = now
        refresh_brachy_overlays(self)


def on_brachy_edit_release(self, view, interactor):
    drag = getattr(self, '_brachy_drag', None)
    if drag is None:
        return
    _end_drag(self)
    if drag['moved']:
        commit_channel_edit(self, select_row=drag['j'])
    else:
        refresh_brachy_overlays(self)


def _end_drag(self):
    if getattr(self, '_brachy_drag', None) is None:
        return
    self._brachy_drag = None
    self._text_dragging = False
    QApplication.restoreOverrideCursor()
