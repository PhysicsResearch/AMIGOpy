import os
import csv
import json
import random
import threading
import zipfile
import pandas as pd
from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
    QPushButton, QScrollArea, QLabel, QDialog, QFormLayout, QLineEdit,
    QDoubleSpinBox, QMessageBox, QAbstractItemView, QGridLayout, QFrame, QHeaderView,
    QStyledItemDelegate, QDateEdit, QTabWidget, QTextEdit, QMenu, QApplication,
    QSpinBox, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate, QObject, QEvent, QTimer
from PySide6.QtGui import QColor, QFont, QKeySequence

# Global placeholder states for Matplotlib lazy loading
matplotlib_imported = False
FigureCanvas = None
NavigationToolbar = None
Figure = None

def import_matplotlib_lazy():
    global matplotlib_imported, FigureCanvas, NavigationToolbar, Figure
    if matplotlib_imported:
        return
        
    try:
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
    except ImportError:
        try:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
        except ImportError:
            from matplotlib.backends.backend_template import FigureCanvas
            NavigationToolbar = None
            
    from matplotlib.figure import Figure
    matplotlib_imported = True

default_filaments = [
    {"Material Name": "Prusament PLA", "Brand": "Prusa", "Type": "PLA", "Color": "Galaxy Black", "3DPrinter": "Prusa i3 MK3S+", "RED": "1.15", "RED STD": "0.02", "Zeff": "6.80", "Zeff STD": "0.10"},
    {"Material Name": "Filamentum ABS", "Brand": "Filamentum", "Type": "ABS", "Color": "Natural", "3DPrinter": "Prusa i3 MK3S+", "RED": "1.02", "RED STD": "0.02", "Zeff": "5.70", "Zeff STD": "0.10"},
    {"Material Name": "Overture PETG", "Brand": "Overture", "Type": "PETG", "Color": "Clear", "3DPrinter": "Ultimaker S5", "RED": "1.18", "RED STD": "0.02", "Zeff": "6.20", "Zeff STD": "0.10"},
    {"Material Name": "NinjaTek TPU", "Brand": "NinjaTek", "Type": "TPU", "Color": "Black", "3DPrinter": "All", "RED": "1.10", "RED STD": "0.02", "Zeff": "5.90", "Zeff STD": "0.10"}
]

default_calibrations = [
    # Prusament PLA
    ["Prusament PLA", "80", "140", "150.0000", "5.0000", "200.0000", "6.0000", "1.1500", "0.0200", "6.8000", "0.1000", "215", "60", "100", "Grid", "1.0", "100", "Cylinder", "0.2", "0.4", "45"],
    # Filamentum ABS
    ["Filamentum ABS", "80", "140", "20.0000", "4.0000", "50.0000", "5.0000", "1.0200", "0.0200", "5.7000", "0.1000", "245", "100", "100", "Grid", "1.0", "100", "Cylinder", "0.2", "0.4", "50"]
]

# Focus-only SpinBox and ComboBox to prevent mouse wheel events from triggering unless focused
class FocusSpinBox(QSpinBox):
    def wheelEvent(self, event):
        if not self.hasFocus():
            event.ignore()
        else:
            super().wheelEvent(event)

class FocusDoubleSpinBox(QDoubleSpinBox):
    def wheelEvent(self, event):
        if not self.hasFocus():
            event.ignore()
        else:
            super().wheelEvent(event)

class FocusComboBox(QComboBox):
    def wheelEvent(self, event):
        if not self.hasFocus():
            event.ignore()
        else:
            super().wheelEvent(event)

class ClipboardTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Enable custom context menu for column header name right-click actions
        self.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self.show_header_context_menu)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self.copy_selection()
            event.accept()
        elif event.matches(QKeySequence.Paste):
            self.paste_selection()
            event.accept()
        else:
            super().keyPressEvent(event)

    def copy_selection(self):
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return
        
        # Determine bounding box of selection
        top = min(r.topRow() for r in selected_ranges)
        bottom = max(r.bottomRow() for r in selected_ranges)
        left = min(r.leftColumn() for r in selected_ranges)
        right = max(r.rightColumn() for r in selected_ranges)
        
        rows_text = []
        for r in range(top, bottom + 1):
            row_vals = []
            for c in range(left, right + 1):
                item = self.item(r, c)
                if item is not None:
                    val = item.data(Qt.EditRole)
                    if val is not None:
                        row_vals.append(str(val))
                    else:
                        row_vals.append(item.text())
                else:
                    row_vals.append("")
            rows_text.append("\t".join(row_vals))
            
        clipboard_text = "\n".join(rows_text)
        QApplication.clipboard().setText(clipboard_text)

    def paste_selection(self):
        clipboard_text = QApplication.clipboard().text()
        if not clipboard_text:
            return
            
        rows = [line.split('\t') for line in clipboard_text.replace('\r', '').strip('\n').split('\n')]
        if not rows:
            return
            
        self.setSortingEnabled(False)
        self.blockSignals(True)
        
        current_item = self.currentItem()
        start_row = current_item.row() if current_item else 0
        start_col = current_item.column() if current_item else 0
        
        selected_ranges = self.selectedRanges()
        is_single_value = (len(rows) == 1 and len(rows[0]) == 1)
        
        if is_single_value and selected_ranges:
            val_str = rows[0][0]
            for r_range in selected_ranges:
                for r in range(r_range.topRow(), r_range.bottomRow() + 1):
                    for c in range(r_range.leftColumn(), r_range.rightColumn() + 1):
                        self.set_cell_value(r, c, val_str)
        else:
            for r_idx, row_vals in enumerate(rows):
                r = start_row + r_idx
                if r >= self.rowCount():
                    break
                for c_idx, val_str in enumerate(row_vals):
                    c = start_col + c_idx
                    if c >= self.columnCount():
                        break
                    self.set_cell_value(r, c, val_str)
                    
        self.blockSignals(False)
        self.setSortingEnabled(True)
        
        # Trigger post-paste handler since signals are blocked during paste
        handler = getattr(self, "post_paste_handler", None)
        if handler:
            handler()

    def set_cell_value(self, r, c, val_str):
        # Don't overwrite the Actions/View column
        header_item = self.horizontalHeaderItem(c)
        if header_item and header_item.text() == "Actions":
            return
            
        # Clean value string to support comma decimal separators from regional Excel copies
        cleaned_val = val_str.replace(',', '.')
        
        widget = self.cellWidget(r, c)
        if isinstance(widget, QComboBox):
            widget.setCurrentText(val_str)
            return
        elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
            try:
                widget.setValue(float(cleaned_val))
            except ValueError:
                pass
            return
            
        item = self.item(r, c)
        if item is None:
            item = QTableWidgetItem()
            self.setItem(r, c, item)
            
        delegate = self.itemDelegateForColumn(c)
        if delegate is not None:
            try:
                float_val = float(cleaned_val)
                item.setData(Qt.EditRole, float_val)
                item.setText(f"{float_val:.4f}")
            except ValueError:
                item.setData(Qt.EditRole, 0.0)
                item.setText("0.0000")
        else:
            item.setData(Qt.EditRole, val_str)
            item.setText(val_str)

    def show_context_menu(self, pos):
        item = self.itemAt(pos)
        if item is None:
            return
            
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e24;
                color: #ffffff;
                border: 1px solid #3c4450;
            }
            QMenu::item:selected {
                background-color: #3b82f6;
            }
        """)
        
        copy_action = menu.addAction("Copy")
        paste_action = menu.addAction("Paste")
        menu.addSeparator()
        fill_col_action = menu.addAction("Fill Column with This Value")
        
        action = menu.exec(self.mapToGlobal(pos))
        if action == copy_action:
            self.copy_selection()
        elif action == paste_action:
            self.paste_selection()
        elif action == fill_col_action:
            self.fill_column(item.row(), item.column())

    def fill_column(self, ref_row, col):
        ref_item = self.item(ref_row, col)
        if ref_item is None:
            return
        val = ref_item.data(Qt.EditRole)
        val_str = ref_item.text()
        
        self.setSortingEnabled(False)
        self.blockSignals(True)
        for r in range(self.rowCount()):
            item = self.item(r, col)
            if item is None:
                item = QTableWidgetItem()
                self.setItem(r, col, item)
            item.setData(Qt.EditRole, val)
            item.setText(val_str)
        self.blockSignals(False)
        self.setSortingEnabled(True)

    # Column header context menu
    def show_header_context_menu(self, pos):
        col = self.horizontalHeader().logicalIndexAt(pos)
        if col < 0:
            return
            
        header_item = self.horizontalHeaderItem(col)
        col_name = header_item.text() if header_item else f"Column {col}"
        
        if col_name == "Actions":
            return
            
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e24;
                color: #ffffff;
                border: 1px solid #3c4450;
            }
            QMenu::item:selected {
                background-color: #3b82f6;
            }
        """)
        
        paste_col_action = menu.addAction(f"Paste Clipboard Values to '{col_name}'")
        action = menu.exec(self.horizontalHeader().mapToGlobal(pos))
        if action == paste_col_action:
            self.paste_column_values(col)

    def paste_column_values(self, col):
        clipboard_text = QApplication.clipboard().text()
        if not clipboard_text:
            return
            
        lines = [line.strip() for line in clipboard_text.replace('\r', '').split('\n')]
        if lines and not lines[-1]:
            lines.pop()
            
        if not lines:
            return
            
        self.setSortingEnabled(False)
        self.blockSignals(True)
        
        # Read the custom row inserter
        inserter = getattr(self, "row_inserter", None)
        
        for r_idx, val_str in enumerate(lines):
            r = r_idx
            if r >= self.rowCount():
                if inserter:
                    inserter(r)
                else:
                    self.insertRow(r)
            self.set_cell_value(r, col, val_str)
            
        self.blockSignals(False)
        self.setSortingEnabled(True)
        
        # Run the post-paste synchronization triggers
        handler = getattr(self, "post_paste_handler", None)
        if handler:
            handler()

# Safe Float delegate implementation with explicit editor getters/setters to quieten terminal editor warnings
class FloatDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(4)
        editor.setRange(-2000.0, 5000.0)
        return editor

    def setEditorData(self, editor, index):
        val = index.model().data(index, Qt.EditRole)
        if val is not None:
            try:
                editor.setValue(float(val))
            except (ValueError, TypeError):
                editor.setValue(0.0)

    def setModelData(self, editor, model, index):
        val = editor.value()
        model.setData(index, val, Qt.EditRole)
        model.setData(index, f"{val:.4f}", Qt.DisplayRole)

# Custom delegate to draw mix group boundary borders in the MatMix table
class MixGroupDelegate(QStyledItemDelegate):
    def __init__(self, table, parent=None):
        super().__init__(parent)
        self.table = table

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        row = index.row()
        is_start = self.table.property(f"group_start_{row}")
        is_end = self.table.property(f"group_end_{row}")
        
        painter.save()
        pen = painter.pen()
        pen.setColor(QColor("#3b82f6")) # Blue divider
        pen.setWidth(2)
        painter.setPen(pen)
        
        if is_start:
            # Draw line along top edge
            painter.drawLine(option.rect.topLeft(), option.rect.topRight())
        if is_end:
            # Draw line along bottom edge
            painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        painter.restore()

def get_db_path():
    appdata_dir = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser('~/AppData/Local')), 'AMIGOpy')
    os.makedirs(appdata_dir, exist_ok=True)
    return os.path.join(appdata_dir, 'filaments_3d_db.csv')

def get_cal_db_path():
    appdata_dir = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser('~/AppData/Local')), 'AMIGOpy')
    os.makedirs(appdata_dir, exist_ok=True)
    return os.path.join(appdata_dir, 'filaments_calibration_db.csv')

def get_notes_db_path():
    appdata_dir = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser('~/AppData/Local')), 'AMIGOpy')
    os.makedirs(appdata_dir, exist_ok=True)
    return os.path.join(appdata_dir, 'filaments_notes_db.json')

def get_mix_db_path():
    appdata_dir = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser('~/AppData/Local')), 'AMIGOpy')
    os.makedirs(appdata_dir, exist_ok=True)
    return os.path.join(appdata_dir, 'filaments_mix_db.csv')

def get_mix_cal_db_path():
    appdata_dir = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser('~/AppData/Local')), 'AMIGOpy')
    os.makedirs(appdata_dir, exist_ok=True)
    return os.path.join(appdata_dir, 'filaments_mix_calibration_db.csv')

def get_mix_notes_db_path():
    appdata_dir = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser('~/AppData/Local')), 'AMIGOpy')
    os.makedirs(appdata_dir, exist_ok=True)
    return os.path.join(appdata_dir, 'filaments_mix_notes_db.json')

# Predictive Zeff and RED calculations weighted by the mass weight (%value/100) using main database or matmix top table references
def calculate_predicted_values(self, row_idx, table_source):
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is None:
        return None, None
        
    start_row = -1
    total_rows = self.table_mat_mix.rowCount()
    for r in range(total_rows):
        spin = self.table_mat_mix.cellWidget(r, 0)
        if isinstance(spin, QSpinBox) and spin.property("mix_id") == mix_id:
            start_row = r
            group_size = spin.value()
            break
            
    if start_row == -1:
        return None, None
        
    comp_reds = []
    comp_zeffs = []
    for i in range(group_size):
        r = start_row + i
        if r >= self.table_mat_mix.rowCount():
            break
            
        # Get selected material name from top MatMix table (column 1 combobox)
        combo = self.table_mat_mix.cellWidget(r, 1)
        mat_name = combo.currentText().strip() if isinstance(combo, QComboBox) else ""
        
        # Look up RED and Zeff in the matmix top table first, then fallback to main database self.table_3d_db
        ref_red = 0.0
        ref_zeff = 0.0
        
        # 1. Read from matmix top table (RED is column 3, Zeff is column 4)
        red_item = self.table_mat_mix.item(r, 3)
        zeff_item = self.table_mat_mix.item(r, 4)
        if red_item and red_item.text().strip():
            try:
                ref_red = float(red_item.text().replace(',', '.'))
            except ValueError:
                pass
        if zeff_item and zeff_item.text().strip():
            try:
                ref_zeff = float(zeff_item.text().replace(',', '.'))
            except ValueError:
                pass
                
        # 2. Fallback to main database if still not found/0
        if ref_red == 0.0 or ref_zeff == 0.0:
            if mat_name:
                for r_db in range(self.table_3d_db.rowCount()):
                    item_db = self.table_3d_db.item(r_db, 0)
                    if item_db and item_db.text().strip() == mat_name:
                        if ref_red == 0.0:
                            try:
                                ref_red = float(self.table_3d_db.item(r_db, 6).text().replace(',', '.')) if self.table_3d_db.item(r_db, 6) else 0.0
                            except ValueError:
                                ref_red = 0.0
                        if ref_zeff == 0.0:
                            try:
                                ref_zeff = float(self.table_3d_db.item(r_db, 8).text().replace(',', '.')) if self.table_3d_db.item(r_db, 8) else 0.0
                            except ValueError:
                                ref_zeff = 0.0
                        break
        comp_reds.append(ref_red)
        comp_zeffs.append(ref_zeff)
        
    n_mats = len(comp_reds)
    percentages = []
    for idx in range(n_mats):
        item = table_source.item(row_idx, idx)
        try:
            val = float(item.data(Qt.EditRole)) if item else 0.0
        except (ValueError, TypeError):
            try:
                val = float(item.text().replace(',', '.')) if item and item.text() else 0.0
            except ValueError:
                val = 0.0
        percentages.append(val)
        
    total_p = sum(percentages)
    if total_p <= 0:
        return 0.0, 0.0
        
    # Pred. RED is the sum of reference RED of each material multiplied by the mass weight (%value/100)
    pred_red = 0.0
    for idx in range(n_mats):
        pred_red += (percentages[idx] / 100.0) * comp_reds[idx]
        
    # Pred. Zeff follows: (Zeff_Mat1^m * %_Mat1/100 + Zeff_Mat2^m * %_Mat2/100 + ...)^(1/m)
    # using reference Zeff from main material database or matmix top table, with configurable m-value
    power = 3.4
    if mix_id is not None and hasattr(self, "mix_m_value_cache"):
        power = self.mix_m_value_cache.get(mix_id, 3.4)
        
    term_sum = 0.0
    for idx in range(n_mats):
        term_sum += (comp_zeffs[idx] ** power) * (percentages[idx] / 100.0)
    pred_zeff = term_sum ** (1.0 / power) if power != 0 else 0.0
    
    return pred_red, pred_zeff

def update_row_predictions(self, row, n_mats):
    if not hasattr(self, "table_mix_z_red"):
        return
    pred_red, pred_zeff = calculate_predicted_values(self, row, self.table_mix_z_red)
    if pred_red is not None and pred_zeff is not None:
        self.table_mix_z_red.blockSignals(True)
        
        # Read measured Zeff from column n_mats
        z_item = self.table_mix_z_red.item(row, n_mats)
        try:
            val_z = float(z_item.data(Qt.EditRole)) if z_item else 0.0
        except (ValueError, TypeError):
            try:
                val_z = float(z_item.text().replace(',', '.')) if z_item and z_item.text() else 0.0
            except ValueError:
                val_z = 0.0
                
        # Read measured RED from column n_mats + 4
        r_item = self.table_mix_z_red.item(row, n_mats + 4)
        try:
            val_r = float(r_item.data(Qt.EditRole)) if r_item else 0.0
        except (ValueError, TypeError):
            try:
                val_r = float(r_item.text().replace(',', '.')) if r_item and r_item.text() else 0.0
            except ValueError:
                val_r = 0.0
                
        # Update Pred. Zeff (column n_mats + 2)
        pz_item = self.table_mix_z_red.item(row, n_mats + 2)
        if not pz_item:
            pz_item = QTableWidgetItem()
            pz_item.setFlags(pz_item.flags() & ~Qt.ItemIsEditable)
            self.table_mix_z_red.setItem(row, n_mats + 2, pz_item)
        pz_item.setData(Qt.EditRole, pred_zeff)
        pz_item.setText(f"{pred_zeff:.4f}")
        
        # Update Diff. Zeff (column n_mats + 3): Zeff - Pred. Zeff
        diff_z = val_z - pred_zeff
        dz_item = self.table_mix_z_red.item(row, n_mats + 3)
        if not dz_item:
            dz_item = QTableWidgetItem()
            dz_item.setFlags(dz_item.flags() & ~Qt.ItemIsEditable)
            self.table_mix_z_red.setItem(row, n_mats + 3, dz_item)
        dz_item.setData(Qt.EditRole, diff_z)
        dz_item.setText(f"{diff_z:.4f}")
        
        # Update Pred. RED (column n_mats + 6)
        pr_item = self.table_mix_z_red.item(row, n_mats + 6)
        if not pr_item:
            pr_item = QTableWidgetItem()
            pr_item.setFlags(pr_item.flags() & ~Qt.ItemIsEditable)
            self.table_mix_z_red.setItem(row, n_mats + 6, pr_item)
        pr_item.setData(Qt.EditRole, pred_red)
        pr_item.setText(f"{pred_red:.4f}")
        
        # Update Diff. RED (column n_mats + 7): RED - Pred. RED
        diff_r = val_r - pred_red
        dr_item = self.table_mix_z_red.item(row, n_mats + 7)
        if not dr_item:
            dr_item = QTableWidgetItem()
            dr_item.setFlags(dr_item.flags() & ~Qt.ItemIsEditable)
            self.table_mix_z_red.setItem(row, n_mats + 7, dr_item)
        dr_item.setData(Qt.EditRole, diff_r)
        dr_item.setText(f"{diff_r:.4f}")
        
        self.table_mix_z_red.blockSignals(False)

