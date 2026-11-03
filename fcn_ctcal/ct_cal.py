# -*- coding: utf-8 -*-
"""
ct_cal.py - HU tables of the Density Map tab (MonteCarlo > Density Map)
=======================================================================
HU -> mass density, RED (relative electron density) or SPR (stopping power ratio) tables, picked
in the dropdown above the table: one CSV per table in %LOCALAPPDATA%\\AMIGOpy\\ct_cal_curves (file
name = table name; its type is the name of the second column: DENSITY, RED or SPR). Every edit of
the table is saved to the table shown; New / Duplicate / Rename / Delete work as the HU LUTs of the
Material Assignment tab; the bundled tables are copied there when the folder has none, and the last
used table (settings.json) is shown at start. The graph next to the table follows the Figures menu
and, with "Hold plot", keeps the curves of the tables shown before, for comparison.

File format (line 1 is skipped, line 2 is the header, as older AMIGOpy versions read it):

    Exported from AMIGOpy 2025-06-26 09:58:34,
    HU,DENSITY
    -1024.0,0.001
    ...
"""
import csv
import os
import shutil
import sys
from datetime import datetime

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QHeaderView,
                               QInputDialog, QLineEdit, QMessageBox, QTableWidgetItem, QVBoxLayout)

from fcn_3DPrinting.safe_io import atomic_write_csv
from fcn_display.figure_style import figure_style
from fcn_materialassignment.hu_lut import _BAD_NAME_CHARS, _RESERVED_NAMES, _get_setting, _set_setting

# type key (second column of the file) -> (name in the interface, axis label)
TYPES = {"DENSITY": ("Mass density", "Mass density (g/cm$^3$)"),
         "RED": ("RED", "RED"),
         "SPR": ("SPR", "SPR")}
# rows of a new table: air and water
NEW_TABLE_ROWS = {"DENSITY": [(-1000.0, 0.0012), (0.0, 1.0)],
                  "RED": [(-1000.0, 0.001), (0.0, 1.0)],
                  "SPR": [(-1000.0, 0.001), (0.0, 1.0)]}
SETTING = "ct_cal_table"            # settings.json: the last used table
_HELD_COLORS = ("tab:blue", "tab:orange", "tab:green", "tab:purple", "tab:brown", "tab:pink", "tab:gray",
                "tab:olive", "tab:cyan")


def type_key(text):
    """DENSITY, RED or SPR of a column name or label ('Density', 'Mass density', 'red', ...); None if none."""
    t = str(text or "").strip().upper().replace(".", "")
    if t in ("DENSITY", "MASS DENSITY", "MASS DEN", "DEN", "MASS"):
        return "DENSITY"
    return t if t in ("RED", "SPR") else None


def type_label(key):
    return TYPES.get(key, (str(key),))[0]


# ----------------------------------------------------------------------------
# Store: one CSV per table
# ----------------------------------------------------------------------------
def _resource_path(relative_path):
    """Bundled files (PyInstaller / Nuitka) or the source tree."""
    base = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


def get_appdata_ct_cal_dir():
    """%LOCALAPPDATA%\\AMIGOpy\\ct_cal_curves; the bundled tables are copied there when it has none."""
    from fcn_materialassignment.material_assignment_properties import get_appdata_path
    d = os.path.join(get_appdata_path(), "ct_cal_curves")
    os.makedirs(d, exist_ok=True)
    if not any(f.lower().endswith(".csv") for f in os.listdir(d)):
        bundled = _resource_path(os.path.join("fcn_ctcal", "ct_cal_curves"))
        for fname in (os.listdir(bundled) if os.path.isdir(bundled) else []):
            if fname.lower().endswith(".csv"):
                try:
                    shutil.copy2(os.path.join(bundled, fname), os.path.join(d, fname))
                except OSError as e:
                    print(f"[HU tables] could not copy {fname}: {e}")
    return d


def _table_path(name):
    return os.path.join(get_appdata_ct_cal_dir(), name + ".csv")


def list_tables():
    """Names of the saved HU tables (CSV file names without extension), sorted."""
    return sorted((f[:-4] for f in os.listdir(get_appdata_ct_cal_dir()) if f.lower().endswith(".csv")), key=str.lower)


