"""
HU LUTs (fcn_materialassignment.hu_lut): the dropdown above the HU table of the Material assignment
tab. One CSV per LUT, every edit of the table saved to the LUT shown, a Default LUT on first start,
the last used LUT shown at start, and material maps' tables shown through it.
"""
import json
import os
from types import SimpleNamespace

import pandas as pd
import pytest
from PySide6.QtWidgets import QComboBox, QInputDialog, QMessageBox, QTableWidget, QWidget

from fcn_materialassignment import hu_lut
from fcn_materialassignment.material_map import (HU_C_HI, HU_C_MAT, add_mat_HU_row, get_mat_HU_ranges,
                                                 toggle_mat_HU_visibility)

MATERIALS = ["Air", "Water", "Lung-TG186", "Mean adipose-TG186", "Cortical Bone-TG186"]
OLD_HEADER = "Material,From,To,Color,Fixed Density\n"     # as the former 'Save HU LUT' wrote it


@pytest.fixture
def env(qapp, tmp_path, monkeypatch):
    """LUT folder and settings.json in a temp dir; dialogs answered from env.names / env.answer."""
    lut_dir = tmp_path / "HU_LUTs"
    lut_dir.mkdir()
    e = SimpleNamespace(dir=lut_dir, settings=tmp_path / "settings.json", names=[], messages=[],
                        answer=QMessageBox.Yes)
    monkeypatch.setattr(hu_lut, "_lut_dir", lambda: str(lut_dir))
    monkeypatch.setattr(hu_lut, "_settings_path", lambda: str(e.settings))
    monkeypatch.setattr(QInputDialog, "getText",
                        staticmethod(lambda *a, **k: (e.names.pop(0), True) if e.names else ("", False)))
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda _p, _t, text, *a: e.messages.append(text)))
    monkeypatch.setattr(QMessageBox, "warning", staticmethod(lambda _p, _t, text, *a: e.messages.append(text)))
    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: e.answer))
    return e


def _window(materials=MATERIALS):
    """The attributes of the main window the HU table and the LUT dropdown use."""
    w = QWidget()
    w.tableMatToHU = QTableWidget()
    w.hu_lut_combo = QComboBox()
    w.Mat_df = pd.DataFrame({"Name": materials})
    w.hu_lut_combo.currentTextChanged.connect(lambda name: hu_lut.select_hu_lut(w, name))
    hu_lut.init_hu_lut_selector(w)
    return w


def _write(env, name, rows):
    (env.dir / f"{name}.csv").write_text(OLD_HEADER + "".join(f"{r}\n" for r in rows), encoding="utf-8")


def _read(env, name):
    return hu_lut.read_lut(str(env.dir / f"{name}.csv"))


def _combo(w):
    c = w.hu_lut_combo
    return [c.itemText(i) for i in range(c.count())], c.currentText()


def _table(w):
    return [(d["name"], d["min"], d["max"]) for d in w.mat_HU_list]


def test_first_start_creates_the_default_lut(env):
    w = _window()
    assert hu_lut.list_luts() == ["Default"]
    assert _combo(w) == (["Default"], "Default")
    assert _table(w) == [(n, lo, hi) for n, lo, hi in hu_lut.DEFAULT_LUT_ROWS]


def test_default_lut_has_only_materials_of_the_database(env):
    w = _window([m for m in MATERIALS if m != "Lung-TG186"])
    assert [r[0] for r in _read(env, "Default")] == ["Air", "Mean adipose-TG186", "Water", "Cortical Bone-TG186"]
    assert len(w.mat_HU_list) == 4


def test_start_shows_the_last_used_lut_and_writes_nothing(env):
    _write(env, "A", ["Air,-1000.0,-200.0,,1"])
    _write(env, "B", ["Water,-200.0,80.0,#00ff00,0"])
    env.settings.write_text(json.dumps({"hu_lut": "B", "other": 1}))
    before = {f: (env.dir / f).read_bytes() for f in os.listdir(env.dir)}
    w = _window()
    assert _combo(w) == (["A", "B"], "B")
    d, = w.mat_HU_list
    assert (d["name"], d["min"], d["max"], d["color"], d["color_auto"], d["fixed_density"]) == \
        ("Water", -200.0, 80.0, "#00ff00", False, False)
    assert {f: (env.dir / f).read_bytes() for f in os.listdir(env.dir)} == before
    assert json.loads(env.settings.read_text()) == {"hu_lut": "B", "other": 1}


def test_table_edits_are_saved_to_the_lut_shown(env):
    _write(env, "A", ["Air,-1000.0,-200.0,,1"])
    _write(env, "B", ["Water,-200.0,80.0,,1"])
    w = _window()                                           # no last used LUT: the first one
    assert _combo(w) == (["A", "B"], "A")
    w.tableMatToHU.item(0, HU_C_HI).setText("-300")
    w.tableMatToHU.cellWidget(0, HU_C_MAT).setCurrentText("Water")
    add_mat_HU_row(w)                                       # material None, -300 .. -200
    assert _read(env, "A") == (("Water", -1000.0, -300.0, None, True), ("None", -300.0, -200.0, None, True))
    w.hu_lut_combo.setCurrentText("B")
    assert _table(w) == [("Water", -200.0, 80.0)]
    assert json.loads(env.settings.read_text())["hu_lut"] == "B"
    w.hu_lut_combo.setCurrentText("A")
    assert _table(w) == [("Water", -1000.0, -300.0), ("None", -300.0, -200.0)]


