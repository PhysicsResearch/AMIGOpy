"""
Gamma analysis (fcn_evaluation.gamma, Evaluation > Gamma): known gammas of shifted and scaled doses in
3D and 2D, the evaluation grids, and the series of modality Gamma saved with its criteria.
"""
import json

import numpy as np
import pytest

from fcn_evaluation import gamma_panel, isodose
from fcn_evaluation.gamma import gamma_analysis, plane_grid, regular_grid, voxel_points

REF_GEOM = ((-6.0, -6.0, -6.0), (1.0, 1.0, 1.0), (13, 13, 13))
EVAL_GEOM = ((-16.0, -16.0, -16.0), (1.0, 1.0, 1.0), (33, 33, 33))      # larger: no edge effects


def _volume(geom, f):
    _, _, shape = geom
    pts = voxel_points(np.indices(shape).reshape(3, -1), geom)
    return f(pts).reshape(shape).astype(np.float32)


def _crit(dd, dta, threshold=0.0, local=False):
    return {"dd": dd, "dta": dta, "threshold": threshold, "local": local}


def _gammas(result):
    g = result["gamma"]
    return g[g >= 0]


def test_shifted_ramp_has_the_analytic_gamma():
    # D = 10 - 0.1 x Gy shifted by 1 mm: gamma = 1 / sqrt(DTA^2 + (dD / gradient)^2) everywhere
    ref = _volume(REF_GEOM, lambda p: 10 - 0.1 * p[:, 0])
    ev = _volume(EVAL_GEOM, lambda p: 10 - 0.1 * (p[:, 0] - 1.0))
    out = gamma_analysis(ref, REF_GEOM, ev, EVAL_GEOM, [_crit(3, 3), _crit(1, 1)], norm_dose=10.0)
    for res, expected in zip(out["results"], (1 / np.sqrt(18), 1 / np.sqrt(2))):
        g = _gammas(res)
        assert g.size == 13 ** 3 and g == pytest.approx(expected, rel=0.03)     # steps of DTA / 10
        assert res["stats"]["pass_rate"] == 100.0


def test_one_mm_shift_passes_2mm_and_fails_half_a_mm():
    # steep ramp (1 Gy/mm) shifted by 1 mm, 3 % of 10 Gy: gamma = 1 / sqrt(DTA^2 + 0.3^2), mostly the shift / DTA
    # (a dose criterion much finer than the step, dD / gradient < DTA / fraction, makes the search overestimate)
    geom = ((-3.0, -3.0, -3.0), (1.0, 1.0, 1.0), (7, 7, 7))
    ref = _volume(geom, lambda p: 10 - p[:, 0])
    ev = _volume(EVAL_GEOM, lambda p: 10 - (p[:, 0] - 1.0))
    out = gamma_analysis(ref, geom, ev, EVAL_GEOM, [_crit(3, 2.0), _crit(3, 0.5)], norm_dose=10.0)
    passed, failed = out["results"]
    assert _gammas(passed) == pytest.approx(1 / np.sqrt(4.09), rel=0.03) and passed["stats"]["pass_rate"] == 100.0
    assert _gammas(failed) == pytest.approx(1 / np.sqrt(0.34), rel=0.03) and failed["stats"]["pass_rate"] == 0.0


