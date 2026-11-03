"""
MCNP mesh tally output (fcn_mcnp.mcnp_meshtal, File > Open > MCNPout): read by its labels in the table
(OUT=ik) and column formats, geometry from the bin boundaries printed with 2 decimals, and the mesh put
on the patient as AMIGOpy writes inputs (MCNP X = x, Y = z, Z = -y), rows stored as AMIGOpy stores them.
"""
import numpy as np
import pytest

from fcn_mcnp.mcnp_meshtal import dose_factor, mesh_geometry, read_meshtal, read_title, stored, title_axes, uniform_bins

EDGES = {"X": [-1.0, -0.9, -0.8], "Y": [0.0, 0.3, 0.6, 0.9], "Z": [5.0, 5.2, 5.4]}
NX, NY, NZ = 2, 3, 2
RESULT = np.array([[[100 * i + 10 * j + k + 1 for k in range(NZ)] for j in range(NY)] for i in range(NX)], float)
ERROR = RESULT / 1000.0


def _centres(a):
    e = EDGES[a]
    return [(lo + hi) / 2 for lo, hi in zip(e[:-1], e[1:])]


def _header(energies="1.00E-03 1.00E+36"):
    return ["mcnp   version 6     ld=06/23/14  probid =  11/01/26 13:28:42",
            " c title",
            " Number of histories used for normalizing tallies =       1000.00", "",
            " Mesh Tally Number         4", " photon   mesh tally.",
            " This mesh tally is modified by a dose response function.", "",
            " Tally bin boundaries:"] + \
           [f"    {a} direction:  " + " ".join(f"{v:8.2f}" for v in EDGES[a]) for a in "XYZ"] + \
           [f"    Energy bin boundaries: {energies}", "", " Energy Bin:  1.00E-03 - 1.00E+36 MeV", ""]


def _table_format():
    """OUT=ik: per Y bin, X (across) by Z (down), results then relative errors."""
    lines = _header()
    for j, (lo, hi) in enumerate(zip(EDGES["Y"][:-1], EDGES["Y"][1:])):
        lines += [f"  Y bin:   {lo:8.2f}   -   {hi:8.2f}", ""]
        for title, values, fmt in (("     Tally Results:  X (across) by Z (down)", RESULT, "{:.5E}"),
                                   ("     Relative Errors", ERROR, "{:.5f}")):
            lines += [title, "        " + " ".join(f"{c:10.2f}" for c in _centres("X"))]
            for k, z in enumerate(_centres("Z")):
                lines.append(f"  {z:10.2f} " + " ".join(fmt.format(values[i, j, k]) for i in range(NX)))
            lines.append("")
    return "\n".join(lines) + "\n"


def _column_format():
    lines = _header() + ["   X         Y         Z     Result     Rel Error"]
    for i, x in enumerate(_centres("X")):
        for j, y in enumerate(_centres("Y")):
            for k, z in enumerate(_centres("Z")):
                lines.append(f"  {x:8.3f} {y:8.3f} {z:8.3f} {RESULT[i, j, k]:.5E} {ERROR[i, j, k]:.5E}")
    return "\n".join(lines) + "\n"


@pytest.mark.parametrize("text", [_table_format(), _column_format()], ids=["table (OUT=ik)", "columns"])
def test_mesh_tally_read_by_its_labels(tmp_path, text):
    path = tmp_path / "meshtal"
    path.write_text(text)
    t, = read_meshtal(str(path))
    assert (t["number"], t["histories"]) == (4, 1000.0)
    assert "modified by a dose response function" in t["comments"][1]
    assert t["result"] == pytest.approx(RESULT) and t["error"] == pytest.approx(ERROR)


def test_several_energy_bins_are_not_read(tmp_path):
    path = tmp_path / "meshtal"
    path.write_text("\n".join(_header("0.00E+00 1.00E-01 1.00E+36")) + "\n")
    with pytest.raises(ValueError, match="energy bins"):
        read_meshtal(str(path))


def test_bin_geometry_from_boundaries_printed_with_2_decimals():
    first, width = -20.833021, 0.100111                  # (as in a real meshtal: 1.00111 mm bins)
    edges = np.round(first + np.arange(329) * width, 2)
    f, w = uniform_bins(edges)
    assert abs(f - first) < 1e-3 and abs(w - width) < 1e-5
    with pytest.raises(ValueError, match="evenly"):
        uniform_bins(np.array([0.0, 0.1, 0.25, 0.3]))


