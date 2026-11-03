"""
MCNP input (fcn_mcnp.mcnp_input): MCNP axes X = DICOM x, Y = DICOM z (slices), Z = -DICOM y (rows,
anterior up as in AMIGO's axial view); lattice cell and fill in the order X, Z, Y; boxes at the voxel
edges of the CT, whose rows are stored flipped (row r as shown is DICOM row n_rows - 1 - r).
"""
import re
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from fcn_mcnp.mcnp_import import build_maps, parse_mcnp_input, plane_mismatch, uncovered_axes
from fcn_mcnp.mcnp_input import MAX_COL, build_mcnp_cards, lattice_axis, mesh_title, to_mcnp_axes
from fcn_mcnp.mcnp_meshtal import dose_factor, read_title

IPP = (-10.0, 20.0, 30.0)            # centre of the voxel with the lowest x, y, z (mm)
PS_COL, PS_ROW, ST = 0.8, 0.9, 2.0    # column, row, slice spacing (mm)
NS, NR, NC = 4, 5, 6                  # slices, rows, columns


class _Value:
    def __init__(self, v):
        self._v = v

    def value(self):
        return self._v


class _Text:
    def __init__(self, t):
        self._t = t

    def currentText(self):
        return self._t


def _app(vox=(0, NC - 1, 0, NS - 1, 0, NR - 1), grid=None, grid_mode="voxel", res=(PS_COL, ST, PS_ROW),
         dwell=(12.3, -45.6, 78.9, 0.6, 0.0, 0.8), selected="RTPLAN", lattice=None):
    """
    Stand-in for the main window: a CT whose lattice map (lattice: (map, universe table)) has by
    default universe 1000 + voxel number, the MonteCarlo tab boxes (xmin, xmax, ymin, ymax, zmin,
    zmax: x = columns, y = slices, z = rows as shown), a plan with one dwell (x, y, z mm,
    direction) and the series selected in the data tree.
    """
    uni = (1000 + np.arange(NS * NR * NC)).reshape(NS, NR, NC).astype(np.int32)
    universes = [{'universe': int(u), 'material_index': 2, 'material_key': 2, 'material': 'Water', 'density': 1.0}
                 for u in uni.ravel()]
    if lattice is not None:
        uni, universes = lattice
    ct = {'3DMatrix': np.zeros((NS, NR, NC), np.float32), 'SeriesNumber': 7,
          'metadata': {'ImagePositionPatient': list(IPP), 'PixelSpacing': [PS_ROW, PS_COL], 'SliceThickness': ST,
                       'SeriesInstanceUID': '1.2.3.4', 'FrameOfReferenceUID': '1.2.3.5'},
          'mcnp_lattice_maps': {'lat': {'3DMatrix': uni, 'universes': universes}}}
    dw = np.array([[1, 0, 10.0, *dwell]], dtype=float)
    plan = {'metadata': {'Plan_Brachy_Channels': [{'DwellInfo': dw}]}}
    app = SimpleNamespace(medical_image={'P': {'S': {'CT': [ct], 'RTPLAN': [plan]}}},
                          patientID='P', studyID='S', modality=selected, series_index=0,
                          patientID_plan='P', studyID_plan='S', modality_plan='RTPLAN', series_index_plan=0,
                          mcnp_source_combo=_Text("GammaMed Plus"), mc_grid_mode_combo=_Text(grid_mode),
                          Mat_df=pd.DataFrame())
    for prefix, values in (('mc_vox', vox), ('mc_grid', grid or vox)):
        for name, v in zip((f"{prefix}_{a}{k}" for a in "xyz" for k in ("min", "max")), values):
            setattr(app, name, _Value(float(v)))
    for a, r in zip("xyz", res):
        setattr(app, f"mc_grid_{a}res", _Value(float(r)))
    return app, ct, uni


def _cards(app, ct):
    return build_mcnp_cards(app, ct, 'lat')[0]


def _surfaces(lines):
    """{number: (type, value)} of the plane surfaces."""
    out = {}
    for line in lines:
        m = re.match(r"\s+(\d+)\s+(p[xyz])\s+(\S+)\s*$", line)
        if m:
            out[int(m.group(1))] = (m.group(2), float(m.group(3)))
    return out