def test_nothing_is_written_without_a_change(env, monkeypatch):
    _write(env, "A", ["Air,-1000.0,-200.0,,1"])
    _write(env, "B", ["Water,-200.0,80.0,,1"])
    writes = []
    monkeypatch.setattr(hu_lut, "write_lut", lambda path, rows: writes.append(path))
    w = _window()
    w.hu_lut_combo.setCurrentText("B")
    toggle_mat_HU_visibility(w)                             # display state, not part of the LUT
    get_mat_HU_ranges(w)                                    # (Create Material Map)
    w.hu_lut_combo.setCurrentText("A")
    assert writes == []


def test_new_duplicate_rename_delete(env):
    _write(env, "A", ["Air,-1000.0,-200.0,,1"])
    w = _window()
    env.names += ["Bad/name", "a", "Mine"]                  # asked again until the name can be used
    hu_lut.new_hu_lut(w)
    assert len(env.messages) == 2 and env.names == []
    assert _combo(w) == (["A", "Mine"], "Mine") and w.mat_HU_list == [] and _read(env, "Mine") == ()
    assert json.loads(env.settings.read_text())["hu_lut"] == "Mine"

    w.hu_lut_combo.setCurrentText("A")
    env.names.append("A copy")
    hu_lut.duplicate_hu_lut(w)
    assert _combo(w) == (["A", "A copy", "Mine"], "A copy") and _read(env, "A copy") == _read(env, "A")

    env.names.append("B")
    hu_lut.rename_hu_lut(w)
    assert _combo(w) == (["A", "B", "Mine"], "B") and _read(env, "B") == _read(env, "A")
    assert json.loads(env.settings.read_text())["hu_lut"] == "B"

    env.answer = QMessageBox.No
    hu_lut.delete_hu_lut(w)
    assert hu_lut.list_luts() == ["A", "B", "Mine"]
    env.answer = QMessageBox.Yes
    hu_lut.delete_hu_lut(w)                                 # the next LUT is shown
    assert _combo(w) == (["A", "Mine"], "Mine")
    hu_lut.delete_hu_lut(w)
    hu_lut.delete_hu_lut(w)                                 # the last one: Default again
    assert _combo(w) == (["Default"], "Default") and len(w.mat_HU_list) == len(hu_lut.DEFAULT_LUT_ROWS)


def test_material_map_table_shown_through_the_dropdown(env):
    _write(env, "A", ["Air,-1000.0,-200.0,,1"])
    w = _window()
    same = [{"name": "Air", "key": 0, "min": -1000.0, "max": -200.0, "fixed_density": True,
             "color": "#e6194b", "color_auto": True, "visible": False}]
    other = [{"name": "Water", "key": 1, "min": -50.0, "max": 50.0, "fixed_density": True,
              "color": "#3cb44b", "color_auto": True, "visible": True}]

    hu_lut.show_map_hu_table(w, same, "MatMap_1")           # made with LUT A: A is shown
    assert _combo(w) == (["A"], "A") and hu_lut.list_luts() == ["A"]

    hu_lut.show_map_hu_table(w, other, "MatMap/2")          # no LUT with these rows: nothing written
    assert _combo(w) == (["MatMap/2 (material map)", "A"], "MatMap/2 (material map)")
    assert _table(w) == [("Water", -50.0, 50.0)] and hu_lut.list_luts() == ["A"]
    w.tableMatToHU.item(0, HU_C_HI).setText("60")           # an edit: saved as a LUT named after the map
    assert _combo(w) == (["A", "MatMap_2"], "MatMap_2")
    assert _read(env, "MatMap_2") == (("Water", -50.0, 60.0, None, True),)

    hu_lut.show_map_hu_table(w, other, "MatMap_3")
    w.hu_lut_combo.setCurrentText("A")                      # a saved LUT chosen: the map's entry goes
    assert _combo(w) == (["A", "MatMap_2"], "A") and _table(w) == [("Air", -1000.0, -200.0)]
    assert hu_lut.list_luts() == ["A", "MatMap_2"]


def test_materials_missing_from_the_database_become_none(env):
    _write(env, "Old", ["Air,-1000.0,-200.0,,1", "Mean gland-TG186,80.0,100.0,,1"])
    _write(env, "Other", ["Air,-1000.0,-200.0,,1"])
    w = _window()
    assert _table(w) == [("Air", -1000.0, -200.0), ("None", 80.0, 100.0)]
    assert env.messages == []                               # at start: no dialog (rows show None)
    w.hu_lut_combo.setCurrentText("Other")
    w.hu_lut_combo.setCurrentText("Old")                    # chosen by the user: told which ones
    assert "Mean gland-TG186" in env.messages[-1]
    assert [r[0] for r in _read(env, "Old")] == ["Air", "Mean gland-TG186"]   # file kept until an edit
