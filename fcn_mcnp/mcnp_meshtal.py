# -*- coding: utf-8 -*-
"""
mcnp_meshtal.py - read an MCNP mesh tally output (meshtal) into AMIGOpy (File > Open > MCNPout)
==============================================================================================
Reads the rectangular mesh tallies (FMESH) of a meshtal file by their labels, in any OUT order:
"Mesh Tally Number", "Tally bin boundaries:" with "X / Y / Z direction:" and "Energy bin
boundaries:", then per bin of one axis ("Y bin: a - b") the tables "Tally Results:  X (across) by
Z (down)" and "Relative Errors", or the column format "X  Y  Z  Result  Rel Error".

The mesh is put on the patient as AMIGOpy writes the MCNP input (mcnp_input.to_mcnp_axes: MCNP
X = DICOM x, Y = DICOM z (slices), Z = -DICOM y (rows, anterior up)). Its bins come from the title
of the inputs AMIGOpy writes (line 2 of the meshtal, mcnp_input.mesh_title: FMESH origin and bin
size, source and Sk, input file) when they give the printed boundaries, else from a straight line
through the boundaries (printed with 2 decimals). Each tally becomes an RTDOSE of the study shown,
in Gy with the source and Sk of the title (dose_factor, as MATLAB AMIGO), else as MCNP writes it
(per source particle), and its relative errors an MCNP series, both overlaying the image.
"""
import os
import re

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QProgressDialog

from fcn_mcnp.mcnp_input import SOURCE_DOSE

_PROBID = re.compile(r"^\s*mcnp\w*\s+version\b.*\bprobid\b", re.I)    # the title follows
_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
_TRIPLE = rf"({_NUM}),({_NUM}),({_NUM})"
_TITLE = re.compile(rf"^\s*(?:origin|o)={_TRIPLE}\s+(?:voxel|v)={_TRIPLE}"
                    rf"(?:\s+(\S+)\s+Sk=({_NUM}))?(?:\s+(\S.*?))?\s*$", re.I)
_HISTORIES = re.compile(r"Number of histories used for normalizing tallies\s*=\s*(\S+)", re.I)
_TALLY = re.compile(r"^\s*Mesh Tally Number\s+(\d+)", re.I)
_BOUNDARIES = re.compile(r"^\s*Tally bin boundaries:", re.I)
_DIRECTION = re.compile(r"^\s*([A-Za-z]+) direction:(.*)$", re.I)
_ENERGIES = re.compile(r"^\s*Energy bin boundaries:(.*)$", re.I)
_BIN = re.compile(r"^\s*([XYZ]) bin:\s*(\S+)\s+-\s+(\S+)", re.I)
_TABLE = re.compile(r"^\s*Tally Results:\s*([XYZ]) \(across\) by ([XYZ]) \(down\)", re.I)
_ERRORS = re.compile(r"^\s*Relative Errors\s*$", re.I)
_COLUMNS = re.compile(r"^\s*(Energy\s+)?X\s+Y\s+Z\s+Result\s+Rel\s*Error", re.I)
_PRINT_STEP = 0.01      # the boundaries and bin centres are printed with 2 decimals (cm)


def _floats(text):
    return np.array(text.split(), dtype=float)


def _bin_index(edges, centres):
    """Bin (0-based) of each centre between the edges (cm); -1 outside."""
    k = np.searchsorted(edges, np.atleast_1d(centres)) - 1
    return np.where((k >= 0) & (k < len(edges) - 1), k, -1)


