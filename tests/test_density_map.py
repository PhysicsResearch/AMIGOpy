"""
Density Map tab: HU tables (fcn_ctcal.ct_cal: one CSV per table in AppData with its type, every edit
saved, New / Duplicate / Rename / Delete, graph in the Figures menu style with Hold plot) and density
maps (fcn_densitymap.density_map: HU table values, the material map as reference and the non-tissue
override with the values of the material database).
"""
import os
import shutil
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
from PySide6.QtWidgets import QCheckBox, QComboBox, QInputDialog, QMessageBox, QTableWidget, QWidget

from fcn_ctcal import ct_cal
from fcn_densitymap import density_map
from fcn_densitymap.density_map import build_density_map, compute_density, fixed_flags

BUNDLED = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fcn_ctcal", "ct_cal_curves")


@pytest.fixture
def store(tmp_path, monkeypatch):
    """The HU tables and settings.json in a temporary AppData folder (the bundled tables copied there)."""
    from fcn_materialassignment import hu_lut, material_assignment_properties
    monkeypatch.setattr(material_assignment_properties, "get_appdata_path", lambda: str(tmp_path))
    monkeypatch.setattr(hu_lut, "_settings_path", lambda: str(tmp_path / "settings.json"))
    for name in ("warning", "information", "critical"):
        monkeypatch.setattr(QMessageBox, name, staticmethod(lambda *a, **k: None))
    return tmp_path / "ct_cal_curves"


@pytest.fixture
def tab(qapp, store):
    """Main window stand-in with the Density Map tab widgets, the last used table shown."""
    w = SimpleNamespace(ct_cal_list=QComboBox(), ct_cal_type=QComboBox(), ct_cal_table=QTableWidget(),
                        ct_cal_hold=QCheckBox(), ct_cal_plot=QWidget(), selected_background="White")
    for key, (label, _) in ct_cal.TYPES.items():
        w.ct_cal_type.addItem(label, key)
    w.ct_cal_list.currentTextChanged.connect(lambda name: ct_cal.select_ct_cal_table(w, name))
    w.ct_cal_table.itemChanged.connect(lambda _i: ct_cal.on_ct_cal_table_edited(w))
    w.ct_cal_type.currentIndexChanged.connect(lambda _i: ct_cal.on_ct_cal_type_changed(w))
    w.ct_cal_hold.toggled.connect(lambda _c: ct_cal.on_ct_cal_hold_toggled(w))
    ct_cal.init_ct_cal_selector(w)
    return w


def test_bundled_tables_copied_with_their_types(store):
    assert ct_cal.list_tables() == ["MAASTRO_CT_2_2023_MASS", "MAASTRO_CT_2_2023_red"]
    kind, rows = ct_cal.read_table(str(store / "MAASTRO_CT_2_2023_MASS.csv"))
    assert kind == "DENSITY" and rows[0] == (-1024.0, 0.001) and len(rows) == 10
    assert ct_cal.read_table(str(store / "MAASTRO_CT_2_2023_red.csv"))[0] == "RED"


def test_table_files_read_as_older_versions_do(tmp_path):
    path = str(tmp_path / "t.csv")
    ct_cal.write_table(path, "SPR", [(-1000.0, 0.001), (0.0, 1.0), (1200.0, 1.7)])
    old = pd.read_csv(path, skiprows=[0])             # how AMIGOpy read the tables before
    assert old.columns.tolist() == ["HU", "SPR"] and old["SPR"].tolist() == [0.001, 1.0, 1.7]
    (tmp_path / "semi.csv").write_text("calibration\nHU;Mass density\n-1000;0,0012\n0;1\n", encoding="utf-8")
    assert ct_cal.read_table(str(tmp_path / "semi.csv")) == ("DENSITY", ((-1000.0, 0.0012), (0.0, 1.0)))
    (tmp_path / "bad.csv").write_text("a,b\n1,2\n")
    with pytest.raises(ValueError):
        ct_cal.read_table(str(tmp_path / "bad.csv"))


