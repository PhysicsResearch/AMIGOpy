import itertools

import numpy as np
import pytest
from PySide6.QtWidgets import QCheckBox, QComboBox, QLineEdit, QMainWindow, QTableWidget, QTableWidgetItem

import fcn_init.create_3D_database_tab as m
from fcn_3DPrinting import add_to_cal_mat_db as bridge
from fcn_3DPrinting import db_schema as schema


def _roi_table(headers, rows):
    table = QTableWidget(len(rows), len(headers))
    table.setHorizontalHeaderLabels(headers)
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            table.setItem(r, c, QTableWidgetItem(str(value)))
    return table


def test_parse_headers_single_series(qapp):
    headers = ["Mean_L0", "STD_L0", "N_L0", "Mean_L1", "STD_L1", "N_L1", "Mean_L2", "STD_L2", "N_L2", "Mean_L3", "STD_L3", "N_L3"]
    table = _roi_table(headers, [[352.28, 13.84, 1902, 252.56, 13.07, 1902, 1.2094, 0.0107, 1902, 9.192, 0.0888, 1902]])
    sources, vertical = bridge.parse_roi_value_sources(table)
    assert not vertical and [s.key for s in sources] == ["L0", "L1", "L2", "L3"]
    roles = bridge.default_role_assignment(sources)
    assert [roles[r].key for r in bridge.ROLES] == ["L0", "L1", "L2", "L3"]
    rows = bridge.read_roi_rows(table, sources, vertical)
    assert rows[0]["values"]["L2"] == {"mean": 1.2094, "std": 0.0107, "n": 1902}
    mv = bridge.measurements_for_row(rows[0], roles)
    assert mv["hu_low"] == 352.28 and mv["hu_high"] == 252.56 and mv["zeff"] == 9.192 and not mv["from_dect"]


def test_parse_headers_multi_series_prefix_and_vertical(qapp):
    headers = ["S3_Mean_L0", "S3_STD_L0", "S3_N_L0", "S7_Mean_L0", "S7_STD_L0", "S7_N_L0"]
    table = _roi_table(headers, [[100, 1, 5, 200, 2, 5]])
    sources, vertical = bridge.parse_roi_value_sources(table)
    assert [s.key for s in sources] == ["S3_L0", "S7_L0"] and not vertical
    roles = bridge.default_role_assignment(sources, {"S3": 140.0, "S7": 80.0})
    assert roles["hu_low"].key == "S7_L0" and roles["hu_high"].key == "S3_L0" and roles["red"] is None
    roles = bridge.default_role_assignment(sources, {})
    assert roles["hu_low"].key == "S3_L0"  # falls back to series order

    table = _roi_table(["Series", "Mean_L0", "STD_L0", "N_L0"], [["Series 3", 10, 1, 4], ["Series 7", 20, 2, 4]])
    sources, vertical = bridge.parse_roi_value_sources(table)
    assert vertical and [s.key for s in sources] == ["L0"]
    rows = bridge.read_roi_rows(table, sources, vertical)
    assert [r["series_label"] for r in rows] == ["Series 3", "Series 7"] and rows[1]["values"]["L0"]["mean"] == 20.0


class _FakeDect(QMainWindow):
    """Just the widgets creat_DECT_derived_maps reads, plus a tiny two-series image."""

    def __init__(self, red_method, zeff_method, hu_low, hu_high):
        super().__init__()
        self.RED_method_list = QComboBox(); self.RED_method_list.addItems(["Saito", "Hunemohr"])
        self.RED_method_list.setCurrentText(red_method)
        self.Zeff_method_list = QComboBox(); self.Zeff_method_list.addItems(["Saito", "Hunemohr"])
        self.Zeff_method_list.setCurrentText(zeff_method)
        self.Zeff_m = QLineEdit("3.1")
        self.RED_fit_01_text = QLineEdit("0.9950" if red_method == "Saito" else "0.6200")
        self.RED_fit_02_text = QLineEdit("0.4300")
        self.RED_fit_03_text = QLineEdit("1.0010")
        self.Zeff_fit_01_text = QLineEdit("1.0450" if zeff_method == "Saito" else "0.8500")
        self.Zeff_fit_02_text = QLineEdit("-0.0120")
        self.checkBox_Im_RED = QCheckBox(); self.checkBox_Im_RED.setChecked(True)
        self.checkBox_Im_Zeff = QCheckBox(); self.checkBox_Im_Zeff.setChecked(True)
        self.checkBox_Im_I = QCheckBox()
        self.checkBox_Im_SPR = QCheckBox()
        self.scatter_plot_im_01 = QComboBox(); self.scatter_plot_im_01.addItems(["L", "H"]); self.scatter_plot_im_01.setCurrentIndex(0)
        self.scatter_plot_im_02 = QComboBox(); self.scatter_plot_im_02.addItems(["L", "H"]); self.scatter_plot_im_02.setCurrentIndex(1)
        self.series_info_dict = {0: ("L", "p", "s", "CT", 0), 1: ("H", "p", "s", "CT", 1)}

        def series(matrix):
            return {"3DMatrix": matrix, "SeriesNumber": 1, "metadata": {"ImageComments": "x", "DCM_Info": {}}}
        self.medical_image = {"p": {"s": {"CT": [series(hu_low), series(hu_high)]}}}