def read_meshtal(path, progress=None):
    """
    Rectangular mesh tallies of a meshtal file: list of dicts 'number', 'title' (of the input, the
    line after the 'mcnp version ... probid' line), 'histories', 'comments', 'edges' {'X', 'Y',
    'Z': bin boundaries (cm)}, 'energies', 'result' and 'error' (X, Y, Z arrays, MCNP axes).
    progress(fraction) is called while reading. ValueError if it cannot be read.
    """
    size = max(1, os.path.getsize(path))
    tallies, histories, cur, title = [], None, None, None
    with open(path, "r", errors="replace") as f:
        lines = iter(f)
        read = 0
        for line in lines:
            read += len(line)
            if title is None and _PROBID.match(line):
                title = next(lines, "")
                read += len(title)
                title = title.strip()
                continue
            m = _HISTORIES.search(line)
            if m:
                histories = float(m.group(1))
                continue
            m = _TALLY.match(line)
            if m:
                cur = {'number': int(m.group(1)), 'title': title, 'histories': histories, 'comments': [], 'edges': {},
                       'energies': None, 'result': None, 'error': None, 'filled': None}
                tallies.append(cur)
                for line in lines:                      # its description, up to the bin boundaries
                    read += len(line)
                    if _BOUNDARIES.match(line):
                        break
                    if line.strip():
                        cur['comments'].append(line.strip())
                continue
            if cur is None:
                continue
            m = _DIRECTION.match(line)
            if m:
                axis = m.group(1).upper()
                if axis not in "XYZ":
                    raise ValueError(f"mesh tally {cur['number']} is not rectangular ({m.group(1)} direction): "
                                     "only XYZ meshes are read")
                cur['edges'][axis] = _floats(m.group(2))
                continue
            m = _ENERGIES.match(line)
            if m:
                cur['energies'] = _floats(m.group(1))
                if len(cur['energies']) > 2:
                    raise ValueError(f"mesh tally {cur['number']} has {len(cur['energies']) - 1} energy bins: "
                                     "only one energy bin is read")
                if set(cur['edges']) != set("XYZ"):
                    raise ValueError(f"mesh tally {cur['number']} has no X, Y and Z bin boundaries")
                shape = tuple(len(cur['edges'][a]) - 1 for a in "XYZ")
                cur['result'], cur['error'] = np.zeros(shape, np.float32), np.zeros(shape, np.float32)
                cur['filled'] = np.zeros(shape, bool)
                cur['bin'] = None
                continue
            if cur['result'] is None:
                continue
            m = _BIN.match(line)
            if m:
                axis = m.group(1).upper()
                k = _bin_index(cur['edges'][axis], (float(m.group(2)) + float(m.group(3))) / 2)[0]
                cur['bin'] = (axis, k)
                continue
            m = _TABLE.match(line)
            if m or _ERRORS.match(line):
                if m:
                    cur['table'] = (m.group(1).upper(), m.group(2).upper())
                read += _read_table(cur, lines, errors=m is None)
                if progress is not None:
                    progress(read / size)
                continue
            if _COLUMNS.match(line):
                read += _read_columns(cur, lines, energy=bool(_COLUMNS.match(line).group(1)))
    out = [t for t in tallies if t['result'] is not None]
    if not out:
        raise ValueError("no rectangular mesh tally (Mesh Tally Number ... Tally bin boundaries) was found")
    for t in out:
        if not t['filled'].all():
            raise ValueError(f"mesh tally {t['number']}: {int((~t['filled']).sum())} of {t['filled'].size} bins "
                             "have no result in the file")
        del t['filled']
        t.pop('bin', None)
        t.pop('table', None)
    return out


def _read_table(cur, lines, errors):
    """One table (header of across centres, rows 'down centre, values') into the result or error array."""
    across, down = cur.get('table', (None, None))
    if across is None or cur.get('bin') is None:
        raise ValueError(f"mesh tally {cur['number']}: a table without its 'Tally Results' or bin label")
    third, k = cur['bin']
    if {across, down, third} != set("XYZ") or k < 0:
        raise ValueError(f"mesh tally {cur['number']}: tables of {across} by {down} in {third} bins")
    read = 0
    header = next(lines)
    read += len(header)
    i_across = _bin_index(cur['edges'][across], _floats(header))
    target = cur['error'] if errors else cur['result']
    axes = "XYZ"
    for line in lines:
        read += len(line)
        if not line.strip():
            break
        values = _floats(line)
        j = _bin_index(cur['edges'][down], values[0])[0]
        if j < 0 or len(values) - 1 != len(i_across) or (i_across < 0).any():
            raise ValueError(f"mesh tally {cur['number']}: a row of {down} = {values[0]} does not fit the bins")
        index = [None, None, None]
        index[axes.index(across)], index[axes.index(down)], index[axes.index(third)] = i_across, j, k
        target[tuple(index)] = values[1:]
        if not errors:
            cur['filled'][tuple(index)] = True
    return read


