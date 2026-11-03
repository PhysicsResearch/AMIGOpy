"""
TR cards of the dwell positions (fcn_mcnp/mcnp_input.py, the SSR source): where the recorded
source (phase space on the capsule surfaces) is placed and how it is turned.

MCNP TRn card (manual): trN O1 O2 O3 xx' yx' zx' xy' yy' zy' xz' yz' zz' (m = 1, omitted).
O is the origin of the source frame (the dwell position) in the problem (MCNP axes, cm); each
triple is one axis of the source frame in the problem axes (xx' = cos(x, x'), yx' = cos(y, x'), ...):
x' first, then y', then z'. A recorded particle at r' starts at O + R r', R with columns x', y', z'.

The source models are recorded along x (cx / px / kx surfaces): x' is the source axis, the distal
end at -x', the cable at +x'. So x' points away from the catheter tip (its first point), towards the
connector. Plans may store the source orientation the other way (Varian: towards the tip); its
sign is checked against the catheter path. y', z': the smallest rotation taking MCNP X onto x'.
"""
import re

import numpy as np

from fcn_display.brachy_channel_edit import DWELL_PATH_TOL_MM, project_on_polyline

MAX_TR = 999                    # TRn numbers: 1..999
POSITION_DECIMALS = 5           # cm (0.1 um), as before
COSINE_DECIMALS = 7             # MCNP warns above ~0.001 rad of non-orthogonality
# How each dwell's source axis was found (dir_basis)
PLAN, PLAN_REVERSED, PATH, DWELLS, NONE = "plan", "plan reversed", "path", "dwells", "none"


def mcnp_vector(v):
    """MCNP axes (X, Y, Z) of a DICOM vector (x, y, z): X = x, Y = z, Z = -y (mcnp_input.to_mcnp_axes)."""
    v = np.asarray(v, dtype=float)
    return np.array([v[0], v[2], 0.0 - v[1]])


def dicom_vector(v):
    """DICOM (x, y, z) of an MCNP vector (X, Y, Z): the inverse of mcnp_vector."""
    v = np.asarray(v, dtype=float)
    return np.array([v[0], 0.0 - v[2], v[1]])


def smallest_rotation(axis):
    """
    Rotation taking MCNP X onto the unit vector 'axis' by the smallest angle (Rodrigues), columns
    x' (= axis), y', z'. X itself: the identity; -X: half a turn about Z. No axis: the identity.
    """
    a = np.asarray(axis, dtype=float)
    norm = np.linalg.norm(a)
    if not np.isfinite(norm) or norm < 1e-12:
        return np.eye(3)
    a = a / norm
    c = a[0]                                    # X . axis
    if c < -1.0 + 1e-12:
        return np.diag([-1.0, -1.0, 1.0])
    v = np.array([0.0, -a[2], a[1]])            # X x axis
    vx = np.array([[0.0, -v[2], v[1]], [v[2], 0.0, -v[0]], [-v[1], v[0], 0.0]])
    return np.eye(3) + vx + vx @ vx / (1.0 + c)


def _fmt(value, decimals):
    """A number as written in the cards: no -0.0."""
    return f"{round(float(value), decimals) + 0.0:.{decimals}f}"


def tr_card_lines(n, origin_cm, rotation, indent="     "):
    """
    trN over 4 lines: the dwell position (cm), then the source axes x', y', z' of 'rotation'
    (its columns, MCNP axes), one per line, as MCNP reads them (xx' yx' zx' xy' ... zz').
    """
    lines = [f"tr{n} " + " ".join(_fmt(v, POSITION_DECIMALS) for v in origin_cm) + " &"]
    for k, axis in enumerate(np.asarray(rotation, dtype=float).T):
        values = "  ".join(f"{_fmt(v, COSINE_DECIMALS):>10}" for v in axis)
        lines.append(f"{indent}{values}" + (" &" if k < 2 else ""))
    return lines


def path_tangents(xyz, cat_pts, tol=DWELL_PATH_TOL_MM):
    """Unit direction of the catheter path at each dwell, away from the tip (its first point); NaN off the path."""
    xyz = np.asarray(xyz, dtype=float).reshape(-1, 3)
    out = np.full(xyz.shape, np.nan)
    if cat_pts is None or len(cat_pts) < 2 or not len(xyz):
        return out
    pts = np.asarray(cat_pts, dtype=float)[:, :3]
    seg, _, _, dist = project_on_polyline(xyz, pts)
    tangent = pts[seg + 1] - pts[seg]
    norm = np.linalg.norm(tangent, axis=1)
    ok = (dist <= tol) & (norm > 1e-9)
    out[ok] = tangent[ok] / norm[ok, None]
    return out


