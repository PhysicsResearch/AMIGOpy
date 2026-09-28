import json

import pytest
from PySide6.QtWidgets import QSpinBox

import fcn_init.create_3D_database_tab as m
from fcn_3DPrinting import matmix_package as pkgmod
from fcn_3DPrinting import material_props as props


def _material_names(stub):
    return [stub.table_3d_db.item(r, 0).text() for r in range(stub.table_3d_db.rowCount())]


def _mix_ids(stub):
    ids = []
    for r in range(stub.table_mat_mix.rowCount()):
        spin = stub.table_mat_mix.cellWidget(r, 0)
        if isinstance(spin, QSpinBox):
            ids.append(spin.property("mix_id"))
    return ids


def test_material_package_round_trip(app_stub, tmp_path):
    item = pkgmod.build_material_item(app_stub, "Maastro Bone")
    assert item["material"]["red"] == 1.38 and item["calibration"][0]["Infill Pattern"] == "Grid"
    path = tmp_path / pkgmod.suggested_file_name("Maastro Bone")
    pkgmod.write_package(str(path), pkgmod.build_package([item]))
    pkg = pkgmod.read_package(str(path))
    assert pkg["schema_version"] == 1 and pkgmod.validate_package(pkg) == []

    # remove the material locally, then import it back
    app_stub.table_3d_db.removeRow(0)
    del app_stub.calibration_data_cache["Maastro Bone"]
    del app_stub.notes_cache["Maastro Bone"]
    plan = pkgmod.plan_import(app_stub, pkg)
    assert [a.action for a in plan.actions] == ["add"]
    result = pkgmod.apply_import(app_stub, pkg, plan)
    assert result.added_materials == ["Maastro Bone"]
    assert "Maastro Bone" in _material_names(app_stub)
    assert app_stub.calibration_data_cache["Maastro Bone"][0][13] == "Grid"
    assert app_stub.notes_cache["Maastro Bone"] == "hello"
    assert props.get_material_reference_values(app_stub, "Maastro Bone")["red"].value == 1.38


def test_material_conflict_modes(app_stub):
    pkg = pkgmod.build_package([pkgmod.build_material_item(app_stub, "Maastro Bone")])
    pkg["items"][0]["material"]["brand"] = "Changed"
    pkg["items"][0]["notes"] = "new notes"

    plan = pkgmod.plan_import(app_stub, pkg, "skip")
    assert plan.actions[0].action == "skip"
    result = pkgmod.apply_import(app_stub, pkg, plan)
    assert result.skipped == ["Maastro Bone"] and app_stub.notes_cache["Maastro Bone"] == "hello"

    plan = pkgmod.plan_import(app_stub, pkg, "rename")
    assert plan.actions[0].action == "rename" and plan.actions[0].new_name == "Maastro Bone (imported 1)"
    result = pkgmod.apply_import(app_stub, pkg, plan)
    assert "Maastro Bone (imported 1)" in _material_names(app_stub)
    assert app_stub.notes_cache["Maastro Bone (imported 1)"] == "new notes"
    assert app_stub.notes_cache["Maastro Bone"] == "hello"

    plan = pkgmod.plan_import(app_stub, pkg, "overwrite")
    result = pkgmod.apply_import(app_stub, pkg, plan)
    assert result.overwritten == ["Maastro Bone"]
    assert props.get_material_db_map(app_stub)["Maastro Bone"]["brand"] == "Changed"
    assert app_stub.notes_cache["Maastro Bone"] == "new notes"
    assert _material_names(app_stub).count("Maastro Bone") == 1


