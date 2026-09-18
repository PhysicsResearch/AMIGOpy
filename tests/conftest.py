import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest  # noqa: E402


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


@pytest.fixture
def db_dir(tmp_path, monkeypatch):
    """Point %LOCALAPPDATA% at a temp dir so no test touches the real databases."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    from fcn_3DPrinting.db_paths import get_3dp_db_dir
    return get_3dp_db_dir()


def _make_row(infill, red, zeff):
    row = ["0"] * 14
    row[0], row[6], row[9] = str(infill), str(red), str(zeff)
    return row


@pytest.fixture
def app_stub(qapp, db_dir):
    """A QMainWindow carrying the 3DP tables and caches the module functions expect."""
    from PySide6.QtWidgets import (QMainWindow, QTabWidget, QTableWidget, QTableWidgetItem,
                                   QSpinBox, QComboBox, QTextEdit, QListWidget, QLabel)
    from fcn_3DPrinting import db_schema

    w = QMainWindow()
    w.D3 = QTabWidget()
    w.selected_background = "Transparent"
    w.current_viewed_filament = None
    w.current_viewed_mix_id = None
    w._is_loading = False

    w.table_3d_db = QTableWidget(2, 10)
    for r, vals in enumerate([
        ["Maastro Bone", "ColorFabb", "PLA PABT", "White", "X1E", "2026-08-31", "1.38", "0.045", "11.7", "0.14"],
        ["PolyLite PLA White", "Polymaker", "PLA", "White", "X1E", "2026-07-27", "1.12", "0.013", "6.4", "0.36"],
    ]):
        for c, v in enumerate(vals):
            w.table_3d_db.setItem(r, c, QTableWidgetItem(v))

    w.table_calibration_info = QTableWidget(0, 20)
    w.table_calibration_info.setHorizontalHeaderLabels(db_schema.MATERIAL_CAL_UI_HEADERS)
    w.txt_notes = QTextEdit()
    w.lbl_cal_title = QLabel()
    w.lbl_notes_title = QLabel()
    w.calibration_data_cache = {"Maastro Bone": [list(db_schema.MATERIAL_CAL_DEFAULTS)]}
    w.notes_cache = {"Maastro Bone": "hello"}

    w.table_mat_mix = QTableWidget(2, 9)
    spin = QSpinBox()
    spin.setProperty("mix_id", 1)
    spin.setValue(2)
    w.table_mat_mix.setCellWidget(0, 0, spin)
    for r, name in enumerate(["Maastro Bone", "PolyLite PLA White"]):
        combo = QComboBox()
        combo.addItem(name)
        combo.setCurrentText(name)
        w.table_mat_mix.setCellWidget(r, 1, combo)
        w.table_mat_mix.setItem(r, 2, QTableWidgetItem("Bone/PLA" if r == 0 else ""))
        w.table_mat_mix.setItem(r, 3, QTableWidgetItem("1.38" if r == 0 else "1.12"))
        w.table_mat_mix.setItem(r, 4, QTableWidgetItem("11.7" if r == 0 else "6.4"))

    w.table_mix_calibration_info = QTableWidget(0, 2 + 19)
    w.table_mix_z_red = QTableWidget(0, 2 + 8)
    w.table_mix_red_cal = QTableWidget(0, 14)
    w.list_mix_red_ratios = QListWidget()
    w.txt_mix_notes = QTextEdit()
    w.mix_calibration_cache = {1: [["50.0000,50.0000"] + list(db_schema.MIX_CAL_DEFAULTS)]}
    w.mix_notes_cache = {1: "mix notes"}
    w.mix_m_value_cache = {1: 3.4}
    w.mix_red_cache = {
        1: [
            {"percentage": [100, 0], "rows": [_make_row(80, 1.30, 11.5), _make_row(90, 1.34, 11.6), _make_row(100, 1.38, 11.7)]},
            {"percentage": [50, 50], "rows": [_make_row(80, 1.15, 9.0), _make_row(90, 1.19, 9.1), _make_row(100, 1.23, 9.2)]},
            {"percentage": [0, 100], "rows": [_make_row(80, 1.00, 6.3), _make_row(90, 1.05, 6.35), _make_row(100, 1.12, 6.4)]},
        ]
    }
    return w