# Triggered when user alters the Zeff m-value selector
def on_m_value_changed(self, val):
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is None:
        return
        
    self.mix_m_value_cache[mix_id] = val
    
    # Recalculate predictions and differences for all rows in Z & RED table
    start_row = -1
    total_rows = self.table_mat_mix.rowCount()
    for r in range(total_rows):
        spin = self.table_mat_mix.cellWidget(r, 0)
        if isinstance(spin, QSpinBox) and spin.property("mix_id") == mix_id:
            start_row = r
            group_size = spin.value()
            break
            
    if start_row != -1:
        mat_names = get_materials_in_mix(self, start_row, group_size)
        n_mats = len(mat_names)
        for r in range(self.table_mix_z_red.rowCount()):
            update_row_predictions(self, r, n_mats)
            
    update_mix_graph(self)

def sync_mix_tables(self, source, changed_item):
    if not hasattr(self, "table_mix_calibration_info") or not hasattr(self, "table_mix_z_red"):
        return
        
    row = changed_item.row()
    col = changed_item.column()
    
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is None:
        return
        
    start_row = -1
    total_rows = self.table_mat_mix.rowCount()
    for r in range(total_rows):
        spin = self.table_mat_mix.cellWidget(r, 0)
        if isinstance(spin, QSpinBox) and spin.property("mix_id") == mix_id:
            start_row = r
            group_size = spin.value()
            break
            
    if start_row == -1:
        return
        
    mat_names = get_materials_in_mix(self, start_row, group_size)
    n_mats = len(mat_names)
    
    val = changed_item.data(Qt.EditRole)
    val_str = changed_item.text()
    
    if source == self.table_mix_calibration_info:
        self.table_mix_z_red.blockSignals(True)
        if col < n_mats:
            target_item = self.table_mix_z_red.item(row, col)
            if not target_item:
                target_item = QTableWidgetItem()
                self.table_mix_z_red.setItem(row, col, target_item)
            target_item.setData(Qt.EditRole, val)
            target_item.setText(val_str)
            update_row_predictions(self, row, n_mats)
        else:
            std_col = col - n_mats
            if std_col == 6:  # RED in Info
                target_col = n_mats + 4  # RED in Z & RED
                set_target_cell(self.table_mix_z_red, row, target_col, val, val_str)
            elif std_col == 7:  # RED_STD in Info
                target_col = n_mats + 5  # STD in Z & RED
                set_target_cell(self.table_mix_z_red, row, target_col, val, val_str)
            elif std_col == 8:  # Zeff in Info
                target_col = n_mats  # Zeff in Z & RED
                set_target_cell(self.table_mix_z_red, row, target_col, val, val_str)
            elif std_col == 9:  # Zeff STD in Info
                target_col = n_mats + 1  # STD in Z & RED
                set_target_cell(self.table_mix_z_red, row, target_col, val, val_str)
        update_row_predictions(self, row, n_mats)
        self.table_mix_z_red.blockSignals(False)
        update_mix_graph(self)
        
    elif source == self.table_mix_z_red:
        self.table_mix_calibration_info.blockSignals(True)
        if col < n_mats:
            target_item = self.table_mix_calibration_info.item(row, col)
            if not target_item:
                target_item = QTableWidgetItem()
                self.table_mix_calibration_info.setItem(row, col, target_item)
            target_item.setData(Qt.EditRole, val)
            target_item.setText(val_str)
            update_row_predictions(self, row, n_mats)
        else:
            std_col = col - n_mats
            if std_col == 0:  # Zeff in Z & RED
                target_col = n_mats + 8  # Zeff in Info
                set_target_cell(self.table_mix_calibration_info, row, target_col, val, val_str)
            elif std_col == 1:  # STD (Zeff STD) in Z & RED
                target_col = n_mats + 9  # Zeff STD in Info
                set_target_cell(self.table_mix_calibration_info, row, target_col, val, val_str)
            elif std_col == 4:  # RED in Z & RED
                target_col = n_mats + 6  # RED in Info
                set_target_cell(self.table_mix_calibration_info, row, target_col, val, val_str)
            elif std_col == 5:  # STD (RED STD) in Z & RED
                target_col = n_mats + 7  # RED_STD in Info
                set_target_cell(self.table_mix_calibration_info, row, target_col, val, val_str)
        update_row_predictions(self, row, n_mats)
        self.table_mix_calibration_info.blockSignals(False)
        update_mix_graph(self)

def set_target_cell(table, r, c, val, val_str):
    item = table.item(r, c)
    if not item:
        item = QTableWidgetItem()
        table.setItem(r, c, item)
    item.setData(Qt.EditRole, val)
    item.setText(val_str)

def setup_3d_database_tab(self):
    # Create a vertical splitter to divide the Database tab into two rows
    self.splitter_3d_db = QSplitter(Qt.Vertical)
    
    # ------------------ TOP ROW (Table & Controls) ------------------
    top_widget = QWidget()
    top_layout = QVBoxLayout(top_widget)
    top_layout.setContentsMargins(5, 5, 5, 5)
    
    # Table Setup - 10 Columns
    self.table_3d_db = ClipboardTableWidget()
    self.table_3d_db.setColumnCount(10)
    self.table_3d_db.setHorizontalHeaderLabels([
        "Material Name", "Brand", "Type", "Color", "3DPrinter", "Date",
        "RED", "RED STD", "Zeff", "Zeff STD"
    ])
    self.table_3d_db.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.table_3d_db.setSelectionMode(QAbstractItemView.SingleSelection)
    self.table_3d_db.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    self.table_3d_db.horizontalHeader().setStretchLastSection(True)
    self.table_3d_db.setSortingEnabled(True)
    top_layout.addWidget(self.table_3d_db)
    
    # Connect cellClicked signal to automatically update details below ONLY when explicitly clicked (deferred to avoid closeEditor warning)
    self.table_3d_db.cellClicked.connect(lambda row, col: QTimer.singleShot(0, lambda: display_selected_filament_details(self)))
    
    # Connect itemChanged to automatically update the dropdown values in the mixed materials tab in real-time
    self.table_3d_db.itemChanged.connect(lambda: update_mat_mix_comboboxes(self))
    
    # Define row inserter and post paste handlers for main database
    def insert_db_row(r):
        self.table_3d_db.insertRow(r)
        for c in range(10):
            self.table_3d_db.setItem(r, c, QTableWidgetItem(""))
    self.table_3d_db.row_inserter = insert_db_row
    self.table_3d_db.post_paste_handler = lambda: update_mat_mix_comboboxes(self)
    
    # Set custom delegate for float columns to allow 4 decimal places during inline editing
    self.float_delegate = FloatDelegate(self.table_3d_db)
    self.table_3d_db.setItemDelegateForColumn(6, self.float_delegate)
    self.table_3d_db.setItemDelegateForColumn(7, self.float_delegate)
    self.table_3d_db.setItemDelegateForColumn(8, self.float_delegate)
    self.table_3d_db.setItemDelegateForColumn(9, self.float_delegate)
    
    # Add/Remove/Save buttons below the table
    btn_layout = QHBoxLayout()
    
    self.btn_3d_db_add = QPushButton("Add")
    self.btn_3d_db_add.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
    self.btn_3d_db_add.clicked.connect(lambda: add_material_dialog(self))
    
    self.btn_3d_db_remove = QPushButton("Remove")
    self.btn_3d_db_remove.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
    self.btn_3d_db_remove.clicked.connect(lambda: remove_selected_material(self))
    
    self.btn_3d_db_save = QPushButton("Save Changes")
    self.btn_3d_db_save.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
    self.btn_3d_db_save.clicked.connect(lambda: save_3d_database_action(self))
    
    btn_layout.addWidget(self.btn_3d_db_add)
    btn_layout.addWidget(self.btn_3d_db_remove)
    btn_layout.addWidget(self.btn_3d_db_save)
    btn_layout.addStretch()
    top_layout.addLayout(btn_layout)
    
    # ------------------ BOTTOM ROW (Tab Widget Details & Calibration) ------------------
    self.tabWidget_3d_detail = QTabWidget()
    
    # First Tab: Info (Calibration Measurements Table)
    self.tab_info = QWidget()
    self.info_layout = QVBoxLayout(self.tab_info)
    self.info_layout.setContentsMargins(10, 10, 10, 10)
    
    self.lbl_cal_title = QLabel("Calibration Measurements")
    self.lbl_cal_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #3b82f6;")
    self.info_layout.addWidget(self.lbl_cal_title)
    
    # Calibration Info Table Setup - 20 Columns
    self.table_calibration_info = ClipboardTableWidget()
    self.table_calibration_info.setColumnCount(20)
    self.table_calibration_info.setHorizontalHeaderLabels([
        "kV - Low", "kV - High", "HU-Low", "HU-Low STD", "HU-High", "HU-High STD",
        "RED", "RED_STD", "Zeff", "Zeff STD", "Print. Temp (C)", "Bed Temp (C)",
        "Infill Density (%)", "Infill Pattern", "Flow Multiplier", "Flow (%)",
        "Shape", "Layer Height (mm)", "Line Width (mm)", "Print Speed (mm/s)"
    ])
    self.table_calibration_info.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    self.table_calibration_info.horizontalHeader().setStretchLastSection(True)
    self.table_calibration_info.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.table_calibration_info.setSelectionMode(QAbstractItemView.SingleSelection)
    self.table_calibration_info.setSortingEnabled(True)
    self.info_layout.addWidget(self.table_calibration_info)
    
    # Define row inserter for calibration table
    def insert_cal_row(r):
        self.table_calibration_info.insertRow(r)
        self.table_calibration_info.setItem(r, 0, QTableWidgetItem("80"))
        self.table_calibration_info.setItem(r, 1, QTableWidgetItem("140"))
        for c in range(2, 20):
            item = QTableWidgetItem()
            if c in [13, 16]:
                item.setText("Grid" if c == 13 else "Cylinder")
            else:
                item.setData(Qt.EditRole, 0.0)
                item.setText("0.0000")
            self.table_calibration_info.setItem(r, c, item)
    self.table_calibration_info.row_inserter = insert_cal_row
    
    # Connect FloatDelegate to calibration table float columns (all except 0, 1, 13, 16)
    cal_float_cols = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 17, 18, 19]
    for c in cal_float_cols:
        self.table_calibration_info.setItemDelegateForColumn(c, self.float_delegate)
        
    # Calibration Action Buttons
    cal_btn_layout = QHBoxLayout()
    
    self.btn_cal_add = QPushButton("Add Calibration Row")
    self.btn_cal_add.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
    self.btn_cal_add.clicked.connect(lambda: add_calibration_row(self))
    
    self.btn_cal_remove = QPushButton("Remove Calibration Row")
    self.btn_cal_remove.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
    self.btn_cal_remove.clicked.connect(lambda: remove_calibration_row(self))
    
    cal_btn_layout.addWidget(self.btn_cal_add)
    cal_btn_layout.addWidget(self.btn_cal_remove)
    cal_btn_layout.addStretch()
    self.info_layout.addLayout(cal_btn_layout)
    
    # Second Tab: Notes
    self.tab_notes = QWidget()
    self.notes_layout = QVBoxLayout(self.tab_notes)
    self.notes_layout.setContentsMargins(10, 10, 10, 10)
    
    self.lbl_notes_title = QLabel("Filament Notes / Specifications")
    self.lbl_notes_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #3b82f6;")
    self.notes_layout.addWidget(self.lbl_notes_title)
    
    self.txt_notes = QTextEdit()
    self.txt_notes.setPlaceholderText("Enter notes, specs, or other general details about the filament...")
    self.txt_notes.setStyleSheet("background-color: #1e1e24; color: #ffffff; border: 1px solid #3c4450; border-radius: 4px;")
    self.notes_layout.addWidget(self.txt_notes)
    
    # Add Tabs to Detail Panel
    self.tabWidget_3d_detail.addTab(self.tab_info, "Info")
    self.tabWidget_3d_detail.addTab(self.tab_notes, "Notes")
    
    # Add rows to Splitter
    self.splitter_3d_db.addWidget(top_widget)
    self.splitter_3d_db.addWidget(self.tabWidget_3d_detail)
    self.splitter_3d_db.setSizes([300, 300])
    
    # Assign splitter to self.tab_18 layout
    layout_18 = QVBoxLayout(self.tab_18)
    layout_18.setContentsMargins(0, 0, 0, 0)
    layout_18.addWidget(self.splitter_3d_db)
    
    # Initialize variables for current filament view
    self.current_viewed_filament = None
    
    # Load all databases initially
    load_3d_database(self)
    load_all_calibration_data(self)
    
    # Select first row by default and trigger manual detail load on startup
    if self.table_3d_db.rowCount() > 0:
        self.table_3d_db.selectRow(0)
        display_selected_filament_details(self)