def _lattice(lines):
    """Surfaces of the lattice cell 600 in their order, fill ranges, fill values as an (i, j, k) array."""
    k = next(i for i, line in enumerate(lines) if line.startswith("600 "))
    order = [int(t) for t in re.findall(r"-?\d+", lines[k].split("lat=")[0])[2:]]
    ranges = [tuple(map(int, r.split(":"))) for r in lines[k + 1].split()[1:4]]
    values = []
    for line in lines[k + 2:]:
        if line.startswith("c"):
            break
        for tok in line.replace("&", " ").split():
            if tok.endswith("r"):
                values += [values[-1]] * int(tok[:-1])
            else:
                values.append(int(tok))
    return order, ranges, np.array(values).reshape([hi - lo + 1 for lo, hi in ranges], order="F")


def _element(order, surfaces, point):
    """
    Lattice element [i, j, k] holding an MCNP point (cm), as MCNP numbers them: beyond the 1st / 3rd /
    5th surface of the lattice cell is element +1 of the 1st / 2nd / 3rd index (beyond the 2nd / 4th /
    6th, element -1).
    """
    idx = []
    for first, second in zip(order[0::2], order[1::2]):
        kind, v1 = surfaces[abs(first)]
        _, v2 = surfaces[abs(second)]
        idx.append(int(np.floor((point["xyz".index(kind[1])] - v2) / (v1 - v2))))
    return tuple(idx)


def _fmesh(lines):
    """ORIGIN, IMESH, IINTS, JMESH, JINTS, KMESH, KINTS of the first FMESH tally."""
    k = next(i for i, line in enumerate(lines) if "FMESH" in line and "ORIGIN" in line)
    text = " ".join(lines[k:k + 4]).replace("&", " ")
    origin = [float(v) for v in re.search(r"ORIGIN=\s*(\S+)\s+(\S+)\s+(\S+)", text).groups()]
    get = lambda key: re.search(key + r"=\s*(\S+)", text).group(1)
    return (origin, float(get("IMESH")), int(get("IINTS")), float(get("JMESH")), int(get("JINTS")),
            float(get("KMESH")), int(get("KINTS")))


def test_mcnp_axes_slices_on_y_anterior_up():
    assert to_mcnp_axes(1, 2, 3) == (1, 3, -2)
    # a rotation of the patient, not a mirror image
    assert np.linalg.det(np.array([to_mcnp_axes(*e) for e in np.eye(3)])) == pytest.approx(1.0)


@pytest.mark.parametrize("selected", ["CT", "RTPLAN"])
def test_lattice_holds_each_voxel_at_its_dicom_position(selected):
    # phantom box: columns 1..4, slices 1..3, rows as shown 0..2 (= DICOM rows 2..4: not symmetric)
    app, ct, uni = _app(vox=(1, 4, 1, 3, 0, 2), selected=selected)
    lines = _cards(app, ct)
    order, ranges, fill = _lattice(lines)
    surf = _surfaces(lines)
    assert order == [-602, 601, -606, 605, -604, 603]            # planes X, then Z, then Y
    assert [surf[n][0] for n in range(601, 607)] == ['px', 'px', 'py', 'py', 'pz', 'pz']
    assert ranges == [(0, 3), (0, 2), (0, 2)]                     # X: 4 columns, Z: 3 rows, Y: 3 slices
    for s in range(1, 4):
        for r in range(0, 3):
            for c in range(1, 5):
                centre = (IPP[0] + c * PS_COL, IPP[1] + (NR - 1 - r) * PS_ROW, IPP[2] + s * ST)
                point = [v / 10.0 for v in to_mcnp_axes(*centre)]
                assert fill[_element(order, surf, point)] == uni[s, r, c]


def test_lattice_rows_run_up_as_in_the_axial_view():
    # MCNP Z (j) runs anterior-ward, as AMIGO shows the stored rows (bottom to top): the fill read
    # as (slices, j, columns) is the stored crop, so an MCNP py plot (X right, Z up) shows the
    # patient as AMIGO's axial view does
    app, ct, uni = _app(vox=(1, 4, 1, 3, 0, 2))
    _, _, fill = _lattice(_cards(app, ct))
    assert np.array_equal(fill.transpose(2, 1, 0), uni[1:4, 0:3, 1:5])