def read_table(path):
    """
    (type key or None, rows ((HU, value), ...)) of an HU table file: the header is the first line whose
    first cell is HU (',' or ';' separated); the lines before it are comments, rows that are not two
    numbers are skipped.
    """
    with open(path, "r", newline="", encoding="utf-8-sig", errors="replace") as f:
        lines = f.read().splitlines()
    start = next((i for i, line in enumerate(lines) if line.replace(";", ",").split(",")[0].strip().upper() == "HU"), None)
    if start is None:
        raise ValueError("no header line 'HU,<DENSITY | RED | SPR>'")
    delimiter = ";" if ";" in lines[start] else ","     # ';' files may use decimal commas
    header = [c.strip() for c in next(csv.reader([lines[start]], delimiter=delimiter))]
    rows = []
    for cells in csv.reader(lines[start + 1:], delimiter=delimiter):
        try:
            rows.append(tuple(float(c.strip().replace(",", ".")) for c in cells[:2]))
        except ValueError:
            continue
    return type_key(header[1] if len(header) > 1 else ""), tuple(r for r in rows if len(r) == 2)


def write_table(path, kind, rows):
    """Write an HU table (crash-safe: temporary file + replace) in the format older versions read."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    atomic_write_csv(path, [f"Exported from AMIGOpy {stamp}", ""],
                     [["HU", kind]] + [[_fmt(hu), _fmt(v)] for hu, v in rows])


def _fmt(v):
    return f"{float(v):.10g}"


def curve(rows):
    """(HU, value) arrays of table rows, sorted by HU."""
    arr = np.array(sorted(rows), dtype=float).reshape(-1, 2)
    return arr[:, 0], arr[:, 1]


# ----------------------------------------------------------------------------
# Names
# ----------------------------------------------------------------------------
def _safe_name(text):
    name = "".join("_" if c in _BAD_NAME_CHARS or ord(c) < 32 else c for c in str(text))
    name = name.strip().rstrip(".")[:100].strip()
    return name if name and name.upper() not in _RESERVED_NAMES else "HU table"


def _unique_name(base):
    taken = {n.lower() for n in list_tables()}
    name, i = base, 2
    while name.lower() in taken:
        name, i = f"{base} {i}", i + 1
    return name


def _name_problem(name, ignore=None):
    """Why 'name' cannot be used for a table (None if it can); 'ignore': the table being renamed."""
    if not name:
        return "Please type a name."
    if any(c in _BAD_NAME_CHARS or ord(c) < 32 for c in name) or name.endswith(".") or name.upper() in _RESERVED_NAMES:
        return 'A name cannot contain < > : " / \\ | ? * or end with a dot.'
    if len(name) > 100:
        return "Please use a shorter name (up to 100 characters)."
    if name.lower() in {n.lower() for n in list_tables()} - {(ignore or "").lower()}:
        return f"There is already an HU table named '{name}'."
    return None


def _ask_name(self, title, label, text, ignore=None):
    """A table name typed by the user (None if cancelled); asks again while it cannot be used."""
    while True:
        text, ok = QInputDialog.getText(self, title, label, QLineEdit.EchoMode.Normal, text)
        if not ok:
            return None
        problem = _name_problem(text.strip(), ignore)
        if problem is None:
            return text.strip()
        QMessageBox.warning(self, title, problem)


def _ask_new_table(self, kind):
    """Name and type of a new table (small dialog); None if cancelled."""
    dlg = QDialog(self)
    dlg.setWindowTitle("New HU table")
    form = QFormLayout(dlg)
    name_edit = QLineEdit(_unique_name("New table"), dlg)
    type_combo = QComboBox(dlg)
    for key, (label, _) in TYPES.items():
        type_combo.addItem(label, key)
    type_combo.setCurrentIndex(max(0, type_combo.findData(kind)))
    form.addRow("Name:", name_edit)
    form.addRow("Type:", type_combo)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dlg)
    form.addRow(buttons)
    buttons.rejected.connect(dlg.reject)

    def accept():
        problem = _name_problem(name_edit.text().strip())
        if problem:
            QMessageBox.warning(dlg, "New HU table", problem)
        else:
            dlg.accept()
    buttons.accepted.connect(accept)
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return None
    return name_edit.text().strip(), type_combo.currentData()


# ----------------------------------------------------------------------------
# The table shown
# ----------------------------------------------------------------------------
def table_rows(self):
    """Rows of the table widget whose two cells are numbers, in table order."""
    table, rows = self.ct_cal_table, []
    for r in range(table.rowCount()):
        cells = [table.item(r, c) for c in (0, 1)]
        try:
            rows.append(tuple(float(c.text().replace(",", ".")) for c in cells))
        except (AttributeError, ValueError):
            continue
    return tuple(rows)


def _show_rows(self, kind, rows):
    """Put a table in the widget (no signals) and its type in the type box."""
    table = self.ct_cal_table
    table.blockSignals(True)
    table.clear()
    table.setColumnCount(2)
    table.setRowCount(len(rows))
    table.setHorizontalHeaderLabels(["HU", type_label(kind)])
    for r, (hu, v) in enumerate(rows):
        for c, value in enumerate((hu, v)):
            item = QTableWidgetItem(_fmt(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(r, c, item)
    table.horizontalHeader().setVisible(True)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.blockSignals(False)
    combo = getattr(self, "ct_cal_type", None)
    if combo is not None:
        combo.blockSignals(True)
        combo.setCurrentIndex(max(0, combo.findData(kind)))
        combo.blockSignals(False)


def _fill_combo(self, current):
    combo = self.ct_cal_list
    combo.blockSignals(True)
    combo.clear()
    combo.addItems(list_tables())
    combo.setCurrentIndex(max(0, combo.findText(current)))
    combo.blockSignals(False)


def init_ct_cal_selector(self):
    """At start: the saved tables in the dropdown (the bundled ones if none) and the last used one shown (once)."""
    if getattr(self, "ct_cal_list", None) is None or getattr(self, "_ct_cal_ready", False):
        return
    self._ct_cal_ready = True
    self.ct_cal_list.setToolTip(f"Saved HU tables ({get_appdata_ct_cal_dir()}).\n"
                                "Changes in the table are saved to the table shown here.")
    names = list_tables()
    if names:
        last = _get_setting(SETTING)
        select_ct_cal_table(self, last if last in names else names[0], remember=False)


def select_ct_cal_table(self, name, remember=True):
    """Show the saved table 'name' (dropdown choice); later edits are saved to it."""
    if not name:
        return
    try:
        kind, rows = read_table(_table_path(name))
    except (OSError, ValueError) as e:
        QMessageBox.warning(self, "HU table", f"Could not read the HU table '{name}':\n{e}")
        return
    _fill_combo(self, name)
    self.ct_cal_name, self.ct_cal_kind, self._ct_cal_saved = name, kind or "DENSITY", rows
    _show_rows(self, self.ct_cal_kind, rows)
    held = list(getattr(self, "ct_cal_plot_names", None) or []) if _holding(self) else []
    self.ct_cal_plot_names = held + ([name] if name not in held else [])
    if remember:
        _set_setting(SETTING, name)
    plot_ct_cal(self)


def _save(self, kind, rows):
    name = getattr(self, "ct_cal_name", None)
    if name is None:
        return False
    try:
        write_table(_table_path(name), kind, rows)
    except OSError as e:
        QMessageBox.warning(self, "HU table", f"Could not save the HU table '{name}':\n{e}")
        return False
    self.ct_cal_kind, self._ct_cal_saved = kind, rows
    return True


def on_ct_cal_table_edited(self, *args):
    """Every edit of the table: saved to the table shown, graph redrawn."""
    rows = table_rows(self)
    if rows != getattr(self, "_ct_cal_saved", None):
        _save(self, self.ct_cal_kind, rows)
    plot_ct_cal(self)


def on_ct_cal_type_changed(self, *args):
    """Type box: the table shown becomes a table of that type."""
    kind = self.ct_cal_type.currentData()
    if kind and kind != getattr(self, "ct_cal_kind", None) and _save(self, kind, table_rows(self)):
        self.ct_cal_table.setHorizontalHeaderLabels(["HU", type_label(kind)])
        plot_ct_cal(self)


def add_row_to_ct_table(self):
    """'Add row': an empty row (saved once both cells hold numbers)."""
    table = self.ct_cal_table
    table.blockSignals(True)
    r = table.rowCount()
    table.insertRow(r)
    for c in (0, 1):
        item = QTableWidgetItem("")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(r, c, item)
    table.blockSignals(False)
    table.setCurrentCell(r, 0)
    table.editItem(table.item(r, 0))


def delete_ct_table_rows(self):
    """'Delete row': the selected rows (the current one if none is selected)."""
    table = self.ct_cal_table
    rows = sorted({i.row() for i in table.selectedIndexes()} or ({table.currentRow()} - {-1}), reverse=True)
    if not rows:
        return
    table.blockSignals(True)
    for r in rows:
        table.removeRow(r)
    table.blockSignals(False)
    on_ct_cal_table_edited(self)


# ---- New / Duplicate / Rename / Delete / Import / Export --------------------
def _create(self, name, kind, rows):
    try:
        write_table(_table_path(name), kind, rows)
    except OSError as e:
        QMessageBox.warning(self, "HU table", f"Could not save the HU table '{name}':\n{e}")
        return
    select_ct_cal_table(self, name)


def new_ct_cal_table(self):
    """'New': a table of the chosen type with two rows (air, water)."""
    answer = _ask_new_table(self, getattr(self, "ct_cal_kind", None) or "DENSITY")
    if answer:
        name, kind = answer
        _create(self, name, kind, NEW_TABLE_ROWS[kind])


def duplicate_ct_cal_table(self):
    """'Duplicate': the table shown saved under a new name."""
    base = getattr(self, "ct_cal_name", None) or "HU table"
    name = _ask_name(self, "Duplicate HU table", f"Name of the copy of '{base}':", _unique_name(f"{base} copy"))
    if name:
        _create(self, name, getattr(self, "ct_cal_kind", None) or "DENSITY", table_rows(self))


def rename_ct_cal_table(self):
    """'Rename': rename the table shown."""
    old = getattr(self, "ct_cal_name", None)
    if old is None:
        return
    name = _ask_name(self, "Rename HU table", f"New name of '{old}':", old, ignore=old)
    if not name or name == old:
        return
    try:
        os.replace(_table_path(old), _table_path(name))
    except OSError as e:
        QMessageBox.warning(self, "HU table", f"Could not rename the HU table '{old}':\n{e}")
        return
    self.ct_cal_name = name
    self.ct_cal_plot_names = [name if n == old else n for n in getattr(self, "ct_cal_plot_names", None) or []]
    _fill_combo(self, name)
    _set_setting(SETTING, name)
    plot_ct_cal(self)


def delete_ct_cal_table(self):
    """'Delete': delete the table shown and show the next one (the bundled tables come back when none is left)."""
    name = getattr(self, "ct_cal_name", None)
    if name is None:
        return
    if QMessageBox.question(self, "Delete HU table", f"Delete the HU table '{name}'?",
                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
        return
    names = list_tables()
    i = names.index(name) if name in names else 0
    try:
        os.remove(_table_path(name))
    except FileNotFoundError:
        pass
    except OSError as e:
        QMessageBox.warning(self, "HU table", f"Could not delete the HU table '{name}':\n{e}")
        return
    self.ct_cal_name = None
    self.ct_cal_plot_names = [n for n in getattr(self, "ct_cal_plot_names", None) or [] if n != name]
    left = list_tables()
    if left:
        select_ct_cal_table(self, left[min(i, len(left) - 1)])


def import_ct_cal_table(self):
    """'Import...': a CSV file (HU, DENSITY | RED | SPR) saved as a new table and shown."""
    path, _ = QFileDialog.getOpenFileName(self, "Import an HU table", "", "CSV Files (*.csv);;All Files (*)")
    if not path:
        return
    try:
        kind, rows = read_table(path)
    except (OSError, ValueError) as e:
        QMessageBox.warning(self, "HU table", f"Could not read {os.path.basename(path)}:\n{e}")
        return
    if len(rows) < 2:
        QMessageBox.warning(self, "HU table", f"{os.path.basename(path)} has fewer than two rows of numbers.")
        return
    if kind is None:
        labels = [label for label, _ in TYPES.values()]
        label, ok = QInputDialog.getItem(self, "HU table", "Type of the second column:", labels, 0, False)
        if not ok:
            return
        kind = type_key(label)
    _create(self, _unique_name(_safe_name(os.path.splitext(os.path.basename(path))[0])), kind, rows)


def export_ct_cal_table(self):
    """'Export...': the table shown written to a CSV file."""
    name = getattr(self, "ct_cal_name", None) or "HU table"
    path, _ = QFileDialog.getSaveFileName(self, "Export the HU table", f"{name}.csv", "CSV Files (*.csv)")
    if path:
        try:
            write_table(path, getattr(self, "ct_cal_kind", None) or "DENSITY", table_rows(self))
        except OSError as e:
            QMessageBox.warning(self, "HU table", f"Could not save {path}:\n{e}")


# ----------------------------------------------------------------------------
# Graph
# ----------------------------------------------------------------------------
def _holding(self):
    hold = getattr(self, "ct_cal_hold", None)
    return hold is not None and hold.isChecked()


def on_ct_cal_hold_toggled(self, *args):
    """'Hold plot' off: only the table shown is plotted."""
    if not _holding(self):
        name = getattr(self, "ct_cal_name", None)
        self.ct_cal_plot_names = [name] if name else []
    plot_ct_cal(self)


def _canvas(self):
    """Figure, axes and canvas of the graph (created once in the ct_cal_plot container)."""
    if getattr(self, "canvas_ct_cal", None) is None:
        self.fig_ct_cal = Figure()
        self.ax_ct_cal = self.fig_ct_cal.add_subplot(111)
        self.canvas_ct_cal = FigureCanvas(self.fig_ct_cal)
        self.toolbar_ct_cal = NavigationToolbar(self.canvas_ct_cal, self.ct_cal_plot)
        layout = self.ct_cal_plot.layout() or QVBoxLayout(self.ct_cal_plot)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar_ct_cal)
        layout.addWidget(self.canvas_ct_cal)
    return self.fig_ct_cal, self.ax_ct_cal, self.canvas_ct_cal


def plot_ct_cal(self):
    """The table shown (Figures menu line and point style) and, with Hold plot, the tables shown before."""
    if getattr(self, "ct_cal_plot", None) is None:
        return
    fig, ax, canvas = _canvas(self)
    st = figure_style(self)
    transparent = st["background"] == "transparent"
    dark = getattr(self, "current_theme", "dark") == "dark"
    text = "white" if (transparent and dark) else "black"
    face = (0, 0, 0, 0) if transparent else st["background"]
    fig.patch.set_facecolor(face)
    ax.clear()
    ax.set_facecolor(face)
    canvas.setStyleSheet("background-color: transparent;" if transparent else f"background-color: {st['background']};")

    current = getattr(self, "ct_cal_name", None)
    names = [n for n in getattr(self, "ct_cal_plot_names", None) or [] if n != current] + ([current] if current else [])
    curves, colors = [], iter(_HELD_COLORS)
    for name in names:
        if name == current:     # the table shown, as edited: the Figures menu colours
            kind, rows = getattr(self, "ct_cal_kind", None), table_rows(self)
            color, marker_color = st["line_color"], st["point_color"]
        else:
            try:
                kind, rows = read_table(_table_path(name))
            except (OSError, ValueError):
                continue
            color = marker_color = next(colors, None)
        if rows:
            curves.append((name, kind, curve(rows), color, marker_color))
    unique = list(dict.fromkeys(kind for _, kind, _, _, _ in curves if kind))
    for name, kind, (hu, value), color, marker_color in curves:
        ax.plot(hu, value, color=color, linestyle=st["line_style"], linewidth=st["line_width"],
                marker=st["marker"], markersize=st["point_size"], markerfacecolor=marker_color,
                markeredgecolor=marker_color, label=f"{name} ({type_label(kind)})" if len(unique) > 1 else name)
    ax.set_xlabel("HU", fontsize=st["font"], color=text)
    ax.set_ylabel(" / ".join(TYPES[k][1] for k in unique) if unique else "", fontsize=st["font"], color=text)
    ax.set_title(f"HU vs {type_label(unique[0])}" if len(unique) == 1 else "HU tables", fontsize=st["font"] + 2,
                 color=text)
    ax.tick_params(colors=text, labelsize=max(6, st["font"] - 2))
    for spine in ax.spines.values():
        spine.set_color(text)
    ax.grid(True, alpha=0.25)
    if st["legend"] and ax.lines:
        legend = ax.legend(fontsize=st["legend_font"], framealpha=0.3 if transparent else 0.8)
        for t in legend.get_texts():
            t.set_color(text)
    fig.tight_layout()
    canvas.draw_idle()