# Setup MatMix Tab
def setup_mat_mix_tab(self):
    self.splitter_mat_mix = QSplitter(Qt.Vertical)
    
    # ------------------ TOP ROW (Table & Controls) ------------------
    top_widget = QWidget()
    top_layout = QVBoxLayout(top_widget)
    top_layout.setContentsMargins(5, 5, 5, 5)
    
    self.lbl_mix_title = QLabel("Material Mix Database")
    self.lbl_mix_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #3b82f6; margin-bottom: 5px;")
    top_layout.addWidget(self.lbl_mix_title)
    
    # Setup mixed materials table
    self.table_mat_mix = ClipboardTableWidget()
    self.table_mat_mix.setColumnCount(9)
    self.table_mat_mix.setHorizontalHeaderLabels([
        "Mix Size", "Material Select", "Name", "RED", "Zeff",
        "Color", "Brand", "Type", "Printer"
    ])
    self.table_mat_mix.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.table_mat_mix.setSelectionMode(QAbstractItemView.SingleSelection)
    self.table_mat_mix.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    self.table_mat_mix.horizontalHeader().setStretchLastSection(True)
    self.table_mat_mix.setSortingEnabled(False)  # Sorting is disabled as groups represent linked items
    
    # Define row inserter and post paste handlers for mixed materials table
    def insert_mix_row(r):
        self.table_mat_mix.insertRow(r)
        populate_mix_row(self, r, has_spinbox=False)
    self.table_mat_mix.row_inserter = insert_mix_row
    self.table_mat_mix.post_paste_handler = lambda: (update_group_borders_and_properties(self), update_mat_mix_comboboxes(self))
    
    # Connect cellClicked signal to update details ONLY when explicitly clicked (deferred to avoid closeEditor warning)
    self.table_mat_mix.cellClicked.connect(lambda row, col: QTimer.singleShot(0, lambda: display_selected_mix_details(self)))
    
    # Attach Group delegate to draw divider boundaries
    self.mix_delegate = MixGroupDelegate(self.table_mat_mix)
    self.table_mat_mix.setItemDelegate(self.mix_delegate)
    top_layout.addWidget(self.table_mat_mix)
    
    # Buttons layout
    btn_layout = QHBoxLayout()
    
    self.btn_mix_add = QPushButton("Add Mix Group")
    self.btn_mix_add.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
    self.btn_mix_add.clicked.connect(lambda: add_mix_group(self))
    
    self.btn_mix_remove = QPushButton("Remove Selected Mix")
    self.btn_mix_remove.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
    self.btn_mix_remove.clicked.connect(lambda: remove_mix_group(self))
    
    self.btn_mix_save = QPushButton("Save Mixes")
    self.btn_mix_save.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
    self.btn_mix_save.clicked.connect(lambda: save_mix_database_action(self))
    
    btn_layout.addWidget(self.btn_mix_add)
    btn_layout.addWidget(self.btn_mix_remove)
    btn_layout.addWidget(self.btn_mix_save)
    btn_layout.addStretch()
    top_layout.addLayout(btn_layout)
    
    # ------------------ BOTTOM ROW (Tab Widget Details & Calibration) ------------------
    self.tabWidget_mix_detail = QTabWidget()
    
    # First Tab: Info
    self.tab_mix_info = QWidget()
    self.mix_info_layout = QVBoxLayout(self.tab_mix_info)
    self.mix_info_layout.setContentsMargins(10, 10, 10, 10)
    
    self.lbl_mix_cal_title = QLabel("Mix Calibration Data")
    self.lbl_mix_cal_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #3b82f6;")
    self.mix_info_layout.addWidget(self.lbl_mix_cal_title)
    
    # Informative Callout Alert Label above mix table
    self.lbl_mix_help = QLabel(
        "This table is intended for mix calibration and should contain data measured at 100% infill. "
        "Data intended for RED calibration (variable density/flow) are available in the next tab."
    )
    self.lbl_mix_help.setWordWrap(True)
    self.lbl_mix_help.setStyleSheet("""
        QLabel {
            background-color: #2b2b36;
            border-left: 4px solid #3b82f6;
            color: #d1d5db;
            padding: 10px 14px;
            border-radius: 4px;
            font-size: 12px;
            margin-top: 5px;
            margin-bottom: 5px;
            line-height: 1.4;
        }
    """)
    self.mix_info_layout.addWidget(self.lbl_mix_help)
    
    # Table Setup
    self.table_mix_calibration_info = ClipboardTableWidget()
    self.table_mix_calibration_info.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.table_mix_calibration_info.setSelectionMode(QAbstractItemView.SingleSelection)
    self.table_mix_calibration_info.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    self.table_mix_calibration_info.horizontalHeader().setStretchLastSection(True)
    self.table_mix_calibration_info.setSortingEnabled(True)
    self.mix_info_layout.addWidget(self.table_mix_calibration_info)
    
    # Define row inserter for mix calibration table
    def insert_mix_cal_row(r):
        self.table_mix_calibration_info.insertRow(r)
        self.table_mix_z_red.insertRow(r)
        n_mats = self.table_mix_calibration_info.columnCount() - 19
        for idx in range(n_mats):
            # Info ratios
            item_info = QTableWidgetItem()
            item_info.setData(Qt.EditRole, 0.0)
            item_info.setText("0.0000")
            self.table_mix_calibration_info.setItem(r, idx, item_info)
            # Z & RED ratios
            item_z = QTableWidgetItem()
            item_z.setData(Qt.EditRole, 0.0)
            item_z.setText("0.0000")
            self.table_mix_z_red.setItem(r, idx, item_z)
            
        for std_idx in range(19):
            c = n_mats + std_idx
            item = QTableWidgetItem()
            if std_idx == 10:
                item.setText("Grid")
            else:
                item.setData(Qt.EditRole, 0.0)
                item.setText("0.0000")
            self.table_mix_calibration_info.setItem(r, c, item)
            
        # Z & RED Standard columns (Zeff, STD, Pred Zeff, Diff Zeff, RED, STD, Pred RED, Diff RED)
        for std_idx in range(8):
            c = n_mats + std_idx
            item = QTableWidgetItem()
            item.setData(Qt.EditRole, 0.0)
            item.setText("0.0000")
            if std_idx in [2, 3, 6, 7]:  # Pred. and Diff. columns are read-only
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table_mix_z_red.setItem(r, c, item)
            
    self.table_mix_calibration_info.row_inserter = insert_mix_cal_row
    
    # Second Tab: Z & RED
    self.tab_mix_z_red = QWidget()
    self.mix_z_red_layout = QVBoxLayout(self.tab_mix_z_red)
    self.mix_z_red_layout.setContentsMargins(10, 10, 10, 10)
    
    # Header layout containing Title and Zeff m-value selector
    z_red_header_layout = QHBoxLayout()
    
    self.lbl_mix_z_red_title = QLabel("Zeff & RED Predictions")
    self.lbl_mix_z_red_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #3b82f6;")
    z_red_header_layout.addWidget(self.lbl_mix_z_red_title)
    
    z_red_header_layout.addStretch()
    
    self.lbl_m_value = QLabel("Zeff m-value:")
    self.lbl_m_value.setStyleSheet("font-weight: bold; color: #e5e7eb; margin-right: 5px;")
    z_red_header_layout.addWidget(self.lbl_m_value)
    
    self.spin_m_value = FocusDoubleSpinBox()
    self.spin_m_value.setRange(1.0, 10.0)
    self.spin_m_value.setValue(3.4)
    self.spin_m_value.setSingleStep(0.1)
    self.spin_m_value.setDecimals(2)
    self.spin_m_value.setStyleSheet("""
        QDoubleSpinBox {
            background-color: #2b2b36;
            border: 1px solid #4b5563;
            border-radius: 4px;
            color: #ffffff;
            padding: 4px;
            width: 70px;
        }
    """)
    self.spin_m_value.valueChanged.connect(lambda val: on_m_value_changed(self, val))
    z_red_header_layout.addWidget(self.spin_m_value)
    
    self.mix_z_red_layout.addLayout(z_red_header_layout)
    
    self.table_mix_z_red = ClipboardTableWidget()
    self.table_mix_z_red.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.table_mix_z_red.setSelectionMode(QAbstractItemView.SingleSelection)
    self.table_mix_z_red.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    self.table_mix_z_red.horizontalHeader().setStretchLastSection(True)
    self.table_mix_z_red.setSortingEnabled(True)
    self.mix_z_red_layout.addWidget(self.table_mix_z_red)
    
    # Define row inserter for mix Z & RED table
    def insert_mix_z_red_row(r):
        self.table_mix_z_red.insertRow(r)
        self.table_mix_calibration_info.insertRow(r)
        n_mats = self.table_mix_z_red.columnCount() - 8
        for idx in range(n_mats):
            # Z & RED ratios
            item_z = QTableWidgetItem()
            item_z.setData(Qt.EditRole, 0.0)
            item_z.setText("0.0000")
            self.table_mix_z_red.setItem(r, idx, item_z)
            # Info ratios
            item_info = QTableWidgetItem()
            item_info.setData(Qt.EditRole, 0.0)
            item_info.setText("0.0000")
            self.table_mix_calibration_info.setItem(r, idx, item_info)
            
        for std_idx in range(8):
            c = n_mats + std_idx
            item = QTableWidgetItem()
            item.setData(Qt.EditRole, 0.0)
            item.setText("0.0000")
            if std_idx in [2, 3, 6, 7]:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table_mix_z_red.setItem(r, c, item)
            
        for std_idx in range(19):
            c = n_mats + std_idx
            item = QTableWidgetItem()
            if std_idx == 10:
                item.setText("Grid")
            else:
                item.setData(Qt.EditRole, 0.0)
                item.setText("0.0000")
            self.table_mix_calibration_info.setItem(r, c, item)
            
    self.table_mix_z_red.row_inserter = insert_mix_z_red_row
    
    # Connect signals for real-time bi-directional synchronization between the two tables
    self.table_mix_calibration_info.itemChanged.connect(lambda item: sync_mix_tables(self, source=self.table_mix_calibration_info, changed_item=item))
    self.table_mix_z_red.itemChanged.connect(lambda item: sync_mix_tables(self, source=self.table_mix_z_red, changed_item=item))
    
    # Set post paste handlers to coordinate batch pastes correctly
    def sync_after_paste_calibration():
        self.table_mix_z_red.blockSignals(True)
        n_mats = self.table_mix_z_red.columnCount() - 8
        for r in range(self.table_mix_calibration_info.rowCount()):
            if r >= self.table_mix_z_red.rowCount():
                self.table_mix_z_red.insertRow(r)
            for c in range(n_mats):
                item_src = self.table_mix_calibration_info.item(r, c)
                if item_src:
                    set_target_cell(self.table_mix_z_red, r, c, item_src.data(Qt.EditRole), item_src.text())
            z_item = self.table_mix_calibration_info.item(r, n_mats + 8)
            zstd_item = self.table_mix_calibration_info.item(r, n_mats + 9)
            r_item = self.table_mix_calibration_info.item(r, n_mats + 6)
            rstd_item = self.table_mix_calibration_info.item(r, n_mats + 7)
            if z_item:
                set_target_cell(self.table_mix_z_red, r, n_mats, z_item.data(Qt.EditRole), z_item.text())
            if zstd_item:
                set_target_cell(self.table_mix_z_red, r, n_mats + 1, zstd_item.data(Qt.EditRole), zstd_item.text())
            if r_item:
                set_target_cell(self.table_mix_z_red, r, n_mats + 4, r_item.data(Qt.EditRole), r_item.text())
            if rstd_item:
                set_target_cell(self.table_mix_z_red, r, n_mats + 5, rstd_item.data(Qt.EditRole), rstd_item.text())
            update_row_predictions(self, r, n_mats)
        self.table_mix_z_red.blockSignals(False)
        update_mix_graph(self)
    self.table_mix_calibration_info.post_paste_handler = sync_after_paste_calibration
    
    def sync_after_paste_z_red():
        self.table_mix_calibration_info.blockSignals(True)
        n_mats = self.table_mix_z_red.columnCount() - 8
        for r in range(self.table_mix_z_red.rowCount()):
            if r >= self.table_mix_calibration_info.rowCount():
                self.table_mix_calibration_info.insertRow(r)
            for c in range(n_mats):
                item_src = self.table_mix_z_red.item(r, c)
                if item_src:
                    set_target_cell(self.table_mix_calibration_info, r, c, item_src.data(Qt.EditRole), item_src.text())
            z_item = self.table_mix_z_red.item(r, n_mats)
            zstd_item = self.table_mix_z_red.item(r, n_mats + 1)
            r_item = self.table_mix_z_red.item(r, n_mats + 4)
            rstd_item = self.table_mix_z_red.item(r, n_mats + 5)
            if z_item:
                set_target_cell(self.table_mix_calibration_info, r, n_mats + 8, z_item.data(Qt.EditRole), z_item.text())
            if zstd_item:
                set_target_cell(self.table_mix_calibration_info, r, n_mats + 9, zstd_item.data(Qt.EditRole), zstd_item.text())
            if r_item:
                set_target_cell(self.table_mix_calibration_info, r, n_mats + 6, r_item.data(Qt.EditRole), r_item.text())
            if rstd_item:
                set_target_cell(self.table_mix_calibration_info, r, n_mats + 7, rstd_item.data(Qt.EditRole), rstd_item.text())
            update_row_predictions(self, r, n_mats)
        self.table_mix_calibration_info.blockSignals(False)
        update_mix_graph(self)
    self.table_mix_z_red.post_paste_handler = sync_after_paste_z_red
    
    # Buttons for Mix Calibration
    mix_cal_btn_layout = QHBoxLayout()
    self.btn_mix_cal_add = QPushButton("Add Calibration Row")
    self.btn_mix_cal_add.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
    self.btn_mix_cal_add.clicked.connect(lambda: add_mix_calibration_row(self))
    
    self.btn_mix_cal_remove = QPushButton("Remove Calibration Row")
    self.btn_mix_cal_remove.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
    self.btn_mix_cal_remove.clicked.connect(lambda: remove_mix_calibration_row(self))
    
    mix_cal_btn_layout.addWidget(self.btn_mix_cal_add)
    mix_cal_btn_layout.addWidget(self.btn_mix_cal_remove)
    mix_cal_btn_layout.addStretch()
    self.mix_info_layout.addLayout(mix_cal_btn_layout)
    
    # Third Tab: Notes
    self.tab_mix_notes = QWidget()
    self.mix_notes_layout = QVBoxLayout(self.tab_mix_notes)
    self.mix_notes_layout.setContentsMargins(10, 10, 10, 10)
    
    self.lbl_mix_notes_title = QLabel("Mix Notes / Specifications")
    self.lbl_mix_notes_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #3b82f6;")
    self.mix_notes_layout.addWidget(self.lbl_mix_notes_title)
    
    self.txt_mix_notes = QTextEdit()
    self.txt_mix_notes.setPlaceholderText("Enter notes, specs, or other general details about the material mix...")
    self.txt_mix_notes.setStyleSheet("background-color: #1e1e24; color: #ffffff; border: 1px solid #3c4450; border-radius: 4px;")
    self.mix_notes_layout.addWidget(self.txt_mix_notes)
    
    # Mix RED tab setup
    self.tab_mix_red = QWidget()
    self.mix_red_layout = QHBoxLayout(self.tab_mix_red)
    self.mix_red_layout.setContentsMargins(10, 10, 10, 10)
    
    self.splitter_mix_red = QSplitter(Qt.Horizontal)
    
    # Left widget: List and Buttons
    mix_red_left = QWidget()
    mix_red_left_layout = QVBoxLayout(mix_red_left)
    mix_red_left_layout.setContentsMargins(0, 0, 0, 0)
    
    self.lbl_mix_red_list_title = QLabel("Percentage Combinations")
    self.lbl_mix_red_list_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #3b82f6;")
    mix_red_left_layout.addWidget(self.lbl_mix_red_list_title)
    
    self.list_mix_red_ratios = QtWidgets.QListWidget()
    self.list_mix_red_ratios.setStyleSheet("""
        QListWidget {
            background-color: #1e1e24;
            color: #ffffff;
            border: 1px solid #3c4450;
            border-radius: 4px;
            padding: 5px;
        }
        QListWidget::item {
            padding: 6px;
            border-bottom: 1px solid #2b2b36;
        }
        QListWidget::item:selected {
            background-color: #3b82f6;
            color: #ffffff;
        }
    """)
    self.list_mix_red_ratios.currentRowChanged.connect(lambda idx: display_selected_mix_red_ratio_details(self, idx))
    mix_red_left_layout.addWidget(self.list_mix_red_ratios)
    
    mix_red_left_btn_layout = QHBoxLayout()
    self.btn_mix_red_ratio_add = QPushButton("Add")
    self.btn_mix_red_ratio_add.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
    self.btn_mix_red_ratio_add.clicked.connect(lambda: add_mix_red_ratio(self))
    
    self.btn_mix_red_ratio_edit = QPushButton("Edit")
    self.btn_mix_red_ratio_edit.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
    self.btn_mix_red_ratio_edit.clicked.connect(lambda: edit_mix_red_ratio(self))
    
    self.btn_mix_red_ratio_remove = QPushButton("Remove")
    self.btn_mix_red_ratio_remove.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
    self.btn_mix_red_ratio_remove.clicked.connect(lambda: remove_mix_red_ratio(self))
    
    mix_red_left_btn_layout.addWidget(self.btn_mix_red_ratio_add)
    mix_red_left_btn_layout.addWidget(self.btn_mix_red_ratio_edit)
    mix_red_left_btn_layout.addWidget(self.btn_mix_red_ratio_remove)
    mix_red_left_layout.addLayout(mix_red_left_btn_layout)
    
    # Right widget: Table and Buttons
    mix_red_right = QWidget()
    mix_red_right_layout = QVBoxLayout(mix_red_right)
    mix_red_right_layout.setContentsMargins(0, 0, 0, 0)
    
    self.lbl_mix_red_table_title = QLabel("Calibration Measurements for Selected Ratio")
    self.lbl_mix_red_table_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #3b82f6;")
    mix_red_right_layout.addWidget(self.lbl_mix_red_table_title)
    
    self.table_mix_red_cal = ClipboardTableWidget()
    self.table_mix_red_cal.setColumnCount(11)
    self.table_mix_red_cal.setHorizontalHeaderLabels([
        "Infill %", "Flow", "HU-Low", "HU-Low STD", "HU-High", "HU-High STD",
        "RED", "RED STD", "Pred. RED", "kV - Low", "kV - High"
    ])
    self.table_mix_red_cal.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    self.table_mix_red_cal.horizontalHeader().setStretchLastSection(True)
    self.table_mix_red_cal.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.table_mix_red_cal.setSelectionMode(QAbstractItemView.SingleSelection)
    self.table_mix_red_cal.setSortingEnabled(True)
    self.table_mix_red_cal.setItemDelegate(self.float_delegate)
    
    # Connect itemChanged to handle inline cell editing and update Pred. RED / cache
    self.table_mix_red_cal.itemChanged.connect(lambda item: on_mix_red_cal_cell_changed(self, item))
    
    # Connect post-paste handler
    def sync_mix_red_after_paste():
        mix_id = getattr(self, "current_viewed_mix_id", None)
        ratio_idx = self.list_mix_red_ratios.currentRow()
        if mix_id is not None and ratio_idx >= 0:
            mix_red_data = self.mix_red_cache.get(mix_id, [])
            if ratio_idx < len(mix_red_data):
                combination = mix_red_data[ratio_idx]
                ratios = combination["percentage"]
                pred_red = calculate_mix_red_predicted_val(self, ratios)
                
                self.table_mix_red_cal.blockSignals(True)
                for r in range(self.table_mix_red_cal.rowCount()):
                    pred_item = self.table_mix_red_cal.item(r, 8)
                    if not pred_item:
                        pred_item = QTableWidgetItem()
                        pred_item.setFlags(pred_item.flags() & ~Qt.ItemIsEditable)
                        self.table_mix_red_cal.setItem(r, 8, pred_item)
                    pred_item.setData(Qt.EditRole, pred_red)
                    pred_item.setText(f"{pred_red:.4f}")
                self.table_mix_red_cal.blockSignals(False)
                
                save_mix_red_table_to_cache(self, mix_id, ratio_idx)
    self.table_mix_red_cal.post_paste_handler = sync_mix_red_after_paste
    
    mix_red_right_layout.addWidget(self.table_mix_red_cal)
    
    mix_red_right_btn_layout = QHBoxLayout()
    self.btn_mix_red_cal_add = QPushButton("Add Calibration Row")
    self.btn_mix_red_cal_add.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
    self.btn_mix_red_cal_add.clicked.connect(lambda: add_mix_red_cal_row(self))
    
    self.btn_mix_red_cal_remove = QPushButton("Remove Calibration Row")
    self.btn_mix_red_cal_remove.setStyleSheet("background-color: blue; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
    self.btn_mix_red_cal_remove.clicked.connect(lambda: remove_mix_red_cal_row(self))
    
    mix_red_right_btn_layout.addWidget(self.btn_mix_red_cal_add)
    mix_red_right_btn_layout.addWidget(self.btn_mix_red_cal_remove)
    mix_red_right_btn_layout.addStretch()
    mix_red_right_layout.addLayout(mix_red_right_btn_layout)
    
    self.splitter_mix_red.addWidget(mix_red_left)
    self.splitter_mix_red.addWidget(mix_red_right)
    self.splitter_mix_red.setSizes([250, 550])
    self.mix_red_layout.addWidget(self.splitter_mix_red)
    
    # Fourth Tab: Graphs (lazy-loaded placeholder)
    self.tab_mix_graphs = QWidget()
    self.mix_graphs_layout = QVBoxLayout(self.tab_mix_graphs)
    self.mix_graphs_layout.setContentsMargins(10, 10, 10, 10)
    
    # Placeholder label
    self.lbl_graph_placeholder = QLabel("Click to load and view graphs...")
    self.lbl_graph_placeholder.setAlignment(Qt.AlignCenter)
    self.lbl_graph_placeholder.setStyleSheet("color: #9ca3af; font-size: 14px; font-weight: bold;")
    self.mix_graphs_layout.addWidget(self.lbl_graph_placeholder)
    
    self.tabWidget_mix_detail.addTab(self.tab_mix_info, "Info")
    self.tabWidget_mix_detail.addTab(self.tab_mix_z_red, "Z & RED")
    self.tabWidget_mix_detail.addTab(self.tab_mix_red, "Mix RED")
    self.tabWidget_mix_detail.addTab(self.tab_mix_notes, "Notes")
    self.tabWidget_mix_detail.addTab(self.tab_mix_graphs, "Graphs")
    
    # Listen to tab change events to initialize graphs lazily
    self.tabWidget_mix_detail.currentChanged.connect(lambda idx: on_mix_tab_changed(self, idx))
    
    # Add widgets to splitter
    self.splitter_mat_mix.addWidget(top_widget)
    self.splitter_mat_mix.addWidget(self.tabWidget_mix_detail)
    self.splitter_mat_mix.setSizes([300, 300])
    
    # Assign splitter to self.tab_27 layout
    layout_27 = QVBoxLayout(self.tab_27)
    layout_27.setContentsMargins(0, 0, 0, 0)
    layout_27.addWidget(self.splitter_mat_mix)
    
    # Initialize cache structures
    self.current_viewed_mix_id = None
    self.mix_calibration_cache = {}
    self.mix_notes_cache = {}
    self.mix_m_value_cache = {}
    self.mix_red_cache = {}
    
    # Store global trigger update function
    self.update_mix_graph_func = lambda: update_mix_graph(self)
    
    # Load initial mixed filament records
    load_mix_database(self)
    load_all_mix_calibration_data(self)
    
    # Select first row by default and trigger manual detail load on startup
    if self.table_mat_mix.rowCount() > 0:
        self.table_mat_mix.selectRow(0)
        display_selected_mix_details(self)

def on_mix_tab_changed(self, index):
    # Tab 4 is the Graphs tab
    if index == 4:
        initialize_mix_graph(self)

def initialize_mix_graph(self):
    if hasattr(self, "graph_canvas"):
        return # Already initialized
        
    # Remove placeholder label
    if hasattr(self, "lbl_graph_placeholder"):
        self.mix_graphs_layout.removeWidget(self.lbl_graph_placeholder)
        self.lbl_graph_placeholder.deleteLater()
        del self.lbl_graph_placeholder
        
    # Import matplotlib lazily
    import_matplotlib_lazy()
    
    # Axis selector dropdowns layout
    graph_ctrl_layout = QHBoxLayout()
    
    self.lbl_graph_x = QLabel("X Axis:")
    self.lbl_graph_x.setStyleSheet("font-weight: bold; color: #e5e7eb; margin-right: 5px;")
    graph_ctrl_layout.addWidget(self.lbl_graph_x)
    
    self.combo_graph_x = FocusComboBox()
    self.combo_graph_x.setStyleSheet("""
        QComboBox {
            background-color: #2b2b36;
            border: 1px solid #4b5563;
            border-radius: 4px;
            color: #ffffff;
            padding: 4px;
            min-width: 180px;
        }
    """)
    self.combo_graph_x.currentTextChanged.connect(lambda: update_mix_graph(self))
    graph_ctrl_layout.addWidget(self.combo_graph_x)
    
    graph_ctrl_layout.addSpacing(15)
    
    self.lbl_graph_y = QLabel("Y Axis:")
    self.lbl_graph_y.setStyleSheet("font-weight: bold; color: #e5e7eb; margin-right: 5px;")
    graph_ctrl_layout.addWidget(self.lbl_graph_y)
    
    self.combo_graph_y = FocusComboBox()
    self.combo_graph_y.setStyleSheet("""
        QComboBox {
            background-color: #2b2b36;
            border: 1px solid #4b5563;
            border-radius: 4px;
            color: #ffffff;
            padding: 4px;
            min-width: 180px;
        }
    """)
    self.combo_graph_y.currentTextChanged.connect(lambda: update_mix_graph(self))
    graph_ctrl_layout.addWidget(self.combo_graph_y)
    
    graph_ctrl_layout.addStretch()
    self.mix_graphs_layout.addLayout(graph_ctrl_layout)
    
    self.graph_figure = Figure(facecolor="#1e1e24")
    self.graph_canvas = FigureCanvas(self.graph_figure)
    self.graph_canvas.setStyleSheet("background-color: #1e1e24;")
    self.mix_graphs_layout.addWidget(self.graph_canvas)
    
    # Add Navigation Toolbar
    if NavigationToolbar is not None:
        self.graph_toolbar = NavigationToolbar(self.graph_canvas, self.tab_mix_graphs)
        self.graph_toolbar.setStyleSheet("""
            QToolBar {
                background-color: #1e1e24;
                border: none;
                spacing: 5px;
            }
            QToolButton {
                background-color: #2b2b36;
                color: #ffffff;
                border: 1px solid #4b5563;
                border-radius: 4px;
                padding: 2px;
            }
            QToolButton:hover {
                background-color: #3b82f6;
            }
        """)
        self.mix_graphs_layout.addWidget(self.graph_toolbar)
        
    # Re-trigger display details so that the dropdown variables are populated for the first time
    # (Since on startup they were skipped as graph_canvas did not exist yet)
    self.combo_graph_x.blockSignals(True)
    self.combo_graph_y.blockSignals(True)
    
    start_row = -1
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is not None:
        total_rows = self.table_mat_mix.rowCount()
        for r in range(total_rows):
            spin = self.table_mat_mix.cellWidget(r, 0)
            if isinstance(spin, QSpinBox) and spin.property("mix_id") == mix_id:
                start_row = r
                group_size = spin.value()
                break
                
        if start_row != -1:
            mat_names = get_materials_in_mix(self, start_row, group_size)
            
            # 1. Ratios
            for idx, name in enumerate(mat_names):
                self.combo_graph_x.addItem(f"% {name}", ("ratio", idx))
                self.combo_graph_y.addItem(f"% {name}", ("ratio", idx))
                
            # 2. Properties
            props = [
                ("Zeff", ("property", "Zeff")),
                ("Pred. Zeff", ("property", "Pred. Zeff")),
                ("Diff. Zeff", ("property", "Diff. Zeff")),
                ("RED", ("property", "RED")),
                ("Pred. RED", ("property", "Pred. RED")),
                ("Diff. RED", ("property", "Diff. RED"))
            ]
            for label, val in props:
                self.combo_graph_x.addItem(label, val)
                self.combo_graph_y.addItem(label, val)
                
            self.combo_graph_x.setCurrentIndex(0)
            zeff_idx = self.combo_graph_y.findText("Zeff")
            if zeff_idx >= 0:
                self.combo_graph_y.setCurrentIndex(zeff_idx)
            else:
                self.combo_graph_y.setCurrentIndex(min(1, self.combo_graph_y.count() - 1))
                
    self.combo_graph_x.blockSignals(False)
    self.combo_graph_y.blockSignals(False)
    
    update_mix_graph(self)

def display_selected_filament_details(self):
    selected_ranges = self.table_3d_db.selectedRanges()
    if selected_ranges:
        row = selected_ranges[0].topRow()
    else:
        row = self.table_3d_db.currentRow()
        
    if row < 0 or row >= self.table_3d_db.rowCount():
        return
        
    # Save currently active cached values before loading the new selection
    save_current_active_material_cache(self)
    
    # Read the material name
    name_item = self.table_3d_db.item(row, 0)
    name = name_item.text() if name_item else ""
    if not name:
        return
        
    # If same filament is already viewed, don't perform redundant re-rendering
    if name == getattr(self, "current_viewed_filament", None):
        return
        
    self.current_viewed_filament = name
    self.lbl_cal_title.setText(f"Calibration Measurements for: {name}")
    self.lbl_notes_title.setText(f"Notes & Specifications for: {name}")
    
    # Load and display calibration info
    self.table_calibration_info.blockSignals(True)
    self.table_calibration_info.clearContents() # Clear widgets to prevent QAbstractItemView warnings
    self.table_calibration_info.setRowCount(0)
    
    cal_rows = self.calibration_data_cache.get(name, [])
    for row_data in cal_rows:
        row_idx = self.table_calibration_info.rowCount()
        self.table_calibration_info.insertRow(row_idx)
        
        # Text settings (kV_low, kV_hig)
        self.table_calibration_info.setItem(row_idx, 0, QTableWidgetItem(row_data[0]))
        self.table_calibration_info.setItem(row_idx, 1, QTableWidgetItem(row_data[1]))
        
        # Numeric settings (with 4 decimal places)
        numeric_indices = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 17, 18, 19]
        for c in range(20):
            if c in [0, 1]:
                continue
            item = QTableWidgetItem()
            val_str = row_data[c]
            if c in numeric_indices:
                try:
                    float_val = float(val_str)
                    item.setData(Qt.EditRole, float_val)
                    item.setText(f"{float_val:.4f}")
                except ValueError:
                    item.setData(Qt.EditRole, 0.0)
                    item.setText("0.0000")
            else:
                item = QTableWidgetItem(val_str)
            self.table_calibration_info.setItem(row_idx, c, item)
            
    self.table_calibration_info.blockSignals(False)
    
    # Load notes
    filament_notes = self.notes_cache.get(name, "")
    self.txt_notes.setPlainText(filament_notes)

