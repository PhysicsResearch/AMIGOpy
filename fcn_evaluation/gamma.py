# -*- coding: utf-8 -*-
"""
gamma.py - gamma index of an evaluated dose against a reference dose (Evaluation > Gamma)
=======================================================================================
Gamma (Low et al. 1998) of each reference point with a dose above the threshold:

    gamma(r) = min over r' of sqrt(|r' - r|^2 / DTA^2 + (D_eval(r') - D_ref(r))^2 / dD^2)

dD = DD % of the normalization dose (global) or of D_ref(r) (local). The evaluated dose is
interpolated (trilinear, by patient position) on its own grid, so it needs no resampling; r' runs
over shells of growing radius (steps of DTA / fraction, points on the shell spaced about one step)
up to max_gamma x DTA, and a point stops searching once the shell distance alone exceeds its best
gamma. 3D searches in the volume, 2D in the plane of the evaluation grid.

Grids are geom = (ImagePositionPatient, (ps_col, ps_row, st), (n_slices, n_rows, n_cols)) with
volumes stored as AMIGOpy stores them: (slices, rows, columns), rows flipped (stored row r is DICOM
row n_rows - 1 - r; ImagePositionPatient is the centre of the voxel with the lowest x, y, z).
"""
import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from scipy.ndimage import map_coordinates

PLANES = ("axial", "coronal", "sagittal")
# in-plane search directions (DICOM x, y, z) of a 2D gamma
PLANE_AXES = {"axial": ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
              "coronal": ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
              "sagittal": ((0.0, 1.0, 0.0), (0.0, 0.0, 1.0))}
NOT_EVALUATED = -1.0
BATCH_POINTS = 1_000_000
WORKERS = max(1, min(16, (os.cpu_count() or 2) - 1))   # threads: map_coordinates and numpy release the GIL
PARALLEL_POINTS = 20_000


class GammaCancelled(Exception):
    pass


# ----------------------------------------------------------------------------
# Grids
# ----------------------------------------------------------------------------
def index_coords(points, geom):
    """(slice, stored row, column) float indices of DICOM points (N, 3), as AMIGOpy stores volumes."""
    (x0, y0, z0), (psc, psr, st), (_, nr, _) = geom
    points = np.asarray(points, dtype=np.float64)
    return np.stack(((points[:, 2] - z0) / st, (nr - 1) - (points[:, 1] - y0) / psr, (points[:, 0] - x0) / psc))


def voxel_points(indices, geom):
    """DICOM points (N, 3) of voxel indices (slices, stored rows, columns)."""
    (x0, y0, z0), (psc, psr, st), (_, nr, _) = geom
    s, r, c = (np.asarray(a, dtype=np.float64) for a in indices)
    return np.column_stack((x0 + c * psc, y0 + (nr - 1 - r) * psr, z0 + s * st))


def sample(volume, geom, points):
    """Trilinear values of a volume at DICOM points; NaN beyond half a voxel outside it."""
    idx = index_coords(points, geom)
    shape = np.asarray(volume.shape, dtype=np.float64)[:, None]
    inside = np.all((idx >= -0.5) & (idx <= shape - 0.5), axis=0)
    out = np.full(idx.shape[1], np.nan)
    if inside.any():
        out[inside] = map_coordinates(volume, idx[:, inside], order=1, mode="nearest", prefilter=False)
    return out


def resample(volume, geom, new_geom):
    """A volume on another grid (trilinear, NaN outside), slice by slice."""
    _, _, (ns, nr, nc) = new_geom
    out = np.empty((ns, nr, nc), np.float32)
    r, c = np.meshgrid(np.arange(nr), np.arange(nc), indexing="ij")
    for s in range(ns):
        pts = voxel_points((np.full(r.size, s), r.ravel(), c.ravel()), new_geom)
        out[s] = sample(volume, geom, pts).reshape(nr, nc)
    return out


def regular_grid(geom, spacing):
    """A grid of 'spacing' mm over the voxel centres of geom (same first voxel centre)."""
    ipp, (psc, psr, st), (ns, nr, nc) = geom
    n = tuple(int(np.floor((m - 1) * p / spacing + 1e-9)) + 1 for m, p in ((ns, st), (nr, psr), (nc, psc)))
    # the lowest y stays at the voxel centre of the reference with the lowest y
    return tuple(ipp), (spacing, spacing, spacing), n


