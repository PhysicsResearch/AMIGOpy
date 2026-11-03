# -*- coding: utf-8 -*-
"""
mcnp_import.py - read an MCNP input written by AMIGOpy back into AMIGOpy
=======================================================================

Rebuilds the voxels written to the lattice (the phantom box: the whole image or a part of it)
from an input made by mcnp_input.build_mcnp_cards:

  * the AMIGO reference of the header (mcnp_input.reference_lines): where the written voxels are
    (ImagePositionPatient of the one with the lowest x, y, z, spacing, shape), their indices in
    the image they come from and that image, and the AMIGO ID and name of each MCNP material;
  * the fill of the lattice cell (i = columns, j = rows as AMIGOpy stores them, k = slices);
  * the universe cells (material number and mass density of each universe).

The universe, material and density (g/cm3) maps become a new image series (modality "MCNP") in
the patient / study of the image, with the geometry of the written voxels: on a layer over the
original image, the overlay puts it in place by the patient position.
"""
import os
import re
from array import array

import numpy as np
from PySide6.QtWidgets import QFileDialog, QMessageBox

from fcn_mcnp.mcnp_input import REFERENCE_FORMAT, lattice_axis, mcnp_box, mcnp_sizes, parse_reference

MODALITY = "MCNP"
_COMMENT = re.compile(r"^ {0,4}[cC]( |$)")
_CELL = re.compile(r"^ {0,4}(\d+)\s+(\d+)\s+(-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)\s+(.*)$")
_UNIVERSE = re.compile(r"\bu\s*=\s*(\d+)", re.I)
_MATERIAL_COMMENT = re.compile(r"^[cC]\s+Material\s+(\d+):\s*(.*?)\s*$")
_PLANE = re.compile(r"^\s*(\d+)\s+(p[xyz])\s+(\S+)\s*$", re.I)


def _blocks(lines):
    """Cell and surface cards of an input (after the title card; a blank line ends a block)."""
    blocks, current = [], []
    for line in lines[1:]:
        if line.strip():
            current.append(line)
            continue
        blocks.append(current)
        current = []
        if len(blocks) == 2:
            break
    blocks.append(current)
    return blocks[0], blocks[1] if len(blocks) > 1 else []


def _code(line):
    """A card line without its inline comment ($) and continuation mark (&)."""
    return line.split("$")[0].replace("&", " ")


def lattice_fill(cells):
    """
    Index ranges ((i0, i1), (j0, j1), (k0, k1)) and values (i fastest; 'v Nr' repeats expanded)
    of the fill of the lattice cell (lat=) in the cell cards.
    """
    start = next((k for k, line in enumerate(cells)
                  if not _COMMENT.match(line) and "lat=" in _code(line).lower()), None)
    if start is None:
        raise ValueError("there is no lattice cell (lat=) in the cell cards")

    def tokens():
        for line in cells[start:]:
            if not _COMMENT.match(line):
                yield from _code(line).split()

    it = tokens()
    for tok in it:
        if tok.lower().startswith("fill"):
            break
    else:
        raise ValueError("the lattice cell has no fill")
    head = [t for t in (tok[4:].lstrip("=*"),) if t]   # 'fill=0:9 ...' or 'fill 0:9 ...'
    ranges = []
    while len(ranges) < 3:
        lo, hi = (int(v) for v in (head.pop(0) if head else next(it)).split(":"))
        ranges.append((lo, hi))
    count = int(np.prod([hi - lo + 1 for lo, hi in ranges]))
    values, repeats, total = array("q"), array("q"), 0
    for tok in it:
        if total >= count:
            break
        if tok[-1] in "rR" and tok[:-1].isdigit():
            if not values:
                raise ValueError("the lattice fill starts with a repeat (r)")
            repeats[-1] += int(tok[:-1])
            total += int(tok[:-1])
        else:
            values.append(int(tok))
            repeats.append(1)
            total += 1
    if total < count:
        raise ValueError(f"the lattice fill has {total} values, {count} expected")
    fill = np.repeat(np.frombuffer(values, dtype=np.int64), np.frombuffer(repeats, dtype=np.int64))
    return ranges, fill[:count]