def test_edits_saved_type_shown_and_changed(tab, store):
    assert tab.ct_cal_name == "MAASTRO_CT_2_2023_MASS" and tab.ct_cal_type.currentData() == "DENSITY"
    assert tab.ct_cal_table.horizontalHeaderItem(1).text() == "Mass density"
    tab.ct_cal_table.item(0, 1).setText("0.0015")                      # an edit is saved at once
    assert ct_cal.read_table(str(store / "MAASTRO_CT_2_2023_MASS.csv"))[1][0] == (-1024.0, 0.0015)
    tab.ct_cal_type.setCurrentIndex(tab.ct_cal_type.findData("SPR"))  # the type is saved with the table
    assert ct_cal.read_table(str(store / "MAASTRO_CT_2_2023_MASS.csv"))[0] == "SPR"
    tab.ct_cal_list.setCurrentText("MAASTRO_CT_2_2023_red")
    assert tab.ct_cal_type.currentText() == "RED" and tab.ct_cal_table.horizontalHeaderItem(1).text() == "RED"


def test_new_duplicate_rename_delete(tab, store, monkeypatch):
    monkeypatch.setattr(ct_cal, "_ask_new_table", lambda self, kind: ("Water RED", "RED"))
    ct_cal.new_ct_cal_table(tab)
    assert tab.ct_cal_name == "Water RED" and ct_cal.read_table(str(store / "Water RED.csv")) == \
        ("RED", ((-1000.0, 0.001), (0.0, 1.0)))
    names = iter(["Water RED 2", "Renamed"])
    monkeypatch.setattr(QInputDialog, "getText", staticmethod(lambda *a, **k: (next(names), True)))
    ct_cal.duplicate_ct_cal_table(tab)
    assert tab.ct_cal_name == "Water RED 2" and (store / "Water RED 2.csv").exists()
    ct_cal.rename_ct_cal_table(tab)
    assert tab.ct_cal_name == "Renamed" and not (store / "Water RED 2.csv").exists()
    assert tab.ct_cal_list.currentText() == "Renamed"
    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    ct_cal.delete_ct_cal_table(tab)
    assert not (store / "Renamed.csv").exists() and tab.ct_cal_name in ct_cal.list_tables()
    for name in ct_cal.list_tables():            # all deleted: the bundled tables come back
        tab.ct_cal_list.setCurrentText(name)
        ct_cal.delete_ct_cal_table(tab)
    assert "MAASTRO_CT_2_2023_MASS" in ct_cal.list_tables()


def test_graph_hold_and_figures_style(tab):
    from fcn_init.create_menu import add_figure_style_listener, trigger_mix_graph_update
    ax = tab.ax_ct_cal
    assert len(ax.lines) == 1 and ax.get_ylabel() == "Mass density (g/cm$^3$)"
    tab.ct_cal_hold.setChecked(True)
    tab.ct_cal_list.setCurrentText("MAASTRO_CT_2_2023_red")
    assert tab.ct_cal_plot_names == ["MAASTRO_CT_2_2023_MASS", "MAASTRO_CT_2_2023_red"] and len(ax.lines) == 2
    assert [line.get_label() for line in ax.lines] == ["MAASTRO_CT_2_2023_MASS (Mass density)",
                                                       "MAASTRO_CT_2_2023_red (RED)"]
    # the Figures menu: the table shown in its line colour, width and style
    tab.selected_line_color, tab.selected_line_width, tab.selected_line_style = "Green", 3.0, "Dashed"
    add_figure_style_listener(tab, "ct_cal", lambda: ct_cal.plot_ct_cal(tab))
    trigger_mix_graph_update(tab)
    shown = ax.lines[-1]
    assert (shown.get_color(), shown.get_linewidth(), shown.get_linestyle()) == ("green", 3.0, "--")
    tab.ct_cal_hold.setChecked(False)
    assert tab.ct_cal_plot_names == ["MAASTRO_CT_2_2023_red"] and len(ax.lines) == 1


# ---- density maps ------------------------------------------------------------
ROWS = [(-1000.0, 0.0012), (0.0, 1.0), (1000.0, 2.0)]
MAT_DF = pd.DataFrame({"Name": ["Air", "Water", "Cortical Bone-TG186"],
                       "Den": ["        0.0012", "        1", "        1.92"],    # as the database file loads
                       "RED": [0, 0, 0], "SPR": [0, 0, 1.75], "Tissue": [0.0, 1.0, 1.0]})


def _ct_and_material_map():
    ct = np.array([[[-990.0, -500.0, 0.0], [500.0, 1000.0, 1500.0]]], np.float32)   # (1, 2, 3)
    mat = np.array([[[0, 1, 1], [1, 2, 2]]], np.int16)                                 # Air, Water, Bone keys
    return ct, mat, {0: "Air", 1: "Water", 2: "Cortical Bone-TG186"}