def plane_grid(geom, plane, position, spacing=None):
    """
    2D evaluation grid: the plane of geom nearest to 'position' (DICOM mm along the plane normal:
    z axial, y coronal, x sagittal), as a geom with one voxel across the plane; in-plane spacing
    'spacing' (mm) or that of geom. None if the plane misses the volume.
    """
    (x0, y0, z0), (psc, psr, st), (ns, nr, nc) = geom
    if plane == "axial":
        k = int(np.round((position - z0) / st))
        if not 0 <= k < ns:
            return None
        new = ((x0, y0, z0 + k * st), (psc, psr, st), (1, nr, nc))
    elif plane == "coronal":
        j = int(np.round((position - y0) / psr))           # DICOM row
        if not 0 <= j < nr:
            return None
        new = ((x0, y0 + j * psr, z0), (psc, psr, st), (ns, 1, nc))
    else:
        k = int(np.round((position - x0) / psc))
        if not 0 <= k < nc:
            return None
        new = ((x0 + k * psc, y0, z0), (psc, psr, st), (ns, nr, 1))
    if spacing:
        ipp, sp, n = new[0], list(new[1]), list(new[2])
        # in-plane axes: (shape index (slices, rows, columns), spacing index (column, row, slice))
        for i_n, i_sp in {"axial": ((1, 1), (2, 0)), "coronal": ((0, 2), (2, 0)), "sagittal": ((0, 2), (1, 1))}[plane]:
            n[i_n] = int(np.floor((n[i_n] - 1) * sp[i_sp] / spacing + 1e-9)) + 1
            sp[i_sp] = spacing
        new = (ipp, tuple(sp), tuple(n))
    return new


# ----------------------------------------------------------------------------
# Gamma search
# ----------------------------------------------------------------------------
def shell_offsets(distance, step, axes=None):
    """
    Offsets (M, 3) mm at 'distance' from a point, about 'step' apart: on a sphere (3D, Fibonacci
    points) or on a circle in the plane of two unit vectors 'axes' (2D); the point itself at 0.
    """
    if distance <= 0:
        return np.zeros((1, 3))
    if axes is None:
        n = max(6, int(np.ceil(4.0 * np.pi * distance * distance / (step * step))))
        k = np.arange(n) + 0.5
        polar = np.arccos(1.0 - 2.0 * k / n)
        azimuth = np.pi * (1.0 + 5.0 ** 0.5) * k
        return distance * np.column_stack((np.cos(azimuth) * np.sin(polar), np.sin(azimuth) * np.sin(polar),
                                           np.cos(polar)))
    u, v = (np.asarray(a, dtype=np.float64) for a in axes)
    n = max(4, int(np.ceil(2.0 * np.pi * distance / step)))
    a = 2.0 * np.pi * np.arange(n) / n
    return distance * (np.cos(a)[:, None] * u + np.sin(a)[:, None] * v)