def universe_cells(cells):
    """{universe: (MCNP material number, mass density g/cm3, None if given as atom density)}."""
    out = {}
    for line in cells:
        if _COMMENT.match(line):
            continue
        m = _CELL.match(line)
        if m is None:
            continue
        rest = m.group(4)
        u = _UNIVERSE.search(rest)
        if u is None or "lat" in rest.lower() or int(m.group(2)) == 0:
            continue
        rho = float(m.group(3))
        out[int(u.group(1))] = (int(m.group(2)), -rho if rho < 0 else None)
    return out


def material_comments(lines):
    """{MCNP material number: name} of the 'c Material n: name' comments of the material cards."""
    return {int(m.group(1)): m.group(2) for m in map(_MATERIAL_COMMENT.match, lines) if m}


def plane_surfaces(surfaces):
    """{surface number: value (cm)} of the plane surfaces (px, py, pz)."""
    return {int(m.group(1)): float(m.group(3)) for m in map(_PLANE.match, surfaces) if m}


def parse_mcnp_input(text):
    """
    AMIGO reference, lattice fill as an (i, j, k) array, universes, material names (comments) and
    plane surfaces of an input made by AMIGOpy. ValueError if it cannot be read back.
    """
    lines = text.splitlines()
    ref = parse_reference(lines)
    if ref is None:
        raise ValueError("its header has no AMIGO reference: create the input again with this "
                         "version of AMIGOpy (MonteCarlo > MCNP > Create input)")
    if ref["format"] > REFERENCE_FORMAT:
        raise ValueError(f"its AMIGO reference has format {ref['format']}; this AMIGOpy reads "
                         f"format {REFERENCE_FORMAT}")
    cells, surfaces = _blocks(lines)
    ranges, values = lattice_fill(cells)
    dims = [hi - lo + 1 for lo, hi in ranges]
    ns, nr, nc = ref["shape"]
    if dims != [nc, nr, ns]:
        raise ValueError(f"the lattice fill is {dims[0]} x {dims[1]} x {dims[2]} (i x j x k), the AMIGO "
                         f"reference {nc} x {nr} x {ns} (columns x rows x slices)")
    return {"ref": ref, "fill": values.reshape(dims, order="F"), "universes": universe_cells(cells),
            "material_names": material_comments(lines), "planes": plane_surfaces(surfaces)}


def plane_mismatch(ref, planes, tol_cm=1e-3):
    """
    Phantom box and lattice planes (501-506, 601-606) missing or more than tol_cm (0.01 mm, the
    rounding of lattice_axis) from where the AMIGO reference puts them.
    """
    ns, nr, nc = ref["shape"]
    ps_col, ps_row, st = ref["spacing"]
    x0, y0, z0 = ref["ipp"]
    box = ((x0 - ps_col / 2, x0 + (nc - 0.5) * ps_col), (y0 - ps_row / 2, y0 + (nr - 0.5) * ps_row),
           (z0 - st / 2, z0 + (ns - 0.5) * st))
    expected = {}
    for k, ((lo, _), pitch, n) in enumerate(zip(mcnp_box(box), mcnp_sizes(ps_col, ps_row, st), (nc, ns, nr))):
        expected.update(zip((501 + 2 * k, 502 + 2 * k, 601 + 2 * k, 602 + 2 * k),
                            lattice_axis(lo / 10.0, pitch / 10.0, n)))
    return sorted(n for n, v in expected.items() if n not in planes or abs(planes[n] - v) > tol_cm)


def uncovered_axes(ref, planes):
    """MCNP axes along which the phantom box (501-506) reaches beyond the lattice elements of the fill (601-606)."""
    ns, nr, nc = ref["shape"]
    out = []
    for k, (axis, n) in enumerate(zip("XYZ", (nc, ns, nr))):
        surfaces = [501 + 2 * k, 502 + 2 * k, 601 + 2 * k, 602 + 2 * k]
        if all(s in planes for s in surfaces):
            box0, box1, cell0, cell1 = (planes[s] for s in surfaces)
            if box0 < cell0 or box1 > cell0 + n * (cell1 - cell0):
                out.append(axis)
    return out