def test_mesh_on_the_patient_as_amigopy_inputs():
    # MCNP X = DICOM x, Y = DICOM z (slices), Z = -DICOM y (rows: the last Z bin has the lowest y)
    ipp, spacing, thickness = mesh_geometry({a: np.array(e) for a, e in EDGES.items()})
    assert ipp == pytest.approx((-9.5, -53.0, 1.5)) and spacing == pytest.approx([2.0, 1.0]) and thickness == pytest.approx(3.0)
    vol = stored(RESULT)
    assert vol.shape == (NY, NZ, NX)                    # slices, rows, columns
    for s, r, c in np.ndindex(vol.shape):
        assert vol[s, r, c] == RESULT[c, s, r]          # row r: Z bin r (stored rows run up, like the lattice j)
        # the bin centre in DICOM: x = X, z = Y, y = -Z, with stored row r = DICOM row NZ - 1 - r
        x, y, z = ipp[0] + c * spacing[1], ipp[1] + (NZ - 1 - r) * spacing[0], ipp[2] + s * thickness
        assert (x / 10, -y / 10, z / 10) == pytest.approx((_centres("X")[c], _centres("Z")[r], _centres("Y")[s]))


def test_title_of_the_input_on_line_2(tmp_path):
    path = tmp_path / "meshtal"
    path.write_text(_table_format())
    assert read_meshtal(str(path))[0]["title"] == "c title"           # the line after 'mcnp version ... probid'
    text = _table_format().replace(" c title", " origin=-1,0,5 voxel=0.1,0.3,0.2 GMP Sk=40700 my input.inp")
    path.write_text(text)
    t, = read_meshtal(str(path))
    title = read_title(t["title"])
    assert title == {'origin': (-1.0, 0.0, 5.0), 'voxel': (0.1, 0.3, 0.2), 'source': 'GMP', 'sk': 40700.0,
                     'input': 'my input.inp'}
    assert title_axes(t["edges"], title) == [(-1.0, 0.1), (0.0, 0.3), (5.0, 0.2)]
    assert read_title("c ===========") is None and read_title("o=1,2,3 v=0.1,0.1,0.1")['input'] is None


def test_mesh_from_the_title_not_the_2_decimal_boundaries():
    # the FMESH of a real input: origin and bins as MCNP has them, boundaries printed with 2 decimals
    origin = (-20.83359375, -10.6, 8.9607421875)
    width = (32.8376953125 / 328, 0.1, 18.33671875 / 183)
    n = (328, 153, 183)
    edges = {a: np.round(o + np.arange(k + 1) * w, 2) for a, o, w, k in zip("XYZ", origin, width, n)}
    title = read_title("origin=-20.8336,-10.6,8.9607 voxel=0.100115,0.1,0.100201 mSv2 Sk=40700 inp")
    ipp, spacing, thickness = mesh_geometry(edges, title)
    exact = (10 * (origin[0] + width[0] / 2), -10 * (origin[2] + (n[2] - 0.5) * width[2]), 10 * (origin[1] + width[1] / 2))
    assert ipp == pytest.approx(exact, abs=1e-3) and spacing == pytest.approx([10 * width[2], 10 * width[0]], abs=1e-5)
    # the title of another mesh is not used: the bins are fitted to the boundaries
    other = read_title("origin=-20.9,-10.6,8.9607 voxel=0.100115,0.1,0.100201 mSv2 Sk=40700 inp")
    assert title_axes(edges, other) is None
    assert mesh_geometry(edges, other) == mesh_geometry(edges)


def test_dose_in_gy_with_the_source_and_sk_of_the_title():
    # MATLAB AMIGO: result x Sk / (sk per source particle x 3600 x 1e6), the SSR weight being the total dwell time
    factor, key = dose_factor(read_title("origin=0,0,0 voxel=0.1,0.1,0.1 mSv2 Sk=40700 inp"))
    assert key == "microselectron" and factor == pytest.approx(40700 / (7.32e-08 * 3600 * 1e6))
    assert dose_factor(read_title("origin=0,0,0 voxel=0.1,0.1,0.1 XYZ Sk=40700")) is None     # unknown source
    assert dose_factor(read_title("origin=0,0,0 voxel=0.1,0.1,0.1 inp")) is None              # no source and Sk
    assert dose_factor(None) is None