def _unit_rows(v):
    v = np.asarray(v, dtype=float).reshape(-1, 3)
    norm = np.linalg.norm(v, axis=1)
    ok = np.isfinite(norm) & (norm > 1e-6)
    out = np.full(v.shape, np.nan)
    out[ok] = v[ok] / norm[ok, None]
    return out


def orientation_sign(plan_dirs, tangents):
    """+1 if most plan orientations point away from the tip (dwells on the path), -1 if towards it, None if unknown."""
    ok = np.isfinite(plan_dirs).all(axis=1) & np.isfinite(tangents).all(axis=1)
    if not ok.any():
        return None
    return -1.0 if np.sum(np.sign(np.einsum("ij,ij->i", plan_dirs[ok], tangents[ok]))) < 0 else 1.0


def cable_directions(catheters, tol=DWELL_PATH_TOL_MM):
    """
    Source axis x' (towards the cable, away from the catheter tip) at each dwell, in patient
    coordinates. catheters: [(dwell xyz (M, 3) mm in plan order, plan orientations (M, 3), NaN where
    none, catheter points (N, 3) from the tip or None)]. For each catheter: (directions (M, 3), zero
    where none; bases (M,) PLAN / PLAN_REVERSED / PATH / DWELLS / NONE; sign checked on this
    catheter's path (bool); path tangents (M, 3)).
    - Plan orientation: the TPS's axis, with the sign that makes most of the catheter's dwells on
      its path face away from the tip; a catheter without dwells on its path takes the sign of the
      other catheters, else orientations are taken to point to the tip (Varian; AMIGOpy's TG43).
    - Else the path at the dwell, else the neighbouring dwells (away from the tip when known).
    """
    prepared = []
    for xyz, plan_dirs, cat_pts in catheters:
        xyz = np.asarray(xyz, dtype=float).reshape(-1, 3)
        plan = _unit_rows(plan_dirs) if plan_dirs is not None else np.full(xyz.shape, np.nan)
        tangents = path_tangents(xyz, cat_pts, tol)
        prepared.append((xyz, plan, cat_pts, tangents, orientation_sign(plan, tangents)))
    known = [sign for *_, sign in prepared if sign is not None]
    plan_wide = (-1.0 if sum(known) < 0 else 1.0) if known else -1.0

    out = []
    for xyz, plan, cat_pts, tangents, sign in prepared:
        dirs = np.zeros(xyz.shape)
        bases = np.full(len(xyz), NONE, dtype=object)
        s = sign if sign is not None else plan_wide
        has_plan = np.isfinite(plan).all(axis=1)
        dirs[has_plan] = s * plan[has_plan]
        bases[has_plan] = PLAN if s > 0 else PLAN_REVERSED
        on_path = ~has_plan & np.isfinite(tangents).all(axis=1)
        dirs[on_path] = tangents[on_path]
        bases[on_path] = PATH
        tip = np.asarray(cat_pts, dtype=float)[0, :3] if cat_pts is not None and len(cat_pts) else None
        for k in np.nonzero(bases == NONE)[0]:
            if len(xyz) < 2:
                continue
            v = xyz[k + 1] - xyz[k] if k + 1 < len(xyz) else xyz[k] - xyz[k - 1]
            if tip is not None and np.dot(v, xyz[k] - tip) < 0:
                v = -v                               # away from the tip
            norm = np.linalg.norm(v)
            if norm > 1e-6:
                dirs[k] = v / norm
                bases[k] = DWELLS
        out.append((dirs, bases, sign is not None, tangents))
    return out


_TR_CARD = re.compile(r"^\s{0,4}tr(\d+)\s+(.*)$", re.IGNORECASE)


def parse_tr_cards(lines):
    """{n: values} of the trN cards in input lines ('&' continuations joined, comments skipped)."""
    cards, current = {}, None
    for line in lines:
        text = line.split("$")[0].rstrip()
        if current is None:
            m = _TR_CARD.match(text)
            if not m:
                continue
            current, body = int(m.group(1)), m.group(2)
            cards[current] = []
        elif text[:1].lower() == "c" and (len(text) == 1 or text[1] == " "):
            continue
        else:
            body = text
        cont = body.endswith("&")
        cards[current] += [float(v) for v in body.rstrip("&").split()]
        if not cont:
            current = None
    return cards