def save_current_active_material_cache(self):
    if hasattr(self, "current_viewed_filament") and self.current_viewed_filament:
        rows = []
        for r in range(self.table_calibration_info.rowCount()):
            row_data = []
            for c in range(20):
                item = self.table_calibration_info.item(r, c)
                if item is not None:
                    if c in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 17, 18, 19]:
                        val = item.data(Qt.EditRole)
                        row_data.append(str(val))
                    else:
                        row_data.append(item.text())
                else:
                    row_data.append("")
            rows.append(row_data)
        self.calibration_data_cache[self.current_viewed_filament] = rows
        
        # Save notes text to cache
        self.notes_cache[self.current_viewed_filament] = self.txt_notes.toPlainText()

def load_3d_database(self):
    db_path = get_db_path()
    
    # If the file does not exist, initialize it with default values
    if not os.path.exists(db_path):
        try:
            with open(db_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["Material Name", "Brand", "Type", "Color", "3DPrinter", "Date", "RED", "RED STD", "Zeff", "Zeff STD"])
                for item in default_filaments:
                    writer.writerow([
                        item["Material Name"], item["Brand"], item["Type"], item["Color"], item["3DPrinter"], "2026-07-19",
                        item["RED"], item["RED STD"], item["Zeff"], item["Zeff STD"]
                    ])
        except Exception as e:
            print(f"Error initializing 3D database: {e}")
            
    # Read the CSV file
    self.table_3d_db.setSortingEnabled(False)
    self.table_3d_db.blockSignals(True)
    self.table_3d_db.clearContents()
    self.table_3d_db.setRowCount(0)
    
    try:
        with open(db_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None) # skip header
            
            for row in reader:
                if not row or len(row) < 8:
                    continue
                
                # Graceful migration for older formats (8-column and 9-column versions)
                if len(row) == 8:
                    row = row[:4] + ["All", "2026-07-19"] + row[4:]
                elif len(row) == 9:
                    row = row[:5] + ["2026-07-19"] + row[5:]
                    
                row_idx = self.table_3d_db.rowCount()
                self.table_3d_db.insertRow(row_idx)
                
                # Material Name, Brand, Type, Color, 3DPrinter, Date
                self.table_3d_db.setItem(row_idx, 0, QTableWidgetItem(row[0]))
                self.table_3d_db.setItem(row_idx, 1, QTableWidgetItem(row[1]))
                self.table_3d_db.setItem(row_idx, 2, QTableWidgetItem(row[2]))
                self.table_3d_db.setItem(row_idx, 3, QTableWidgetItem(row[3]))
                self.table_3d_db.setItem(row_idx, 4, QTableWidgetItem(row[4]))
                self.table_3d_db.setItem(row_idx, 5, QTableWidgetItem(row[5]))
                
                # RED, RED STD, Zeff, Zeff STD (numeric items for numeric sorting)
                for col_offset, val in enumerate(row[6:10]):
                    item = QTableWidgetItem()
                    try:
                        float_val = float(val)
                        item.setData(Qt.EditRole, float_val)
                        item.setText(f"{float_val:.4f}")
                    except ValueError:
                        item.setData(Qt.EditRole, 0.0)
                        item.setText("0.0000")
                    self.table_3d_db.setItem(row_idx, 6 + col_offset, item)
    except Exception as e:
        print(f"Error loading 3D database: {e}")
        
    self.table_3d_db.blockSignals(False)
    self.table_3d_db.setSortingEnabled(True)
    if hasattr(self, "table_mat_mix"):
        update_mat_mix_comboboxes(self)

def save_3d_database(self):
    db_path = get_db_path()
    
    try:
        with open(db_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Material Name", "Brand", "Type", "Color", "3DPrinter", "Date", "RED", "RED STD", "Zeff", "Zeff STD"])
            
            for r in range(self.table_3d_db.rowCount()):
                row_data = []
                for c in range(10):
                    item = self.table_3d_db.item(r, c)
                    if item is not None:
                        val = item.data(Qt.EditRole)
                        row_data.append(str(val))
                    else:
                        row_data.append("")
                writer.writerow(row_data)
    except Exception as e:
        print(f"Error saving 3D database: {e}")

def load_all_calibration_data(self):
    self.calibration_data_cache = {}
    self.notes_cache = {}
    
    cal_db_path = get_cal_db_path()
    
    # Initialize defaults if file doesn't exist
    if not os.path.exists(cal_db_path):
        try:
            with open(cal_db_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Material Name", "kV_low", "kV_hig", "HU_low", "HU_low_STD", "HU_hig", "HU_hig_STD",
                    "RED", "RED_STD", "Zeff", "Zeff STD", "Print Temp", "Bed Temp", "Infill Density", "Infill Pattern",
                    "Flow Multiplier", "Flow", "Shape", "Layer Height", "Line Width", "Print Speed"
                ])
                for row in default_calibrations:
                    writer.writerow(row)
        except Exception as e:
            print(f"Error initializing calibration database: {e}")
            
    # Read the calibration CSV
    try:
        with open(cal_db_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            
            for row in reader:
                if not row or len(row) < 17:
                    continue
                
                # Graceful migration for older 17-column calibration formats (adding the 4 HU columns)
                if len(row) == 17:
                    row = row[:3] + ["100.0000", "5.0000", "150.0000", "5.0000"] + row[3:]
                    
                mat_name = row[0]
                if mat_name not in self.calibration_data_cache:
                    self.calibration_data_cache[mat_name] = []
                self.calibration_data_cache[mat_name].append(row[1:])
    except Exception as e:
        print(f"Error loading calibration database: {e}")
        
    # Read the notes JSON database
    notes_path = get_notes_db_path()
    if os.path.exists(notes_path):
        try:
            with open(notes_path, mode='r', encoding='utf-8') as f:
                self.notes_cache = json.load(f)
        except Exception as e:
            print(f"Error loading notes database: {e}")

def save_calibration_database(self):
    cal_db_path = get_cal_db_path()
    try:
        with open(cal_db_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Material Name", "kV_low", "kV_hig", "HU_low", "HU_low_STD", "HU_hig", "HU_hig_STD",
                "RED", "RED_STD", "Zeff", "Zeff STD", "Print Temp", "Bed Temp", "Infill Density", "Infill Pattern",
                "Flow Multiplier", "Flow", "Shape", "Layer Height", "Line Width", "Print Speed"
            ])
            for mat_name, rows in self.calibration_data_cache.items():
                for row in rows:
                    writer.writerow([mat_name] + row)
    except Exception as e:
        print(f"Error saving calibration database: {e}")
        
    notes_path = get_notes_db_path()
    try:
        with open(notes_path, mode='w', encoding='utf-8') as f:
            json.dump(self.notes_cache, f, indent=4)
    except Exception as e:
        print(f"Error saving notes database: {e}")

def save_3d_database_action(self):
    save_current_active_material_cache(self)
    save_3d_database(self)
    save_calibration_database(self)
    update_mat_mix_comboboxes(self)
    QMessageBox.information(self, "Success", "Material database and calibration info saved successfully!")

def remove_selected_material(self):
    selected_ranges = self.table_3d_db.selectedRanges()
    if selected_ranges:
        row = selected_ranges[0].topRow()
    else:
        row = self.table_3d_db.currentRow()
        
    if row >= 0 and row < self.table_3d_db.rowCount():
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove line {row + 1}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.table_3d_db.setSortingEnabled(False)
            self.table_3d_db.blockSignals(True)
            self.table_3d_db.removeRow(row)
            self.table_3d_db.blockSignals(False)
            self.table_3d_db.setSortingEnabled(True)
            
            # Clear details view
            self.current_viewed_filament = None
            self.lbl_cal_title.setText("Calibration Measurements")
            self.lbl_notes_title.setText("Filament Notes / Specifications")
            self.table_calibration_info.clearContents()
            self.table_calibration_info.setRowCount(0)
            self.txt_notes.clear()
            if hasattr(self, "table_mat_mix"):
                update_mat_mix_comboboxes(self)
    else:
        QMessageBox.information(self, "Information", "Please select a line in the database table to remove first.")

# Insert new calibration row below the selected row
def add_calibration_row(self):
    if not getattr(self, "current_viewed_filament", None):
        QMessageBox.warning(self, "Warning", "Please select a material first.")
        return
        
    selected_ranges = self.table_calibration_info.selectedRanges()
    if selected_ranges:
        current_row = selected_ranges[0].topRow()
    else:
        current_row = self.table_calibration_info.currentRow()
        
    self.table_calibration_info.setSortingEnabled(False)
    self.table_calibration_info.blockSignals(True)
    
    if current_row >= 0:
        row_idx = current_row + 1
    else:
        row_idx = self.table_calibration_info.rowCount()
        
    self.table_calibration_info.insertRow(row_idx)
    
    # kV_low, kV_hig
    self.table_calibration_info.setItem(row_idx, 0, QTableWidgetItem("80"))
    self.table_calibration_info.setItem(row_idx, 1, QTableWidgetItem("140"))
    
    # HU-Low
    item_hulow = QTableWidgetItem()
    item_hulow.setData(Qt.EditRole, 100.0000)
    item_hulow.setText("100.0000")
    self.table_calibration_info.setItem(row_idx, 2, item_hulow)
    
    # HU-Low STD
    item_hulow_std = QTableWidgetItem()
    item_hulow_std.setData(Qt.EditRole, 5.0000)
    item_hulow_std.setText("5.0000")
    self.table_calibration_info.setItem(row_idx, 3, item_hulow_std)
    
    # HU-High
    item_huhigh = QTableWidgetItem()
    item_huhigh.setData(Qt.EditRole, 150.0000)
    item_huhigh.setText("150.0000")
    self.table_calibration_info.setItem(row_idx, 4, item_huhigh)
    
    # HU-High STD
    item_huhigh_std = QTableWidgetItem()
    item_huhigh_std.setData(Qt.EditRole, 5.0000)
    item_huhigh_std.setText("5.0000")
    self.table_calibration_info.setItem(row_idx, 5, item_huhigh_std)
    
    # RED
    item_red = QTableWidgetItem()
    item_red.setData(Qt.EditRole, 1.0000)
    item_red.setText("1.0000")
    self.table_calibration_info.setItem(row_idx, 6, item_red)
    
    # RED STD
    item_red_std = QTableWidgetItem()
    item_red_std.setData(Qt.EditRole, 0.0200)
    item_red_std.setText("0.0200")
    self.table_calibration_info.setItem(row_idx, 7, item_red_std)
    
    # Zeff
    item_zeff = QTableWidgetItem()
    item_zeff.setData(Qt.EditRole, 6.0000)
    item_zeff.setText("6.0000")
    self.table_calibration_info.setItem(row_idx, 8, item_zeff)
    
    # Zeff STD
    item_zeff_std = QTableWidgetItem()
    item_zeff_std.setData(Qt.EditRole, 0.1000)
    item_zeff_std.setText("0.1000")
    self.table_calibration_info.setItem(row_idx, 9, item_zeff_std)
    
    # Print Temp
    item_ptemp = QTableWidgetItem()
    item_ptemp.setData(Qt.EditRole, 210.0)
    item_ptemp.setText("210.0000")
    self.table_calibration_info.setItem(row_idx, 10, item_ptemp)
    
    # Bed Temp
    item_btemp = QTableWidgetItem()
    item_btemp.setData(Qt.EditRole, 60.0)
    item_btemp.setText("60.0000")
    self.table_calibration_info.setItem(row_idx, 11, item_btemp)
    
    # Infill Density
    item_infill = QTableWidgetItem()
    item_infill.setData(Qt.EditRole, 100.0)
    item_infill.setText("100.0000")
    self.table_calibration_info.setItem(row_idx, 12, item_infill)
    
    # Infill Pattern
    self.table_calibration_info.setItem(row_idx, 13, QTableWidgetItem("Grid"))
    
    # Flow Multiplier
    item_fmult = QTableWidgetItem()
    item_fmult.setData(Qt.EditRole, 1.0)
    item_fmult.setText("1.0000")
    self.table_calibration_info.setItem(row_idx, 14, item_fmult)
    
    # Flow
    item_flow = QTableWidgetItem()
    item_flow.setData(Qt.EditRole, 100.0)
    item_flow.setText("100.0000")
    self.table_calibration_info.setItem(row_idx, 15, item_flow)
    
    # Shape
    self.table_calibration_info.setItem(row_idx, 16, QTableWidgetItem("Cylinder"))
    
    # Layer Height
    item_lheight = QTableWidgetItem()
    item_lheight.setData(Qt.EditRole, 0.2000)
    item_lheight.setText("0.2000")
    self.table_calibration_info.setItem(row_idx, 17, item_lheight)
    
    # Line Width
    item_lwidth = QTableWidgetItem()
    item_lwidth.setData(Qt.EditRole, 0.4000)
    item_lwidth.setText("0.4000")
    self.table_calibration_info.setItem(row_idx, 18, item_lwidth)
    
    # Print Speed
    item_speed = QTableWidgetItem()
    item_speed.setData(Qt.EditRole, 50.0)
    item_speed.setText("50.0000")
    self.table_calibration_info.setItem(row_idx, 19, item_speed)
    
    self.table_calibration_info.blockSignals(False)
    self.table_calibration_info.setSortingEnabled(True)
    self.table_calibration_info.selectRow(row_idx)