def _read_columns(cur, lines, energy):
    """Column format: one bin per row ([energy,] X, Y, Z, result, relative error)."""
    read = 0
    for line in lines:
        read += len(line)
        values = line.split()
        if not values:
            break
        try:
            x, y, z, result, error = (float(v) for v in values[1 if energy else 0:][:5])
        except ValueError:
            break
        index = tuple(_bin_index(cur['edges'][a], v)[0] for a, v in zip("XYZ", (x, y, z)))
        if min(index) < 0:
            raise ValueError(f"mesh tally {cur['number']}: a bin at ({x}, {y}, {z}) outside the bin boundaries")
        cur['result'][index], cur['error'][index], cur['filled'][index] = result, error, True
    return read


def uniform_bins(edges):
    """
    (first boundary, bin width) of evenly spaced bin boundaries printed with few decimals: a
    least-squares line through all of them (each is rounded to 0.01 cm, the line is much finer).
    ValueError if they are not evenly spaced.
    """
    k = np.arange(len(edges))
    width, first = np.polyfit(k, edges, 1)
    if np.abs(edges - (first + k * width)).max() > 0.75 * _PRINT_STEP:
        raise ValueError("the mesh bins are not evenly spaced")
    return float(first), float(width)


def read_title(text):
    """
    The title AMIGOpy writes (mcnp_input.mesh_title): {'origin', 'voxel': (X, Y, Z) cm, 'source':
    abbreviation or None, 'sk': U or None, 'input': file name or None}; None if text is not one.
    """
    m = _TITLE.match(text or "")
    if m is None:
        return None
    g = m.groups()
    return {'origin': tuple(float(v) for v in g[0:3]), 'voxel': tuple(float(v) for v in g[3:6]),
            'source': g[6], 'sk': None if g[7] is None else float(g[7]), 'input': g[8]}


def title_axes(edges, title):
    """
    (first boundary, bin width) cm of the X, Y, Z bins from the origin and voxel size of a title
    (read_title), if they give the printed boundaries; None without a title or for another mesh.
    """
    if not title:
        return None
    axes = list(zip(title['origin'], title['voxel']))
    for a, (first, width) in zip("XYZ", axes):
        e = np.asarray(edges[a], float)
        k = np.arange(len(e))
        # printed to 0.01 cm; the title has 4 / 6 decimals
        if width <= 0 or np.abs(first + k * width - e).max() > _PRINT_STEP / 2 + 1e-4 + len(e) * 1e-6:
            return None
    return axes


def dose_factor(title):
    """
    Gy per meshtal result for the source and Sk of a title (read_title), as MATLAB AMIGO: Sk / (sk x
    3600 x 1e6), sk the air kerma strength per source particle of the source (mcnp_input.SOURCE_DOSE),
    the SSR weight being the total dwell time (s). (factor, SOURCE_DOSE key) or None.
    """
    if not title or not title['sk'] or not title['source']:
        return None
    key = next((k for k, (abbr, _) in SOURCE_DOSE.items() if abbr.lower() == title['source'].lower()), None)
    if key is None:
        return None
    return title['sk'] / (SOURCE_DOSE[key][1] * 3600.0 * 1e6), key