def test_phantom_box_at_the_voxel_edges_in_mcnp_axes():
    app, ct, _ = _app(vox=(1, 4, 1, 3, 0, 2))
    surf = _surfaces(_cards(app, ct))
    x = ((IPP[0] + 0.5 * PS_COL) / 10, (IPP[0] + 4.5 * PS_COL) / 10)          # columns 1..4
    y = ((IPP[2] + 0.5 * ST) / 10, (IPP[2] + 3.5 * ST) / 10)                  # slices 1..3 (MCNP Y)
    z = (-(IPP[1] + 4.5 * PS_ROW) / 10, -(IPP[1] + 1.5 * PS_ROW) / 10)        # DICOM rows 2..4 (MCNP Z = -y)
    e = 1e-6                                     # the box ends this much inside the last lattice elements
    expected = {501: x[0], 502: x[1] - e, 503: y[0], 504: y[1] - e, 505: z[0], 506: z[1] - e,
                601: x[0], 602: x[0] + PS_COL / 10, 603: y[0], 604: y[0] + ST / 10, 605: z[0], 606: z[0] + PS_ROW / 10,
                971: x[0] - 2, 972: x[1] - e + 2, 973: y[0] - 2, 974: y[1] - e + 2, 975: z[0] - 2, 976: z[1] - e + 2}
    for n, v in expected.items():
        assert surf[n][1] == pytest.approx(v, abs=1e-9), n


@pytest.mark.parametrize("lo_cm, pitch_cm, n", [(-24.9032227, 0.09765625, 512),   # pitch rounded down
                                                (-23.0512, 0.2999996, 111),        # rounded up
                                                (3.14159265, 0.12345678, 300),
                                                (-0.96, 0.08, 4)])                 # exact
def test_lattice_covers_the_phantom_box_whatever_the_rounding(lo_cm, pitch_cm, n):
    box0, box1, cell0, cell1 = (float(f"{v:.6f}") for v in lattice_axis(lo_cm, pitch_cm, n))   # as MCNP reads them
    lattice_end = cell0 + n * (cell1 - cell0)
    assert box0 == cell0 and box1 < lattice_end < box1 + 2e-6      # covered; the box ends just inside
    assert abs(box1 - (lo_cm + n * pitch_cm)) < 1e-3               # within 0.01 mm of the true end


def _tr_card(lines, n=1):
    """Lines of card trN, with its continuation lines."""
    start = next(i for i, line in enumerate(lines) if line.startswith(f"tr{n} "))
    end = start
    while lines[end].endswith("&"):
        end += 1
    return lines[start:end + 1]


def _axes(card):
    """The source frame axes x', y', z' of a 4-line tr card (MCNP axes)."""
    return [[float(v) for v in line.rstrip("&").split()] for line in card[1:4]]


@pytest.mark.parametrize("direction", [(0.6, 0.48, 0.64), (0.6, 0.0, 0.8)])
def test_source_position_and_direction_in_mcnp_axes(direction):
    app, ct, _ = _app(dwell=(12.3, -45.6, 78.9, *direction))
    lines = _cards(app, ct)
    card = _tr_card(lines)
    assert card[0] == "tr1 1.23000 7.89000 4.56000 &" and len(card) == 4
    # no catheter path to check it: the plan orientation is taken to point to the tip (Varian, TG43),
    # so x' (the source axis, towards the cable) is the other way, in MCNP axes (X = x, Y = z, Z = -y)
    dx, dy, dz = direction
    assert _axes(card)[0] == pytest.approx([-dx, -dz, dy])
    assert "-0.0000000" not in "\n".join(card) and all(len(line) <= MAX_COL for line in lines)
    assert "c   1.23   7.89   4.56  10.00" in lines              # header listing, same axes
    assert "c   plan orientation sign not checked (no catheter path): 1" in lines


@pytest.mark.parametrize("orientation, reversed_", [((0.0, 0.0, -1.0), 1), ((0.0, 0.0, 1.0), 0)])
def test_source_axis_faces_away_from_the_catheter_tip(orientation, reversed_):
    app, ct, _ = _app(dwell=(12.3, -45.6, 78.9, *orientation))
    channel = app.medical_image['P']['S']['RTPLAN'][0]['metadata']['Plan_Brachy_Channels'][0]
    channel['ChPos'] = np.array([[12.3, -45.6, 68.9], [12.3, -45.6, 98.9]])     # from the tip, towards +z
    lines = _cards(app, ct)
    x_axis, y_axis, z_axis = _axes(_tr_card(lines))
    # away from the tip: DICOM +z = MCNP +Y, whichever way the plan stored it; y', z': the smallest
    # rotation taking X onto Y (a quarter turn about Z)
    assert (x_axis, y_axis, z_axis) == ([0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0])
    assert f"c   plan orientations reversed (they point to the tip): {reversed_}" in lines
    assert "c   1/1 dwells on the path, max 0.0 deg from it" in lines


