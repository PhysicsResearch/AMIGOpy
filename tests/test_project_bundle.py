"""
AMIGOpy bundles (File > Save, File > Open > AMIGOpy): the bundle with the MonteCarlo settings (grids,
material assignment, MCNP options), old bundles, and renaming / deleting density, material and MCNP
lattice maps from the data tree.
"""
from types import SimpleNamespace

import numpy as np

from fcn_init.init_data_tree import delete_series_map, rename_series_map
from fcn_load.project_settings import GRID_PREFIXES, TALLIES, apply_project_settings, collect_project_settings
from fcn_load.save_load import BUNDLE_KEY, unpack_bundle


def test_old_and_new_bundles():
    mi = {"P": {"S": {"CT": [{"3DMatrix": np.zeros(2)}]}}}
    image, settings = unpack_bundle(mi)                  # version 1: the medical_image itself
    assert image is mi and settings == {}
    image, settings = unpack_bundle({BUNDLE_KEY: 2, "medical_image": mi, "settings": {"mcnp": {"nps": "1e7"}}})
    assert image is mi and settings == {"mcnp": {"nps": "1e7"}}


def _window():
    """The MonteCarlo tab widgets the settings use (ranges narrower than the values restored)."""
    from PySide6.QtWidgets import QCheckBox, QComboBox, QDoubleSpinBox, QLineEdit, QWidget
    w = QWidget()
    for prefix in GRID_PREFIXES:
        for a in "xyz":
            for k in ("min", "max", "res"):
                sb = QDoubleSpinBox()
                sb.setRange(0, 99)
                sb.setValue(1.0 if k == "res" else 0.0)
                setattr(w, f"{prefix}_{a}{k}", sb)
        setattr(w, f"{prefix}_display", QCheckBox())
    w.mc_grid_mode_combo = QComboBox()
    w.mc_grid_mode_combo.addItems(["voxel", "mm"])
    w.mcnp_source_combo = QComboBox()
    w.mcnp_source_combo.addItems(["None (External beam / custom)", "GammaMedPlus", "TG-186"])
    w.mcnp_nps_input = QLineEdit("1e6")
    for name in TALLIES + ("mcnp_chk_std_cards",):
        setattr(w, name, QCheckBox())
    return w


def test_montecarlo_settings_come_back(qapp):
    w = _window()
    w.mc_grid_mode_combo.setCurrentText("mm")
    for prefix, values in (("mc_vox", (190, 247, 66, 88, 261, 339)), ("mc_grid", (-71.5, -17.2, -30, 32.5, -250, -176))):
        for (a, k), v in zip(((a, k) for a in "xyz" for k in ("min", "max")), values):
            sb = getattr(w, f"{prefix}_{a}{k}")
            sb.setRange(-999, 999)
            sb.setValue(v)
    for a, v in zip("xyz", (1.0, 2.5, 0.5)):
        getattr(w, f"mc_grid_{a}res").setValue(v)
    w.mc_grid_display.setChecked(True)
    w.mcnp_source_combo.setCurrentText("TG-186")
    w.mcnp_nps_input.setText("2e8")
    w.mcnp_chk_dwater_med.setChecked(True)
    w.mcnp_chk_dmed_med_ed.setChecked(True)
    w.mcnp_chk_std_cards.setChecked(True)
    settings = collect_project_settings(w)

    fresh = _window()
    assert collect_project_settings(fresh) != settings
    assert apply_project_settings(fresh, settings) == []
    assert collect_project_settings(fresh) == settings


def test_older_bundle_mm_grid_z_was_dicom_y(qapp):
    # bundles saved before the MCNP axes in the MonteCarlo tab: mm mode Z held DICOM y, now Z = -DICOM y
    w = _window()
    old = {"grid_mode": "mm", "grids": {"mc_grid": {"bounds": [-71.5, -17.2, -30, 32.5, 176, 250]},
                                        "mc_vox": {"bounds": [190, 247, 66, 88, 261, 339]}}}
    assert apply_project_settings(w, old) == []
    assert [w.mc_grid_zmin.value(), w.mc_grid_zmax.value()] == [-250, -176]
    assert [w.mc_vox_zmin.value(), w.mc_vox_zmax.value()] == [261, 339]          # voxel indices: as saved
    assert collect_project_settings(w)["grid_axes"] == 2


def _app():
    lattice = {"3DMatrix": np.zeros(1), "universes": [],
               "metadata": {"material_map": "mat_map_0", "density_map": "map_Density_0"}}
    series = {"mat_maps": {"mat_map_0": {"3DMatrix": np.zeros(1)}, "mat_map_1": {"3DMatrix": np.ones(1)}},
              "density_maps": {"map_Density_0": {"3DMatrix": np.zeros(1), "type": "Density"}},
              "mcnp_lattice_maps": {"mcnp_lattice_0": lattice}}
    return SimpleNamespace(medical_image={"P": {"S": {"CT": [series]}}}, last_selected_mat_map="mat_map_0"), series


def test_rename_map_keeps_its_place_and_its_references():
    app, series = _app()
    assert rename_series_map(app, "P", "S", "CT", 0, "Material maps", "mat_map_0", "Pelvis HU")
    assert list(series["mat_maps"]) == ["Pelvis HU", "mat_map_1"]
    assert series["mcnp_lattice_maps"]["mcnp_lattice_0"]["metadata"]["material_map"] == "Pelvis HU"
    assert app.last_selected_mat_map == "Pelvis HU"
    assert rename_series_map(app, "P", "S", "CT", 0, "Density maps", "map_Density_0", "CT density")
    assert series["mcnp_lattice_maps"]["mcnp_lattice_0"]["metadata"]["density_map"] == "CT density"
    assert rename_series_map(app, "P", "S", "CT", 0, "MCNP lattice maps", "mcnp_lattice_0", "Pelvis lattice")
    assert list(series["mcnp_lattice_maps"]) == ["Pelvis lattice"]
    # taken, empty or unknown names are refused
    assert not rename_series_map(app, "P", "S", "CT", 0, "Material maps", "mat_map_1", "Pelvis HU")
    assert not rename_series_map(app, "P", "S", "CT", 0, "Material maps", "mat_map_1", "")
    assert not rename_series_map(app, "P", "S", "CT", 0, "Density maps", "nope", "x")


def test_delete_map_and_its_empty_folder():
    app, series = _app()
    delete_series_map(app, "P", "S", "CT", 0, "Material maps", "mat_map_0")
    assert list(series["mat_maps"]) == ["mat_map_1"]
    delete_series_map(app, "P", "S", "CT", 0, "MCNP lattice maps", "mcnp_lattice_0")
    assert "mcnp_lattice_maps" not in series             # the folder goes with its last map