def build_maps(parsed, name_to_id):
    """
    Maps of the written voxels as AMIGOpy stores volumes (slices, rows as stored, columns):
    'universes' (int32), 'material' (AMIGO material IDs, int16; -1 for unknown universes) and
    'density' (g/cm3, float32; NaN if unknown), with 'material_used' {ID: name}, the universe
    'table' and 'warnings'. Materials are found by name in the database (name_to_id); the others
    get IDs after the database ones.
    """
    ref = parsed["ref"]
    uni = np.ascontiguousarray(parsed["fill"].transpose(2, 1, 0)).astype(np.int32)
    cells = parsed["universes"]
    names = dict(parsed["material_names"])
    names.update({n: name for n, (_, name) in ref["materials"].items() if name})
    next_id = max(name_to_id.values(), default=-1) + 1
    amigo, missing, atom = {}, [], []

    def material(number):
        """AMIGO ID and name of MCNP material 'number'."""
        nonlocal next_id
        if number not in amigo:
            name = names.get(number, f"MCNP material {number}")
            mid = name_to_id.get(name)
            if mid is None:
                mid, next_id = next_id, next_id + 1
                missing.append(name)
            amigo[number] = (mid, name)
        return amigo[number]

    uniq, inv = np.unique(uni, return_inverse=True)
    mat_lut = np.full(len(uniq), -1, dtype=np.int16)
    den_lut = np.full(len(uniq), np.nan, dtype=np.float32)
    table, unknown = [], []
    for k, u in enumerate(int(v) for v in uniq):
        if u not in cells:
            unknown.append(u)
            continue
        number, rho = cells[u]
        mid, name = material(number)
        mat_lut[k] = mid
        if rho is None:
            atom.append(u)
        else:
            den_lut[k] = rho
        table.append({'universe': u, 'material_index': number, 'material_key': mid, 'material': name,
                      'density': rho})
    inv = inv.reshape(uni.shape)
    warnings = []
    if unknown:
        n_vox = int(np.isin(uni, unknown).sum())
        warnings.append(f"{n_vox} voxels have universes without a cell ({', '.join(map(str, unknown[:8]))}"
                        f"{', ...' if len(unknown) > 8 else ''}): material -1, no density.")
    if missing:
        warnings.append("Not in the material database (new IDs in the material map): " + ", ".join(missing))
    if atom:
        warnings.append(f"{len(atom)} universes have an atom density (no g/cm3): no density there.")
    return {'universes': uni, 'material': mat_lut[inv], 'density': den_lut[inv], 'table': table,
            'material_used': {amigo[n][0]: amigo[n][1] for n in sorted(amigo)}, 'warnings': warnings}


def mcnp_series(path, parsed, maps, series_number):
    """Image series (modality MCNP) of the written voxels: density as the image, the maps as its maps."""
    ref = parsed["ref"]
    ns, nr, nc = maps['universes'].shape
    ps_col, ps_row, st = ref["spacing"]
    name = os.path.splitext(os.path.basename(path))[0]
    source = {'file': path, **{k: ref[k] for k in ('patient', 'study', 'series_uid', 'frame_uid', 'series_number',
                                                   'image_shape', 'image_ipp', 'crop')}}
    meta = {
        'PixelSpacing': [ps_row, ps_col],
        'SliceThickness': st,
        'ImagePositionPatient': list(ref["ipp"]),        # the written voxel with the lowest x, y, z
        'ImageOrientationPatient': "N/A",
        'RescaleSlope': "N/A",
        'RescaleIntercept': "N/A",
        'WindowWidth': "N/A",
        'WindowCenter': "N/A",
        'SeriesDescription': f"MCNP {name}",
        'StudyDescription': '',
        'ImageComments': '',
        'DoseGridScaling': "N/A",
        'AcquisitionNumber': "N/A",
        'Modality': MODALITY,
        'LUTLabel': "N/A",
        'LUTExplanation': "N/A",
        'size': (nc, nr, ns),
        'DataType': 'MCNP',
        'DCM_Info': None,
        'OriginalFilePath': path,
        'FrameOfReferenceUID': ref["frame_uid"] or "N/A",
        'MCNP_reference': source,                        # the image the voxels come from, their crop
    }
    return {
        'SeriesNumber': series_number,
        'metadata': meta,
        'images': {},
        'ImagePositionPatients': [],
        'SliceImageComments': {},
        '3DMatrix': maps['density'],
        'AM_name': None,
        'US_name': None,
        'density_maps': {'mcnp_density': {'3DMatrix': maps['density'], 'type': 'Density', 'source': source}},
        'mat_maps': {'mcnp_materials': {'3DMatrix': maps['material'], 'Material_used': maps['material_used'],
                                        'source': source}},
        'mcnp_lattice_maps': {'mcnp_lattice': {'3DMatrix': maps['universes'], 'universes': maps['table'],
                                               'metadata': {'source': source}}},
    }