def test_tally_mesh_on_the_calculation_grid_voxels():
    # calculation grid: columns 0..5, slices 1..2, rows as shown 0..2 (= DICOM rows 2..4)
    app, ct, _ = _app(grid=(0, 5, 1, 2, 0, 2))
    origin, imesh, iints, jmesh, jints, kmesh, kints = _fmesh(_cards(app, ct))
    assert origin == pytest.approx([(IPP[0] - 0.5 * PS_COL) / 10, (IPP[2] + 0.5 * ST) / 10, -(IPP[1] + 4.5 * PS_ROW) / 10])
    assert (imesh, jmesh, kmesh) == pytest.approx(((IPP[0] + 5.5 * PS_COL) / 10, (IPP[2] + 2.5 * ST) / 10,
                                                   -(IPP[1] + 1.5 * PS_ROW) / 10))
    assert (iints, jints, kints) == (6, 2, 3)


def test_tally_mesh_mm_mode_from_the_typed_voxel_centres():
    # mm mode: mm of the first / last voxel centres in MCNP axes, X = DICOM x, Y = DICOM z, Z = -DICOM y:
    # the mesh is the typed box plus half a CT voxel, the same numbers in AMIGOpy and in MCNP
    app, ct, _ = _app(grid=(-5.0, 5.0, 30.0, 36.0, -24.6, -21.0), grid_mode="mm", res=(1.0, 2.0, 0.9))
    lines = _cards(app, ct)
    origin, imesh, iints, jmesh, jints, kmesh, kints = _fmesh(lines)
    assert origin == pytest.approx([(-5.0 - PS_COL / 2) / 10, (30.0 - ST / 2) / 10, (-24.6 - PS_ROW / 2) / 10])
    assert (imesh, jmesh, kmesh) == pytest.approx(((5.0 + PS_COL / 2) / 10, (36.0 + ST / 2) / 10, (-21.0 + PS_ROW / 2) / 10))
    assert (iints, jints, kints) == (11, 4, 5)
    assert f"c     Z (rows):   {-24.6 - PS_ROW / 2:.3f} to {-21.0 + PS_ROW / 2:.3f} mm" in lines    # header, MCNP axes


def _materials_lattice():
    """Lattice map with Air (MCNP material 1), Water at three densities (2) and bone (3)."""
    n = np.arange(NS * NR * NC).reshape(NS, NR, NC)
    uni = np.where(n % 3 == 0, 1, np.where(n % 3 == 1, 2000 + n % 4 % 3, 4000)).astype(np.int32)
    universes = ([{'universe': 1, 'material_index': 1, 'material_key': 0, 'material': 'Air', 'density': 0.001205}]
                 + [{'universe': 2000 + k, 'material_index': 2, 'material_key': 1, 'material': 'Water',
                     'density': 1.0 + 0.01 * k} for k in range(3)]
                 + [{'universe': 4000, 'material_index': 3, 'material_key': 8, 'material': 'Cortical Bone-TG186',
                     'density': 1.92}])
    return uni, universes


def test_input_reads_back_the_written_voxels():
    # written part: columns 1..4, slices 1..3, rows as shown 0..2 (= DICOM rows 4..2: not symmetric)
    uni, universes = _materials_lattice()
    app, ct, _ = _app(vox=(1, 4, 1, 3, 0, 2), lattice=(uni, universes))
    parsed = parse_mcnp_input("\n".join(_cards(app, ct)))
    ref = parsed["ref"]
    assert (ref["patient"], ref["study"], ref["series_uid"], ref["frame_uid"], ref["series_number"]) == \
        ("P", "S", "1.2.3.4", "1.2.3.5", "7")
    assert ref["image_shape"] == (NS, NR, NC) and ref["image_ipp"] == pytest.approx(IPP)
    assert ref["shape"] == (3, 3, 4) and ref["crop"] == (1, 4, 0, 2, 1, 3)
    assert ref["spacing"] == pytest.approx((PS_COL, PS_ROW, ST))
    # centre of the written voxel with the lowest x, y, z: column 1, DICOM row 2 (row as shown 2), slice 1
    assert ref["ipp"] == pytest.approx((IPP[0] + PS_COL, IPP[1] + 2 * PS_ROW, IPP[2] + ST))
    assert plane_mismatch(ref, parsed["planes"]) == [] and uncovered_axes(ref, parsed["planes"]) == []

    maps = build_maps(parsed, {"Air": 0, "Water": 1, "Cortical Bone-TG186": 8})
    crop = uni[1:4, 0:3, 1:5]                                       # as AMIGOpy stores it
    assert np.array_equal(maps["universes"], crop)
    mat = {1: 0, 2000: 1, 2001: 1, 2002: 1, 4000: 8}
    rho = {1: 0.001205, 2000: 1.0, 2001: 1.01, 2002: 1.02, 4000: 1.92}
    assert np.array_equal(maps["material"], np.vectorize(mat.get)(crop))
    assert maps["density"] == pytest.approx(np.vectorize(rho.get)(crop), abs=1e-6)
    assert maps["material_used"] == {0: "Air", 1: "Water", 8: "Cortical Bone-TG186"} and maps["warnings"] == []

    # another material database: found by name; a missing material gets a new ID
    maps = build_maps(parsed, {"Water": 3, "Air": 5})
    assert maps["material_used"] == {5: "Air", 3: "Water", 6: "Cortical Bone-TG186"}
    assert "Cortical Bone-TG186" in maps["warnings"][0]