def remove_calibration_row(self):
    selected_ranges = self.table_calibration_info.selectedRanges()
    if selected_ranges:
        row = selected_ranges[0].topRow()
    else:
        row = self.table_calibration_info.currentRow()
        
    if row >= 0 and row < self.table_calibration_info.rowCount():
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove calibration row {row + 1}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.table_calibration_info.setSortingEnabled(False)
            self.table_calibration_info.blockSignals(True)
            self.table_calibration_info.removeRow(row)
            self.table_calibration_info.blockSignals(False)
            self.table_calibration_info.setSortingEnabled(True)
    else:
        QMessageBox.information(self, "Information", "Please select a calibration row to remove first.")

# Insert new material row below the selected row
def add_material_dialog(self):
    dlg = QDialog(self)
    dlg.setWindowTitle("Add 3D Printing Material")
    
    dlg.setStyleSheet("""
        QDialog {
            background-color: #1e1e24;
            color: #ffffff;
        }
        QLabel {
            color: #e5e7eb;
            font-weight: bold;
        }
        QLineEdit {
            background-color: #2b2b36;
            border: 1px solid #4b5563;
            border-radius: 4px;
            color: #ffffff;
            padding: 4px;
        }
        QDoubleSpinBox {
            background-color: #2b2b36;
            border: 1px solid #4b5563;
            border-radius: 4px;
            color: #ffffff;
            padding: 4px;
        }
        QDateEdit {
            background-color: #2b2b36;
            border: 1px solid #4b5563;
            border-radius: 4px;
            color: #ffffff;
            padding: 4px;
        }
        QPushButton {
            background-color: blue;
            color: white;
            font-weight: bold;
            padding: 6px 12px;
            border-radius: 4px;
        }
    """)
    
    form = QFormLayout(dlg)
    
    txt_name = QLineEdit()
    txt_brand = QLineEdit()
    txt_type = QLineEdit()
    txt_color = QLineEdit()
    txt_printer = QLineEdit()
    
    spin_date = QDateEdit()
    spin_date.setCalendarPopup(True)
    spin_date.setDate(QDate.currentDate())
    
    spin_red = QDoubleSpinBox()
    spin_red.setRange(0.0, 10.0)
    spin_red.setValue(1.0)
    spin_red.setDecimals(4)
    
    spin_red_std = QDoubleSpinBox()
    spin_red_std.setRange(0.0, 2.0)
    spin_red_std.setValue(0.02)
    spin_red_std.setDecimals(4)
    
    spin_zeff = QDoubleSpinBox()
    spin_zeff.setRange(0.0, 100.0)
    spin_zeff.setValue(6.0)
    spin_zeff.setDecimals(4)
    
    spin_zeff_std = QDoubleSpinBox()
    spin_zeff_std.setRange(0.0, 10.0)
    spin_zeff_std.setValue(0.1)
    spin_zeff_std.setDecimals(4)
    
    form.addRow("Material Name:", txt_name)
    form.addRow("Brand:", txt_brand)
    form.addRow("Type (e.g. PLA):", txt_type)
    form.addRow("Color:", txt_color)
    form.addRow("3D Printer:", txt_printer)
    form.addRow("Date Added:", spin_date)
    form.addRow("RED:", spin_red)
    form.addRow("RED STD:", spin_red_std)
    form.addRow("Zeff:", spin_zeff)
    form.addRow("Zeff STD:", spin_zeff_std)
    
    # Dialog buttons
    btn_layout = QHBoxLayout()
    btn_ok = QPushButton("Add")
    btn_cancel = QPushButton("Cancel")
    btn_cancel.setStyleSheet("background-color: #374151; color: white; border-radius: 4px; padding: 6px 12px;")
    
    btn_layout.addWidget(btn_ok)
    btn_layout.addWidget(btn_cancel)
    form.addRow(btn_layout)
    
    btn_ok.clicked.connect(dlg.accept)
    btn_cancel.clicked.connect(dlg.reject)
    
    if dlg.exec() == QDialog.Accepted:
        name = txt_name.text().strip()
        brand = txt_brand.text().strip()
        m_type = txt_type.text().strip()
        color = txt_color.text().strip()
        printer = txt_printer.text().strip()
        date_str = spin_date.date().toString("yyyy-MM-dd")
        red = spin_red.value()
        red_std = spin_red_std.value()
        zeff = spin_zeff.value()
        zeff_std = spin_zeff_std.value()
        
        if not name:
            QMessageBox.warning(self, "Warning", "Material Name is required!")
            return
            
        selected_ranges = self.table_3d_db.selectedRanges()
        if selected_ranges:
            current_row = selected_ranges[0].topRow()
        else:
            current_row = self.table_3d_db.currentRow()
            
        self.table_3d_db.setSortingEnabled(False)
        self.table_3d_db.blockSignals(True)
        
        if current_row >= 0:
            row_idx = current_row + 1
        else:
            row_idx = self.table_3d_db.rowCount()
            
        self.table_3d_db.insertRow(row_idx)
        
        self.table_3d_db.setItem(row_idx, 0, QTableWidgetItem(name))
        self.table_3d_db.setItem(row_idx, 1, QTableWidgetItem(brand))
        self.table_3d_db.setItem(row_idx, 2, QTableWidgetItem(m_type))
        self.table_3d_db.setItem(row_idx, 3, QTableWidgetItem(color))
        self.table_3d_db.setItem(row_idx, 4, QTableWidgetItem(printer))
        self.table_3d_db.setItem(row_idx, 5, QTableWidgetItem(date_str))
        
        # Numeric values
        for col_offset, val in enumerate([red, red_std, zeff, zeff_std]):
            item = QTableWidgetItem()
            float_val = float(val)
            item.setData(Qt.EditRole, float_val)
            item.setText(f"{float_val:.4f}")
            self.table_3d_db.setItem(row_idx, 6 + col_offset, item)
            
        self.table_3d_db.blockSignals(False)
        self.table_3d_db.setSortingEnabled(True)
        
        self.table_3d_db.selectRow(row_idx)
        display_selected_filament_details(self)
        
        if hasattr(self, "table_mat_mix"):
            update_mat_mix_comboboxes(self)