@pytest.mark.parametrize("red_method,zeff_method", list(itertools.product(["Saito", "Hunemohr"], repeat=2)))
def test_scalar_hu_conversion_matches_dect_matrix_code(qapp, red_method, zeff_method, monkeypatch):
    import fcn_DECT.create_process_dect as dect_mod
    monkeypatch.setattr(dect_mod, "populate_medical_image_tree", lambda *a, **k: None)
    hu_low = np.array([[[-950.0, -100.0], [40.0, 350.0]], [[60.0, 800.0], [1200.0, 20.0]]], dtype=np.float32)
    hu_high = np.array([[[-940.0, -80.0], [45.0, 250.0]], [[55.0, 600.0], [900.0, 25.0]]], dtype=np.float32)
    fake = _FakeDect(red_method, zeff_method, hu_low, hu_high)
    dect_mod.creat_DECT_derived_maps(fake)
    ct = fake.medical_image["p"]["s"]["CT"]
    red_map, zeff_map = ct[-2]["3DMatrix"], ct[-1]["3DMatrix"]

    params = bridge.get_dect_fit_parameters(fake)
    assert params["red_method"] == red_method and params["m"] == 3.1
    for idx in np.ndindex(hu_low.shape):
        red, zeff = bridge.red_zeff_from_hu(float(hu_low[idx]), float(hu_high[idx]), params)
        assert red == pytest.approx(float(red_map[idx]), rel=1e-5, abs=1e-6)
        assert zeff == pytest.approx(float(zeff_map[idx]), rel=1e-4, abs=1e-5)


def test_dect_parameters_unavailable_without_widgets(qapp):
    bare = QMainWindow()
    with pytest.raises(bridge.DectFitUnavailable):
        bridge.get_dect_fit_parameters(bare)
    bare.RED_method_list = QComboBox(); bare.RED_method_list.addItems(["Saito"])
    bare.Zeff_method_list = QComboBox(); bare.Zeff_method_list.addItems(["Saito"])
    bare.Zeff_m = QLineEdit("")
    with pytest.raises(bridge.DectFitUnavailable):
        bridge.get_dect_fit_parameters(bare)
    assert bridge.zeff_water(3.1) == pytest.approx(7.45, abs=0.05)
    assert bridge.red_zeff_from_hu(0.0, 0.0, {"red_method": "Hunemohr", "zeff_method": "Saito", "m": 3.1, "ce": 0.5, "g": 1.0, "g0": 0.0})[0] == pytest.approx(1.0)
    # negative or non-finite bases must not produce complex numbers (numpy gives nan -> 0 in the DECT code)
    assert bridge._root(-1.0, 3.1) == 0.0 and bridge._root(float("nan"), 3.1) == 0.0 and bridge._root(8.0, 3.0) == pytest.approx(2.0)
    zero_red = {"red_method": "Saito", "zeff_method": "Saito", "m": 3.1, "a": 1.0, "alpha": 0.4, "b": 0.0, "g": 1.0, "g0": 0.0}
    assert bridge.red_zeff_from_hu(0.0, 0.0, zero_red) == (0.0, 0.0)


