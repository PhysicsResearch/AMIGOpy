# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 12:01:02 2025

@author: tommaso.siligardi
"""

import pandas as pd
import numpy as np
from PySide6.QtWidgets import QTableWidgetItem, QMessageBox
import csv, math
from copy import deepcopy
from datetime import datetime
from PySide6.QtGui         import QColor, QBrush
from PySide6.QtCore        import Qt
from fcn_load.populate_med_image_list import populate_medical_image_tree
from PySide6.QtWidgets import QInputDialog, QMessageBox, QComboBox, QPushButton, QCheckBox, QWidget, QHBoxLayout, QColorDialog

NONE_MAT = 'None'

# Default colours (material colour = PALETTE[material ID % len])
PALETTE = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
           '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff',
           '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1',
           '#000075', '#a9a9a9']


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def _mat_names(self):
    df = getattr(self, 'Mat_df', None)
    if df is None:
        return []
    try:
        return [str(n) for n in df['Name'].to_numpy().tolist()]
    except Exception:
        return []


def _mat_key(self, name):
    """Return the material ID (Mat_df index) for a material name, or None."""
    if not name or name == NONE_MAT:
        return None
    try:
        return self.Mat_df.index[self.Mat_df['Name'] == name][0]
    except Exception:
        return None


def default_mat_color(self, name):
    key = _mat_key(self, name)
    if key is None:
        return '#a9a9a9'
    try:
        return PALETTE[int(key) % len(PALETTE)]
    except Exception:
        return PALETTE[abs(hash(name)) % len(PALETTE)]


def _to_float(txt):
    try:
        return float(str(txt).strip().replace(',', '.'))
    except Exception:
        return None


def _fmt(v):
    if v is None:
        return ''
    v = float(v)
    return str(int(v)) if v.is_integer() else str(v)


def _ro_item(text):
    it = QTableWidgetItem(str(text))
    it.setTextAlignment(Qt.AlignCenter)
    it.setFlags(it.flags() & ~Qt.ItemIsEditable)
    return it


def _make_mat_combo(self, current, on_change):
    """Material dropdown with 'None' on top (default)."""
    cb = QComboBox()
    cb.addItem(NONE_MAT)
    cb.addItems(_mat_names(self))
    idx = cb.findText(str(current)) if current else 0
    cb.setCurrentIndex(idx if idx >= 0 else 0)
    cb.currentTextChanged.connect(lambda _t: on_change())
    return cb


def _style_color_btn(btn, hex_color):
    btn.setProperty('hex', hex_color)
    btn.setStyleSheet(f"QPushButton {{ background-color: {hex_color}; border: 1px solid #222; "
                      f"margin: 3px 6px; }}")
    btn.setToolTip(f"{hex_color} - click to change the colour")


def _make_color_btn(self, hex_color, auto, on_change):
    btn = QPushButton()
    btn.setProperty('auto', bool(auto))
    _style_color_btn(btn, hex_color)

    def _pick():
        col = QColorDialog.getColor(QColor(btn.property('hex') or '#ff0000'), self, "Overlay colour")
        if col.isValid():
            btn.setProperty('auto', False)
            _style_color_btn(btn, col.name())
            on_change()
    btn.clicked.connect(_pick)
    return btn


def _make_checkbox_cell(checked=True, tooltip="", on_change=None):
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setAlignment(Qt.AlignCenter)
    cb = QCheckBox()
    cb.setChecked(bool(checked))
    if tooltip:
        cb.setToolTip(tooltip)
    if on_change is not None:
        cb.toggled.connect(lambda _c: on_change())
    lay.addWidget(cb)
    return w


def _cell_cb(table, r, c):
    w = table.cellWidget(r, c)
    return w.findChild(QCheckBox) if w is not None else None


def _make_fixed_den_cell(checked=True, on_change=None):
    return _make_checkbox_cell(checked=checked, tooltip="Fixed density: nominal material density", on_change=on_change)


def _fixed_den_cb(table, r, c):
    return _cell_cb(table, r, c)


def _make_show_cell(checked=True, on_change=None):
    return _make_checkbox_cell(checked=checked, tooltip="Show this assignment on the images", on_change=on_change)


def _show_cb(table, r, c):
    return _cell_cb(table, r, c)


def _color_of(table, r, c):
    b = table.cellWidget(r, c)
    if b is None:
        return None, True
    return b.property('hex'), bool(b.property('auto'))


def _setup_table(table, headers, widths):
    from PySide6.QtWidgets import QAbstractItemView, QHeaderView
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setEditTriggers(QAbstractItemView.DoubleClicked |
                          QAbstractItemView.EditKeyPressed |
                          QAbstractItemView.AnyKeyPressed |
                          QAbstractItemView.SelectedClicked)
    hdr = table.horizontalHeader()
    hdr.setStretchLastSection(False)
    for c, w in enumerate(widths):
        hdr.setSectionResizeMode(c, QHeaderView.Interactive)
        table.setColumnWidth(c, w)
    table.verticalHeader().setDefaultSectionSize(24)


def _refresh_overlay(self):
    try:
        from fcn_materialassignment.mat_overlay import update_mat_overlay_all
        update_mat_overlay_all(self)
    except Exception as e:
        print(f"[Material overlay] refresh failed: {e}")


def _toggle_all(self, table, col, sync):
    """Show all if any row is hidden, otherwise hide all."""
    cbs = [_show_cb(table, r, col) for r in range(table.rowCount())]
    cbs = [c for c in cbs if c is not None]
    if not cbs:
        return
    target = not all(c.isChecked() for c in cbs)
    self._mat_tbl_updating = True
    try:
        for c in cbs:
            c.setChecked(target)
    finally:
        self._mat_tbl_updating = False
    sync(self)


# ----------------------------------------------------------------------------
# Materials -> HU ranges table  (Material | ID | From | To | Fixed Density | Color | Show)
# ----------------------------------------------------------------------------
HU_COLS = ['Material', 'ID', 'From', 'To', 'Fixed Density', 'Color', 'Show']
HU_C_MAT, HU_C_ID, HU_C_LO, HU_C_HI, HU_C_FIXED_DEN, HU_C_COL, HU_C_SHOW = range(7)


def setup_mat_hu_table(self):
    t = getattr(self, 'tableMatToHU', None)
    if t is None:
        return None
    _setup_table(t, HU_COLS, [140, 35, 60, 60, 85, 45, 45])
    if not getattr(t, '_amigo_item_conn', False):
        t.itemChanged.connect(lambda _it: sync_mat_HU_from_table(self))
        t._amigo_item_conn = True
    return t


def update_material_list(self):
    """Called when the material database changes."""
    select_mat = getattr(self, 'Select_mat', None)   # legacy widget (may not exist)
    if select_mat is not None and hasattr(select_mat, 'clear'):
        select_mat.clear()
        select_mat.addItem('...Select material...')
        select_mat.addItems(_mat_names(self))


def _insert_hu_row(self, t, name, lo, hi, fixed_density=True, color=None, visible=True):
    r = t.rowCount()
    t.insertRow(r)
    sync = lambda: sync_mat_HU_from_table(self)
    t.setCellWidget(r, HU_C_MAT, _make_mat_combo(self, name, sync))
    key = _mat_key(self, name)
    t.setItem(r, HU_C_ID, _ro_item('' if key is None else key))
    for c, v in ((HU_C_LO, lo), (HU_C_HI, hi)):
        it = QTableWidgetItem(_fmt(v))
        it.setTextAlignment(Qt.AlignCenter)
        t.setItem(r, c, it)
    t.setCellWidget(r, HU_C_FIXED_DEN, _make_fixed_den_cell(fixed_density, sync))
    t.setCellWidget(r, HU_C_COL, _make_color_btn(self, color or default_mat_color(self, name),
                                                 color is None, sync))
    t.setCellWidget(r, HU_C_SHOW, _make_show_cell(visible, sync))
    return r


def add_mat_HU_row(self):
    """'Add Material' button: append an editable row (material = None)."""
    t = setup_mat_hu_table(self)
    if t is None:
        return
    rows = getattr(self, 'mat_HU_list', [])
    lo = rows[-1]['max'] if rows and rows[-1]['max'] is not None else -1000.0
    self._mat_tbl_updating = True
    try:
        r = _insert_hu_row(self, t, NONE_MAT, lo, lo + 100.0, fixed_density=True)
    finally:
        self._mat_tbl_updating = False
    sync_mat_HU_from_table(self)
    t.scrollToBottom()
    t.selectRow(r)


def sync_mat_HU_from_table(self):
    """Read the HU table back into self.mat_HU_list / self.mat_HU."""
    if getattr(self, '_mat_tbl_updating', False):
        return
    t = getattr(self, 'tableMatToHU', None)
    if t is None:
        return
    rows = []
    self._mat_tbl_updating = True
    try:
        for r in range(t.rowCount()):
            cb = t.cellWidget(r, HU_C_MAT)
            name = cb.currentText() if cb is not None else NONE_MAT
            key = _mat_key(self, name)
            lo = _to_float(t.item(r, HU_C_LO).text()) if t.item(r, HU_C_LO) else None
            hi = _to_float(t.item(r, HU_C_HI).text()) if t.item(r, HU_C_HI) else None
            id_item = t.item(r, HU_C_ID)
            if id_item is None:
                t.setItem(r, HU_C_ID, _ro_item('' if key is None else key))
            else:
                id_item.setText('' if key is None else str(key))
            valid = lo is not None and hi is not None and lo < hi
            for c in (HU_C_LO, HU_C_HI):
                it = t.item(r, c)
                if it is not None:
                    it.setData(Qt.ForegroundRole,
                               None if valid else QBrush(QColor('#f87171')))
            f_cb = _fixed_den_cb(t, r, HU_C_FIXED_DEN)
            is_fixed = f_cb.isChecked() if f_cb is not None else True
            # colour follows the material until the user picks one
            color, auto = _color_of(t, r, HU_C_COL)
            btn = t.cellWidget(r, HU_C_COL)
            if btn is not None and auto:
                color = default_mat_color(self, name)
                if btn.property('hex') != color:
                    _style_color_btn(btn, color)
            show = _show_cb(t, r, HU_C_SHOW)
            rows.append({'name': name, 'key': key, 'min': lo, 'max': hi,
                         'fixed_density': is_fixed,
                         'color': color or default_mat_color(self, name),
                         'color_auto': auto,
                         'visible': show.isChecked() if show is not None else True})
    finally:
        self._mat_tbl_updating = False
    self.mat_HU_list = rows
    # Legacy dict view (one entry per material; later rows win)
    self.mat_HU = {d['name']: {'key': d['key'], 'min': d['min'], 'max': d['max'],
                               'fixed_density': d.get('fixed_density', True)}
                   for d in rows
                   if d['key'] is not None and d['min'] is not None
                   and d['max'] is not None and d['min'] < d['max']}
    _refresh_overlay(self)


def update_mat2HU_table(self):
    """Rebuild the HU table from self.mat_HU_list (or legacy self.mat_HU)."""
    t = setup_mat_hu_table(self)
    if t is None:
        return
    rows = getattr(self, 'mat_HU_list', None)
    if rows is None:
        rows = [{'name': n, 'key': d.get('key'), 'min': d.get('min'), 'max': d.get('max'),
                 'fixed_density': d.get('fixed_density', True)}
                for n, d in getattr(self, 'mat_HU', {}).items()]
    self._mat_tbl_updating = True
    try:
        t.setRowCount(0)
        for d in rows:
            color = None if d.get('color_auto', True) else d.get('color')
            _insert_hu_row(self, t, d['name'], d['min'], d['max'],
                           fixed_density=d.get('fixed_density', True),
                           color=color, visible=d.get('visible', True))
    finally:
        self._mat_tbl_updating = False
    sync_mat_HU_from_table(self)


def toggle_mat_HU_visibility(self):
    t = getattr(self, 'tableMatToHU', None)
    if t is not None:
        _toggle_all(self, t, HU_C_SHOW, sync_mat_HU_from_table)


def check_mat2HU(self):
    """Material DB changed: refresh dropdowns/IDs, drop materials that no longer exist."""
    if getattr(self, 'tableMatToHU', None) is None:
        return
    rows = getattr(self, 'mat_HU_list', None)
    if rows is None and not getattr(self, 'mat_HU', None):
        setup_mat_hu_table(self)
        return
    if rows is None:
        rows = [{'name': n, 'key': d.get('key'), 'min': d.get('min'), 'max': d.get('max'),
                 'fixed_density': d.get('fixed_density', True)}
                for n, d in self.mat_HU.items()]
    names = set(_mat_names(self))
    missing = sorted({d['name'] for d in rows if d['name'] != NONE_MAT and d['name'] not in names})
    for d in rows:
        if d['name'] in missing:
            d['name'] = NONE_MAT
    self.mat_HU_list = rows
    update_mat2HU_table(self)
    if missing:
        QMessageBox.information(self, "Warning",
                                "These materials are no longer in the material table and were "
                                "reset to None in the HU ranges:\n" + ", ".join(missing))


def del_mat2HU(self):
    """Remove the selected rows (or the last row) from the HU table."""
    t = getattr(self, 'tableMatToHU', None)
    if t is None or t.rowCount() == 0:
        return
    rows = sorted({i.row() for i in t.selectionModel().selectedRows()}, reverse=True)
    if not rows:
        rows = [t.rowCount() - 1]
    self._mat_tbl_updating = True
    try:
        for r in rows:
            t.removeRow(r)
    finally:
        self._mat_tbl_updating = False
    sync_mat_HU_from_table(self)


def get_mat_HU_ranges(self):
    """Valid (name, key, min, max, fixed_density) rows in table order; invalid rows are reported."""
    sync_mat_HU_from_table(self)
    good, bad = [], []
    for i, d in enumerate(getattr(self, 'mat_HU_list', []), start=1):
        if d['name'] == NONE_MAT:
            continue
        if d['key'] is None or d['min'] is None or d['max'] is None or d['min'] >= d['max']:
            bad.append(i)
            continue
        good.append((d['name'], d['key'], d['min'], d['max'], d.get('fixed_density', True)))
    return good, bad


# ----------------------------------------------------------------------------
# Materials -> structures table  (Structure | Material | ID | Fixed Density | Color | Show)
# ----------------------------------------------------------------------------
STRUCT_COLS = ['Structure', 'Material', 'ID', 'Fixed Density', 'Color', 'Show']
ST_C_NAME, ST_C_MAT, ST_C_ID, ST_C_FIXED_DEN, ST_C_COL, ST_C_SHOW = range(6)


def setup_mat_struct_table(self):
    t = getattr(self, 'mat_to_struct_tab', None)
    if t is None:
        return None
    _setup_table(t, STRUCT_COLS, [130, 140, 35, 85, 45, 45])
    return t


def _current_structure_names(self):
    try:
        s = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]
        return list(s.get('structures_names', []))
    except Exception:
        return None


def _insert_struct_row(self, t, s_name, material, fixed_density=True, color=None, visible=True):
    r = t.rowCount()
    t.insertRow(r)
    sync = lambda: sync_mat_struct_from_table(self)
    it = _ro_item(s_name)
    it.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
    t.setItem(r, ST_C_NAME, it)
    t.setCellWidget(r, ST_C_MAT, _make_mat_combo(self, material, sync))
    t.setItem(r, ST_C_ID, _ro_item(''))
    t.setCellWidget(r, ST_C_FIXED_DEN, _make_fixed_den_cell(fixed_density, sync))
    t.setCellWidget(r, ST_C_COL, _make_color_btn(self, color or default_mat_color(self, material),
                                                 color is None, sync))
    t.setCellWidget(r, ST_C_SHOW, _make_show_cell(visible, sync))
    return r


def _fill_struct_table(self, t, names):
    prev = getattr(self, 'mat_struct', {}) or {}
    view = getattr(self, 'mat_struct_view', {}) or {}
    self._mat_tbl_updating = True
    try:
        t.setRowCount(0)
        for s_name in names:
            p_val = prev.get(s_name, {})
            p_mat = p_val.get('material', NONE_MAT) if isinstance(p_val, dict) else NONE_MAT
            v = view.get(s_name, {})
            f_den = v.get('fixed_density', p_val.get('fixed_density', True) if isinstance(p_val, dict) else True)
            color = None if v.get('auto', True) else v.get('color')
            _insert_struct_row(self, t, s_name, p_mat, fixed_density=f_den,
                               color=color, visible=v.get('visible', True))
    finally:
        self._mat_tbl_updating = False
    sync_mat_struct_from_table(self)


def update_mat_struct_list(self):
    """Fill the structure table with all structures of the selected series.
    Previously chosen materials/colours are kept (matched by structure name)."""
    t = setup_mat_struct_table(self)
    if t is None:
        return
    names = _current_structure_names(self)
    if names is None:
        return
    _fill_struct_table(self, t, names)


def sync_mat_struct_from_table(self):
    if getattr(self, '_mat_tbl_updating', False):
        return
    t = getattr(self, 'mat_to_struct_tab', None)
    if t is None:
        return
    mat_struct = {}
    view = dict(getattr(self, 'mat_struct_view', {}) or {})
    for r in range(t.rowCount()):
        s_item = t.item(r, ST_C_NAME)
        cb = t.cellWidget(r, ST_C_MAT)
        if s_item is None or cb is None:
            continue
        s_name = s_item.text()
        name = cb.currentText()
        key = _mat_key(self, name)
        id_item = t.item(r, ST_C_ID)
        if id_item is not None:
            id_item.setText('' if key is None else str(key))
        f_cb = _fixed_den_cb(t, r, ST_C_FIXED_DEN)
        f_den = f_cb.isChecked() if f_cb is not None else True
        color, auto = _color_of(t, r, ST_C_COL)
        btn = t.cellWidget(r, ST_C_COL)
        if btn is not None and auto:
            color = default_mat_color(self, name)
            if btn.property('hex') != color:
                _style_color_btn(btn, color)
        show = _show_cb(t, r, ST_C_SHOW)
        view[s_name] = {'color': color, 'auto': auto,
                        'visible': show.isChecked() if show is not None else True,
                        'fixed_density': f_den}
        if key is not None:
            mat_struct[s_name] = {'material': name, 'key': key, 'fixed_density': f_den}
    self.mat_struct = mat_struct
    self.mat_struct_view = view
    _refresh_overlay(self)


def update_struct2mat_table(self):
    """Rebuild the structure table (keeps choices from self.mat_struct)."""
    t = setup_mat_struct_table(self)
    if t is None:
        return
    names = _current_structure_names(self)
    if names is None:
        names = list(getattr(self, 'mat_struct', {}).keys())   # no series selected
    _fill_struct_table(self, t, names)


def toggle_mat_struct_visibility(self):
    t = getattr(self, 'mat_to_struct_tab', None)
    if t is not None:
        _toggle_all(self, t, ST_C_SHOW, sync_mat_struct_from_table)


def del_stuct2mat(self):
    """Reset the material of the selected structures (or all) to None."""
    t = getattr(self, 'mat_to_struct_tab', None)
    if t is None or t.rowCount() == 0:
        return
    rows = sorted({i.row() for i in t.selectionModel().selectedRows()})
    if not rows:
        rows = range(t.rowCount())
    self._mat_tbl_updating = True
    try:
        for r in rows:
            cb = t.cellWidget(r, ST_C_MAT)
            if cb is not None:
                cb.setCurrentIndex(0)
    finally:
        self._mat_tbl_updating = False
    sync_mat_struct_from_table(self)


def check_struct2mat(self):
    """Material DB changed: refresh dropdowns, reset removed materials to None."""
    if getattr(self, 'mat_to_struct_tab', None) is None:
        return
    mat_struct = getattr(self, 'mat_struct', {}) or {}
    names = set(_mat_names(self))
    missing = sorted({d['material'] for d in mat_struct.values() if d['material'] not in names})
    self.mat_struct = {k: v for k, v in mat_struct.items() if v['material'] in names}
    if self.mat_to_struct_tab.rowCount() or self.mat_struct:
        update_struct2mat_table(self)
    else:
        setup_mat_struct_table(self)
    if missing:
        QMessageBox.information(self, "Warning",
                                "These materials are no longer in the material table and were "
                                "reset to None for the structures:\n" + ", ".join(missing))


def refresh_mat_assignment_if_visible(self):
    """Refresh the structure list when the Material Assignment tab is shown."""
    tab = getattr(self, 'tab_mat_assignment', None)
    if tab is not None and tab.isVisible():
        update_mat_struct_list(self)
    _refresh_overlay(self)


def generate_mat_map(self):

    # Retrive CT_info
    if not getattr(self, 'patientID', None):
        QMessageBox.critical(self, 'Error', 'No Patient selected')
        return
    target_dict = self.medical_image.get(self.patientID, {}).get(self.studyID, {})
    ct_list = target_dict.get('CT', [])
    if not ct_list:
        QMessageBox.critical(self, 'Error', 'No CT found')
        return
    cur_m = getattr(self, 'modality', None)
    cur_idx = getattr(self, 'series_index', 0)
    ct_idx = cur_idx if (cur_m == 'CT' and 0 <= cur_idx < len(ct_list)) else 0
    self.modality = 'CT'
    self.series_index = ct_idx
    target = ct_list[ct_idx]
    ct_matrix = target['3DMatrix']

    mat_used={}
    mat_map=np.full(ct_matrix.shape,-1,dtype=np.int16)
    
    #Assigning materials using HU ranges (table order; later rows override)
    hu_ranges, bad_rows = get_mat_HU_ranges(self)
    if bad_rows:
        reply = QMessageBox.question(
            self, 'Invalid HU ranges',
            f"Rows {', '.join(map(str, bad_rows))} of the HU table have an invalid range "
            "(From must be lower than To) and will be ignored.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
    for item in hu_ranges:
        mat, key, min_val, max_val = item[:4]
        ID = np.int16(key)
        mat_map[(ct_matrix>=min_val) & (ct_matrix<max_val)]=ID
        mat_used[ID]=mat
    
    #Assign mat to structures
    if getattr(self,'mat_struct',None):
        struct_names=[k for k in self.mat_struct.keys()]
        mats=[d['material'] for d in self.mat_struct.values()]
        IDs=[d['key'] for d in self.mat_struct.values()]
        try:
            struct_dict = target.get('structures', {})
        except:
            QMessageBox.critical(self, 'Error','Structures missing. Are you selecting the correct CT set?')
            return

        
        struct_present = [s.get('Name') for s in struct_dict.values()]

        # Find missing structure names
        missing_structs = [name for name in struct_names if name not in struct_present]
        
        if missing_structs:
            missing_list = ', '.join(missing_structs)
            QMessageBox.warning(
                self,
                'Missing Structures',
                f"The following structures are not found in CT structures and will be ignored:\n{missing_list}"
            )
        final_struct_masks = []
        final_mats = []
        final_IDs = []
            
        for name, mat, ID in zip(struct_names, mats, IDs):
            struct = next((s for s in struct_dict.values() if s.get('Name') == name), None)
            if struct:
                final_struct_masks.append(struct['Mask3D'])
                final_mats.append(mat)
                final_IDs.append(ID)
            # else: name is missing; already warned above
        
        # Use the filtered lists
        for mask, mat, ID in zip(final_struct_masks, final_mats, final_IDs):
            mat_map[mask != 0] = ID
            if ID not in mat_used:
                mat_used[ID] = mat
            #assigned unspecified voxels to water
    if len(mat_map[mat_map==-1])!=0:
        #Retriving index for water
        water_ID = np.int16(self.Mat_df.index[self.Mat_df['Name'] == 'Water'][0])
        mat_map[mat_map==-1]=water_ID
        mat_used[water_ID]='Water'
        QMessageBox.information(self,'Warning' ,'Unassigned voxels will be assigned to Water')
    
    # Build metadata containing table and structure definitions
    sync_mat_HU_from_table(self)
    hu_table_meta = []
    for d in getattr(self, 'mat_HU_list', []):
        hu_table_meta.append({
            'name': d.get('name'),
            'key': d.get('key'),
            'min': d.get('min'),
            'max': d.get('max'),
            'fixed_density': bool(d.get('fixed_density', True)),
            'color': d.get('color'),
            'color_auto': bool(d.get('color_auto', True)),
            'visible': bool(d.get('visible', True))
        })

    struct_meta = {}
    struct_list_meta = []
    t_struct = getattr(self, 'mat_to_struct_tab', None)
    if t_struct is not None:
        sync_mat_struct_from_table(self)
        for r in range(t_struct.rowCount()):
            s_item = t_struct.item(r, ST_C_NAME)
            cb = t_struct.cellWidget(r, ST_C_MAT)
            if s_item is None or cb is None:
                continue
            s_name = s_item.text()
            mat_name = cb.currentText()
            key = _mat_key(self, mat_name)
            f_cb = _fixed_den_cb(t_struct, r, ST_C_FIXED_DEN)
            f_den = f_cb.isChecked() if f_cb is not None else True
            col, c_auto = _color_of(t_struct, r, ST_C_COL)
            s_cb = _show_cb(t_struct, r, ST_C_SHOW)
            s_vis = s_cb.isChecked() if s_cb is not None else True
            info = {
                'structure': s_name,
                'material': mat_name,
                'key': key,
                'fixed_density': f_den,
                'color': col,
                'color_auto': c_auto,
                'visible': s_vis
            }
            struct_list_meta.append(info)
            struct_meta[s_name] = info
    else:
        for s_name, info in getattr(self, 'mat_struct', {}).items():
            v = (getattr(self, 'mat_struct_view', {}) or {}).get(s_name, {})
            entry_s = {
                'structure': s_name,
                'material': info.get('material', NONE_MAT),
                'key': info.get('key'),
                'fixed_density': bool(info.get('fixed_density', True)),
                'color': v.get('color'),
                'color_auto': bool(v.get('auto', True)),
                'visible': bool(v.get('visible', True))
            }
            struct_list_meta.append(entry_s)
            struct_meta[s_name] = entry_s

    map_metadata = {
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'series_index': self.series_index,
        'HU_table': hu_table_meta,
        'structures': struct_meta,
        'structures_list': struct_list_meta,
        'Material_used': dict(mat_used)
    }

    # Store the material map
    existing = target.get('mat_maps', {})
    if not existing:
        target['mat_maps'] = {}

    entry = {
        '3DMatrix': mat_map,
        'Material_used': mat_used,
        'HU_table': hu_table_meta,
        'structures': struct_meta,
        'metadata': map_metadata
    }
    map_key = f'mat_map_{len(existing)}'
    target['mat_maps'][map_key] = entry
    populate_medical_image_tree(self)


def load_mat_map_into_tables(self, map_entry_or_name=None):
    """Retrieve the HU ranges and structure material assignments stored in a material map
    and restore them into tableMatToHU and mat_to_struct_tab."""
    if not getattr(self, 'patientID', None):
        QMessageBox.critical(self, 'Error', 'No Patient selected')
        return False
    target_dict = self.medical_image.get(self.patientID, {}).get(self.studyID, {})
    ct_list = target_dict.get('CT', [])
    if not ct_list:
        QMessageBox.critical(self, 'Error', 'No CT found')
        return False
    cur_m = getattr(self, 'modality', None)
    cur_idx = getattr(self, 'series_index', 0)
    ct_idx = cur_idx if (cur_m == 'CT' and 0 <= cur_idx < len(ct_list)) else 0
    target = ct_list[ct_idx]

    mat_maps = target.get('mat_maps', {})
    if not mat_maps:
        QMessageBox.information(self, 'Retrieve Map', 'No material maps found for this CT.')
        return False

    entry = None
    map_name = "Selected map"
    if isinstance(map_entry_or_name, dict):
        entry = map_entry_or_name
    elif isinstance(map_entry_or_name, str) and map_entry_or_name in mat_maps:
        map_name = map_entry_or_name
        entry = mat_maps[map_name]
    else:
        keys = list(mat_maps.keys())
        default_idx = len(keys) - 1
        item, ok = QInputDialog.getItem(self, "Retrieve Material Map",
                                       "Select material map to restore tables from:",
                                       keys, default_idx, False)
        if not ok or not item:
            return False
        map_name = item
        entry = mat_maps[map_name]

    if entry is None:
        return False

    meta = entry.get('metadata', {})
    hu_table = entry.get('HU_table') or meta.get('HU_table')
    structs = entry.get('structures') or meta.get('structures')

    if hu_table is None and structs is None:
        QMessageBox.warning(self, "Retrieve Map",
                            f"Material map '{map_name}' has no saved table metadata.")
        return False

    # Restore HU table
    if hu_table:
        self.mat_HU_list = deepcopy(hu_table)
        update_mat2HU_table(self)

    # Restore structures table
    if structs:
        struct_dict = {}
        view_dict = getattr(self, 'mat_struct_view', {}) or {}
        if isinstance(structs, list):
            for item in structs:
                s_name = item.get('structure')
                if s_name:
                    struct_dict[s_name] = item
        elif isinstance(structs, dict):
            struct_dict = structs

        for s_name, info in struct_dict.items():
            mat = info.get('material', NONE_MAT)
            key = info.get('key', _mat_key(self, mat))
            f_den = info.get('fixed_density', True)
            col = info.get('color')
            c_auto = info.get('color_auto', col is None)
            vis = info.get('visible', True)
            view_dict[s_name] = {'color': col, 'auto': c_auto, 'visible': vis, 'fixed_density': f_den}
            if key is not None:
                self.mat_struct[s_name] = {'material': mat, 'key': key, 'fixed_density': f_den}
            elif s_name in getattr(self, 'mat_struct', {}):
                self.mat_struct.pop(s_name)

        self.mat_struct_view = view_dict
        update_struct2mat_table(self)

    _refresh_overlay(self)
    return True
    

    

def delete_mat_map(self):
    if not getattr(self, 'patientID', None):
        QMessageBox.critical(self, 'Error', 'No Patient selected')
        return
    target_dict = self.medical_image.get(self.patientID, {}).get(self.studyID, {})
    ct_list = target_dict.get('CT', [])
    if not ct_list:
        QMessageBox.critical(self, 'Error', 'No CT found')
        return
    cur_m = getattr(self, 'modality', None)
    cur_idx = getattr(self, 'series_index', 0)
    ct_idx = cur_idx if (cur_m == 'CT' and 0 <= cur_idx < len(ct_list)) else 0
    self.modality = 'CT'
    self.series_index = ct_idx
    target = ct_list[ct_idx]
    mat_maps=target.get('mat_maps',{})
    if not mat_maps:
        QMessageBox.critical(self, 'Error', 'No material maps found for this CT')
        return
    items = list(mat_maps.keys())
    items.append('All')
    item, ok = QInputDialog.getItem(self, "Delete Material Map", "Select the material map to delete:", items, 0, False)
    if ok and item:
    # Remove from dict or list
        if item=='All':
            target['mat_maps'].clear()
        else:
            target['mat_maps'].pop(item)
        
        populate_medical_image_tree(self)
        
        QMessageBox.information(self, "Deleted", f"Material map '{item}' has been deleted.")



