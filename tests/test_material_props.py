import pytest
from PySide6.QtWidgets import QTableWidgetItem

import fcn_init.create_3D_database_tab as m
from fcn_3DPrinting import material_props as mp


def test_material_db_map_and_reference_values(app_stub):
    db = mp.get_material_db_map(app_stub)
    assert set(db) == {"Maastro Bone", "PolyLite PLA White"}
    assert db["Maastro Bone"]["red"] == 1.38 and db["Maastro Bone"]["zeff_std"] == 0.14
    ref = mp.get_material_reference_values(app_stub, "Maastro Bone")
    assert ref["red"].value == 1.38 and ref["red"].source == "database" and not ref["red"].is_missing
    missing = mp.get_material_reference_values(app_stub, "Nope")
    assert missing["red"].is_missing and missing["zeff"].source == "missing"


def test_mix_components_prefer_matmix_then_database(app_stub):
    comps = mp.get_mix_components(app_stub, 1)
    assert [c["name"] for c in comps] == ["Maastro Bone", "PolyLite PLA White"]
    assert comps[0]["red"].source == "matmix" and comps[0]["red"].value == 1.38
    assert comps[0]["red"].std == 0.045                      # std only exists in the database row

    # blank the MatMix cell -> falls back to the database value
    app_stub.table_mat_mix.setItem(1, 3, QTableWidgetItem(""))
    comps = mp.get_mix_components(app_stub, 1)
    assert comps[1]["red"].source == "database" and comps[1]["red"].value == 1.12

    # zero in both places -> flagged missing
    app_stub.table_3d_db.setItem(1, 6, QTableWidgetItem("0"))
    comps = mp.get_mix_components(app_stub, 1)
    assert comps[1]["red"].is_missing

    assert mp.get_mix_component_reference_values(app_stub, 99) == (None, None)
    reds, zeffs = mp.get_mix_component_reference_values(app_stub, 1)
    assert reds == [1.38, 0.0] and zeffs == [11.7, 6.4]


def test_predictors_match_legacy_functions(app_stub):
    app_stub.current_viewed_mix_id = 1
    for ratios in ([50, 50], [30, 70], [100, 0]):
        legacy_zeff = m.calculate_mix_zeff_predicted_val(app_stub, ratios)
        assert mp.predict_mix_zeff_for(app_stub, 1, ratios) == pytest.approx(legacy_zeff)
        for infill in (80.0, 100.0):
            legacy_red = m.calculate_mix_red_predicted_val(app_stub, ratios, infill)
            assert mp.predict_mix_red_for(app_stub, 1, ratios, infill) == pytest.approx(legacy_red)


def test_power_law_with_m_equal_one_is_linear():
    assert mp.predict_mix_zeff([10.0, 6.0], [25, 75], 1.0) == pytest.approx(7.0)
    assert mp.predict_mix_zeff([10.0, 6.0], [25, 75], 0.0) == 0.0
    assert mp.predict_mix_red([1.4, 1.0], [50, 50]) == pytest.approx(1.2)
    assert mp.fit_red_vs_infill([(80, 1.0), (100, 1.2)]) == pytest.approx({"slope": 0.01, "intercept": 0.2, "n": 2})
    assert mp.fit_red_vs_infill([(100, 1.0), (100, 1.1)]) is None


def test_summaries_and_html(app_stub):
    s = mp.summarize_material(app_stub, "Maastro Bone")
    assert s["n_cal_rows"] == 1 and s["infill_levels"] == [100.0] and s["kv_pairs"] == [("80", "140")]
    assert s["used_in_mixes"][0]["mix_id"] == 1
    # default calibration row has RED 1.0 vs reference 1.38 -> deviation warning
    assert any("deviates" in w for w in s["warnings"])
    html = mp.render_material_overview_html(s)
    assert "Maastro Bone" in html and "Bone/PLA" in html and "deviates" in html

    s2 = mp.summarize_material(app_stub, "PolyLite PLA White")
    assert "No calibration measurements recorded." in s2["warnings"]

    mix = mp.summarize_mix(app_stub, 1)
    assert mix["name"] == "Bone/PLA" and mix["m_value"] == 3.4
    assert mix["n_cal_rows"] == 1 and mix["cal_rows"][0]["ratios"] == [50.0, 50.0]
    assert mix["cal_rows"][0]["pred_red"] == pytest.approx(1.25)
    assert len(mix["red_ratio_combos"]) == 3 and mix["red_ratio_combos"][1]["n_rows"] == 3
    assert mix["warnings"] == []
    html = mp.render_mix_overview_html(mix)
    assert "Bone/PLA" in html and "PolyLite PLA White" in html and "No issues detected" in html

    app_stub.mix_calibration_cache[1][0][0] = "40.0000,50.0000"
    mix = mp.summarize_mix(app_stub, 1)
    assert any("sum to 90.00%" in w for w in mix["warnings"])