def test_two_percent_higher_dose():
    # a broad Gaussian 2 % higher: passes 3 % (global), fails 1 % / 0.2 mm, at the maximum no shift helps
    # (sigma 10 mm: trilinear interpolation of the 1 mm grid keeps the flat top)
    gauss = lambda p: 10 * np.exp(-np.sum(p ** 2, axis=1) / (2 * 10.0 ** 2))
    ref = _volume(REF_GEOM, gauss)
    ev = _volume(EVAL_GEOM, lambda p: 1.02 * gauss(p))
    out = gamma_analysis(ref, REF_GEOM, ev, EVAL_GEOM, [_crit(3, 1, threshold=10), _crit(1, 0.2, threshold=10)])
    assert out["norm_dose"] == pytest.approx(10.0)
    loose, tight = out["results"]
    assert loose["stats"]["pass_rate"] == 100.0 and loose["stats"]["max"] < 0.67
    assert tight["stats"]["pass_rate"] < 50.0
    g = tight["gamma"]
    centre = tuple(n // 2 for n in g.shape)                     # the maximum, in the cropped box
    assert g[centre] == pytest.approx(2.0, abs=0.05)
    # local: 2 % of every dose
    local = gamma_analysis(ref, REF_GEOM, ev, EVAL_GEOM, [_crit(1, 0.2, threshold=10, local=True)])["results"][0]
    assert _gammas(local).max() == pytest.approx(2.0, abs=0.05)


def test_threads_give_the_same_gamma(monkeypatch):
    import fcn_evaluation.gamma as G
    gauss = lambda p: 10 * np.exp(-np.sum((p - 0.4) ** 2, axis=1) / (2 * 4.0 ** 2))
    ref = _volume(REF_GEOM, gauss)
    ev = _volume(EVAL_GEOM, lambda p: 1.03 * gauss(p + np.array([0.7, -0.3, 0.2])))
    crit = [_crit(2, 1, threshold=5)]
    monkeypatch.setattr(G, "WORKERS", 1)
    serial = gamma_analysis(ref, REF_GEOM, ev, EVAL_GEOM, crit)["results"][0]["gamma"]
    monkeypatch.setattr(G, "WORKERS", 4)
    monkeypatch.setattr(G, "PARALLEL_POINTS", 10)
    threaded = gamma_analysis(ref, REF_GEOM, ev, EVAL_GEOM, crit)["results"][0]["gamma"]
    assert np.array_equal(serial, threaded) and (serial > 0).sum() > 1000


def test_2d_plane_and_evaluation_grids():
    ref = _volume(REF_GEOM, lambda p: 10 - 0.1 * p[:, 0])
    ev = _volume(EVAL_GEOM, lambda p: 10 - 0.1 * (p[:, 0] - 1.0))
    out = gamma_analysis(ref, REF_GEOM, ev, EVAL_GEOM, [_crit(3, 3)], plane="coronal", plane_position=2.2,
                         norm_dose=10.0)
    res = out["results"][0]
    assert res["gamma"].shape == (13, 1, 13) and res["geom"][0] == pytest.approx((-6.0, 2.0, -6.0))
    assert _gammas(res) == pytest.approx(1 / np.sqrt(18), rel=0.03)
    assert plane_grid(REF_GEOM, "axial", 40.0) is None
    assert plane_grid(REF_GEOM, "sagittal", 0.0, spacing=2.0) == ((0.0, -6.0, -6.0), (1.0, 2.0, 2.0), (7, 7, 1))
    assert regular_grid(REF_GEOM, 2.5) == ((-6.0, -6.0, -6.0), (2.5, 2.5, 2.5), (5, 5, 5))
    out = gamma_analysis(ref, REF_GEOM, ev, EVAL_GEOM, [_crit(3, 3)], resolution=2.5, norm_dose=10.0)
    assert out["geom"][2] == (5, 5, 5) and out["results"][0]["stats"]["points"] == 125


@pytest.fixture
def panel(qapp, tmp_path, monkeypatch):
    """The Evaluation tab built on a bare widget, settings in a temporary folder, two doses of a patient."""
    from PySide6.QtWidgets import QWidget
    from fcn_create_gui.tab_evaluation import create_tab_evaluation
    monkeypatch.setattr(isodose, "_template_dir", lambda: (tmp_path / "t").mkdir(exist_ok=True) or str(tmp_path / "t"))
    monkeypatch.setattr(isodose, "_settings_path", lambda: str(tmp_path / "settings.json"))
    w = QWidget()
    meta = lambda geom, name: {"ImagePositionPatient": list(geom[0]), "PixelSpacing": [geom[1][1], geom[1][0]],
                               "SliceThickness": geom[1][2], "SeriesDescription": name}
    ref = {"3DMatrix": _volume(REF_GEOM, lambda p: 10 - 0.1 * p[:, 0]), "metadata": meta(REF_GEOM, "TPS"),
           "SeriesNumber": 3}
    ev = {"3DMatrix": _volume(EVAL_GEOM, lambda p: 10 - 0.1 * (p[:, 0] - 1.0)), "metadata": meta(EVAL_GEOM, "MCNP"),
          "SeriesNumber": 4}
    w.medical_image = {"P": {"S": {"RTDOSE": [ref, ev], "CT": []}}}
    w.patientID, w.studyID = "P", "S"
    create_tab_evaluation(w)
    return w


def test_gamma_saved_as_a_series_with_its_criteria(panel, monkeypatch):
    w = panel
    added = []
    monkeypatch.setattr("fcn_load.populate_med_image_list.add_series_tree_item",
                        lambda self, pid, sid, modality, index, label: added.append((pid, sid, modality, index, label)))
    gamma_panel.refresh_gamma_combos(w)
    w.gamma_ref_combo.setCurrentIndex(w.gamma_ref_combo.findText("RTDOSE: TPS"))
    w.gamma_eval_combo.setCurrentIndex(w.gamma_eval_combo.findText("RTDOSE: MCNP"))
    w.gamma_norm_combo.setCurrentIndex(1)
    w.gamma_norm_spin.setValue(10.0)
    assert [c["dd"] for c in gamma_panel.criteria_rows(w)] == [3.0, 2.0, 1.0]       # defaults
    out = gamma_panel.run_gamma(w)
    assert out is not None and w.gamma_table.item(0, 4).text() == "100.00"
    w.gamma_table.selectRow(2)
    series = gamma_panel.save_gamma(w)
    meta = series["metadata"]
    assert added == [("P", "S", "Gamma", 0, f"{meta['SeriesDescription']}_Series: 5")]
    assert w.medical_image["P"]["S"]["Gamma"] == [series]
    assert meta["Modality"] == "Gamma" and (meta["WindowWidth"], meta["WindowCenter"]) == (2.0, 1.0)
    assert meta["SeriesDescription"] == "Gamma 1%/1mm global (MCNP vs TPS)"
    info = meta["Gamma"]
    assert (info["dd_percent"], info["dta_mm"], info["threshold_percent"], info["normalization"]) == (1.0, 1.0, 10.0, "global")
    assert info["normalization_dose_gy"] == 10.0 and info["mode"] == "3D" and info["reference_position"] == [-6.0, -6.0, -6.0]
    assert info["reference"]["description"] == "TPS" and info["evaluated"]["description"] == "MCNP"
    assert info["pass_rate"] == 100.0 and meta["ImagePositionPatient"] == [-6.0, -6.0, -6.0]
    assert series["3DMatrix"].dtype == np.float32 and series["3DMatrix"].shape == (13, 13, 13)
    json.dumps(info)                                            # plain values (saved with the project)
