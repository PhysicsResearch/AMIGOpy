import csv
import json
import os

import fcn_init.create_3D_database_tab as m


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def test_save_functions_write_all_files_atomically_and_rotate(app_stub, db_dir):
    for _ in range(2):
        m.save_3d_database(app_stub)
        m.save_calibration_database(app_stub)
        m.save_mix_database(app_stub)
        m.save_mix_calibration_database(app_stub)

    materials = _read_csv(m.get_db_path())
    assert materials[0][0] == "Material Name"
    assert [r[0] for r in materials[1:]] == ["Maastro Bone", "PolyLite PLA White"]
    cal = _read_csv(m.get_cal_db_path())
    assert len(cal) == 2 and cal[1][0] == "Maastro Bone" and len(cal[1]) == 21
    mixes = _read_csv(m.get_mix_db_path())
    assert [r[2] for r in mixes[1:]] == ["Maastro Bone", "PolyLite PLA White"] and mixes[1][0] == "1"
    mix_cal = _read_csv(m.get_mix_cal_db_path())
    assert mix_cal[1][:2] == ["1", "50.0000,50.0000"]
    with open(m.get_mix_notes_db_path(), encoding="utf-8") as f:
        assert json.load(f) == {"1": {"notes": "mix notes", "m_value": 3.4}}
    with open(m.get_mix_red_db_path(), encoding="utf-8") as f:
        assert len(json.load(f)["1"]) == 3

    for path in (m.get_db_path(), m.get_cal_db_path(), m.get_notes_db_path(), m.get_mix_db_path(),
                 m.get_mix_cal_db_path(), m.get_mix_notes_db_path(), m.get_mix_red_db_path()):
        assert os.path.exists(path + ".bak1"), path
    assert not [f for f in os.listdir(db_dir) if f.endswith(".tmp")]


def test_autosave_collects_failures_and_warns_once(app_stub, db_dir, monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("read-only folder")
    monkeypatch.setattr(m, "atomic_write_csv", boom)
    warnings = []
    monkeypatch.setattr(m.QMessageBox, "warning", lambda *a, **k: warnings.append(a[2]))

    m._do_auto_save(app_stub)
    m._do_auto_save(app_stub)      # inside the 60 s throttle window -> no second dialog

    assert len(warnings) == 1
    assert "filaments_3d_db.csv" in warnings[0] and "filaments_mix_calibration_db.csv" in warnings[0]
    assert app_stub._is_autosaving is False


def test_flush_on_exit_runs_once_and_stops_timer(app_stub, db_dir):
    m.auto_save_all_databases(app_stub)      # arms the 300 ms debounce timer
    assert app_stub._auto_save_timer.isActive()
    m.flush_3dp_databases(app_stub)
    assert not app_stub._auto_save_timer.isActive()
    assert os.path.exists(m.get_db_path())
    os.remove(m.get_db_path())
    m.flush_3dp_databases(app_stub)          # second call is a no-op
    assert not os.path.exists(m.get_db_path())


def test_ensure_3dp_tab_loaded(app_stub, qapp):
    assert m.ensure_3dp_tab_loaded(app_stub) is True      # tables already exist
    from PySide6.QtWidgets import QMainWindow
    bare = QMainWindow()
    assert m.ensure_3dp_tab_loaded(bare) is False          # no tab widgets at all -> cannot load


def test_restore_point_labels():
    assert m._describe_restore_point("pre_import_zip_20260918_141500.zip").startswith(
        "Before import zip - 2026-09-18 14:15:00")
    assert m._describe_restore_point("backup_2026-09-18.zip").startswith("Daily backup - ")
    assert m._describe_restore_point("weird.zip").startswith("weird.zip")


def test_signals_blocked_restores_on_exception(app_stub):
    table = app_stub.table_3d_db
    try:
        with m.signals_blocked(table):
            assert table.signalsBlocked()
            raise RuntimeError("inside")
    except RuntimeError:
        pass
    assert not table.signalsBlocked()