# Dynamic row insertion logic for Mix Groups
def populate_mix_row(self, r, has_spinbox=True, group_size_val=1, mix_id_val=None):
    if has_spinbox:
        spin = FocusSpinBox()
        spin.setRange(1, 20)
        spin.setValue(group_size_val)
        
        if mix_id_val is None:
            max_id = -1
            for row_idx in range(self.table_mat_mix.rowCount()):
                other_spin = self.table_mat_mix.cellWidget(row_idx, 0)
                if isinstance(other_spin, QSpinBox):
                    other_id = other_spin.property("mix_id")
                    if other_id is not None and other_id > max_id:
                        max_id = other_id
            mix_id_val = max_id + 1
        spin.setProperty("mix_id", mix_id_val)
        
        spin.setStyleSheet("""
            QSpinBox {
                background-color: #2b2b36;
                border: 1px solid #4b5563;
                border-radius: 4px;
                color: #ffffff;
                padding: 2px;
            }
        """)
        spin.valueChanged.connect(lambda newVal: on_mix_size_changed(self, spin, newVal))
        self.table_mat_mix.setCellWidget(r, 0, spin)
    else:
        item_empty = QTableWidgetItem("")
        item_empty.setFlags(item_empty.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
        self.table_mat_mix.setItem(r, 0, item_empty)
        
    combo = FocusComboBox()
    combo.setStyleSheet("""
        QComboBox {
            background-color: #2b2b36;
            border: 1px solid #4b5563;
            border-radius: 4px;
            color: #ffffff;
            padding: 2px;
        }
    """)
    combo.currentTextChanged.connect(lambda text: on_mix_material_changed(self, combo, text))
    self.table_mat_mix.setCellWidget(r, 1, combo)
    
    item_name = QTableWidgetItem("")
    self.table_mat_mix.setItem(r, 2, item_name)
    
    for c in range(3, 9):
        item = QTableWidgetItem("")
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        self.table_mat_mix.setItem(r, c, item)

# Called when selection in material combobox changes
def on_mix_material_changed(self, combo, text):
    row = -1
    for r in range(self.table_mat_mix.rowCount()):
        if self.table_mat_mix.cellWidget(r, 1) == combo:
            row = r
            break
    if row == -1:
        return
        
    if not text:
        for c in range(3, 9):
            item = self.table_mat_mix.item(row, c)
            if item:
                item.setText("")
        return
        
    mat_row = -1
    for r in range(self.table_3d_db.rowCount()):
        item = self.table_3d_db.item(r, 0)
        if item and item.text() == text:
            mat_row = r
            break
            
    if mat_row != -1:
        red = self.table_3d_db.item(mat_row, 6).text() if self.table_3d_db.item(mat_row, 6) else ""
        zeff = self.table_3d_db.item(mat_row, 8).text() if self.table_3d_db.item(mat_row, 8) else ""
        color = self.table_3d_db.item(mat_row, 3).text() if self.table_3d_db.item(mat_row, 3) else ""
        brand = self.table_3d_db.item(mat_row, 1).text() if self.table_3d_db.item(mat_row, 1) else ""
        m_type = self.table_3d_db.item(mat_row, 2).text() if self.table_3d_db.item(mat_row, 2) else ""
        printer = self.table_3d_db.item(mat_row, 4).text() if self.table_3d_db.item(mat_row, 4) else ""
        
        self.table_mat_mix.item(row, 3).setText(red)
        self.table_mat_mix.item(row, 4).setText(zeff)
        self.table_mat_mix.item(row, 5).setText(color)
        self.table_mat_mix.item(row, 6).setText(brand)
        self.table_mat_mix.item(row, 7).setText(m_type)
        self.table_mat_mix.item(row, 8).setText(printer)
        
    if hasattr(self, "current_viewed_mix_id") and self.current_viewed_mix_id is not None:
        start_row = row
        while start_row > 0:
            if isinstance(self.table_mat_mix.cellWidget(start_row, 0), QSpinBox):
                break
            start_row -= 1
        spin = self.table_mat_mix.cellWidget(start_row, 0)
        if isinstance(spin, QSpinBox) and spin.property("mix_id") == self.current_viewed_mix_id:
            display_selected_mix_details(self)

# Handles changing spinbox mix values
def on_mix_size_changed(self, spin, newVal):
    row = -1
    for r in range(self.table_mat_mix.rowCount()):
        if self.table_mat_mix.cellWidget(r, 0) == spin:
            row = r
            break
    if row == -1:
        return
        
    curr_size = 1
    for r in range(row + 1, self.table_mat_mix.rowCount()):
        if self.table_mat_mix.cellWidget(r, 0) is not None:
            break
        curr_size += 1
        
    if newVal == curr_size:
        return
        
    self.table_mat_mix.setSortingEnabled(False)
    self.table_mat_mix.blockSignals(True)
    
    if newVal > curr_size:
        insert_pos = row + curr_size
        for _ in range(newVal - curr_size):
            self.table_mat_mix.insertRow(insert_pos)
            populate_mix_row(self, insert_pos, has_spinbox=False)
    else:
        for _ in range(curr_size - newVal):
            self.table_mat_mix.removeRow(row + newVal)
            
    self.table_mat_mix.blockSignals(False)
    self.table_mat_mix.setSortingEnabled(True)
    
    update_group_borders_and_properties(self)
    update_mat_mix_comboboxes(self)
    
    if hasattr(self, "current_viewed_mix_id") and spin.property("mix_id") == self.current_viewed_mix_id:
        display_selected_mix_details(self)

# Assigns property triggers to draw top/bottom borders around groups
def update_group_borders_and_properties(self):
    r = 0
    total_rows = self.table_mat_mix.rowCount()
    for i in range(total_rows):
        self.table_mat_mix.setProperty(f"group_start_{i}", False)
        self.table_mat_mix.setProperty(f"group_end_{i}", False)
        
    while r < total_rows:
        spin = self.table_mat_mix.cellWidget(r, 0)
        if isinstance(spin, QSpinBox):
            n = spin.value()
            self.table_mat_mix.setProperty(f"group_start_{r}", True)
            last_row = min(r + n - 1, total_rows - 1)
            self.table_mat_mix.setProperty(f"group_end_{last_row}", True)
            r += n
        else:
            r += 1
    self.table_mat_mix.viewport().update()

# Refreshes the dropdown list when materials in main table change
def update_mat_mix_comboboxes(self):
    if not hasattr(self, "table_mat_mix") or not hasattr(self, "table_3d_db"):
        return
        
    mat_names = []
    for r in range(self.table_3d_db.rowCount()):
        item = self.table_3d_db.item(r, 0)
        if item:
            name = item.text().strip()
            if name and name not in mat_names:
                mat_names.append(name)
    mat_names.sort()
    
    for r in range(self.table_mat_mix.rowCount()):
        combo = self.table_mat_mix.cellWidget(r, 1)
        if isinstance(combo, QComboBox):
            saved_sel = combo.property("saved_selection")
            current_sel = saved_sel if saved_sel else combo.currentText()
            combo.setProperty("saved_selection", None)
            
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("")
            combo.addItems(mat_names)
            
            if current_sel in mat_names:
                combo.setCurrentText(current_sel)
            else:
                combo.setCurrentIndex(0)
            combo.blockSignals(False)
            
            on_mix_material_changed(self, combo, combo.currentText())

# Insert new mix group below the currently selected mix group
def add_mix_group(self):
    selected_ranges = self.table_mat_mix.selectedRanges()
    if selected_ranges:
        current_row = selected_ranges[0].topRow()
    else:
        current_row = self.table_mat_mix.currentRow()
        
    self.table_mat_mix.setSortingEnabled(False)
    self.table_mat_mix.blockSignals(True)
    
    if current_row >= 0:
        start_row = current_row
        while start_row > 0:
            if isinstance(self.table_mat_mix.cellWidget(start_row, 0), QSpinBox):
                break
            start_row -= 1
        spin = self.table_mat_mix.cellWidget(start_row, 0)
        group_size = spin.value() if isinstance(spin, QSpinBox) else 1
        row_idx = start_row + group_size
    else:
        row_idx = self.table_mat_mix.rowCount()
        
    self.table_mat_mix.insertRow(row_idx)
    populate_mix_row(self, row_idx, has_spinbox=True, group_size_val=1)
    
    self.table_mat_mix.blockSignals(False)
    self.table_mat_mix.setSortingEnabled(True)
    
    update_group_borders_and_properties(self)
    update_mat_mix_comboboxes(self)
    
    self.table_mat_mix.selectRow(row_idx)
    display_selected_mix_details(self)

def remove_mix_group(self):
    selected_ranges = self.table_mat_mix.selectedRanges()
    if selected_ranges:
        row = selected_ranges[0].topRow()
    else:
        row = self.table_mat_mix.currentRow()
        
    if row < 0 or row >= self.table_mat_mix.rowCount():
        QMessageBox.information(self, "Information", "Please select a row in the mixed materials table to remove first.")
        return
        
    start_row = row
    while start_row > 0:
        if isinstance(self.table_mat_mix.cellWidget(start_row, 0), QSpinBox):
            break
        start_row -= 1
        
    spin = self.table_mat_mix.cellWidget(start_row, 0)
    group_size = spin.value() if isinstance(spin, QSpinBox) else 1
    mix_id = spin.property("mix_id") if isinstance(spin, QSpinBox) else None
    
    reply = QMessageBox.question(
        self, "Confirm Removal",
        f"Are you sure you want to remove the entire mix group starting at line {start_row + 1} ({group_size} rows)?",
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        self.table_mat_mix.setSortingEnabled(False)
        self.table_mat_mix.blockSignals(True)
        for _ in range(group_size):
            self.table_mat_mix.removeRow(start_row)
        self.table_mat_mix.blockSignals(False)
        self.table_mat_mix.setSortingEnabled(True)
        
        if mix_id is not None:
            self.mix_calibration_cache.pop(mix_id, None)
            self.mix_notes_cache.pop(mix_id, None)
            self.mix_m_value_cache.pop(mix_id, None)
            if self.current_viewed_mix_id == mix_id:
                self.current_viewed_mix_id = None
                self.lbl_mix_cal_title.setText("Mix Calibration Data")
                self.lbl_mix_notes_title.setText("Mix Notes / Specifications")
                self.table_mix_calibration_info.clearContents()
                self.table_mix_calibration_info.setRowCount(0)
                self.table_mix_z_red.clearContents()
                self.table_mix_z_red.setRowCount(0)
                self.txt_mix_notes.clear()
                
        update_group_borders_and_properties(self)

# Save MatMix CSV
def save_mix_database(self):
    db_path = get_mix_db_path()
    try:
        with open(db_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Mix ID", "Mix Size", "Material Name", "Name", "RED", "Zeff",
                "Color", "Brand", "Type", "Printer"
            ])
            
            total_rows = self.table_mat_mix.rowCount()
            r = 0
            while r < total_rows:
                spin = self.table_mat_mix.cellWidget(r, 0)
                if isinstance(spin, QSpinBox):
                    n = spin.value()
                    mix_id = spin.property("mix_id")
                    for i in range(n):
                        row_idx = r + i
                        if row_idx >= total_rows:
                            break
                        combo = self.table_mat_mix.cellWidget(row_idx, 1)
                        mat_name = combo.currentText() if isinstance(combo, QComboBox) else ""
                        
                        name_item = self.table_mat_mix.item(row_idx, 2)
                        name = name_item.text() if name_item else ""
                        
                        red = self.table_mat_mix.item(row_idx, 3).text() if self.table_mat_mix.item(row_idx, 3) else ""
                        zeff = self.table_mat_mix.item(row_idx, 4).text() if self.table_mat_mix.item(row_idx, 4) else ""
                        color = self.table_mat_mix.item(row_idx, 5).text() if self.table_mat_mix.item(row_idx, 5) else ""
                        brand = self.table_mat_mix.item(row_idx, 6).text() if self.table_mat_mix.item(row_idx, 6) else ""
                        m_type = self.table_mat_mix.item(row_idx, 7).text() if self.table_mat_mix.item(row_idx, 7) else ""
                        printer = self.table_mat_mix.item(row_idx, 8).text() if self.table_mat_mix.item(row_idx, 8) else ""
                        
                        writer.writerow([
                            mix_id, n, mat_name, name, red, zeff, color, brand, m_type, printer
                        ])
                    r += n
                else:
                    r += 1
    except Exception as e:
        print(f"Error saving mixed materials database: {e}")

# Load MatMix CSV
def load_mix_database(self):
    db_path = get_mix_db_path()
    if not os.path.exists(db_path):
        return
        
    self.table_mat_mix.setSortingEnabled(False)
    self.table_mat_mix.blockSignals(True)
    self.table_mat_mix.clearContents()
    self.table_mat_mix.setRowCount(0)
    
    try:
        with open(db_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            
            mix_groups = {}
            for row in reader:
                if not row or len(row) < 10:
                    continue
                mix_id = int(row[0])
                if mix_id not in mix_groups:
                    mix_groups[mix_id] = []
                mix_groups[mix_id].append(row)
                
            for mix_id in sorted(mix_groups.keys()):
                group_rows = mix_groups[mix_id]
                n = len(group_rows)
                
                for i, row_data in enumerate(group_rows):
                    row_idx = self.table_mat_mix.rowCount()
                    self.table_mat_mix.insertRow(row_idx)
                    
                    populate_mix_row(self, row_idx, has_spinbox=(i == 0), group_size_val=n, mix_id_val=mix_id)
                    
                    combo = self.table_mat_mix.cellWidget(row_idx, 1)
                    if isinstance(combo, QComboBox):
                        combo.setProperty("saved_selection", row_data[2])
                        
                    name_item = self.table_mat_mix.item(row_idx, 2)
                    if name_item:
                        name_item.setText(row_data[3])
    except Exception as e:
        print(f"Error loading mixed materials database: {e}")
        
    self.table_mat_mix.blockSignals(False)
    self.table_mat_mix.setSortingEnabled(True)
    
    update_group_borders_and_properties(self)
    update_mat_mix_comboboxes(self)

# Save Mix Action Wrapper
def save_mix_database_action(self):
    save_current_active_mix_cache(self)
    
    errors = []
    for mix_id, rows in self.mix_calibration_cache.items():
        start_row = -1
        total_rows = self.table_mat_mix.rowCount()
        for r in range(total_rows):
            spin = self.table_mat_mix.cellWidget(r, 0)
            if isinstance(spin, QSpinBox) and spin.property("mix_id") == mix_id:
                start_row = r
                group_size = spin.value()
                break
        if start_row == -1:
            continue
            
        mat_names = get_materials_in_mix(self, start_row, group_size)
        n_mats = len(mat_names)
        
        for row_idx, row_data in enumerate(rows):
            ratios_str = row_data[0]
            try:
                ratios = [float(r.strip()) for r in ratios_str.split(',') if r.strip()]
            except ValueError:
                ratios = []
            total_p = sum(ratios)
            
            if abs(total_p - 100.0) > 0.001:
                mix_name = f"Mix ID {mix_id}"
                name_item = self.table_mat_mix.item(start_row, 2)
                if name_item and name_item.text().strip():
                    mix_name = f"Mix '{name_item.text().strip()}' (ID {mix_id})"
                errors.append(f"- {mix_name}, Row {row_idx + 1}: Sum of percentages is {total_p:.4f}% (must be 100.0%)")
                
    if errors:
        error_msg = "Validation failed! The following rows do not sum to 100.0%:\n\n" + "\n".join(errors)
        QMessageBox.warning(self, "Invalid Percentages", error_msg)
        return
        
    save_mix_database(self)
    save_mix_calibration_database(self)
    QMessageBox.information(self, "Success", "Mixed material database and calibration data saved successfully!")

# Details and Dynamic Mix Calibration logic
def get_materials_in_mix(self, start_row, group_size):
    mat_names = []
    for i in range(group_size):
        r = start_row + i
        if r >= self.table_mat_mix.rowCount():
            break
        combo = self.table_mat_mix.cellWidget(r, 1)
        if isinstance(combo, QComboBox):
            text = combo.currentText().strip()
            if text:
                mat_names.append(text)
    return mat_names

def display_selected_mix_details(self):
    selected_ranges = self.table_mat_mix.selectedRanges()
    if selected_ranges:
        row = selected_ranges[0].topRow()
    else:
        row = self.table_mat_mix.currentRow()
        
    if row < 0 or row >= self.table_mat_mix.rowCount():
        return
        
    start_row = row
    while start_row > 0:
        if isinstance(self.table_mat_mix.cellWidget(start_row, 0), QSpinBox):
            break
        start_row -= 1
        
    spin = self.table_mat_mix.cellWidget(start_row, 0)
    if not isinstance(spin, QSpinBox):
        return
        
    group_size = spin.value()
    mix_id = spin.property("mix_id")
    if mix_id is None:
        return
        
    save_current_active_mix_cache(self)
    
    mat_names = get_materials_in_mix(self, start_row, group_size)
    n_mats = len(mat_names)
    
    self.current_viewed_mix_id = mix_id
    self.lbl_mix_cal_title.setText(f"Mix Calibration Data (Mix ID: {mix_id})")
    self.lbl_mix_z_red_title.setText(f"Zeff & RED Predictions (Mix ID: {mix_id})")
    self.lbl_mix_notes_title.setText(f"Notes & Specifications (Mix ID: {mix_id})")
    
    # Load and display Mix RED combinations
    refresh_mix_red_ratios_list(self)
    if self.list_mix_red_ratios.count() > 0:
        self.list_mix_red_ratios.setCurrentRow(0)
    else:
        self.table_mix_red_cal.blockSignals(True)
        self.table_mix_red_cal.clearContents()
        self.table_mix_red_cal.setRowCount(0)
        self.table_mix_red_cal.blockSignals(False)
    
    # Load Zeff m-value for this mix (defaults to 3.4 if not cached)
    m_val = self.mix_m_value_cache.get(mix_id, 3.4)
    self.spin_m_value.blockSignals(True)
    self.spin_m_value.setValue(m_val)
    self.spin_m_value.blockSignals(False)
    
    # Configure columns in mix calibration table dynamically
    self.table_mix_calibration_info.blockSignals(True)
    self.table_mix_calibration_info.setSortingEnabled(False)
    self.table_mix_calibration_info.clearContents()
    self.table_mix_calibration_info.setRowCount(0)
    
    percentage_headers = [f"% {name}" for name in mat_names]
    standard_headers = [
        "kV - Low", "kV - High", "HU-Low", "HU-Low STD", "HU-High", "HU-High STD",
        "RED", "RED_STD", "Zeff", "Zeff STD", "Infill Type", "Infill Density (%)",
        "Layer Height (mm)", "Line Width (mm)", "Print. Temp (C)", "Bed Temp (C)",
        "Flow Multiplier", "Flow (%)", "Print Speed (mm/s)"
    ]
    
    headers = percentage_headers + standard_headers
    self.table_mix_calibration_info.setColumnCount(len(headers))
    self.table_mix_calibration_info.setHorizontalHeaderLabels(headers)
    
    for c in range(self.table_mix_calibration_info.columnCount()):
        if c == n_mats + 10:
            self.table_mix_calibration_info.setItemDelegateForColumn(c, None)
        else:
            self.table_mix_calibration_info.setItemDelegateForColumn(c, self.float_delegate)
            
    # Configure columns in mix Z & RED table dynamically
    self.table_mix_z_red.blockSignals(True)
    self.table_mix_z_red.setSortingEnabled(False)
    self.table_mix_z_red.clearContents()
    self.table_mix_z_red.setRowCount(0)
    
    z_red_headers = percentage_headers + [
        "Zeff", "STD", "Pred. Zeff", "Diff. Zeff", "RED", "STD", "Pred. RED", "Diff. RED"
    ]
    self.table_mix_z_red.setColumnCount(len(z_red_headers))
    self.table_mix_z_red.setHorizontalHeaderLabels(z_red_headers)
    
    for c in range(self.table_mix_z_red.columnCount()):
        self.table_mix_z_red.setItemDelegateForColumn(c, self.float_delegate)
        
    cal_rows = self.mix_calibration_cache.get(mix_id, [])
    for row_data in cal_rows:
        if len(row_data) < 20:
            continue
            
        row_idx = self.table_mix_calibration_info.rowCount()
        self.table_mix_calibration_info.insertRow(row_idx)
        self.table_mix_z_red.insertRow(row_idx)
        
        ratios_str = row_data[0]
        ratios_list = [r.strip() for r in ratios_str.split(',') if r.strip()]
        for idx in range(n_mats):
            val_str = ratios_list[idx] if idx < len(ratios_list) else f"{100.0/n_mats:.4f}"
            item = QTableWidgetItem()
            try:
                float_val = float(val_str)
                item.setData(Qt.EditRole, float_val)
                item.setText(f"{float_val:.4f}")
            except ValueError:
                item.setData(Qt.EditRole, 0.0)
                item.setText("0.0000")
            self.table_mix_calibration_info.setItem(row_idx, idx, item)
            
            item_z = QTableWidgetItem()
            item_z.setData(Qt.EditRole, item.data(Qt.EditRole))
            item_z.setText(item.text())
            self.table_mix_z_red.setItem(row_idx, idx, item_z)
            
        for std_idx, val_str in enumerate(row_data[1:]):
            c = n_mats + std_idx
            if std_idx == 10:
                item = QTableWidgetItem(val_str)
            else:
                item = QTableWidgetItem()
                try:
                    float_val = float(val_str)
                    item.setData(Qt.EditRole, float_val)
                    item.setText(f"{float_val:.4f}")
                except ValueError:
                    item.setData(Qt.EditRole, 0.0)
                    item.setText("0.0000")
            self.table_mix_calibration_info.setItem(row_idx, c, item)
            
        # Zeff (col n_mats)
        item_zeff = QTableWidgetItem()
        try:
            val_zeff = float(row_data[9])
            item_zeff.setData(Qt.EditRole, val_zeff)
            item_zeff.setText(f"{val_zeff:.4f}")
        except ValueError:
            item_zeff.setData(Qt.EditRole, 0.0)
            item_zeff.setText("0.0000")
        self.table_mix_z_red.setItem(row_idx, n_mats, item_zeff)
        
        # Zeff STD
        item_zeff_std = QTableWidgetItem()
        try:
            val_zstd = float(row_data[10])
            item_zeff_std.setData(Qt.EditRole, val_zstd)
            item_zeff_std.setText(f"{val_zstd:.4f}")
        except ValueError:
            item_zeff_std.setData(Qt.EditRole, 0.0)
            item_zeff_std.setText("0.0000")
        self.table_mix_z_red.setItem(row_idx, n_mats + 1, item_zeff_std)
        
        # RED
        item_red = QTableWidgetItem()
        try:
            val_red = float(row_data[7])
            item_red.setData(Qt.EditRole, val_red)
            item_red.setText(f"{val_red:.4f}")
        except ValueError:
            item_red.setData(Qt.EditRole, 0.0)
            item_red.setText("0.0000")
        self.table_mix_z_red.setItem(row_idx, n_mats + 4, item_red)
        
        # RED STD
        item_red_std = QTableWidgetItem()
        try:
            val_rstd = float(row_data[8])
            item_red_std.setData(Qt.EditRole, val_rstd)
            item_red_std.setText(f"{val_rstd:.4f}")
        except ValueError:
            item_red_std.setData(Qt.EditRole, 0.0)
            item_red_std.setText("0.0000")
        self.table_mix_z_red.setItem(row_idx, n_mats + 5, item_red_std)
        
        update_row_predictions(self, row_idx, n_mats)
        
    self.table_mix_calibration_info.blockSignals(False)
    self.table_mix_calibration_info.setSortingEnabled(True)
    
    self.table_mix_z_red.blockSignals(False)
    self.table_mix_z_red.setSortingEnabled(True)
    
    self.txt_mix_notes.setPlainText(self.mix_notes_cache.get(mix_id, ""))
    
    if hasattr(self, "combo_graph_x") and hasattr(self, "combo_graph_y"):
        # Repopulate graph variable dropdowns dynamically for X and Y axes
        self.combo_graph_x.blockSignals(True)
        self.combo_graph_y.blockSignals(True)
        
        old_x = self.combo_graph_x.currentText()
        old_y = self.combo_graph_y.currentText()
        
        self.combo_graph_x.clear()
        self.combo_graph_y.clear()
        
        # 1. Ratios (% of each material)
        for idx, name in enumerate(mat_names):
            self.combo_graph_x.addItem(f"% {name}", ("ratio", idx))
            self.combo_graph_y.addItem(f"% {name}", ("ratio", idx))
            
        # 2. Properties
        props = [
            ("Zeff", ("property", "Zeff")),
            ("Pred. Zeff", ("property", "Pred. Zeff")),
            ("Diff. Zeff", ("property", "Diff. Zeff")),
            ("RED", ("property", "RED")),
            ("Pred. RED", ("property", "Pred. RED")),
            ("Diff. RED", ("property", "Diff. RED"))
        ]
        for label, val in props:
            self.combo_graph_x.addItem(label, val)
            self.combo_graph_y.addItem(label, val)
            
        # Restore selections
        idx_x = self.combo_graph_x.findText(old_x)
        if idx_x >= 0:
            self.combo_graph_x.setCurrentIndex(idx_x)
        else:
            self.combo_graph_x.setCurrentIndex(0)
            
        idx_y = self.combo_graph_y.findText(old_y)
        if idx_y >= 0:
            self.combo_graph_y.setCurrentIndex(idx_y)
        else:
            zeff_idx = self.combo_graph_y.findText("Zeff")
            if zeff_idx >= 0:
                self.combo_graph_y.setCurrentIndex(zeff_idx)
            else:
                self.combo_graph_y.setCurrentIndex(min(1, self.combo_graph_y.count() - 1))
                
        self.combo_graph_x.blockSignals(False)
        self.combo_graph_y.blockSignals(False)
        
        update_mix_graph(self)

# Dynamic Plot Canvas Refresher
def update_mix_graph(self):
    if not hasattr(self, "graph_canvas") or not hasattr(self, "combo_graph_x") or not hasattr(self, "combo_graph_y"):
        return
        
    self.graph_figure.clear()
    ax = self.graph_figure.add_subplot(111)
    
    # Retrieve background color setting dynamically
    background_color = getattr(self, "selected_background", "Transparent")
    if background_color.lower() == 'transparent':
        text_color = 'white'
        bg = '#1e1e24'
        spine_color = '#4b5563'
        grid_color = '#2b2b36'
    elif background_color.lower() == 'white':
        text_color = 'black'
        bg = 'white'
        spine_color = '#cccccc'
        grid_color = '#e5e7eb'
    else:
        text_color = 'black'
        bg = background_color
        spine_color = '#cccccc'
        grid_color = '#e5e7eb'
        
    # Set background color for the plot area and figure
    ax.set_facecolor(bg)
    self.graph_figure.patch.set_facecolor(bg)
    self.graph_canvas.setStyleSheet(f"background-color: {bg};")
    
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is None:
        self.graph_canvas.draw()
        return
        
    # Get active mix group size
    start_row = -1
    total_rows = self.table_mat_mix.rowCount()
    for r in range(total_rows):
        spin = self.table_mat_mix.cellWidget(r, 0)
        if isinstance(spin, QSpinBox) and spin.property("mix_id") == mix_id:
            start_row = r
            group_size = spin.value()
            break
            
    if start_row == -1:
        self.graph_canvas.draw()
        return
        
    mat_names = get_materials_in_mix(self, start_row, group_size)
    n_mats = len(mat_names)
    
    num_rows = self.table_mix_z_red.rowCount()
    if num_rows == 0:
        self.graph_canvas.draw()
        return
        
    sel_idx_x = self.combo_graph_x.currentIndex()
    sel_idx_y = self.combo_graph_y.currentIndex()
    if sel_idx_x < 0 or sel_idx_y < 0:
        self.graph_canvas.draw()
        return
        
    user_data_x = self.combo_graph_x.itemData(sel_idx_x)
    user_data_y = self.combo_graph_y.itemData(sel_idx_y)
    if not user_data_x or not user_data_y:
        self.graph_canvas.draw()
        return
        
    x_data = []
    y_data = []
    x_err = []
    y_err = []
    
    x_label = ""
    y_label = ""
    
    # Extract data series
    for r in range(num_rows):
        ratios = []
        for c in range(n_mats):
            item = self.table_mix_z_red.item(r, c)
            try:
                val = float(item.data(Qt.EditRole)) if item else 0.0
            except (ValueError, TypeError):
                val = 0.0
            ratios.append(val)
            
        item_z = self.table_mix_z_red.item(r, n_mats)
        val_z = float(item_z.data(Qt.EditRole)) if item_z else 0.0
        
        item_zstd = self.table_mix_z_red.item(r, n_mats + 1)
        val_zstd = float(item_zstd.data(Qt.EditRole)) if item_zstd else 0.0
        
        item_pz = self.table_mix_z_red.item(r, n_mats + 2)
        val_pz = float(item_pz.data(Qt.EditRole)) if item_pz else 0.0
        
        item_dz = self.table_mix_z_red.item(r, n_mats + 3)
        val_dz = float(item_dz.data(Qt.EditRole)) if item_dz else 0.0
        
        item_red = self.table_mix_z_red.item(r, n_mats + 4)
        val_red = float(item_red.data(Qt.EditRole)) if item_red else 0.0
        
        item_red_std = self.table_mix_z_red.item(r, n_mats + 5)
        val_red_std = float(item_red_std.data(Qt.EditRole)) if item_red_std else 0.0
        
        item_pr = self.table_mix_z_red.item(r, n_mats + 6)
        val_pr = float(item_pr.data(Qt.EditRole)) if item_pr else 0.0
        
        item_dr = self.table_mix_z_red.item(r, n_mats + 7)
        val_dr = float(item_dr.data(Qt.EditRole)) if item_dr else 0.0
        
        # Extract X Axis Value
        if user_data_x[0] == "ratio":
            mat_idx = user_data_x[1]
            x_val = ratios[mat_idx]
            x_err_val = 0.0
            x_label = f"% {mat_names[mat_idx]}"
        else:
            prop_name = user_data_x[1]
            x_label = prop_name
            if prop_name == "Zeff":
                x_val = val_z
                x_err_val = val_zstd
            elif prop_name == "Pred. Zeff":
                x_val = val_pz
                x_err_val = 0.0
            elif prop_name == "Diff. Zeff":
                x_val = val_dz
                x_err_val = 0.0
            elif prop_name == "RED":
                x_val = val_red
                x_err_val = val_red_std
            elif prop_name == "Pred. RED":
                x_val = val_pr
                x_err_val = 0.0
            elif prop_name == "Diff. RED":
                x_val = val_dr
                x_err_val = 0.0
            else:
                x_val = 0.0
                x_err_val = 0.0
                
        # Extract Y Axis Value
        if user_data_y[0] == "ratio":
            mat_idx = user_data_y[1]
            y_val = ratios[mat_idx]
            y_err_val = 0.0
            y_label = f"% {mat_names[mat_idx]}"
        else:
            prop_name = user_data_y[1]
            y_label = prop_name
            if prop_name == "Zeff":
                y_val = val_z
                y_err_val = val_zstd
            elif prop_name == "Pred. Zeff":
                y_val = val_pz
                y_err_val = 0.0
            elif prop_name == "Diff. Zeff":
                y_val = val_dz
                y_err_val = 0.0
            elif prop_name == "RED":
                y_val = val_red
                y_err_val = val_red_std
            elif prop_name == "Pred. RED":
                y_val = val_pr
                y_err_val = 0.0
            elif prop_name == "Diff. RED":
                y_val = val_dr
                y_err_val = 0.0
            else:
                y_val = 0.0
                y_err_val = 0.0
                
        x_data.append(x_val)
        y_data.append(y_val)
        x_err.append(x_err_val)
        y_err.append(y_err_val)
        
    if not x_data:
        self.graph_canvas.draw()
        return
        
    # Read layout details from Figures menu bar states
    color_map = {
        "blue": "#3b82f6",
        "red": "#ef4444",
        "green": "#10b981",
        "orange": "#f59e0b",
        "purple": "#8b5cf6",
        "cyan": "#06b6d4",
        "yellow": "#eab308",
        "magenta": "#ec4899",
        "white": "#ffffff",
        "black": "#000000"
    }
    sel_color = color_map.get(getattr(self, "selected_line_color", "red").lower(), "#ef4444")
    
    font_family = "sans-serif"
    font_size = getattr(self, "selected_font_size", 10)
    
    marker_map = {
        "circle": "o",
        "square": "s",
        "triangle": "^",
        "star": "*",
        "none": ""
    }
    marker_sym = marker_map.get(getattr(self, "selected_marker_type", "circle").lower(), "o")
    marker_sz = getattr(self, "selected_point_size", 6)
    
    style_map = {
        "solid": "-",
        "dashed": "--",
        "dotted": ":",
        "dash-dot": "-.",
        "none": ""
    }
    line_style = style_map.get(getattr(self, "selected_line_style", "solid").lower(), "-")
    line_width = getattr(self, "selected_line_width", 2.0)
        
    sorted_pairs = sorted(zip(x_data, y_data, x_err, y_err))
    x_sorted = [p[0] for p in sorted_pairs]
    y_sorted = [p[1] for p in sorted_pairs]
    x_err_sorted = [p[2] for p in sorted_pairs]
    y_err_sorted = [p[3] for p in sorted_pairs]
    
    font_settings = {
        'family': font_family,
        'size': font_size
    }
    
    has_x_err = any(e > 0 for e in x_err_sorted)
    has_y_err = any(e > 0 for e in y_err_sorted)
    
    xerr_arg = x_err_sorted if has_x_err else None
    yerr_arg = y_err_sorted if has_y_err else None
    
    ax.errorbar(
        x_sorted, y_sorted, xerr=xerr_arg, yerr=yerr_arg,
        color=sel_color, marker=marker_sym, markersize=marker_sz,
        linestyle=line_style, linewidth=line_width, ecolor="#9ca3af", elinewidth=1, capsize=3
    )
    
    ax.set_title(f"{y_label} vs {x_label}", fontdict=font_settings, color=text_color, pad=10)
    ax.set_xlabel(x_label, fontdict=font_settings, color=text_color)
    ax.set_ylabel(y_label, fontdict=font_settings, color=text_color)
    
    ax.tick_params(axis='both', colors=text_color, labelsize=font_size)
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontfamily(font_family)
        
    for spine in ax.spines.values():
        spine.set_color(spine_color)
        
    ax.grid(True, color=grid_color, linestyle='--', linewidth=0.5)
    
    self.graph_figure.tight_layout()
    self.graph_canvas.draw()

def save_current_active_mix_cache(self):
    if hasattr(self, "current_viewed_mix_id") and self.current_viewed_mix_id is not None:
        mix_id = self.current_viewed_mix_id
        
        # Save active Mix RED table to cache
        if hasattr(self, "list_mix_red_ratios"):
            ratio_idx = self.list_mix_red_ratios.currentRow()
            if ratio_idx >= 0:
                save_mix_red_table_to_cache(self, mix_id, ratio_idx)
                
        if hasattr(self, "spin_m_value"):
            self.mix_m_value_cache[mix_id] = self.spin_m_value.value()
            
        start_row = -1
        total_rows = self.table_mat_mix.rowCount()
        for r in range(total_rows):
            spin = self.table_mat_mix.cellWidget(r, 0)
            if isinstance(spin, QSpinBox) and spin.property("mix_id") == mix_id:
                start_row = r
                group_size = spin.value()
                break
                
        if start_row == -1:
            return
            
        mat_names = get_materials_in_mix(self, start_row, group_size)
        n_mats = len(mat_names)
        
        rows = []
        for r in range(self.table_mix_calibration_info.rowCount()):
            ratios = []
            for c in range(n_mats):
                item = self.table_mix_calibration_info.item(r, c)
                val = item.data(Qt.EditRole) if item else 0.0
                ratios.append(f"{float(val):.4f}" if val is not None else "0.0000")
            ratios_str = ",".join(ratios)
            
            row_data = [ratios_str]
            for std_idx in range(19):
                c = n_mats + std_idx
                item = self.table_mix_calibration_info.item(r, c)
                if std_idx == 10:
                    val_str = item.text() if item else "Grid"
                else:
                    val = item.data(Qt.EditRole) if item else 0.0
                    val_str = str(val) if val is not None else "0.0"
                row_data.append(val_str)
            rows.append(row_data)
            
        self.mix_calibration_cache[mix_id] = rows
        self.mix_notes_cache[mix_id] = self.txt_mix_notes.toPlainText()

def load_all_mix_calibration_data(self):
    self.mix_calibration_cache = {}
    self.mix_notes_cache = {}
    self.mix_m_value_cache = {}
    self.mix_red_cache = {}
    
    cal_db_path = get_mix_cal_db_path()
    
    if not os.path.exists(cal_db_path):
        try:
            with open(cal_db_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Mix ID", "Ratios", "kV_low", "kV_hig", "HU_low", "HU_low_STD", "HU_hig", "HU_hig_STD",
                    "RED", "RED_STD", "Zeff", "Zeff STD", "Infill Type", "Infill Density", "Layer Height",
                    "Line Width", "Print Temp", "Bed Temp", "Flow Multiplier", "Flow", "Print Speed"
                ])
                writer.writerow([
                    "0", "50.0000,50.0000", "80", "140", "80.0000", "5.0000", "120.0000", "6.0000",
                    "1.0850", "0.0200", "6.2500", "0.1000", "Grid", "100.0000", "0.2000",
                    "0.4000", "230.0000", "80.0000", "1.0000", "100.0000", "45.0000"
                ])
        except Exception as e:
            print(f"Error initializing mix calibration database: {e}")
            
    try:
        with open(cal_db_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if not row or len(row) < 21:
                    continue
                mix_id = int(row[0])
                if mix_id not in self.mix_calibration_cache:
                    self.mix_calibration_cache[mix_id] = []
                self.mix_calibration_cache[mix_id].append(row[1:])
    except Exception as e:
        print(f"Error loading mix calibration database: {e}")
        
    notes_path = get_mix_notes_db_path()
    if os.path.exists(notes_path):
        try:
            with open(notes_path, mode='r', encoding='utf-8') as f:
                data = json.load(f)
                for mix_str_id, mix_data in data.items():
                    mix_id = int(mix_str_id)
                    if isinstance(mix_data, dict):
                        self.mix_notes_cache[mix_id] = mix_data.get("notes", "")
                        self.mix_m_value_cache[mix_id] = mix_data.get("m_value", 3.4)
                    else:
                        self.mix_notes_cache[mix_id] = mix_data
                        self.mix_m_value_cache[mix_id] = 3.4
        except Exception as e:
            print(f"Error loading mix notes database: {e}")
            
    # Load Mix RED cache
    self.mix_red_cache = {}
    mix_red_path = get_mix_red_db_path()
    if os.path.exists(mix_red_path):
        try:
            with open(mix_red_path, mode='r', encoding='utf-8') as f:
                raw_data = json.load(f)
                for mix_str_id, combo_list in raw_data.items():
                    self.mix_red_cache[int(mix_str_id)] = combo_list
        except Exception as e:
            print(f"Error loading Mix RED cache: {e}")

def save_mix_calibration_database(self):
    cal_db_path = get_mix_cal_db_path()
    try:
        with open(cal_db_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Mix ID", "Ratios", "kV_low", "kV_hig", "HU_low", "HU_low_STD", "HU_hig", "HU_hig_STD",
                "RED", "RED_STD", "Zeff", "Zeff STD", "Infill Type", "Infill Density", "Layer Height",
                "Line Width", "Print Temp", "Bed Temp", "Flow Multiplier", "Flow", "Print Speed"
            ])
            for mix_id, rows in self.mix_calibration_cache.items():
                for row in rows:
                    writer.writerow([mix_id] + row)
    except Exception as e:
        print(f"Error saving mix calibration database: {e}")
        
    notes_path = get_mix_notes_db_path()
    try:
        with open(notes_path, mode='w', encoding='utf-8') as f:
            data = {}
            all_mix_ids = set(self.mix_notes_cache.keys()).union(self.mix_m_value_cache.keys())
            for mix_id in all_mix_ids:
                notes = self.mix_notes_cache.get(mix_id, "")
                m_val = self.mix_m_value_cache.get(mix_id, 3.4)
                data[str(mix_id)] = {
                    "notes": notes,
                    "m_value": m_val
                }
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving mix notes database: {e}")
        
    # Save Mix RED cache
    mix_red_path = get_mix_red_db_path()
    try:
        with open(mix_red_path, mode='w', encoding='utf-8') as f:
            serializable_data = {str(k): v for k, v in self.mix_red_cache.items()}
            json.dump(serializable_data, f, indent=4)
    except Exception as e:
        print(f"Error saving Mix RED cache: {e}")

# Insert new mix calibration row below the currently selected row
def add_mix_calibration_row(self):
    if not getattr(self, "current_viewed_mix_id", None) is not None:
        QMessageBox.warning(self, "Warning", "Please select a material mix first.")
        return
        
    mix_id = self.current_viewed_mix_id
    
    start_row = -1
    total_rows = self.table_mat_mix.rowCount()
    for r in range(total_rows):
        spin = self.table_mat_mix.cellWidget(r, 0)
        if isinstance(spin, QSpinBox) and spin.property("mix_id") == mix_id:
            start_row = r
            group_size = spin.value()
            break
            
    if start_row == -1:
        return
        
    mat_names = get_materials_in_mix(self, start_row, group_size)
    n_mats = len(mat_names)
    
    selected_ranges = self.table_mix_calibration_info.selectedRanges()
    if selected_ranges:
        current_row = selected_ranges[0].topRow()
    else:
        current_row = self.table_mix_calibration_info.currentRow()
        
    self.table_mix_calibration_info.setSortingEnabled(False)
    self.table_mix_calibration_info.blockSignals(True)
    self.table_mix_z_red.blockSignals(True)
    
    if current_row >= 0:
        row_idx = current_row + 1
    else:
        row_idx = self.table_mix_calibration_info.rowCount()
        
    self.table_mix_calibration_info.insertRow(row_idx)
    self.table_mix_z_red.insertRow(row_idx)
    
    default_ratio = 100.0 / n_mats if n_mats > 0 else 100.0
    for idx in range(n_mats):
        item = QTableWidgetItem()
        item.setData(Qt.EditRole, default_ratio)
        item.setText(f"{default_ratio:.4f}")
        self.table_mix_calibration_info.setItem(row_idx, idx, item)
        
        item_z = QTableWidgetItem()
        item_z.setData(Qt.EditRole, default_ratio)
        item_z.setText(f"{default_ratio:.4f}")
        self.table_mix_z_red.setItem(row_idx, idx, item_z)
        
    defaults = [
        ("80", "kV_low"),
        ("140", "kV_hig"),
        ("100.0000", "HU_low"),
        ("5.0000", "HU_low_STD"),
        ("150.0000", "HU_hig"),
        ("5.0000", "HU_hig_STD"),
        ("1.0000", "RED"),
        ("0.0200", "RED_STD"),
        ("6.0000", "Zeff"),
        ("0.1000", "Zeff_STD"),
        ("Grid", "Infill Type"),
        ("100.0000", "Infill Density"),
        ("0.2000", "Layer Height"),
        ("0.4000", "Line Width"),
        ("210.0000", "Print Temp"),
        ("60.0000", "Bed Temp"),
        ("1.0000", "Flow Multiplier"),
        ("100.0000", "Flow"),
        ("50.0000", "Print Speed")
    ]
    
    for std_idx, (val_str, name) in enumerate(defaults):
        c = n_mats + std_idx
        if std_idx == 10:
            item = QTableWidgetItem(val_str)
        else:
            item = QTableWidgetItem()
            float_val = float(val_str)
            item.setData(Qt.EditRole, float_val)
            item.setText(f"{float_val:.4f}")
        self.table_mix_calibration_info.setItem(row_idx, c, item)
        
    item_zeff = QTableWidgetItem()
    item_zeff.setData(Qt.EditRole, 6.0)
    item_zeff.setText("6.0000")
    self.table_mix_z_red.setItem(row_idx, n_mats, item_zeff)
    
    item_zstd = QTableWidgetItem()
    item_zstd.setData(Qt.EditRole, 0.1)
    item_zstd.setText("0.1000")
    self.table_mix_z_red.setItem(row_idx, n_mats + 1, item_zstd)
    
    item_red = QTableWidgetItem()
    item_red.setData(Qt.EditRole, 1.0)
    item_red.setText("1.0000")
    self.table_mix_z_red.setItem(row_idx, n_mats + 4, item_red)
    
    item_rstd = QTableWidgetItem()
    item_rstd.setData(Qt.EditRole, 0.02)
    item_rstd.setText("0.0200")
    self.table_mix_z_red.setItem(row_idx, n_mats + 5, item_rstd)
    
    update_row_predictions(self, row_idx, n_mats)
    
    self.table_mix_calibration_info.blockSignals(False)
    self.table_mix_calibration_info.setSortingEnabled(True)
    self.table_mix_calibration_info.selectRow(row_idx)
    
    self.table_mix_z_red.blockSignals(False)
    update_mix_graph(self)

def remove_mix_calibration_row(self):
    selected_ranges = self.table_mix_calibration_info.selectedRanges()
    if selected_ranges:
        row = selected_ranges[0].topRow()
    else:
        row = self.table_mix_calibration_info.currentRow()
        
    if row >= 0 and row < self.table_mix_calibration_info.rowCount():
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove calibration row {row + 1}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.table_mix_calibration_info.setSortingEnabled(False)
            self.table_mix_calibration_info.blockSignals(True)
            self.table_mix_calibration_info.removeRow(row)
            self.table_mix_calibration_info.blockSignals(False)
            self.table_mix_calibration_info.setSortingEnabled(True)
            
            self.table_mix_z_red.blockSignals(True)
            self.table_mix_z_red.removeRow(row)
            self.table_mix_z_red.blockSignals(False)
            update_mix_graph(self)
    else:
        QMessageBox.information(self, "Information", "Please select a calibration row in the mix table to remove first.")

# Mix RED tab helper methods
def get_mix_red_db_path():
    appdata_dir = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser('~/AppData/Local')), 'AMIGOpy')
    os.makedirs(appdata_dir, exist_ok=True)
    return os.path.join(appdata_dir, 'filaments_mix_red_db.json')