def mesh_geometry(edges, title=None):
    """
    ImagePositionPatient (mm, centre of the bin with the lowest DICOM x, y, z), PixelSpacing (row,
    column mm) and SliceThickness (mm) of a mesh in MCNP axes (DICOM x = X, y = -Z, z = Y), as
    AMIGOpy stores volumes: slices = Y bins, rows = Z bins upwards (the last Z bin has the lowest
    y), columns = X bins. Bins from the title (title_axes) or a line through the boundaries.
    """
    (x0, dx), (y0, dy), (z0, dz) = title_axes(edges, title) or [uniform_bins(edges[a]) for a in "XYZ"]
    nz = len(edges['Z']) - 1
    ipp = (10.0 * (x0 + dx / 2), -10.0 * (z0 + (nz - 0.5) * dz), 10.0 * (y0 + dy / 2))
    return ipp, [10.0 * dz, 10.0 * dx], 10.0 * dy


def stored(volume):
    """An (X, Y, Z) mesh array as AMIGOpy stores volumes: (slices = Y, rows = Z upwards, columns = X)."""
    return np.ascontiguousarray(np.transpose(volume, (1, 2, 0)))


def _dose_window(volume):
    """Window of a dose as RTDOSE files get it on loading (load_dcm): twice the mean of the positive values."""
    active = volume[volume > 0]
    if active.size:
        mean = float(active.mean())
        return 2.0 * mean, mean
    top = float(np.nanmax(volume)) if volume.size else 0.0
    return (top, top / 2) if top > 0 else (10.0, 5.0)


def _series(volume, description, ipp, pixel_spacing, slice_thickness, series_number, extra, window=None):
    top = float(np.nanmax(volume)) if volume.size else 1.0
    width, centre = window or (top or 1.0, (top or 1.0) / 2)
    meta = {'SeriesDescription': description, 'WindowWidth': width, 'WindowCenter': centre,
            'AcquisitionNumber': 1, 'DCM_Info': {}, 'StudyDescription': 'AMIGOpy',
            'ImageComments': 'MCNP mesh tally, not for clinical use', 'SliceThickness': slice_thickness,
            'PixelSpacing': pixel_spacing, 'ImagePositionPatient': list(ipp), 'DataType': 'MCNP', **extra}
    return {'3DMatrix': volume, 'metadata': meta, 'SeriesNumber': series_number}


def _raw_reason(title):
    """Why the results stay as MCNP writes them (no dose_factor)."""
    if title is None:
        return "line 2 is not an AMIGOpy title"
    if not title['source'] or not title['sk']:
        return "no source and Sk in the title"
    return f"source {title['source']} unknown"