def check_tr_cards(lines, dwells):
    """
    The trN cards of 'lines' back in patient coordinates against the dwells (mcnp_input dwell dicts,
    card n = dwell n): dict of the figures, and short report lines (comments) for the input.
    - position: the card's origin (MCNP cm) back in DICOM mm against the plan's dwell position;
    - x' against the catheter path (angle, facing away from the tip) and the plan's orientation;
    - the rotation orthonormal with det +1 (cards with all 9 values).
    """
    cards = parse_tr_cards(lines)
    pos_err, path_angle, facing, on_path, reversed_plan, ortho, dets = [], [], 0, 0, 0, [], []
    missing = []
    for n, d in enumerate(dwells, start=1):
        values = cards.get(n)
        if values is None or len(values) < 3:
            missing.append(n)
            continue
        origin_mm = 10.0 * dicom_vector(values[:3])
        pos_err.append(float(np.linalg.norm(origin_mm - [d["x_mm"], d["y_mm"], d["z_mm"]])))
        if len(values) < 6:
            continue
        x_axis = dicom_vector(values[3:6])
        tangent = np.asarray(d.get("path_dir", (np.nan,) * 3), dtype=float)
        if np.isfinite(tangent).all():
            on_path += 1
            along = float(np.dot(x_axis, tangent))
            facing += along > 0
            path_angle.append(float(np.degrees(np.arccos(min(1.0, abs(along) / max(np.linalg.norm(x_axis), 1e-12))))))
        plan = np.asarray(d.get("plan_dir", (np.nan,) * 3), dtype=float)
        if np.isfinite(plan).all() and float(np.dot(x_axis, plan)) < 0:
            reversed_plan += 1
        if len(values) >= 12:
            rot = np.asarray(values[3:12]).reshape(3, 3).T      # columns x', y', z'
            ortho.append(float(np.abs(rot.T @ rot - np.eye(3)).max()))
            dets.append(float(np.linalg.det(rot)))
    bases = [d.get("dir_basis", NONE) for d in dwells]
    checked = sum(1 for d in dwells if d.get("sign_checked"))
    result = {"dwells": len(dwells), "missing": missing, "max_position_mm": max(pos_err, default=0.0),
              "on_path": on_path, "facing_connector": facing, "max_path_angle_deg": max(path_angle, default=0.0),
              "plan_reversed": reversed_plan, "max_orthogonality": max(ortho, default=0.0),
              "det_min": min(dets, default=1.0), "det_max": max(dets, default=1.0),
              "bases": {b: bases.count(b) for b in (PLAN, PLAN_REVERSED, PATH, DWELLS, NONE) if bases.count(b)},
              "plan_sign_checked": checked}
    report = [f"TR cards back in patient coordinates: {len(dwells)} dwells",
              f"  at the plan positions within {result['max_position_mm']:.5f} mm"]
    if missing:
        report.append(f"  cards missing: {', '.join(map(str, missing[:10]))}")
    report += [f"  x' (source axis, to the cable) faces away from the catheter tip:",
               f"  {facing}/{on_path} dwells on the path, max {result['max_path_angle_deg']:.1f} deg from it",
               f"  plan orientations reversed (they point to the tip): {reversed_plan}",
               f"  source axis from the path: {result['bases'].get(PATH, 0)},"
               f" from neighbouring dwells: {result['bases'].get(DWELLS, 0)}"]
    unchecked = sum(1 for d in dwells if d.get("dir_basis") in (PLAN, PLAN_REVERSED) and not d.get("sign_checked"))
    if unchecked:
        report.append(f"  plan orientation sign not checked (no catheter path): {unchecked}")
    if result["bases"].get(NONE):
        report.append(f"  without direction (identity): {result['bases'][NONE]}")
    if ortho:
        report.append(f"  rotations orthonormal within {result['max_orthogonality']:.1e},")
        report.append(f"  det {result['det_min']:.6f} to {result['det_max']:.6f}")
    return result, report


def check_summary(result):
    """One sentence of a check_tr_cards result (the message after the input is written)."""
    text = (f"TR cards: {result['dwells']} dwells at the plan positions (max {result['max_position_mm']:.4f} mm), "
            f"source axis toward the connector {result['facing_connector']}/{result['on_path']} "
            f"(max {result['max_path_angle_deg']:.1f} deg from the catheter)")
    if result["plan_reversed"]:
        text += f", {result['plan_reversed']} plan orientations reversed"
    return text
