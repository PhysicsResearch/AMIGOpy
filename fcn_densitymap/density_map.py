import os
import numpy as np
import vtk
from copy import deepcopy
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, 
    QWidget, QLineEdit, QLabel, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog, QMessageBox)

from PySide6.QtCore import Qt  # Import Qt to use Qt.ItemIsEditable flag
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
from fcn_load.populate_med_image_list import populate_medical_image_tree


def display_message_box(msg):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle('Error')
    msg_box.setText(msg)
    msg_box.exec()


def _extract_ct_cal_from_table(self):
    """Extract numeric calibration curve from the GUI table if >= 2 rows."""
    table = getattr(self, 'ct_cal_table', None)
    if table is None:
        return None
    row_count = table.rowCount()
    col_count = table.columnCount()
    if row_count < 2 or col_count < 2:
        return None
    headers = []
    for col in range(col_count):
        item = table.item(0, col)
        headers.append(item.text().strip().upper() if item and item.text() else f"COL_{col}")
    data = []
    for row in range(1, row_count):
        row_data = []
        for col in range(col_count):
            item = table.item(row, col)
            row_data.append(item.text().strip() if item and item.text() else "")
        if any(row_data):
            data.append(row_data)
    if len(data) < 2:
        return None
    try:
        df = pd.DataFrame(data, columns=headers)
        df = df.apply(pd.to_numeric, errors='coerce').dropna()
        if len(df) >= 2:
            df = df.sort_values(by=df.columns[0]).reset_index(drop=True)
            return df
    except Exception:
        pass
    return None