def import_meshtal(self, path=None):
    """File > Open > MCNPout: each mesh tally of a meshtal file as an RTDOSE (+ relative errors) of the study shown."""
    if path is None:
        path, _ = QFileDialog.getOpenFileName(self, "Open MCNP mesh tally output", getattr(self, 'last_mcnp_dir', ""),
                                              "MCNP mesh tally (meshtal* *.msht *.out);;All files (*)")
        if not path:
            return None
    prog = QProgressDialog(f"Reading {os.path.basename(path)}...", None, 0, 100, self)
    prog.setWindowTitle("MCNP mesh tally")
    prog.setWindowModality(Qt.WindowModality.ApplicationModal)
    prog.setMinimumDuration(0)

    def progress(fraction):
        prog.setValue(int(100 * fraction))
        QApplication.processEvents()

    try:
        tallies = read_meshtal(path, progress)
        title = read_title(tallies[0]['title'])
        geometry = [mesh_geometry(t['edges'], title) for t in tallies]
    except (OSError, ValueError) as e:
        QMessageBox.critical(self, "MCNP mesh tally", f"Could not read {os.path.basename(path)}:\n{e}")
        return None
    finally:
        prog.close()
    self.last_mcnp_dir = os.path.dirname(path)

    from fcn_display.brachy_plan_actions import _next_series_number
    from fcn_load.populate_med_image_list import add_series_tree_item, rtdose_tree_label
    pid = getattr(self, 'patientID', None) or "MCNP"
    sid = getattr(self, 'studyID', None) or "MCNP"
    if not isinstance(getattr(self, 'medical_image', None), dict):
        self.medical_image = {}
    study = self.medical_image.setdefault(pid, {}).setdefault(sid, {})
    name = os.path.basename(path)
    label = f"{name} of {title['input']}" if title and title['input'] else name
    factor = dose_factor(title)
    lines = [f"{name}: added to Patient {pid}, Study {sid} (the study shown)."]
    if title:
        lines.append(f"Title of the input (line 2): {tallies[0]['title']}")
    lines.append("")
    for t, (ipp, spacing, thickness) in zip(tallies, geometry):
        exact = title_axes(t['edges'], title) is not None
        values = t['result'] * np.float32(factor[0]) if factor else t['result']
        source = {'file': path, 'tally': t['number'], 'title': t['title'], 'bins_from_title': exact,
                  'gy_per_result': factor[0] if factor else None, 'histories': t['histories'],
                  'comments': t['comments'], 'energy_bins': None if t['energies'] is None else t['energies'].tolist(),
                  'edges_cm': {a: e.tolist() for a, e in t['edges'].items()}}
        dose = _series(stored(values), f"MCNP tally {t['number']} ({label})", ipp, spacing, thickness,
                       _next_series_number(study),
                       {'DoseUnits': 'GY' if factor else 'MCNP result per source particle', 'MCNP_meshtal': source},
                       window=_dose_window(values))
        study.setdefault('RTDOSE', []).append(dose)
        add_series_tree_item(self, pid, sid, 'RTDOSE', len(study['RTDOSE']) - 1, rtdose_tree_label(study, dose))
        error = _series(stored(t['error']), f"MCNP tally {t['number']} relative error ({label})", ipp, spacing,
                        thickness, _next_series_number(study), {'Modality': 'MCNP', 'MCNP_meshtal': source})
        study.setdefault('MCNP', []).append(error)
        add_series_tree_item(self, pid, sid, 'MCNP', len(study['MCNP']) - 1,
                             f"{error['metadata']['SeriesDescription']}_Series: {error['SeriesNumber']}")
        ny, nz, nx = dose['3DMatrix'].shape
        peak = np.unravel_index(int(np.argmax(t['result'])), t['result'].shape)
        if factor:
            what = (f"dose (Gy) = result x Sk / (sk x 3600 x 1e6) = result x {factor[0]:.6g} ({title['source']}: "
                    f"sk {SOURCE_DOSE[factor[1]][1]:.3g}, Sk {title['sk']:.6g} U), max {float(values.max()):.4g} Gy")
        else:
            what = (f"the results as MCNP writes them (per source particle, not Gy: {_raw_reason(title)}), "
                    f"max {float(t['result'].max()):.4g}")
        if t['number'] == 14:
            what += "; FM14 -1 0 -5 -6 scores per cm3: divide by the density for the dose to medium (not done)"
        lines += [f"Tally {t['number']}: {nx} x {nz} x {ny} bins (columns x rows x slices) of {spacing[1]:.4f} x "
                  f"{spacing[0]:.4f} x {thickness:.4f} mm "
                  + ("(origin and voxel size of the title)" if exact else "(fitted to the boundaries, 2 decimals)")
                  + f", first bin centre ({ipp[0]:.3f}, {ipp[1]:.3f}, {ipp[2]:.3f}) mm;"
                  + (f" {t['histories']:.0f} histories." if t['histories'] else ""),
                  f"  RTDOSE '{dose['metadata']['SeriesDescription']}': {what} (relative error at the maximum "
                  f"{t['error'][peak]:.3f});",
                  f"  MCNP '{error['metadata']['SeriesDescription']}': the relative errors."]
    lines += ["", "Placed with the MCNP axes of the inputs AMIGOpy writes (X = x, Y = z, Z = -y)."]
    QMessageBox.information(self, "MCNP mesh tally", "\n".join(lines))
    return tallies