def format_ratio_string(mat_names, ratios):
    parts = []
    for name, ratio in zip(mat_names, ratios):
        ratio_str = f"{ratio:g}"
        parts.append(f"{name} - {ratio_str}%")
    return " | ".join(parts)

def add_mix_red_ratio(self):
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is None:
        QMessageBox.warning(self, "Warning", "Please select a material mix first.")
        return
        
    start_row = -1
    total_rows = self.table_mat_mix.rowCount()
    for r in range(total_rows):
        spin = self.table_mat_mix.cellWidget(r, 0)
        if isinstance(spin, QSpinBox) and spin.property("mix_id") == mix_id:
            start_row = r
            group_size = spin.value()
            break
            
    if start_row == -1:
        return
        
    mat_names = get_materials_in_mix(self, start_row, group_size)
    if not mat_names:
        QMessageBox.warning(self, "Warning", "Active mix group contains no materials!")
        return
        
    dlg = QDialog(self)
    dlg.setWindowTitle("Add Percentage Combination")
    dlg.setStyleSheet("""
        QDialog {
            background-color: #1e1e24;
            color: #ffffff;
        }
        QLabel {
            color: #e5e7eb;
            font-weight: bold;
        }
        QDoubleSpinBox {
            background-color: #2b2b36;
            border: 1px solid #4b5563;
            border-radius: 4px;
            color: #ffffff;
            padding: 4px;
        }
        QPushButton {
            background-color: blue;
            color: white;
            font-weight: bold;
            padding: 6px 12px;
            border-radius: 4px;
        }
    """)
    
    form = QFormLayout(dlg)
    spinboxes = []
    for name in mat_names:
        spin = QDoubleSpinBox()
        spin.setRange(0.0, 100.0)
        spin.setDecimals(2)
        spin.setValue(100.0 / len(mat_names))
        form.addRow(f"% {name}:", spin)
        spinboxes.append(spin)
        
    btn_layout = QHBoxLayout()
    btn_ok = QPushButton("Add")
    btn_cancel = QPushButton("Cancel")
    btn_cancel.setStyleSheet("background-color: #374151; color: white; border-radius: 4px; padding: 6px 12px;")
    btn_layout.addWidget(btn_ok)
    btn_layout.addWidget(btn_cancel)
    form.addRow(btn_layout)
    
    btn_ok.clicked.connect(dlg.accept)
    btn_cancel.clicked.connect(dlg.reject)
    
    while dlg.exec() == QDialog.Accepted:
        ratios = [spin.value() for spin in spinboxes]
        total_p = sum(ratios)
        if abs(total_p - 100.0) > 0.001:
            QMessageBox.warning(dlg, "Invalid Sum", f"The sum of percentages must be exactly 100.0% (currently {total_p:.2f}%). Please adjust the values.")
            continue
            
        if mix_id not in self.mix_red_cache:
            self.mix_red_cache[mix_id] = []
            
        self.mix_red_cache[mix_id].append({
            "percentage": ratios,
            "rows": []
        })
        
        refresh_mix_red_ratios_list(self)
        self.list_mix_red_ratios.setCurrentRow(self.list_mix_red_ratios.count() - 1)
        break