def _get_ct_cal_curve(self, map_type='DENSITY'):
    """Get a calibration curve DataFrame (HU, value) for converting CT to density/RED/SPR."""
    map_u = str(map_type).upper()
    # 1. From active ct_cal_table
    df = _extract_ct_cal_from_table(self)
    if df is not None and len(df) >= 2:
        return df

    # 2. From loaded curves in memory
    curves = getattr(self, 'ct_cal_curves', {}) or {}
    for name, cdf in curves.items():
        if isinstance(cdf, pd.DataFrame) and len(cdf) >= 2:
            if len(cdf.columns) >= 2 and cdf.columns[1].upper() == map_u:
                return cdf
    for name, cdf in curves.items():
        if isinstance(cdf, pd.DataFrame) and len(cdf) >= 2:
            return cdf

    # 3. From sample calibration files on disk
    base_dir = os.path.dirname(__file__)
    cal_dir = os.path.join(base_dir, '..', 'fcn_ctcal', 'ct_cal_curves')
    sample_file = 'MAASTRO_CT_2_2023_red.csv' if map_u == 'RED' else 'MAASTRO_CT_2_2023_MASS.csv'
    p = os.path.abspath(os.path.join(cal_dir, sample_file))
    if os.path.exists(p):
        try:
            with open(p, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            delim = ';' if (len(lines) > 1 and ';' in lines[1]) else ','
            cdf = pd.read_csv(p, skiprows=[0], delimiter=delim)
            cdf = cdf.apply(pd.to_numeric, errors='coerce').dropna()
            if len(cdf) >= 2:
                cdf = cdf.sort_values(by=cdf.columns[0]).reset_index(drop=True)
                return cdf
        except Exception:
            pass

    # 4. Built-in physical fallback (HU -> Density / RED / SPR)
    if map_u == 'RED':
        return pd.DataFrame({'HU': [-1024.0, 0.0, 1000.0, 3000.0],
                             'RED': [0.001, 1.0, 1.65, 2.5]})
    elif map_u == 'SPR':
        return pd.DataFrame({'HU': [-1024.0, 0.0, 1000.0, 3000.0],
                             'SPR': [0.001, 1.0, 1.60, 2.4]})
    else:
        return pd.DataFrame({'HU': [-1024.0, -950.0, -120.0, 0.0, 100.0, 1000.0, 3000.0],
                             'DENSITY': [0.0012, 0.05, 0.93, 1.0, 1.07, 1.85, 2.8]})


def compute_density(ct_matrix, ct_cal_curve):
    """Convert CT matrix (HU) to density using calibration curve segments."""
    HU = ct_cal_curve.iloc[:, 0].to_numpy(dtype=np.float32)
    density = ct_cal_curve.iloc[:, 1].to_numpy(dtype=np.float32)

    sort_idx = np.argsort(HU)
    HU = HU[sort_idx]
    density = density[sort_idx]

    slopes = np.diff(density) / np.diff(HU)
    intercepts = density[:-1] - slopes * HU[:-1]
    density_map = np.zeros_like(ct_matrix, dtype=np.float32)

    # Below calibration range: clamp to first value
    density_map[ct_matrix < HU[0]] = density[0]

    for i in range(len(slopes)):
        mask = (ct_matrix >= HU[i]) & (ct_matrix < HU[i+1])
        density_map[mask] = ct_matrix[mask] * slopes[i] + intercepts[i]

    # Above calibration range: extrapolate using last slope and intercept
    mask_last = ct_matrix >= HU[-1]
    if len(slopes) > 0:
        density_map[mask_last] = ct_matrix[mask_last] * slopes[-1] + intercepts[-1]
    else:
        density_map[mask_last] = density[-1]

    # Apply lower and upper limits
    min_limit = max(0.0, float(density[0]))
    max_limit = max(float(density[-1]), 2.9)
    density_map[density_map < min_limit] = min_limit
    density_map[density_map > max_limit] = max_limit

    return density_map


def create_density_map(self, use_mat_map=False):
    # Retrieve CT_info
    if getattr(self, 'patientID', None):
        target_dict = self.medical_image[self.patientID][self.studyID]
    else:
        display_message_box('No patient selected')
        return
    try:
        ct_matrix = target_dict['CT'][self.series_index]['3DMatrix']
    except Exception:
        display_message_box('No CT found')
        return

    # If using material map
    if use_mat_map:
        mat_maps = target_dict['CT'][self.series_index].get('mat_maps', {})
        if not mat_maps:
            QMessageBox.critical(self, 'Error', 'No material maps found for this CT')
            return

        item, ok = QInputDialog.getItem(self, "Choose Material Map", "Select the material map:", list(mat_maps.keys()), 0, False)
        if not ok or not item:
            return  # Cancelled safely

        map_type, ok_2 = QInputDialog.getItem(self, "Choose Map type", "Choose the map type:", ['Density', 'RED', 'SPR'], 0, False)
        if not ok_2 or not map_type:
            return  # Cancelled safely

        mat_map_entry = target_dict['CT'][self.series_index]['mat_maps'][item]
        mat_map_matrix = mat_map_entry['3DMatrix']
        mat_used = mat_map_entry.get('Material_used', {})

        # Compute baseline continuous density from CT
        ct_cal = _get_ct_cal_curve(self, map_type)
        ct_density = compute_density(ct_matrix, ct_cal)
        density_matrix = ct_density.copy()

        # Build lookup of fixed density per material/structure from metadata or active tables
        hu_table = mat_map_entry.get('HU_table') or mat_map_entry.get('metadata', {}).get('HU_table', [])
        struct_table = mat_map_entry.get('structures') or mat_map_entry.get('metadata', {}).get('structures', {})

        mat_fixed_dict = {}
        for row in hu_table:
            k = row.get('key')
            n = row.get('name')
            f = row.get('fixed_density', True)
            if k is not None:
                mat_fixed_dict[k] = f
            if n is not None:
                mat_fixed_dict[n] = f

        s_items = struct_table.items() if isinstance(struct_table, dict) else [(s.get('structure'), s) for s in struct_table]
        for s_name, s_info in s_items:
            k = s_info.get('key')
            n = s_info.get('material')
            f = s_info.get('fixed_density', True)
            if k is not None:
                mat_fixed_dict[k] = f
            if n is not None:
                mat_fixed_dict[n] = f

        # If metadata wasn't stored (e.g. legacy map), fallback to active session tables
        if not mat_fixed_dict:
            for row in getattr(self, 'mat_HU_list', []) or []:
                k = row.get('key')
                n = row.get('name')
                f = row.get('fixed_density', True)
                if k is not None:
                    mat_fixed_dict[k] = f
                if n is not None:
                    mat_fixed_dict[n] = f
            for s_info in (getattr(self, 'mat_struct', {}) or {}).values():
                k = s_info.get('key')
                n = s_info.get('material')
                f = s_info.get('fixed_density', True)
                if k is not None:
                    mat_fixed_dict[k] = f
                if n is not None:
                    mat_fixed_dict[n] = f

        # Apply density per material: fixed from database, or otherwise from CT
        for mat_key, material in mat_used.items():
            mat_info = self.Mat_df[self.Mat_df['Name'] == material]
            if not len(mat_info):
                QMessageBox.warning(self, 'Warning', f'Material {material} not found in the material database. Skipping')
                continue

            is_fixed = mat_fixed_dict.get(mat_key, mat_fixed_dict.get(material, True))
            if is_fixed:
                if map_type == 'Density':
                    value = mat_info['Den'].values[0]
                else:
                    value = mat_info[map_type].values[0]
                density_matrix[mat_map_matrix == mat_key] = value
            else:
                # Use density from CT for this material's voxels
                density_matrix[mat_map_matrix == mat_key] = ct_density[mat_map_matrix == mat_key]

        # Apply structure-level overrides if individual structures were given specific fixed_density
        struct_dict = target_dict['CT'][self.series_index].get('structures', {})
        for s_name, s_info in s_items:
            s_mat = s_info.get('material')
            s_fixed = s_info.get('fixed_density', True)
            s_struct = next((s for s in struct_dict.values() if s.get('Name') == s_name), None)
            if s_struct and 'Mask3D' in s_struct:
                mask = (s_struct['Mask3D'] != 0)
                if s_fixed:
                    s_mat_info = self.Mat_df[self.Mat_df['Name'] == s_mat]
                    if len(s_mat_info):
                        val = s_mat_info['Den'].values[0] if map_type == 'Density' else s_mat_info[map_type].values[0]
                        density_matrix[mask] = val
                else:
                    density_matrix[mask] = ct_density[mask]

    else:
        # Retrieve CT_cal from table
        ct_cal = _extract_ct_cal_from_table(self)
        if ct_cal is None or len(ct_cal) < 2:
            display_message_box('The CT calibration curve needs to have at least two rows!')
            return

        density_matrix = compute_density(ct_matrix, ct_cal)
        map_type = ct_cal.columns[1]

        # Check if override density is checked
        if getattr(self, 'override_no_tissue', None) and self.override_no_tissue.isChecked():
            mat_maps = target_dict['CT'][self.series_index].get('mat_maps', {})
            if not mat_maps:
                QMessageBox.critical(self, 'Error', 'No material maps found for this CT')
                return

            item, ok = QInputDialog.getItem(self, "Choose Material Map", "Select the material map:", list(mat_maps.keys()), 0, False)
            if not ok or not item:
                return  # Cancelled safely

            mat_map_matrix = target_dict['CT'][self.series_index]['mat_maps'][item]['3DMatrix']
            mat_used = target_dict['CT'][self.series_index]['mat_maps'][item]['Material_used']
            for mat_key in mat_used.keys():
                material = mat_used[mat_key]
                mat_info = self.Mat_df[self.Mat_df['Name'] == material]
                if not len(mat_info):
                    QMessageBox.warning(self, 'Warning', f'Material {material} not found in the material database. Skipping')
                    continue
                if float(mat_info['Tissue'].values[0]) == 0:
                    if map_type.upper() == 'DENSITY':
                        value = mat_info['Den'].values[0]
                    else:
                        value = mat_info[map_type].values[0]
                    density_matrix[mat_map_matrix == mat_key] = value

    # Store the density map
    target = target_dict['CT'][self.series_index]
    existing = target.get('density_maps', {})
    if not existing:
        target['density_maps'] = {}

    entry = {'3DMatrix': density_matrix, 'type': map_type}
    target['density_maps'][f'map_{map_type}_{len(existing)}'] = entry
    populate_medical_image_tree(self)


def del_density_map(self):
    if getattr(self, 'patientID', None):
        target_dict = self.medical_image[self.patientID][self.studyID]
    else:
        QMessageBox.critical(self, 'Error', 'No Patient selected')
        return
    try:
        target = target_dict['CT'][self.series_index]
    except Exception:
        QMessageBox.critical(self, 'Error', 'No CT found')
        return
    density_maps = target.get('density_maps', {})
    if not density_maps:
        QMessageBox.critical(self, 'Error', 'No density maps found for this CT')
        return

    items = list(density_maps.keys())
    items.append('All')
    item, ok = QInputDialog.getItem(self, "Delete Density Map", "Select the density map to delete:", items, 0, False)
    if not ok or not item:
        return  # Cancelled safely

    if item == 'All':
        target['density_maps'].clear()
        message = 'All density maps have been deleted.'
    else:
        target['density_maps'].pop(item)
        message = f"Density map '{item}' has been deleted."

    populate_medical_image_tree(self)
    QMessageBox.information(self, "Deleted", message)