def test_hu_table_values():
    ct, _, _ = _ct_and_material_map()
    values, missing = build_density_map(ct, ROWS, "DENSITY")
    assert values == pytest.approx(compute_density(ct, ct_cal.curve(ROWS)))
    assert values[0, 0] == pytest.approx([0.0012 + 10 * 0.9988 / 1000, 0.5006, 1.0], rel=1e-5)   # float32
    assert values[0, 1] == pytest.approx([1.5, 2.0, 2.5]) and missing == []


def test_material_map_reference_and_non_tissue_override():
    ct, mat, used = _ct_and_material_map()
    base = compute_density(ct, ct_cal.curve(ROWS))
    hu_table = [{"key": 0, "name": "Air", "fixed_density": True}, {"key": 1, "name": "Water", "fixed_density": False},
                {"key": 2, "name": "Cortical Bone-TG186", "fixed_density": True}]
    flags = fixed_flags(hu_table, {})
    out, missing = build_density_map(ct, ROWS, "DENSITY", MAT_DF, mat, used, flags, reference=True)
    assert out[mat == 0] == pytest.approx([0.0012]) and out[mat == 2] == pytest.approx([1.92, 1.92])
    assert out[mat == 1] == pytest.approx(base[mat == 1]) and missing == []
    # only the non-tissue override: Air from the database, the rest from the HU table
    out, _ = build_density_map(ct, ROWS, "DENSITY", MAT_DF, mat, used, flags, non_tissue=True)
    assert out[mat == 0] == pytest.approx([0.0012]) and out[mat != 0] == pytest.approx(base[mat != 0])
    # a structure without fixed density keeps the HU table values even where its material is fixed
    mask = np.zeros(ct.shape, bool)
    mask[0, 1, 2] = True
    structures = {"Implant": {"material": "Cortical Bone-TG186", "fixed_density": False}}
    out, _ = build_density_map(ct, ROWS, "DENSITY", MAT_DF, mat, used, flags, structures, {"Implant": mask}, True)
    assert out[0, 1, 1] == pytest.approx(1.92) and out[0, 1, 2] == pytest.approx(base[0, 1, 2])


def test_missing_database_values_keep_the_hu_table_value():
    ct, mat, used = _ct_and_material_map()
    rows = [(-1000.0, 0.001), (0.0, 1.0), (1000.0, 1.6)]
    out, missing = build_density_map(ct, rows, "RED", MAT_DF, mat, used, {}, reference=True)
    assert missing == ["Air", "Cortical Bone-TG186", "Water"]      # RED 0 in the database
    assert out == pytest.approx(compute_density(ct, ct_cal.curve(rows)))
    out_spr, missing_spr = build_density_map(ct, rows, "SPR", MAT_DF, mat, used, {}, reference=True)
    assert out_spr[mat == 2] == pytest.approx([1.75, 1.75]) and missing_spr == ["Air", "Water"]


def test_create_density_map_stores_type_and_how_it_was_made(tab, store, monkeypatch):
    ct, mat, used = _ct_and_material_map()
    series = {"3DMatrix": ct, "metadata": {},
              "mat_maps": {"mat_map_0": {"3DMatrix": mat, "Material_used": used,
                                         "HU_table": [{"key": 0, "name": "Air", "fixed_density": True}]}}}
    tab.medical_image, tab.patientID, tab.studyID = {"P": {"S": {"CT": [series]}}}, "P", "S"
    tab.modality, tab.series_index, tab.Mat_df = "CT", 0, MAT_DF
    shutil.copy(os.path.join(BUNDLED, "MAASTRO_CT_2_2023_MASS.csv"), store / "mass.csv")
    monkeypatch.setattr(density_map, "ask_density_map", lambda self, target: {
        "kind": "DENSITY", "table": "mass", "mat_map": "mat_map_0", "reference": True, "non_tissue": False,
        "name": "map_DENSITY_0"})
    monkeypatch.setattr(density_map, "populate_medical_image_tree", lambda self: None)
    density_map.create_density_map(tab)
    entry = series["density_maps"]["map_DENSITY_0"]
    assert entry["type"] == "DENSITY" and entry["3DMatrix"].shape == ct.shape
    assert entry["metadata"]["hu_table"] == "mass" and entry["metadata"]["material_map"] == "mat_map_0"
    assert entry["metadata"]["material_map_reference"] is True and entry["metadata"]["units"] == "g/cm3"
    assert entry["3DMatrix"][mat == 0] == pytest.approx([0.0012])