def remove_mix_red_ratio(self):
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is None:
        return
        
    idx = self.list_mix_red_ratios.currentRow()
    if idx < 0:
        QMessageBox.information(self, "Information", "Please select a combination to remove first.")
        return
        
    reply = QMessageBox.question(
        self, "Confirm Removal",
        "Are you sure you want to remove the selected percentage combination and all its calibration measurements?",
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    if reply == QMessageBox.Yes:
        mix_red_data = self.mix_red_cache.get(mix_id, [])
        if idx < len(mix_red_data):
            mix_red_data.pop(idx)
            refresh_mix_red_ratios_list(self)
            
            if self.list_mix_red_ratios.count() > 0:
                self.list_mix_red_ratios.setCurrentRow(0)
            else:
                self.table_mix_red_cal.blockSignals(True)
                self.table_mix_red_cal.clearContents()
                self.table_mix_red_cal.setRowCount(0)
                self.table_mix_red_cal.blockSignals(False)

def refresh_mix_red_ratios_list(self):
    self.list_mix_red_ratios.blockSignals(True)
    self.list_mix_red_ratios.clear()
    
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is None:
        self.list_mix_red_ratios.blockSignals(False)
        return
        
    start_row = -1
    total_rows = self.table_mat_mix.rowCount()
    for r in range(total_rows):
        spin = self.table_mat_mix.cellWidget(r, 0)
        if isinstance(spin, QSpinBox) and spin.property("mix_id") == mix_id:
            start_row = r
            group_size = spin.value()
            break
            
    if start_row == -1:
        self.list_mix_red_ratios.blockSignals(False)
        return
        
    mat_names = get_materials_in_mix(self, start_row, group_size)
    
    mix_red_data = self.mix_red_cache.get(mix_id, [])
    for combo in mix_red_data:
        ratios = combo["percentage"]
        item_text = format_ratio_string(mat_names, ratios)
        self.list_mix_red_ratios.addItem(item_text)
        
    self.list_mix_red_ratios.blockSignals(False)

def display_selected_mix_red_ratio_details(self, idx):
    self.table_mix_red_cal.blockSignals(True)
    self.table_mix_red_cal.clearContents()
    self.table_mix_red_cal.setRowCount(0)
    
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is None or idx < 0:
        self.table_mix_red_cal.blockSignals(False)
        return
        
    mix_red_data = self.mix_red_cache.get(mix_id, [])
    if idx >= len(mix_red_data):
        self.table_mix_red_cal.blockSignals(False)
        return
        
    combination = mix_red_data[idx]
    ratios = combination["percentage"]
    rows = combination.get("rows", [])
    
    pred_red = calculate_mix_red_predicted_val(self, ratios)
    
    for row_vals in rows:
        row_idx = self.table_mix_red_cal.rowCount()
        self.table_mix_red_cal.insertRow(row_idx)
        
        # Check if we need to migrate from older 8-column format
        is_migration = (len(row_vals) == 8)
        if is_migration:
            new_row_vals = ["100.0", "100.0", row_vals[2], row_vals[3], row_vals[4], row_vals[5], row_vals[6], row_vals[7], "0.0", row_vals[0], row_vals[1]]
        else:
            new_row_vals = row_vals
            
        for c in range(11):
            if c == 8:
                pred_item = QTableWidgetItem()
                pred_item.setFlags(pred_item.flags() & ~Qt.ItemIsEditable)
                pred_item.setData(Qt.EditRole, pred_red)
                pred_item.setText(f"{pred_red:.4f}")
                self.table_mix_red_cal.setItem(row_idx, 8, pred_item)
            else:
                val_str = new_row_vals[c] if c < len(new_row_vals) else "0.0"
                item = QTableWidgetItem()
                try:
                    float_val = float(val_str)
                    item.setData(Qt.EditRole, float_val)
                    item.setText(f"{float_val:.4f}")
                except ValueError:
                    item.setData(Qt.EditRole, 0.0)
                    item.setText("0.0000")
                self.table_mix_red_cal.setItem(row_idx, c, item)
        
    self.table_mix_red_cal.blockSignals(False)

def calculate_mix_red_predicted_val(self, ratios):
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is None:
        return 0.0
        
    start_row = -1
    total_rows = self.table_mat_mix.rowCount()
    for r in range(total_rows):
        spin = self.table_mat_mix.cellWidget(r, 0)
        if isinstance(spin, QSpinBox) and spin.property("mix_id") == mix_id:
            start_row = r
            group_size = spin.value()
            break
            
    if start_row == -1:
        return 0.0
        
    comp_reds = []
    for i in range(group_size):
        r = start_row + i
        if r >= self.table_mat_mix.rowCount():
            break
            
        combo = self.table_mat_mix.cellWidget(r, 1)
        mat_name = combo.currentText().strip() if isinstance(combo, QComboBox) else ""
        
        ref_red = 0.0
        red_item = self.table_mat_mix.item(r, 3)
        if red_item and red_item.text().strip():
            try:
                ref_red = float(red_item.text().replace(',', '.'))
            except ValueError:
                pass
                
        if ref_red == 0.0 and mat_name:
            for r_db in range(self.table_3d_db.rowCount()):
                item_db = self.table_3d_db.item(r_db, 0)
                if item_db and item_db.text().strip() == mat_name:
                    try:
                        ref_red = float(self.table_3d_db.item(r_db, 6).text().replace(',', '.')) if self.table_3d_db.item(r_db, 6) else 0.0
                    except ValueError:
                        ref_red = 0.0
                    break
        comp_reds.append(ref_red)
        
    pred_red = 0.0
    for idx, ratio in enumerate(ratios):
        if idx < len(comp_reds):
            pred_red += (ratio / 100.0) * comp_reds[idx]
    return pred_red

def save_mix_red_table_to_cache(self, mix_id, ratio_idx):
    if mix_id not in self.mix_red_cache:
        return
        
    mix_red_data = self.mix_red_cache[mix_id]
    if ratio_idx >= len(mix_red_data):
        return
        
    combination = mix_red_data[ratio_idx]
    
    rows_data = []
    for r in range(self.table_mix_red_cal.rowCount()):
        row_vals = []
        for c in range(11):
            item = self.table_mix_red_cal.item(r, c)
            if item is not None:
                val = item.data(Qt.EditRole)
                row_vals.append(str(val) if val is not None else "0.0")
            else:
                row_vals.append("0.0")
        rows_data.append(row_vals)
    combination["rows"] = rows_data

def add_mix_red_cal_row(self):
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is None:
        return
        
    ratio_idx = self.list_mix_red_ratios.currentRow()
    if ratio_idx < 0:
        QMessageBox.warning(self, "Warning", "Please select a percentage combination on the left first.")
        return
        
    mix_red_data = self.mix_red_cache.get(mix_id, [])
    if ratio_idx >= len(mix_red_data):
        return
        
    combination = mix_red_data[ratio_idx]
    ratios = combination["percentage"]
    
    pred_red = calculate_mix_red_predicted_val(self, ratios)
    
    selected_ranges = self.table_mix_red_cal.selectedRanges()
    if selected_ranges:
        current_row = selected_ranges[0].topRow()
    else:
        current_row = self.table_mix_red_cal.currentRow()
        
    self.table_mix_red_cal.setSortingEnabled(False)
    self.table_mix_red_cal.blockSignals(True)
    
    if current_row >= 0:
        row_idx = current_row + 1
    else:
        row_idx = self.table_mix_red_cal.rowCount()
        
    self.table_mix_red_cal.insertRow(row_idx)
    
    defaults = [
        ("100.0000", "Infill %"),
        ("100.0000", "Flow"),
        ("100.0000", "HU_low"),
        ("5.0000", "HU_low_STD"),
        ("150.0000", "HU_hig"),
        ("5.0000", "HU_hig_STD"),
        ("1.0000", "RED"),
        ("0.0200", "RED_STD"),
    ]
    
    for c, (val_str, name) in enumerate(defaults):
        item = QTableWidgetItem()
        float_val = float(val_str)
        item.setData(Qt.EditRole, float_val)
        item.setText(f"{float_val:.4f}")
        self.table_mix_red_cal.setItem(row_idx, c, item)
        
    # Pred. RED in col 8
    pred_item = QTableWidgetItem()
    pred_item.setFlags(pred_item.flags() & ~Qt.ItemIsEditable)
    pred_item.setData(Qt.EditRole, pred_red)
    pred_item.setText(f"{pred_red:.4f}")
    self.table_mix_red_cal.setItem(row_idx, 8, pred_item)
    
    # kV - Low in col 9
    item_kv_low = QTableWidgetItem()
    item_kv_low.setData(Qt.EditRole, 80.0)
    item_kv_low.setText("80.0000")
    self.table_mix_red_cal.setItem(row_idx, 9, item_kv_low)
    
    # kV - High in col 10
    item_kv_high = QTableWidgetItem()
    item_kv_high.setData(Qt.EditRole, 140.0)
    item_kv_high.setText("140.0000")
    self.table_mix_red_cal.setItem(row_idx, 10, item_kv_high)
    
    self.table_mix_red_cal.blockSignals(False)
    self.table_mix_red_cal.setSortingEnabled(True)
    self.table_mix_red_cal.selectRow(row_idx)
    
    save_mix_red_table_to_cache(self, mix_id, ratio_idx)

def remove_mix_red_cal_row(self):
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is None:
        return
        
    ratio_idx = self.list_mix_red_ratios.currentRow()
    if ratio_idx < 0:
        return
        
    selected_ranges = self.table_mix_red_cal.selectedRanges()
    if selected_ranges:
        row = selected_ranges[0].topRow()
    else:
        row = self.table_mix_red_cal.currentRow()
        
    if row >= 0 and row < self.table_mix_red_cal.rowCount():
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove calibration row {row + 1}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.table_mix_red_cal.setSortingEnabled(False)
            self.table_mix_red_cal.blockSignals(True)
            self.table_mix_red_cal.removeRow(row)
            self.table_mix_red_cal.blockSignals(False)
            self.table_mix_red_cal.setSortingEnabled(True)
            
            save_mix_red_table_to_cache(self, mix_id, ratio_idx)
    else:
        QMessageBox.information(self, "Information", "Please select a calibration row in the table to remove first.")

def on_mix_red_cal_cell_changed(self, item):
    row = item.row()
    col = item.column()
    if col == 8:
        return
        
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is None:
        return
        
    ratio_idx = self.list_mix_red_ratios.currentRow()
    if ratio_idx < 0:
        return
        
    mix_red_data = self.mix_red_cache.get(mix_id, [])
    if ratio_idx >= len(mix_red_data):
        return
        
    combination = mix_red_data[ratio_idx]
    ratios = combination["percentage"]
    
    pred_red = calculate_mix_red_predicted_val(self, ratios)
    
    self.table_mix_red_cal.blockSignals(True)
    pred_item = self.table_mix_red_cal.item(row, 8)
    if not pred_item:
        pred_item = QTableWidgetItem()
        pred_item.setFlags(pred_item.flags() & ~Qt.ItemIsEditable)
        self.table_mix_red_cal.setItem(row, 8, pred_item)
    pred_item.setData(Qt.EditRole, pred_red)
    pred_item.setText(f"{pred_red:.4f}")
    self.table_mix_red_cal.blockSignals(False)
    
    save_mix_red_table_to_cache(self, mix_id, ratio_idx)

def edit_mix_red_ratio(self):
    mix_id = getattr(self, "current_viewed_mix_id", None)
    if mix_id is None:
        return
        
    idx = self.list_mix_red_ratios.currentRow()
    if idx < 0:
        QMessageBox.information(self, "Information", "Please select a percentage combination to edit first.")
        return
        
    start_row = -1
    total_rows = self.table_mat_mix.rowCount()
    for r in range(total_rows):
        spin = self.table_mat_mix.cellWidget(r, 0)
        if isinstance(spin, QSpinBox) and spin.property("mix_id") == mix_id:
            start_row = r
            group_size = spin.value()
            break
            
    if start_row == -1:
        return
        
    mat_names = get_materials_in_mix(self, start_row, group_size)
    if not mat_names:
        return
        
    mix_red_data = self.mix_red_cache.get(mix_id, [])
    if idx >= len(mix_red_data):
        return
        
    combination = mix_red_data[idx]
    current_percentages = combination["percentage"]
    
    dlg = QDialog(self)
    dlg.setWindowTitle("Edit Percentage Combination")
    dlg.setStyleSheet("""
        QDialog {
            background-color: #1e1e24;
            color: #ffffff;
        }
        QLabel {
            color: #e5e7eb;
            font-weight: bold;
        }
        QDoubleSpinBox {
            background-color: #2b2b36;
            border: 1px solid #4b5563;
            border-radius: 4px;
            color: #ffffff;
            padding: 4px;
        }
        QPushButton {
            background-color: blue;
            color: white;
            font-weight: bold;
            padding: 6px 12px;
            border-radius: 4px;
        }
    """)
    
    form = QFormLayout(dlg)
    spinboxes = []
    for i, name in enumerate(mat_names):
        spin = QDoubleSpinBox()
        spin.setRange(0.0, 100.0)
        spin.setDecimals(2)
        val = current_percentages[i] if i < len(current_percentages) else (100.0 / len(mat_names))
        spin.setValue(val)
        form.addRow(f"% {name}:", spin)
        spinboxes.append(spin)
        
    btn_layout = QHBoxLayout()
    btn_ok = QPushButton("Save")
    btn_cancel = QPushButton("Cancel")
    btn_cancel.setStyleSheet("background-color: #374151; color: white; border-radius: 4px; padding: 6px 12px;")
    btn_layout.addWidget(btn_ok)
    btn_layout.addWidget(btn_cancel)
    form.addRow(btn_layout)
    
    btn_ok.clicked.connect(dlg.accept)
    btn_cancel.clicked.connect(dlg.reject)
    
    while dlg.exec() == QDialog.Accepted:
        ratios = [spin.value() for spin in spinboxes]
        total_p = sum(ratios)
        if abs(total_p - 100.0) > 0.001:
            QMessageBox.warning(dlg, "Invalid Sum", f"The sum of percentages must be exactly 100.0% (currently {total_p:.2f}%). Please adjust the values.")
            continue
            
        combination["percentage"] = ratios
        
        # Save any current active table changes to cache
        save_mix_red_table_to_cache(self, mix_id, idx)
        
        # Recalculate Pred. RED for all rows in the calibration table
        pred_red = calculate_mix_red_predicted_val(self, ratios)
        
        self.table_mix_red_cal.blockSignals(True)
        for r in range(self.table_mix_red_cal.rowCount()):
            pred_item = self.table_mix_red_cal.item(r, 8)
            if not pred_item:
                pred_item = QTableWidgetItem()
                pred_item.setFlags(pred_item.flags() & ~Qt.ItemIsEditable)
                self.table_mix_red_cal.setItem(r, 8, pred_item)
            pred_item.setData(Qt.EditRole, pred_red)
            pred_item.setText(f"{pred_red:.4f}")
        self.table_mix_red_cal.blockSignals(False)
            
        # Refresh left list display text without changing row selection
        refresh_mix_red_ratios_list(self)
        self.list_mix_red_ratios.setCurrentRow(idx)
        
        # Force redraw details of the edited item
        display_selected_mix_red_ratio_details(self, idx)
        break

def export_3dp_database_action(self):
    # Save active cached changes first
    if hasattr(self, "current_viewed_filament") and self.current_viewed_filament:
        save_current_active_material_cache(self)
    if hasattr(self, "current_viewed_mix_id") and self.current_viewed_mix_id is not None:
        save_current_active_mix_cache(self)
        
    # Save to disk
    if hasattr(self, "table_3d_db"):
        save_3d_database(self)
        save_calibration_database(self)
    if hasattr(self, "table_mat_mix"):
        save_mix_calibration_database(self)
        
    db_dir = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser('~/AppData/Local')), 'AMIGOpy')
    files_to_export = [
        "filaments_db.csv",
        "filaments_calibration_db.csv",
        "filaments_notes_db.json",
        "filaments_mix_db.csv",
        "filaments_mix_calibration_db.csv",
        "filaments_mix_notes_db.json",
        "filaments_mix_red_db.json"
    ]
    
    # Check if any file exists
    existing_files = [f for f in files_to_export if os.path.exists(os.path.join(db_dir, f))]
    if not existing_files:
        QMessageBox.warning(self, "Warning", "No database files found to export!")
        return
        
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Export 3DP Database", "AMIGO_3DP_Database.zip", "Zip Files (*.zip)"
    )
    if not file_path:
        return
        
    try:
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for f in existing_files:
                full_path = os.path.join(db_dir, f)
                zipf.write(full_path, f)
        QMessageBox.information(self, "Success", f"3DP Database exported successfully to:\n{file_path}")
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to export 3DP Database:\n{e}")

def import_3dp_database_action(self):
    reply = QMessageBox.warning(
        self, "Confirm Overwrite",
        "Importing a new 3DP Database will permanently overwrite and replace the current database on this computer.\n\n"
        "Do you want to continue?",
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    if reply != QMessageBox.Yes:
        return
        
    file_path, _ = QFileDialog.getOpenFileName(
        self, "Import 3DP Database", "", "Zip Files (*.zip)"
    )
    if not file_path:
        return
        
    db_dir = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser('~/AppData/Local')), 'AMIGOpy')
    os.makedirs(db_dir, exist_ok=True)
    
    try:
        # First, validate zip content
        with zipfile.ZipFile(file_path, 'r') as zipf:
            namelist = zipf.namelist()
            has_valid_files = any(f.endswith('.csv') or f.endswith('.json') for f in namelist)
            if not has_valid_files:
                QMessageBox.critical(self, "Invalid Database", "The selected zip file does not contain valid database files.")
                return
                
            # Extract and overwrite
            zipf.extractall(db_dir)
            
        # Hot-reload databases in the GUI
        self.current_viewed_filament = None
        self.current_viewed_mix_id = None
        
        load_3d_database(self)
        load_all_calibration_data(self)
        load_mix_database(self)
        load_all_mix_calibration_data(self)
        
        # Select first row in database if available
        if self.table_3d_db.rowCount() > 0:
            self.table_3d_db.selectRow(0)
            display_selected_filament_details(self)
        else:
            self.table_calibration_info.clearContents()
            self.table_calibration_info.setRowCount(0)
            self.txt_notes.clear()
            
        # Select first row in mix database if available
        if self.table_mat_mix.rowCount() > 0:
            self.table_mat_mix.selectRow(0)
            display_selected_mix_details(self)
        else:
            self.table_mix_calibration_info.clearContents()
            self.table_mix_calibration_info.setRowCount(0)
            self.table_mix_z_red.clearContents()
            self.table_mix_z_red.setRowCount(0)
            self.txt_mix_notes.clear()
            
        # Update graphs if initialized
        if hasattr(self, "graph_canvas"):
            update_mix_graph(self)
            
        QMessageBox.information(self, "Success", "3DP Database imported and loaded successfully!")
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to import 3DP Database:\n{e}")