def test_read_back_voxels_overlay_the_image_by_patient_position():
    # voxel (s, r, c) of the written part placed by its own ImagePositionPatient (rows as stored:
    # row r is DICOM row n_rows - 1 - r) is at the place of image voxel (s0 + s, r0 + r, c0 + c)
    app, ct, _ = _app(vox=(1, 4, 1, 3, 0, 2))
    ref = parse_mcnp_input("\n".join(_cards(app, ct)))["ref"]
    ns, nr, nc = ref["shape"]
    c0, _, r0, _, s0, _ = ref["crop"]

    def place(ipp, n_rows, s, r, c):
        return ipp[0] + c * PS_COL, ipp[1] + (n_rows - 1 - r) * PS_ROW, ipp[2] + s * ST

    for s, r, c in np.ndindex(ns, nr, nc):
        assert place(ref["ipp"], nr, s, r, c) == pytest.approx(place(IPP, NR, s0 + s, r0 + r, c0 + c))


def test_input_without_amigo_reference_is_not_read():
    app, ct, _ = _app()
    lines = [line for line in _cards(app, ct) if not line.startswith("c @")]
    with pytest.raises(ValueError, match="AMIGO reference"):
        parse_mcnp_input("\n".join(lines))


def test_title_holds_the_mesh_source_and_sk_for_the_meshtal():
    # line 1 of the input = line 2 of the meshtal, whose bin boundaries have 2 decimals only
    app, ct, _ = _app(grid=(0, 5, 1, 2, 0, 2), res=(PS_COL, ST, 0.6))
    app.medical_image['P']['S']['RTPLAN'][0]['metadata']['ReferenceAirKermaRate'] = 38123.4
    lines = build_mcnp_cards(app, ct, 'lat', file_name="phantom.inp")[0]
    origin, imesh, iints, jmesh, jints, kmesh, kints = _fmesh(lines)
    title = read_title(lines[0])
    assert len(lines[0]) <= 80 and lines[1].startswith("c ====")
    assert title['origin'] == pytest.approx(origin, abs=5e-5)
    assert title['voxel'] == pytest.approx(((imesh - origin[0]) / iints, (jmesh - origin[1]) / jints,
                                            (kmesh - origin[2]) / kints), abs=5e-7)
    assert (title['source'], title['sk'], title['input']) == ("GMP", 38123.4, "phantom.inp")
    # the dose as MATLAB AMIGO: result x Sk / (sk per source particle x 3600 x 1e6), GammaMed Plus sk 7.28e-8
    assert dose_factor(title) == (pytest.approx(38123.4 / (7.28e-08 * 3600 * 1e6)), "gammamed")

    # a file name that does not fit is left out, never the mesh, source or Sk
    title = read_title(build_mcnp_cards(app, ct, 'lat', file_name="x" * 40 + ".inp")[0][0])
    assert title['input'] is None and title['sk'] == 38123.4
    # no brachy source: no source and Sk (the results stay per source particle)
    app.mcnp_source_combo = _Text("None (External beam / custom)")
    title = read_title(build_mcnp_cards(app, ct, 'lat', file_name="phantom.inp")[0][0])
    assert (title['source'], title['sk'], title['input']) == (None, None, "phantom.inp") and dose_factor(title) is None


def test_title_fits_80_columns_for_far_meshes():
    # long numbers: shorter labels first, then fewer decimals, never more than 80 columns
    title = mesh_title((-123.456789, -1234.56789, -123.456789), (0.0976563, 0.0976563, 0.0976563), "TG186", 40669.317)
    assert len(title) <= 80 and read_title(title)['sk'] == pytest.approx(40669.3)
    assert read_title(title)['origin'] == pytest.approx((-123.456789, -1234.56789, -123.456789), abs=5e-4)