def gamma_search(points, ref_dose, eval_volume, eval_geom, tolerance, dta, max_gamma=2.0, fraction=10,
                 axes=None, progress=None, batch=BATCH_POINTS):
    """
    Gamma of reference points (N, 3, DICOM mm) with doses ref_dose and dose tolerances 'tolerance'
    (Gy, per point) against an evaluated dose: shells up to max_gamma x DTA in steps of DTA /
    fraction (beyond DTA, where gamma > 1 anyway, the points of a shell are spaced in proportion to
    its radius). inf where no agreement was found within max_gamma. progress(fraction done) may
    return False to cancel (GammaCancelled).
    """
    ref_dose = np.asarray(ref_dose, dtype=np.float64)
    tolerance = np.broadcast_to(np.asarray(tolerance, dtype=np.float64), ref_dose.shape)
    step = dta / float(fraction)
    radii = np.arange(0.0, max_gamma * dta + 0.5 * step, step)
    _, (psc, psr, st), _ = eval_geom
    # index space of the evaluated dose, padded by one voxel (edge values; NaN beyond: no dose there)
    base = index_coords(points, eval_geom) + 1.0
    padded = np.pad(np.asarray(eval_volume, dtype=np.float32), 1, mode="edge")
    to_index = np.array([[0.0, 0.0, 1.0 / st], [0.0, -1.0 / psr, 0.0], [1.0 / psc, 0.0, 0.0]])   # (x, y, z) mm -> (s, r, c)
    g2 = np.full(len(ref_dose), np.inf)
    pool = ThreadPoolExecutor(WORKERS) if WORKERS > 1 and len(ref_dose) >= PARALLEL_POINTS else None
    hopeless = _beyond_local_range(padded, base, (psc, psr, st), ref_dose, tolerance, max_gamma * dta, max_gamma)
    g2[hopeless] = np.inf
    todo = ~hopeless
    try:
        for i_radius, d in enumerate(radii):
            dist2 = (d / dta) ** 2
            live = np.flatnonzero(todo & (g2 > dist2))     # a closer agreement is still possible
            if live.size == 0:
                break
            # beyond DTA only failing points search (gamma > 1): points on the shell spaced step x d / DTA
            steps = to_index @ shell_offsets(d, step * max(1.0, d / dta), axes).T     # (3, M) index offsets
            args = (base[:, live], ref_dose[live], tolerance[live], g2[live])
            if pool is None or live.size < PARALLEL_POINTS:
                g2[live] = _shell_best(padded, steps, dist2, batch, *args)
            else:                                      # chunks of points in threads
                parts = np.array_split(np.arange(live.size), WORKERS)
                futures = [pool.submit(_shell_best, padded, steps, dist2, max(1, batch // WORKERS),
                                       *(a[..., part] for a in args)) for part in parts]
                g2[live] = np.concatenate([f.result() for f in futures])
            if progress is not None and progress((i_radius + 1) / len(radii)) is False:
                raise GammaCancelled()
    finally:
        if pool is not None:
            pool.shutdown()
    return np.sqrt(g2)


def _shell_best(padded, steps, dist2, batch, coords, ref, tol, best):
    """Best squared gamma of points (index coords) over the offsets of one shell (index steps), in batches."""
    per_batch = max(1, batch // max(1, coords.shape[1]))
    for j in range(0, steps.shape[1], per_batch):
        off = steps[:, j:j + per_batch]
        ev = map_coordinates(padded, (coords[:, None, :] + off[:, :, None]).reshape(3, -1), order=1,
                             mode="constant", cval=np.nan, prefilter=False)
        cand = dist2 + ((ev.reshape(off.shape[1], -1) - ref) / tol) ** 2
        best = np.minimum(best, np.where(np.isnan(cand), np.inf, cand).min(axis=0))
    return best


def _beyond_local_range(padded, coords, spacing, ref_dose, tolerance, radius, max_gamma):
    """
    Points whose dose is further than max_gamma tolerances from every evaluated dose within the
    search radius (a box around it): their gamma is above max_gamma, no search needed.
    """
    from scipy.ndimage import maximum_filter, minimum_filter
    if not len(ref_dose):
        return np.zeros(0, bool)
    half = np.array([int(np.ceil(radius / p)) + 1 for p in spacing[::-1]])     # voxels: slices, rows, columns
    near = np.rint(coords).astype(np.intp)
    lo = np.maximum(near.min(axis=1) - half, 0)
    hi = np.minimum(near.max(axis=1) + half + 1, padded.shape)
    if np.any(hi <= lo):
        return np.zeros(len(ref_dose), bool)
    box = padded[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]          # the points and their search boxes
    size = tuple(int(2 * h + 1) for h in half)
    high = maximum_filter(box, size=size, mode="nearest")
    low = minimum_filter(box, size=size, mode="nearest")
    near = tuple(np.clip(n - l, 0, m - 1) for n, l, m in zip(near, lo, box.shape))
    margin = max_gamma * tolerance
    return (ref_dose > high[near] + margin) | (ref_dose < low[near] - margin)


def gamma_stats(gamma, max_gamma):
    """Pass rate (%, gamma <= 1), mean, 95th percentile and maximum (capped at max_gamma), points."""
    gamma = np.asarray(gamma, dtype=np.float64)
    if gamma.size == 0:
        return {"pass_rate": float("nan"), "mean": float("nan"), "gamma95": float("nan"), "max": float("nan"),
                "points": 0, "capped": False}
    capped = np.minimum(gamma, max_gamma)
    return {"pass_rate": float(100.0 * np.mean(gamma <= 1.0)), "mean": float(capped.mean()),
            "gamma95": float(np.percentile(capped, 95)), "max": float(capped.max()),
            "points": int(gamma.size), "capped": bool(np.any(gamma >= max_gamma))}


def crop_box(mask):
    """(slices, rows, columns) slices of the bounding box of a mask (None if empty)."""
    idx = np.nonzero(mask)
    if not idx[0].size:
        return None
    return tuple(slice(int(a.min()), int(a.max()) + 1) for a in idx)


def crop_geom(geom, box):
    """Geometry of a box (crop_box) of a grid; rows stored flipped: the last row of the box has the lowest y."""
    (x0, y0, z0), sp, (_, nr, _) = geom
    psc, psr, st = sp
    return ((x0 + box[2].start * psc, y0 + (nr - box[1].stop) * psr, z0 + box[0].start * st), sp,
            (box[0].stop - box[0].start, box[1].stop - box[1].start, box[2].stop - box[2].start))


def gamma_analysis(ref_volume, ref_geom, eval_volume, eval_geom, criteria, plane=None, plane_position=None,
                   resolution=None, norm_dose=None, max_gamma=2.0, fraction=10, progress=None):
    """
    Gamma of an evaluated dose against a reference for each criterion {'dd' (%), 'dta' (mm),
    'threshold' (% of the normalization dose), 'local' (bool)}.
    3D (plane None) on the reference grid or a grid of 'resolution' mm; 2D on the reference plane
    nearest to plane_position (plane 'axial', 'coronal' or 'sagittal'). norm_dose: Gy, default the
    maximum of the reference volume. Returns {'geom', 'norm_dose', 'outside', 'results': [{'criterion',
    'gamma' (volume of the evaluated box, NOT_EVALUATED where not evaluated), 'geom' (of that box),
    'stats'}]}; progress(criterion index, fraction) may return False to cancel.
    """
    if plane is None:
        geom = regular_grid(ref_geom, resolution) if resolution else ref_geom
        axes = None
    else:
        geom = plane_grid(ref_geom, plane, plane_position, resolution)
        if geom is None:
            raise ValueError("the plane shown does not cross the reference dose")
        axes = PLANE_AXES[plane]
    values = ref_volume if geom == ref_geom else resample(ref_volume, ref_geom, geom)
    if norm_dose is None:
        norm_dose = float(np.nanmax(ref_volume))
    if not norm_dose or norm_dose <= 0:
        raise ValueError("the normalization dose is 0")
    results, outside = [], 0
    for i, crit in enumerate(criteria):
        mask = np.isfinite(values) & (values > 0) & (values >= crit["threshold"] / 100.0 * norm_dose)
        idx = np.nonzero(mask)
        points = voxel_points(idx, geom)
        inside = np.isfinite(sample(eval_volume, eval_geom, points))     # evaluated dose there
        outside = int((~inside).sum())
        idx = tuple(a[inside] for a in idx)
        points = points[inside]
        ref = np.asarray(values[idx], dtype=np.float64)
        tol = crit["dd"] / 100.0 * (ref if crit["local"] else norm_dose)
        report = None if progress is None else (lambda f, k=i: progress(k, f))
        gamma = gamma_search(points, ref, eval_volume, eval_geom, tol, crit["dta"], max_gamma, fraction, axes,
                             report) if len(points) else np.empty(0)
        evaluated = np.zeros(values.shape, bool)
        evaluated[idx] = True
        box = crop_box(evaluated)
        if box is None:
            vol, box_geom = np.full((1, 1, 1), NOT_EVALUATED, np.float32), geom
        else:
            full = np.full(values.shape, NOT_EVALUATED, np.float32)
            full[idx] = np.minimum(gamma, max_gamma)
            vol, box_geom = np.ascontiguousarray(full[box]), crop_geom(geom, box)
        results.append({"criterion": dict(crit), "gamma": vol, "geom": box_geom,
                        "stats": gamma_stats(gamma, max_gamma)})
    return {"geom": geom, "norm_dose": float(norm_dose), "outside": outside, "results": results}