def test_mix_package_recreates_missing_components_and_gets_fresh_id(app_stub):
    item = pkgmod.build_mix_item(app_stub, 1, include_component_calibration=True)
    assert item["mix"]["name"] == "Bone/PLA" and [c["name"] for c in item["components"]] == ["Maastro Bone", "PolyLite PLA White"]
    assert item["components"][0]["reference"]["zeff"] == 11.7
    assert item["calibration"][0]["ratios"] == [50.0, 50.0]
    assert len(item["red_ratio_combos"]) == 3 and item["red_ratio_combos"][0]["rows"][0]["Infill %"] == "80"
    pkg = json.loads(json.dumps(pkgmod.build_package([item])))  # simulate a file round trip

    # wipe the local MatMix data and one of the component materials
    app_stub.table_mat_mix.setRowCount(0)
    app_stub.mix_calibration_cache.clear(); app_stub.mix_notes_cache.clear()
    app_stub.mix_m_value_cache.clear(); app_stub.mix_red_cache.clear()
    app_stub.table_3d_db.removeRow(1)
    del app_stub.calibration_data_cache["Maastro Bone"]

    plan = pkgmod.plan_import(app_stub, pkg)
    kinds = [(a.kind, a.action, a.synthesized) for a in plan.actions]
    assert ("material", "add", True) in kinds and ("mix", "add", False) in kinds
    assert any("PolyLite PLA White" in w for w in plan.warnings)

    result = pkgmod.apply_import(app_stub, pkg, plan)
    assert result.added_mix_ids == [0]
    assert "PolyLite PLA White" in _material_names(app_stub)
    assert _mix_ids(app_stub) == [0]
    comps = props.get_mix_components(app_stub, 0)
    assert [c["name"] for c in comps] == ["Maastro Bone", "PolyLite PLA White"]
    assert comps[1]["zeff"].value == 6.4
    assert app_stub.mix_calibration_cache[0][0][0] == "50.0000,50.0000"
    assert app_stub.mix_m_value_cache[0] == 3.4 and app_stub.mix_notes_cache[0] == "mix notes"
    assert len(app_stub.mix_red_cache[0]) == 3 and app_stub.mix_red_cache[0][2]["percentage"] == [0.0, 100.0]
    assert app_stub.mix_red_cache[0][0]["rows"][0][0] == "80.0000"
    assert props.get_mix_name(app_stub, 0) == "Bone/PLA"

    # importing the same mix again: rename mode adds a second group with a fresh id
    plan = pkgmod.plan_import(app_stub, pkg, "rename")
    mix_action = next(a for a in plan.actions if a.kind == "mix")
    assert mix_action.action == "add" and mix_action.new_name == "Bone/PLA (imported)"
    pkgmod.apply_import(app_stub, pkg, plan)
    assert _mix_ids(app_stub) == [0, 1]

    # overwrite mode replaces the caches of the existing mix in place
    pkg["items"][0]["notes"] = "replaced"
    plan = pkgmod.plan_import(app_stub, pkg, "overwrite")
    mix_action = next(a for a in plan.actions if a.kind == "mix")
    assert mix_action.action == "overwrite" and mix_action.existing_id == 0
    pkgmod.apply_import(app_stub, pkg, plan)
    assert app_stub.mix_notes_cache[0] == "replaced" and _mix_ids(app_stub) == [0, 1]


def test_validate_and_read_errors(tmp_path):
    assert pkgmod.validate_package({"kind": "x"}) != []
    assert "no items" in " ".join(pkgmod.validate_package({"kind": pkgmod.PACKAGE_KIND, "schema_version": 1, "items": []}))
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    with pytest.raises(pkgmod.PackageError):
        pkgmod.read_package(str(bad))
    wrong = tmp_path / "wrong.json"
    wrong.write_text(json.dumps({"kind": "other", "schema_version": 1, "items": [{"kind": "material", "material": {}}]}))
    with pytest.raises(pkgmod.PackageError):
        pkgmod.read_package(str(wrong))


def test_numeric_strings_and_missing_fields_are_tolerated(app_stub):
    pkg = pkgmod.build_package([{
        "kind": "material",
        "material": {"name": "Loose PLA", "red": "1,05", "zeff": 6},
        "calibration": [{"HU_low": "12.5", "Shape": "Cube"}],
    }])
    assert pkgmod.validate_package(pkg) == []
    result = pkgmod.apply_import(app_stub, pkg, pkgmod.plan_import(app_stub, pkg))
    assert result.added_materials == ["Loose PLA"]
    assert props.get_material_reference_values(app_stub, "Loose PLA")["red"].value == 1.05
    row = app_stub.calibration_data_cache["Loose PLA"][0]
    assert len(row) == 20 and row[2] == "12.5000" and row[16] == "Cube" and row[13] == "Grid"
    assert "Loose PLA" in pkgmod.summarize_result(result)