def _original_image(self, ref, patient, study):
    """(modality, series) of the loaded image the input was made from (same SeriesInstanceUID), or None."""
    if not ref["series_uid"]:
        return None
    for modality, series_list in (self.medical_image.get(patient, {}).get(study, {}) or {}).items():
        for series in series_list:
            if (series.get('metadata', {}) or {}).get('SeriesInstanceUID') == ref["series_uid"]:
                return modality, series
    return None


def import_summary(self, path, parsed, maps, patient, study):
    ref = parsed["ref"]
    ns, nr, nc = ref["shape"]
    NS, NR, NC = ref["image_shape"]
    c0, c1, r0, r1, s0, s1 = ref["crop"]
    x0, y0, z0 = ref["ipp"]
    ps_col, ps_row, st = ref["spacing"]
    rho = maps['density'][np.isfinite(maps['density'])]
    lines = [f"'{os.path.basename(path)}' was added as MCNP {os.path.splitext(os.path.basename(path))[0]} "
             f"(Patient {patient}, Study {study}, Modality {MODALITY}) with its material map, density map (g/cm3) "
             f"and MCNP lattice map.", "",
             f"Voxels: {nc} x {nr} x {ns} (columns x rows x slices) = columns {c0}-{c1}, rows {r0}-{r1}, "
             f"slices {s0}-{s1} of the {NC} x {NR} x {NS} image.",
             f"First voxel (lowest x, y, z): ({x0:.2f}, {y0:.2f}, {z0:.2f}) mm; spacing {ps_col:.4f} x {ps_row:.4f} "
             f"x {st:.4f} mm.",
             f"{len(maps['material_used'])} materials, {len(maps['table'])} universes"
             + (f", density {rho.min():.3f}-{rho.max():.3f} g/cm3." if rho.size else "."), ""]
    original = _original_image(self, ref, patient, study)
    if original is not None:
        lines.append(f"Original image: {original[0]} series {original[1].get('SeriesNumber')}. On a layer over it, "
                     "the MCNP series is put in place by its patient position.")
    else:
        lines.append(f"The original image (series {ref['series_number'] or '?'}) is not loaded; the MCNP series "
                     "keeps its patient position.")
    mismatch = plane_mismatch(ref, parsed["planes"])
    if mismatch:
        lines.append(f"Surfaces {', '.join(map(str, mismatch))} are not where the AMIGO reference puts them "
                     "(was the input edited?): the maps follow the reference.")
    uncovered = uncovered_axes(ref, parsed["planes"])
    if uncovered:
        lines.append(f"The phantom box reaches beyond the lattice along MCNP {', '.join(uncovered)}: MCNP would "
                     "find points there in lattice elements outside the fill.")
    lines += maps['warnings']
    return "\n".join(lines)


def import_mcnp_input(self, path=None):
    """File > Open > MCNPinp: read an MCNP input made by AMIGOpy; its maps become an MCNP image series. The series (or None)."""
    if path is None:
        path, _ = QFileDialog.getOpenFileName(self, "Import MCNP input", getattr(self, 'last_mcnp_dir', ""),
                                              "MCNP input (*.inp *.i *.txt);;All files (*)")
        if not path:
            return None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            parsed = parse_mcnp_input(f.read())
        df = getattr(self, 'Mat_df', None)
        name_to_id = {} if df is None else {str(n): int(i) for i, n in zip(df.index, df['Name'])}
        maps = build_maps(parsed, name_to_id)
    except (OSError, ValueError) as e:
        QMessageBox.critical(self, "Import MCNP input", f"Could not read {os.path.basename(path)}:\n{e}")
        return None
    self.last_mcnp_dir = os.path.dirname(path)
    ref = parsed["ref"]
    patient, study = ref["patient"] or MODALITY, ref["study"] or MODALITY
    if not isinstance(getattr(self, 'medical_image', None), dict):
        self.medical_image = {}
    series_list = self.medical_image.setdefault(patient, {}).setdefault(study, {}).setdefault(MODALITY, [])
    series = mcnp_series(path, parsed, maps, len(series_list) + 1)
    series_list.append(series)
    from fcn_load.populate_med_image_list import populate_medical_image_tree
    populate_medical_image_tree(self)
    QMessageBox.information(self, "Import MCNP input", import_summary(self, path, parsed, maps, patient, study))
    return series