def test_row_builders_and_commits(app_stub, qapp):
    headers = ["Mean_L0", "STD_L0", "N_L0", "Mean_L1", "STD_L1", "N_L1", "Mean_L2", "STD_L2", "N_L2", "Mean_L3", "STD_L3", "N_L3"]
    table = _roi_table(headers, [
        [300, 10, 500, 200, 9, 500, 1.20, 0.01, 500, 9.0, 0.1, 500],
        [100, 5, 500, 80, 4, 500, 1.05, 0.02, 500, 7.5, 0.2, 500],
    ])
    sources, vertical = bridge.parse_roi_value_sources(table)
    roles = bridge.default_role_assignment(sources)
    roi_rows = bridge.read_roi_rows(table, sources, vertical)
    per_row = {0: {"infill": 100, "flow": 100, "use": True}, 1: {"infill": 80, "flow": 95, "use": True}}
    settings = {"Print Temp": 215, "Infill Pattern": "Gyroid", "Shape": "Cube", "Layer Height": 0.15}

    rows = bridge.build_material_cal_rows(roi_rows, roles, "90", "150", settings, per_row)
    assert len(rows) == 2 and all(len(r) == 20 for r in rows)
    d = schema.row_to_dict(schema.MATERIAL_CAL_FIELDS, rows[1])
    assert d["kV_low"] == "90" and d["HU_low"] == "100.0000" and d["HU_hig_STD"] == "4.0000"
    assert d["RED"] == "1.0500" and d["Zeff"] == "7.5000" and d["Infill Density"] == "80.0000" and d["Flow"] == "95.0000"
    assert d["Infill Pattern"] == "Gyroid" and d["Shape"] == "Cube" and d["Print Temp"] == "215.0000" and d["Line Width"] == "0.4000"

    per_row[1]["use"] = False
    mix_rows = bridge.build_mix_red_rows(app_stub, 1, [50, 50], roi_rows, roles, 90.0, 150.0, per_row)
    assert len(mix_rows) == 1 and len(mix_rows[0]) == 14
    md = schema.row_to_dict(schema.MIX_RED_FIELDS, mix_rows[0])
    assert md["Infill %"] == "100.0000" and md["HU-Low"] == "300.0000" and md["kV - Low"] == "90.0000"
    from fcn_3DPrinting import material_props as props
    assert float(md["Pred. RED"]) == pytest.approx(props.predict_mix_red_for(app_stub, 1, [50, 50], 100.0), abs=1e-4)
    assert float(md["Pred. Zeff"]) == pytest.approx(props.predict_mix_zeff_for(app_stub, 1, [50, 50]), abs=1e-4)

    cal_rows = bridge.build_mix_cal_rows(roi_rows, roles, [30, 70], "90", "150", settings, per_row)
    assert len(cal_rows) == 1 and len(cal_rows[0]) == 20 and cal_rows[0][0] == "30.0000,70.0000"
    cd = schema.row_to_dict(schema.MIX_CAL_FIELDS, cal_rows[0][1:])
    assert cd["Infill Type"] == "Gyroid" and cd["Print Temp"] == "215.0000"

    # commits update the caches and write the databases
    n_before = len(app_stub.calibration_data_cache["Maastro Bone"])
    bridge.commit_to_material(app_stub, "Maastro Bone", rows)
    assert len(app_stub.calibration_data_cache["Maastro Bone"]) == n_before + 2
    bridge.commit_to_mix_red(app_stub, 1, 1, mix_rows)
    assert len(app_stub.mix_red_cache[1][1]["rows"]) == 4
    bridge.commit_to_mix_cal(app_stub, 1, cal_rows)
    assert len(app_stub.mix_calibration_cache[1]) == 2
    import os
    assert os.path.exists(m.get_cal_db_path()) and os.path.exists(m.get_mix_red_db_path())


def test_dect_rows_use_computed_values_and_std_propagation(qapp):
    headers = ["Mean_L0", "STD_L0", "N_L0", "Mean_L1", "STD_L1", "N_L1"]
    table = _roi_table(headers, [[300, 10, 50, 200, 9, 50]])
    sources, vertical = bridge.parse_roi_value_sources(table)
    roles = bridge.default_role_assignment(sources)
    roi_rows = bridge.read_roi_rows(table, sources, vertical)
    dect = {"red_method": "Hunemohr", "zeff_method": "Hunemohr", "m": 3.1, "ce": 0.6, "de": 0.85}
    mv = bridge.measurements_for_row(roi_rows[0], roles, dect, propagate_std=False)
    assert mv["from_dect"] and mv["red"] == pytest.approx(0.6 * 1.3 + 0.4 * 1.2) and mv["red_std"] == 0.0
    mv2 = bridge.measurements_for_row(roi_rows[0], roles, dect, propagate_std=True)
    assert mv2["red_std"] > 0 and mv2["zeff_std"] > 0
    rows = bridge.build_material_cal_rows(roi_rows, roles, "80", "140", {}, None, dect, True)
    d = schema.row_to_dict(schema.MATERIAL_CAL_FIELDS, rows[0])
    assert float(d["RED"]) == pytest.approx(mv["red"], abs=1e-4) and float(d["RED_STD"]) > 0


def test_dialog_builds_and_previews_without_blocking(app_stub, monkeypatch):
    from PySide6.QtWidgets import QDialog, QMessageBox
    headers = ["Mean_L0", "STD_L0", "N_L0", "Mean_L1", "STD_L1", "N_L1", "Mean_L2", "STD_L2", "N_L2", "Mean_L3", "STD_L3", "N_L3"]
    app_stub.table_roi_c_values = _roi_table(headers, [
        [300, 10, 500, 200, 9, 500, 1.20, 0.01, 500, 9.0, 0.1, 500],
        [100, 5, 500, 80, 4, 500, 1.05, 0.02, 500, 7.5, 0.2, 500],
    ])
    app_stub.current_viewed_filament = "Maastro Bone"
    built = {}

    def fake_exec(dialog):
        built["dialog"] = dialog
        return QDialog.Rejected
    monkeypatch.setattr(QDialog, "exec", fake_exec)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: built.setdefault("warnings", []).append(a[2]))

    bridge.open_add_roi_to_3dp_dialog(app_stub)
    assert "dialog" in built and "warnings" not in built
    tables = built["dialog"].findChildren(QTableWidget)
    preview = next(t for t in tables if t.columnCount() == 12)
    assert preview.rowCount() == 2
    assert preview.item(0, 3).text() == "300.0" and preview.item(1, 7).text() == "1.0500"

    # without ROI data the dialog refuses politely
    app_stub.table_roi_c_values.setRowCount(0)
    bridge.open_add_roi_to_3dp_dialog(app_stub)
    assert built["warnings"] and "Get Data" in built["warnings"][-1]
