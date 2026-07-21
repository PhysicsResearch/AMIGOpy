from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QPushButton,
                             QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
                             QRadioButton, QGroupBox, QDialogButtonBox, QLabel, QColorDialog, QComboBox)
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtCore import Qt
import pandas as pd
import os
import numpy as np
import random
from fcn_display.display_images  import displayaxial, displaycoronal, displaysagittal
import vtk

def update_color_button_style(button, qcolor):
    hex_color = qcolor.name()
    brightness = (qcolor.red() * 299 + qcolor.green() * 587 + qcolor.blue() * 114) / 1000
    text_color = "#000000" if brightness > 128 else "#ffffff"
    button.setText(hex_color.upper())
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: {hex_color};
            color: {text_color};
            font-weight: bold;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 3px;
        }}
        QPushButton:hover {{
            border: 2px solid #ffffff;
        }}
    """)

def open_color_dialog_for_row(self, row):
    try:
        r_item = self.table_circ_roi.item(row, 8) or self.table_circ_roi.item(row, 7) or self.table_circ_roi.item(row, 6)
        g_item = self.table_circ_roi.item(row, 9) or self.table_circ_roi.item(row, 8) or self.table_circ_roi.item(row, 7)
        b_item = self.table_circ_roi.item(row, 10) or self.table_circ_roi.item(row, 9) or self.table_circ_roi.item(row, 8)
        initial_color = QColor.fromRgbF(float(r_item.text()), float(g_item.text()), float(b_item.text()))
    except Exception:
        initial_color = QColor(255, 0, 0)

    chosen_color = QColorDialog.getColor(initial_color, self if hasattr(self, 'inherits') else None, f"Select Color for ROI {row+1}")
    if chosen_color.isValid():
        r_val = f"{chosen_color.redF():.2f}"
        g_val = f"{chosen_color.greenF():.2f}"
        b_val = f"{chosen_color.blueF():.2f}"

        self.table_circ_roi.blockSignals(True)
        self.table_circ_roi.setItem(row, 8, QTableWidgetItem(r_val))
        self.table_circ_roi.setItem(row, 9, QTableWidgetItem(g_val))
        self.table_circ_roi.setItem(row, 10, QTableWidgetItem(b_val))
        self.table_circ_roi.blockSignals(False)

        btn = self.table_circ_roi.cellWidget(row, 6)
        if btn:
            update_color_button_style(btn, chosen_color)

        update_row_color(self, row)
        displayaxial(self)
        displaycoronal(self)
        displaysagittal(self)

def toggle_rois(self):
    # Function to delete current visible ROIs and reset self.circle_actors
    renderer = self.vtkWidgetAxial.GetRenderWindow().GetRenderers().GetFirstRenderer()
    for actor in self.circle_actors_ax:
        renderer.RemoveActor(actor)
    self.circle_actors_ax.clear()
    self.vtkWidgetAxial.GetRenderWindow().Render()
    #
    renderer = self.vtkWidgetCoronal.GetRenderWindow().GetRenderers().GetFirstRenderer()
    for actor in self.circle_actors_co:
        renderer.RemoveActor(actor)
    self.circle_actors_co.clear()
    self.vtkWidgetCoronal.GetRenderWindow().Render()
    #
    renderer = self.vtkWidgetSagittal.GetRenderWindow().GetRenderers().GetFirstRenderer()
    for actor in self.circle_actors_sa:
        renderer.RemoveActor(actor)
    self.circle_actors_sa.clear()
    #
    displayaxial(self)
    displaycoronal(self)
    displaysagittal(self)

def on_roi_direction_changed(self, row, new_direction):
    if row < 0 or row >= self.table_circ_roi.rowCount():
        return
    item_0 = self.table_circ_roi.item(row, 0)
    if not item_0:
        return
    old_dir = item_0.data(Qt.UserRole + 1) or "Axial"
    if old_dir == new_direction:
        return

    item_0.setData(Qt.UserRole + 1, new_direction)

    idx = 0
    sag_val = 0
    cor_val = 0
    ax_val = 0

    if hasattr(self, 'current_sagittal_slice_index') and isinstance(self.current_sagittal_slice_index, list) and 0 <= idx < len(self.current_sagittal_slice_index) and self.current_sagittal_slice_index[idx] != -1:
        sag_val = self.current_sagittal_slice_index[idx]
    elif hasattr(self, 'SagittalSlider'):
        sag_val = self.SagittalSlider.value()

    if hasattr(self, 'current_coronal_slice_index') and isinstance(self.current_coronal_slice_index, list) and 0 <= idx < len(self.current_coronal_slice_index) and self.current_coronal_slice_index[idx] != -1:
        cor_val = self.current_coronal_slice_index[idx]
    elif hasattr(self, 'CoronalSlider'):
        cor_val = self.CoronalSlider.value()

    if hasattr(self, 'current_axial_slice_index') and isinstance(self.current_axial_slice_index, list) and 0 <= idx < len(self.current_axial_slice_index) and self.current_axial_slice_index[idx] != -1:
        ax_val = self.current_axial_slice_index[idx]
    elif hasattr(self, 'AxialSlider'):
        ax_val = self.AxialSlider.value()

    try:
        sli_ini = int(float(self.table_circ_roi.item(row, 3).text()))
        sli_fin = int(float(self.table_circ_roi.item(row, 4).text()))
        num_slices = max(1, sli_fin - sli_ini + 1)
    except Exception:
        num_slices = 1

    if new_direction == "Sagittal":
        x_val, y_val, slice_val = str(cor_val), str(ax_val), str(sag_val)
    elif new_direction == "Coronal":
        x_val, y_val, slice_val = str(sag_val), str(ax_val), str(cor_val)
    else: # Axial
        x_val, y_val, slice_val = str(sag_val), str(cor_val), str(ax_val)

    init_slice = int(slice_val)
    last_slice = init_slice + num_slices - 1

    self.table_circ_roi.blockSignals(True)
    item_0.setText(x_val)
    self.table_circ_roi.setItem(row, 1, QTableWidgetItem(y_val))
    self.table_circ_roi.setItem(row, 3, QTableWidgetItem(str(init_slice)))
    self.table_circ_roi.setItem(row, 4, QTableWidgetItem(str(last_slice)))
    self.table_circ_roi.blockSignals(False)

    update_row_color(self, row)
    displayaxial(self)
    displaycoronal(self)
    displaysagittal(self)
    c_roi_getdata(self)

def move_center_to_current(self, target_row=None):
    row = target_row
    if row is None:
        button = self.sender()
        if button is not None:
            for r in range(self.table_circ_roi.rowCount()):
                if self.table_circ_roi.cellWidget(r, 11) == button or self.table_circ_roi.cellWidget(r, 10) == button:
                    row = r
                    break
    if row is None or row < 0 or row >= self.table_circ_roi.rowCount():
        return
    
    # Update coordinates of this row based on its stored direction
    idx = 0
    sag_val = "0"
    cor_val = "0"
    ax_val = "0"

    if hasattr(self, 'current_sagittal_slice_index') and isinstance(self.current_sagittal_slice_index, list) and 0 <= idx < len(self.current_sagittal_slice_index) and self.current_sagittal_slice_index[idx] != -1:
        sag_val = str(self.current_sagittal_slice_index[idx])
    elif hasattr(self, 'SagittalSlider'):
        sag_val = str(self.SagittalSlider.value())

    if hasattr(self, 'current_coronal_slice_index') and isinstance(self.current_coronal_slice_index, list) and 0 <= idx < len(self.current_coronal_slice_index) and self.current_coronal_slice_index[idx] != -1:
        cor_val = str(self.current_coronal_slice_index[idx])
    elif hasattr(self, 'CoronalSlider'):
        cor_val = str(self.CoronalSlider.value())

    if hasattr(self, 'current_axial_slice_index') and isinstance(self.current_axial_slice_index, list) and 0 <= idx < len(self.current_axial_slice_index) and self.current_axial_slice_index[idx] != -1:
        ax_val = str(self.current_axial_slice_index[idx])
    elif hasattr(self, 'AxialSlider'):
        ax_val = str(self.AxialSlider.value())

    item_0 = self.table_circ_roi.item(row, 0)
    direction = item_0.data(Qt.UserRole + 1) if item_0 is not None else "Axial"
    if not direction:
        direction = "Axial"

    if direction == "Sagittal":
        x_val, y_val, slice_val = cor_val, ax_val, sag_val
    elif direction == "Coronal":
        x_val, y_val, slice_val = sag_val, ax_val, cor_val
    else: # Axial
        x_val, y_val, slice_val = sag_val, cor_val, ax_val

    num_slices = self.roi_slices.value() if hasattr(self, 'roi_slices') else 1
    try:
        init_slice = int(slice_val)
    except ValueError:
        init_slice = 0
    last_slice = init_slice + num_slices - 1

    # Temporarily disconnect signals to prevent intermediate updates
    self.table_circ_roi.blockSignals(True)
    if item_0:
        item_0.setText(x_val)
    else:
        new_item_0 = QTableWidgetItem(x_val)
        new_item_0.setData(Qt.UserRole + 1, direction)
        self.table_circ_roi.setItem(row, 0, new_item_0)
    self.table_circ_roi.setItem(row, 1, QTableWidgetItem(y_val))
    self.table_circ_roi.setItem(row, 3, QTableWidgetItem(str(init_slice)))
    self.table_circ_roi.setItem(row, 4, QTableWidgetItem(str(last_slice)))
    self.table_circ_roi.blockSignals(False)

    update_row_color(self, row)

    # Redraw and get data
    displayaxial(self)
    displaycoronal(self)
    displaysagittal(self)
    c_roi_getdata(self)

def roi_c_add_row(self):
    self.table_circ_roi.blockSignals(True)
    row_position = self.table_circ_roi.rowCount()
    self.table_circ_roi.insertRow(row_position)
    self.table_circ_roi.setColumnCount(12)
    self.table_circ_roi.setColumnHidden(8, True)
    self.table_circ_roi.setColumnHidden(9, True)
    self.table_circ_roi.setColumnHidden(10, True)
    
    idx = 0
    sag_val = "0"
    cor_val = "0"
    ax_val = "0"

    if hasattr(self, 'current_sagittal_slice_index') and isinstance(self.current_sagittal_slice_index, list) and 0 <= idx < len(self.current_sagittal_slice_index) and self.current_sagittal_slice_index[idx] != -1:
        sag_val = str(self.current_sagittal_slice_index[idx])
    elif hasattr(self, 'SagittalSlider'):
        sag_val = str(self.SagittalSlider.value())

    if hasattr(self, 'current_coronal_slice_index') and isinstance(self.current_coronal_slice_index, list) and 0 <= idx < len(self.current_coronal_slice_index) and self.current_coronal_slice_index[idx] != -1:
        cor_val = str(self.current_coronal_slice_index[idx])
    elif hasattr(self, 'CoronalSlider'):
        cor_val = str(self.CoronalSlider.value())

    if hasattr(self, 'current_axial_slice_index') and isinstance(self.current_axial_slice_index, list) and 0 <= idx < len(self.current_axial_slice_index) and self.current_axial_slice_index[idx] != -1:
        ax_val = str(self.current_axial_slice_index[idx])
    elif hasattr(self, 'AxialSlider'):
        ax_val = str(self.AxialSlider.value())

    direction = "Axial"
    if hasattr(self, 'roi_direction_combo') and self.roi_direction_combo is not None:
        direction = self.roi_direction_combo.currentText()

    if direction == "Sagittal":
        x_val, y_val, slice_val = cor_val, ax_val, sag_val
    elif direction == "Coronal":
        x_val, y_val, slice_val = sag_val, ax_val, cor_val
    else: # Axial
        x_val, y_val, slice_val = sag_val, cor_val, ax_val

    num_slices = self.roi_slices.value() if hasattr(self, 'roi_slices') else 1
    rad_val = str(self.roi_default_pixel_size.value()) if hasattr(self, 'roi_default_pixel_size') else "10"

    try:
        init_slice = int(slice_val)
    except ValueError:
        init_slice = 0
    last_slice = init_slice + num_slices - 1

    r_float = random.random()
    g_float = random.random()
    b_float = random.random()
    r_val = f"{r_float:.2f}"
    g_val = f"{g_float:.2f}"
    b_val = f"{b_float:.2f}"

    item_0 = QTableWidgetItem(x_val)
    item_0.setData(Qt.UserRole + 1, direction)

    self.table_circ_roi.setItem(row_position, 0, item_0)
    self.table_circ_roi.setItem(row_position, 1, QTableWidgetItem(y_val))
    self.table_circ_roi.setItem(row_position, 2, QTableWidgetItem(rad_val))
    self.table_circ_roi.setItem(row_position, 3, QTableWidgetItem(str(init_slice)))
    self.table_circ_roi.setItem(row_position, 4, QTableWidgetItem(str(last_slice)))
    self.table_circ_roi.setItem(row_position, 5, QTableWidgetItem("0.5"))
    self.table_circ_roi.setItem(row_position, 8, QTableWidgetItem(r_val))
    self.table_circ_roi.setItem(row_position, 9, QTableWidgetItem(g_val))
    self.table_circ_roi.setItem(row_position, 10, QTableWidgetItem(b_val))

    qcolor = QColor.fromRgbF(r_float, g_float, b_float)
    color_btn = QPushButton()
    update_color_button_style(color_btn, qcolor)
    color_btn.clicked.connect(lambda _, r=row_position: open_color_dialog_for_row(self, r))
    self.table_circ_roi.setCellWidget(row_position, 6, color_btn)

    dir_combo = QComboBox()
    dir_combo.addItems(["Axial", "Sagittal", "Coronal"])
    dir_combo.setCurrentText(direction)
    dir_combo.setStyleSheet("""
        QComboBox {
            background-color: #1e1e24;
            color: #ffffff;
            border: 1px solid #3c4450;
            border-radius: 3px;
            padding: 2px;
            font-weight: bold;
        }
        QComboBox QAbstractItemView {
            background-color: #1e1e24;
            color: #ffffff;
            selection-background-color: #3b82f6;
        }
    """)
    dir_combo.currentTextChanged.connect(lambda new_dir, r=row_position: on_roi_direction_changed(self, r, new_dir))
    self.table_circ_roi.setCellWidget(row_position, 7, dir_combo)

    btn = QPushButton("Move center two slice")
    btn.setStyleSheet("background-color: #3b82f6; color: white; font-weight: bold;")
    btn.clicked.connect(lambda _, r=row_position: move_center_to_current(self, r))
    self.table_circ_roi.setCellWidget(row_position, 11, btn)

    update_row_color(self, row_position)
    self.table_circ_roi.blockSignals(False)

    displayaxial(self)
    displaycoronal(self)
    displaysagittal(self)
    c_roi_getdata(self)

def roi_c_remove_row(self):
    selected_ranges = self.table_circ_roi.selectedRanges()
    if selected_ranges:
        row = selected_ranges[0].topRow()
    else:
        row = self.table_circ_roi.currentRow()

    if row >= 0 and row < self.table_circ_roi.rowCount():
        reply = QMessageBox.question(
            None, "Confirm Removal",
            f"Are you sure you want to remove line {row + 1}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.table_circ_roi.removeRow(row)
            displayaxial(self)
            displaycoronal(self)
            displaysagittal(self)
            c_roi_getdata(self)
    else:
        QMessageBox.information(None, "Information", "Please select a line in the circles ROI table to remove first.")
        
def on_roitable_item_changed(self, item):
    if item.column() in [5, 7, 8, 9]:
        try:
            value = float(item.text())
            if value < 0:
                item.setText("0")
            elif value > 1:
                item.setText("1")
        except ValueError:
            item.setText("0")
    elif item.column() in [1, 2, 3, 4]:
        try:
            value = float(item.text())
            if value < 0:
                item.setText("0")
        except ValueError:
            item.setText("0")  
    update_row_color(self, item.row())        
    displayaxial(self)
    displaycoronal(self)
    displaysagittal(self)
    
def on_roi_table_selection_changed(self):
    curr_row = self.table_circ_roi.currentRow()
    for r in range(self.table_circ_roi.rowCount()):
        v_item = self.table_circ_roi.verticalHeaderItem(r)
        is_selected = (r == curr_row)
        if v_item:
            font = v_item.font()
            font.setBold(is_selected)
            v_item.setFont(font)
            v_item.setText(f"► ROI {r + 1}" if is_selected else f"ROI {r + 1}")

def update_row_color(self, row):
    try:
        R_item = self.table_circ_roi.item(row, 7) or self.table_circ_roi.item(row, 6)
        G_item = self.table_circ_roi.item(row, 8) or self.table_circ_roi.item(row, 7)
        B_item = self.table_circ_roi.item(row, 9) or self.table_circ_roi.item(row, 8)
        transparency_item = self.table_circ_roi.item(row, 5)

        if R_item is None or G_item is None or B_item is None or transparency_item is None:
            return

        R = float(R_item.text())
        G = float(G_item.text())
        B = float(B_item.text())
        transparency = float(transparency_item.text())

        R = min(max(R, 0), 1)
        G = min(max(G, 0), 1)
        B = min(max(B, 0), 1)
        transparency = min(max(transparency, 0), 1)

        color = QColor(int(R * 255), int(G * 255), int(B * 255), int(transparency * 255))
        color_opaque = QColor(int(R * 255), int(G * 255), int(B * 255))

        btn = self.table_circ_roi.cellWidget(row, 6)
        if btn:
            update_color_button_style(btn, color_opaque)

        lum = 0.299 * R + 0.587 * G + 0.114 * B
        fg_color = QColor(0, 0, 0) if lum > 0.5 else QColor(255, 255, 255)

        is_selected = (row == self.table_circ_roi.currentRow())
        header_text = f"► ROI {row + 1}" if is_selected else f"ROI {row + 1}"

        v_item = self.table_circ_roi.verticalHeaderItem(row)
        if v_item is None:
            v_item = QTableWidgetItem(header_text)
            self.table_circ_roi.setVerticalHeaderItem(row, v_item)
        else:
            v_item.setText(header_text)

        v_item.setBackground(color_opaque)
        v_item.setForeground(fg_color)
        font = v_item.font()
        font.setBold(is_selected)
        v_item.setFont(font)

        item_0 = self.table_circ_roi.item(row, 0)
        if item_0:
            item_0.setBackground(color_opaque)
            item_0.setForeground(fg_color)

        for col in range(1, self.table_circ_roi.columnCount()):
            item = self.table_circ_roi.item(row, col)
            if item:
                item.setBackground(QBrush())
                item.setForeground(QBrush())

    except ValueError:
        print(f'Skipping row {row} due to invalid data')
            
def export_roi_circ_table_to_csv(self):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Save Coordinates CSV", "roi_circles_coordinates.csv", "CSV Files (*.csv)", options=options
    )

    if file_path:
        data = []
        for row in range(self.table_circ_roi.rowCount()):
            row_data = []
            for c in range(6):
                item = self.table_circ_roi.item(row, c)
                row_data.append(item.text() if item is not None else "")
            for c in [7, 8, 9]:
                item = self.table_circ_roi.item(row, c)
                row_data.append(item.text() if item is not None else "0.0")
            data.append(row_data)

        df = pd.DataFrame(data)
        try:
            df.to_csv(file_path, index=False, header=False)
            print(f"Table exported to {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not write to {file_path}. Please close the file if it is open in another program.")

def export_roi_circ_values_to_csv(self):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Save Values CSV", "roi_circles_values.csv", "CSV Files (*.csv)", options=options
    )

    if file_path:
        if hasattr(self, 'exportVoxValsROI') and self.exportVoxValsROI.isChecked():
            voxels_data = c_roi_getvoxels(self)
            df_vox = pd.DataFrame({k:pd.Series(v) for k,v in voxels_data.items()})
            base, ext = os.path.splitext(file_path)
            voxels_file_path = f"{base}_voxels{ext}"
            try:
                df_vox.to_csv(voxels_file_path, index=False)
            except:
                QMessageBox.warning(None, "Warning", f"Could not write to {voxels_file_path}. Please close the file if it is open in another program.")
                return

        data = []
        headers = []
        for col in range(self.table_roi_c_values.columnCount()):
            header_item = self.table_roi_c_values.horizontalHeaderItem(col)
            headers.append(header_item.text() if header_item is not None else f"Column {col}")

        for row in range(self.table_roi_c_values.rowCount()):
            row_data = []
            for col in range(self.table_roi_c_values.columnCount()):
                item = self.table_roi_c_values.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append('')
            data.append(row_data)

        df = pd.DataFrame(data, columns=headers)
        try:
            df.to_csv(file_path, index=False)
            print(f"Values exported to {file_path}")
        except:
            QMessageBox.warning(None, "Warning", f"Could not write to {file_path}. Please close the file if it is open in another program.")
            return

def import_roi_circ_table(self):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)

    if file_name:
        df = pd.read_csv(file_name, header=None)

        self.table_circ_roi.setRowCount(0)
        self.table_circ_roi.setColumnCount(12)
        column_names = ["X Cent. (Px)", "Y Cent. (Px)", "Rad. (Px)", "Init. Slice", "Last. Slice", "Trasnp.", "Color", "Dir.", "R", "G", "B", "Actions"]
        self.table_circ_roi.setHorizontalHeaderLabels(column_names)
        self.table_circ_roi.setColumnHidden(8, True)
        self.table_circ_roi.setColumnHidden(9, True)
        self.table_circ_roi.setColumnHidden(10, True)

        self.table_circ_roi.blockSignals(True)
        for row in df.itertuples(index=False):
            row_position = self.table_circ_roi.rowCount()
            self.table_circ_roi.insertRow(row_position)
            row_vals = list(row)
            
            for col in range(min(6, len(row_vals))):
                self.table_circ_roi.setItem(row_position, col, QTableWidgetItem(str(row_vals[col])))
            
            r_val = str(row_vals[6]) if len(row_vals) > 6 else "0.5"
            g_val = str(row_vals[7]) if len(row_vals) > 7 else "0.5"
            b_val = str(row_vals[8]) if len(row_vals) > 8 else "0.5"

            self.table_circ_roi.setItem(row_position, 8, QTableWidgetItem(r_val))
            self.table_circ_roi.setItem(row_position, 9, QTableWidgetItem(g_val))
            self.table_circ_roi.setItem(row_position, 10, QTableWidgetItem(b_val))

            try:
                qcolor = QColor.fromRgbF(float(r_val), float(g_val), float(b_val))
            except Exception:
                qcolor = QColor(255, 0, 0)

            color_btn = QPushButton()
            update_color_button_style(color_btn, qcolor)
            color_btn.clicked.connect(lambda _, r=row_position: open_color_dialog_for_row(self, r))
            self.table_circ_roi.setCellWidget(row_position, 6, color_btn)

            dir_combo = QComboBox()
            dir_combo.addItems(["Axial", "Sagittal", "Coronal"])
            dir_combo.setCurrentText("Axial")
            dir_combo.setStyleSheet("""
                QComboBox {
                    background-color: #1e1e24;
                    color: #ffffff;
                    border: 1px solid #3c4450;
                    border-radius: 3px;
                    padding: 2px;
                    font-weight: bold;
                }
                QComboBox QAbstractItemView {
                    background-color: #1e1e24;
                    color: #ffffff;
                    selection-background-color: #3b82f6;
                }
            """)
            dir_combo.currentTextChanged.connect(lambda new_dir, r=row_position: on_roi_direction_changed(self, r, new_dir))
            self.table_circ_roi.setCellWidget(row_position, 7, dir_combo)

            btn = QPushButton("Move center two slice")
            btn.setStyleSheet("background-color: #3b82f6; color: white; font-weight: bold;")
            btn.clicked.connect(lambda _, r=row_position: move_center_to_current(self, r))
            self.table_circ_roi.setCellWidget(row_position, 11, btn)
            
            update_row_color(self, row_position)
            
        self.table_circ_roi.blockSignals(False)

        print(f"Table populated from {file_name}")
        displayaxial(self)
        displaycoronal(self)
        displaysagittal(self)
        c_roi_getdata(self)

def open_series_selection_dialog(self):
    if getattr(self, 'DataType', None) not in ["DICOM", "Nifti"]:
        QMessageBox.warning(self if hasattr(self, 'inherits') else None, "Warning", "No DICOM/NIfTI data was found")
        return False
        
    try:
        series_list = self.medical_image[self.patientID][self.studyID][self.modality]
    except Exception:
        series_list = []

    if not series_list:
        QMessageBox.warning(self if hasattr(self, 'inherits') else None, "Warning", "No image series found for current patient/study/modality.")
        return False

    dialog = QDialog(self if hasattr(self, 'inherits') else None)
    dialog.setWindowTitle("Select Image Series & Layout")
    dialog.setMinimumWidth(420)
    
    layout = QVBoxLayout(dialog)
    
    lbl = QLabel("Select series to include in ROI calculation:")
    lbl.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
    layout.addWidget(lbl)
    
    list_widget = QListWidget()
    list_widget.setStyleSheet("""
        QListWidget {
            background-color: #1e1e24;
            color: #ffffff;
            border: 1px solid #3c4450;
            border-radius: 4px;
        }
        QListWidget::item {
            padding: 4px;
        }
    """)
    
    prev_selected = getattr(self, 'selected_series_indices', None)
    
    for idx, s_data in enumerate(series_list):
        if s_data is None:
            continue
        s_num = s_data.get('SeriesNumber', str(idx + 1)) if isinstance(s_data, dict) else str(idx + 1)
        meta = s_data.get('metadata', {}) if isinstance(s_data, dict) else {}
        s_desc = s_data.get('SeriesDescription', meta.get('SeriesDescription', f"Series {s_num}")) if isinstance(s_data, dict) else f"Series {s_num}"
        item_text = f"Series {s_num}: {s_desc}"
        
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, idx)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        
        if prev_selected is not None:
            item.setCheckState(Qt.Checked if idx in prev_selected else Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
            
        list_widget.addItem(item)
        
    layout.addWidget(list_widget)
    
    btn_box_check = QHBoxLayout()
    btn_check_all = QPushButton("Check All")
    btn_clear_all = QPushButton("Clear All")
    btn_check_all.setStyleSheet("background-color: #2b2b36; color: white; padding: 4px;")
    btn_clear_all.setStyleSheet("background-color: #2b2b36; color: white; padding: 4px;")
    
    def check_all_action():
        for i in range(list_widget.count()):
            list_widget.item(i).setCheckState(Qt.Checked)
            
    def clear_all_action():
        for i in range(list_widget.count()):
            list_widget.item(i).setCheckState(Qt.Unchecked)
            
    btn_check_all.clicked.connect(check_all_action)
    btn_clear_all.clicked.connect(clear_all_action)
    
    btn_box_check.addWidget(btn_check_all)
    btn_box_check.addWidget(btn_clear_all)
    layout.addLayout(btn_box_check)
    
    grp_dir = QGroupBox("Data Table Layout Option")
    grp_dir.setStyleSheet("QGroupBox { font-weight: bold; color: #3b82f6; }")
    dir_layout = QHBoxLayout(grp_dir)
    
    rdo_horizontal = QRadioButton("Horizontal (append to the side)")
    rdo_vertical = QRadioButton("Vertical (append at the bottom)")
    
    curr_dir = getattr(self, 'series_layout_direction', 'horizontal')
    if curr_dir == 'vertical':
        rdo_vertical.setChecked(True)
    else:
        rdo_horizontal.setChecked(True)
        
    dir_layout.addWidget(rdo_horizontal)
    dir_layout.addWidget(rdo_vertical)
    layout.addWidget(grp_dir)
    
    btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    layout.addWidget(btn_box)
    
    btn_box.accepted.connect(dialog.accept)
    btn_box.rejected.connect(dialog.reject)
    
    if dialog.exec() == QDialog.Accepted:
        chosen_indices = []
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item.checkState() == Qt.Checked:
                chosen_indices.append(item.data(Qt.UserRole))
                
        if not chosen_indices:
            QMessageBox.warning(self if hasattr(self, 'inherits') else None, "Warning", "No series selected. At least one series must be checked.")
            return False
            
        self.selected_series_indices = chosen_indices
        self.series_layout_direction = 'vertical' if rdo_vertical.isChecked() else 'horizontal'
        return True
    else:
        return False

def on_all_series_checkbox_toggled(self):
    if hasattr(self, 'checkBox_circ_roi_data_01') and self.checkBox_circ_roi_data_01.isChecked():
        success = open_series_selection_dialog(self)
        if not success and not getattr(self, 'selected_series_indices', None):
            self.checkBox_circ_roi_data_01.blockSignals(True)
            self.checkBox_circ_roi_data_01.setChecked(False)
            self.checkBox_circ_roi_data_01.blockSignals(False)

def roi_c_clear_all_rois(self):
    if self.table_circ_roi.rowCount() == 0:
        return
    reply = QMessageBox.question(
        self if hasattr(self, 'inherits') else None, "Confirm Clear All ROIs",
        "Are you sure you want to clear all ROIs from the table?",
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    if reply == QMessageBox.Yes:
        self.table_circ_roi.setRowCount(0)
        toggle_rois(self)
        displayaxial(self)
        displaycoronal(self)
        displaysagittal(self)
        self.table_roi_c_values.clearContents()
        self.table_roi_c_values.setRowCount(0)
        self.table_roi_c_values.setColumnCount(0)

def roi_c_clear_all_data(self):
    if self.table_roi_c_values.rowCount() == 0 and self.table_roi_c_values.columnCount() == 0:
        return
    reply = QMessageBox.question(
        self if hasattr(self, 'inherits') else None, "Confirm Clear All Data",
        "Are you sure you want to clear all calculated ROI data from the table?",
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
    )
    if reply == QMessageBox.Yes:
        self.table_roi_c_values.clearContents()
        self.table_roi_c_values.setRowCount(0)
        self.table_roi_c_values.setColumnCount(0)

def c_roi_getvoxels(self):
    if getattr(self, 'DataType', None) not in ["DICOM", "Nifti"]:
        QMessageBox.warning(None, "Warning", "No DICOM/NIfTI data was found")
        return
    if self.checkBox_circ_roi_data_01.isChecked():
        series_list = self.medical_image[self.patientID][self.studyID][self.modality]
    else:
        series_list = [self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]]
    
    voxels_data = {}
    skip = False
    
    for i, series_data in enumerate(series_list):
        reference_image = series_data['3DMatrix']
        series_number = series_data['SeriesNumber']
        
        for row in range(self.table_circ_roi.rowCount()):
            try:
                item_x = self.table_circ_roi.item(row, 0)
                item_y = self.table_circ_roi.item(row, 1)
                item_radius = self.table_circ_roi.item(row, 2)
                sli_ini = self.table_circ_roi.item(row, 3)
                sli_fin = self.table_circ_roi.item(row, 4)
    
                if item_x is None or item_y is None or item_radius is None or sli_ini is None or sli_fin is None:
                    print(f'Skipping row {row} due to missing data')
                    continue

                center_x = float(item_x.text())
                center_y = float(item_y.text())
                radius = float(item_radius.text())
                slice_ini = int(float(sli_ini.text()))
                slice_fin = int(float(sli_fin.text()))
    
                mask = np.zeros(reference_image.shape, dtype=bool)
                for z in range(slice_ini, slice_fin + 1):
                    y, x = np.ogrid[-center_y:reference_image.shape[1] - center_y, -center_x:reference_image.shape[2] - center_x]
                    try:
                        mask[z] = x*x + y*y <= radius*radius
                    except:
                        QMessageBox.warning(None, "Warning", f"Slice index {z} is out of bounds for the image with shape {reference_image.shape}")
                        skip = True
                        break
            
                if skip: 
                    break
                masked_data = reference_image[mask]
                voxels_data[f'Series_{series_number}_ROI_{row}'] = masked_data.flatten()
    
            except ValueError:
                print(f'Skipping row {row} due to invalid data')
                continue

    return voxels_data

def export_all_roi_voxel_values_to_csv(self):
    if not hasattr(self, 'display_data') or not self.display_data:
        QMessageBox.warning(None, "Warning", "No image dataset loaded.")
        return

    num_rois = self.table_circ_roi.rowCount()
    if num_rois == 0:
        QMessageBox.warning(None, "Warning", "No ROIs found in table.")
        return

    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Save ROI Voxel Values CSV", "roi_voxel_values.csv", "CSV Files (*.csv)", options=options
    )

    if not file_path:
        return

    idx = self.layer_selected.currentIndex() if hasattr(self, 'layer_selected') else 0
    if hasattr(self, 'display_data') and isinstance(self.display_data, dict) and idx in self.display_data:
        reference_image = self.display_data[idx]
    elif hasattr(self, 'display_data') and isinstance(self.display_data, dict) and self.display_data:
        reference_image = list(self.display_data.values())[0]
    else:
        QMessageBox.warning(None, "Warning", "No valid 3D image matrix available.")
        return

    lines = []
    for row in range(num_rois):
        try:
            item_x = self.table_circ_roi.item(row, 0)
            item_y = self.table_circ_roi.item(row, 1)
            item_r = self.table_circ_roi.item(row, 2)
            sli_ini = self.table_circ_roi.item(row, 3)
            sli_fin = self.table_circ_roi.item(row, 4)

            if not (item_x and item_y and item_r and sli_ini and sli_fin):
                continue

            center_x = float(item_x.text())
            center_y = float(item_y.text())
            radius = float(item_r.text())
            slice_ini = int(float(sli_ini.text()))
            slice_fin = int(float(sli_fin.text()))

            dir_widget = self.table_circ_roi.cellWidget(row, 7)
            if dir_widget is not None and hasattr(dir_widget, 'currentText'):
                row_dir = dir_widget.currentText()
            else:
                row_dir = item_x.data(Qt.UserRole + 1) if item_x is not None else "Axial"
            if not row_dir:
                row_dir = "Axial"

            mask = np.zeros(reference_image.shape, dtype=bool)

            if row_dir == "Sagittal":
                max_x = reference_image.shape[2]
                s_ini = max(0, min(slice_ini, max_x - 1))
                s_fin = max(0, min(slice_fin, max_x - 1))
                cy_i, cz_i = int(center_x), int(center_y)
                for x_idx in range(s_ini, s_fin + 1):
                    z, y = np.ogrid[-cz_i:reference_image.shape[0] - cz_i, -cy_i:reference_image.shape[1] - cy_i]
                    mask[z, y, x_idx] = (z*z + y*y <= radius*radius)
            elif row_dir == "Coronal":
                max_y = reference_image.shape[1]
                s_ini = max(0, min(slice_ini, max_y - 1))
                s_fin = max(0, min(slice_fin, max_y - 1))
                cx_i, cz_i = int(center_x), int(center_y)
                for y_idx in range(s_ini, s_fin + 1):
                    z, x = np.ogrid[-cz_i:reference_image.shape[0] - cz_i, -cx_i:reference_image.shape[2] - cx_i]
                    mask[z, y_idx, x] = (z*z + x*x <= radius*radius)
            else: # Axial
                max_z = reference_image.shape[0]
                s_ini = max(0, min(slice_ini, max_z - 1))
                s_fin = max(0, min(slice_fin, max_z - 1))
                cx_i, cy_i = int(center_x), int(center_y)
                for z_idx in range(s_ini, s_fin + 1):
                    y, x = np.ogrid[-cy_i:reference_image.shape[1] - cy_i, -cx_i:reference_image.shape[2] - cx_i]
                    mask[z_idx, y, x] = (x*x + y*y <= radius*radius)

            voxels = reference_image[mask].flatten()
            roi_label = f"ROI{row + 1}"
            val_strs = [str(v) for v in voxels]
            line = f"{roi_label};" + ";".join(val_strs)
            lines.append(line)
        except Exception as e:
            print(f"Skipping ROI {row + 1} voxel export due to error: {e}")
            continue

    if not lines:
        QMessageBox.warning(None, "Warning", "No voxels were extracted from selected ROIs.")
        return

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for l in lines:
                f.write(l + "\n")
        QMessageBox.information(None, "Success", f"Exported voxel values for {len(lines)} ROIs to CSV:\n{file_path}")
        print(f"Voxel values exported to {file_path}")
    except Exception as e:
        QMessageBox.warning(None, "Warning", f"Could not write to file {file_path}:\n{e}")

    
def c_roi_getdata(self, ask_user=False):
    if not hasattr(self, 'display_data') or not self.display_data:
        if ask_user:
            QMessageBox.warning(None, "Warning", "No image data was found")
        return

    num_rois = self.table_circ_roi.rowCount()
    if num_rois == 0:
        if ask_user:
            QMessageBox.warning(None, "Warning", "No ROIs found in table")
        return

    use_all_series = hasattr(self, 'checkBox_circ_roi_data_01') and self.checkBox_circ_roi_data_01.isChecked()
    
    if use_all_series:
        mode = "replace"
        selected_indices = getattr(self, 'selected_series_indices', None)
        
        all_series = []
        if hasattr(self, 'medical_image') and hasattr(self, 'patientID') and hasattr(self, 'studyID') and hasattr(self, 'modality'):
            try:
                all_series = self.medical_image[self.patientID][self.studyID][self.modality]
            except Exception:
                all_series = []

        if isinstance(all_series, dict):
            series_items = list(all_series.items())
        elif isinstance(all_series, list):
            series_items = [(idx, item) for idx, item in enumerate(all_series) if item is not None]
        else:
            series_items = []

        if selected_indices is not None and len(selected_indices) > 0:
            target_series_list = [(idx, s_data) for idx, s_data in series_items if idx in selected_indices]
        else:
            target_series_list = series_items

        if not target_series_list:
            if hasattr(self, 'display_data') and 0 in self.display_data and self.display_data[0] is not None:
                target_series_list = [(0, {'3DMatrix': self.display_data[0], 'SeriesNumber': 1})]

        if not target_series_list:
            if ask_user:
                QMessageBox.warning(None, "Warning", "No valid image series selected")
            return
    else:
        target_series_list = [(getattr(self, 'series_index', 0), {'3DMatrix': self.display_data[0] if hasattr(self, 'display_data') and 0 in self.display_data else None, 'SeriesNumber': getattr(self, 'series_index', 0)})]

    active_layers = []
    for l in range(4):
        if l in self.display_data and self.display_data[l] is not None:
            active_layers.append(l)

    if not active_layers:
        if ask_user:
            QMessageBox.warning(None, "Warning", "No active layers with image data found")
        return

    if not use_all_series:
        mode = "replace"
        if ask_user and self.table_roi_c_values.rowCount() > 0:
            msgBox = QMessageBox(self if hasattr(self, 'inherits') else None)
            msgBox.setWindowTitle("Get ROI Data")
            msgBox.setText("Do you want to append the calculated ROI data to the table or replace existing data?")
            btn_append = msgBox.addButton("Append", QMessageBox.AcceptRole)
            btn_replace = msgBox.addButton("Replace", QMessageBox.AcceptRole)
            btn_cancel = msgBox.addButton("Cancel", QMessageBox.RejectRole)
            msgBox.setDefaultButton(btn_replace)
            msgBox.exec()

            clicked = msgBox.clickedButton()
            if clicked == btn_cancel:
                return
            elif clicked == btn_append:
                mode = "append"
            else:
                mode = "replace"

    direction = getattr(self, 'series_layout_direction', 'horizontal') if use_all_series else 'horizontal'

    if direction == "horizontal":
        horizontalLabels = []
        for s_idx, s_data in target_series_list:
            s_idx_safe = s_idx if (s_idx is not None and isinstance(s_idx, int)) else 0
            s_num = s_data.get('SeriesNumber', str(s_idx_safe + 1)) if isinstance(s_data, dict) else str(s_idx_safe + 1)
            prefix = f"S{s_num}_" if len(target_series_list) > 1 else ""
            for l in active_layers:
                horizontalLabels.extend([f"{prefix}Mean_L{l}", f"{prefix}STD_L{l}", f"{prefix}N_L{l}"])

        self.table_roi_c_values.setColumnCount(len(horizontalLabels))
        self.table_roi_c_values.setHorizontalHeaderLabels(horizontalLabels)
        from PySide6.QtWidgets import QHeaderView
        self.table_roi_c_values.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        for c in range(self.table_roi_c_values.columnCount()):
            self.table_roi_c_values.horizontalHeader().setSectionResizeMode(c, QHeaderView.Interactive)
        self.table_roi_c_values.horizontalHeader().setStretchLastSection(True)

        if mode == "replace":
            start_row = 0
            self.table_roi_c_values.setRowCount(num_rois)
        else:
            start_row = self.table_roi_c_values.rowCount()
            self.table_roi_c_values.setRowCount(start_row + num_rois)

        for row in range(num_rois):
            target_row = start_row + row
            col_offset = 0
            
            try:
                item_x = self.table_circ_roi.item(row, 0)
                item_y = self.table_circ_roi.item(row, 1)
                item_radius = self.table_circ_roi.item(row, 2)
                sli_ini = self.table_circ_roi.item(row, 3)
                sli_fin = self.table_circ_roi.item(row, 4)
                if item_x is None or item_y is None or item_radius is None or sli_ini is None or sli_fin is None:
                    continue

                center_x = float(item_x.text())
                center_y = float(item_y.text())
                radius = float(item_radius.text())
                slice_ini_raw = int(float(sli_ini.text()))
                slice_fin_raw = int(float(sli_fin.text()))
            except Exception as e:
                print(f"Skipping row {row} due to invalid parameters: {e}")
                continue

            for s_idx, s_data in target_series_list:
                for l in active_layers:
                    if isinstance(s_data, dict) and '3DMatrix' in s_data and s_data['3DMatrix'] is not None:
                        ref_img = s_data['3DMatrix']
                    elif l in self.display_data:
                        ref_img = self.display_data[l]
                    else:
                        ref_img = None

                    if ref_img is None or not hasattr(ref_img, 'shape'):
                        self.table_roi_c_values.setItem(target_row, col_offset, QTableWidgetItem("0.0000"))
                        self.table_roi_c_values.setItem(target_row, col_offset+1, QTableWidgetItem("0.0000"))
                        self.table_roi_c_values.setItem(target_row, col_offset+2, QTableWidgetItem("0"))
                        col_offset += 3
                        continue

                    direction = item_x.data(Qt.UserRole + 1) if item_x is not None else "Axial"
                    if not direction:
                        direction = "Axial"

                    cx_i, cy_i = int(center_x), int(center_y)

                    if direction == "Sagittal":
                        max_slices = ref_img.shape[2]
                        slice_ini = max(0, min(slice_ini_raw, max_slices - 1))
                        slice_fin = max(0, min(slice_fin_raw, max_slices - 1))

                        mask = np.zeros(ref_img.shape, dtype=bool)
                        for x_idx in range(slice_ini, slice_fin + 1):
                            z, y = np.ogrid[-cy_i:ref_img.shape[0] - cy_i, -cx_i:ref_img.shape[1] - cx_i]
                            mask[z, y, x_idx] = z*z + y*y <= radius*radius
                    elif direction == "Coronal":
                        max_slices = ref_img.shape[1]
                        slice_ini = max(0, min(slice_ini_raw, max_slices - 1))
                        slice_fin = max(0, min(slice_fin_raw, max_slices - 1))

                        mask = np.zeros(ref_img.shape, dtype=bool)
                        for y_idx in range(slice_ini, slice_fin + 1):
                            z, x = np.ogrid[-cy_i:ref_img.shape[0] - cy_i, -cx_i:ref_img.shape[2] - cx_i]
                            mask[z, y_idx, x] = z*z + x*x <= radius*radius
                    else:
                        max_slices = ref_img.shape[0]
                        slice_ini = max(0, min(slice_ini_raw, max_slices - 1))
                        slice_fin = max(0, min(slice_fin_raw, max_slices - 1))

                        mask = np.zeros(ref_img.shape, dtype=bool)
                        for z in range(slice_ini, slice_fin + 1):
                            y, x = np.ogrid[-cy_i:ref_img.shape[1] - cy_i, -cx_i:ref_img.shape[2] - cx_i]
                            mask[z] = x*x + y*y <= radius*radius

                    masked_data = ref_img[mask]
                    if masked_data.size > 0:
                        mean_val = np.mean(masked_data)
                        std_val = np.std(masked_data)
                        n_vox = masked_data.size
                    else:
                        mean_val, std_val, n_vox = 0.0, 0.0, 0

                    self.table_roi_c_values.setItem(target_row, col_offset, QTableWidgetItem(f"{mean_val:.4f}"))
                    self.table_roi_c_values.setItem(target_row, col_offset+1, QTableWidgetItem(f"{std_val:.4f}"))
                    self.table_roi_c_values.setItem(target_row, col_offset+2, QTableWidgetItem(str(n_vox)))
                    col_offset += 3

    else: # direction == "vertical"
        horizontalLabels = ["Series"]
        for l in active_layers:
            horizontalLabels.extend([f"Mean_L{l}", f"STD_L{l}", f"N_L{l}"])

        self.table_roi_c_values.setColumnCount(len(horizontalLabels))
        self.table_roi_c_values.setHorizontalHeaderLabels(horizontalLabels)
        from PySide6.QtWidgets import QHeaderView
        self.table_roi_c_values.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        for c in range(self.table_roi_c_values.columnCount()):
            self.table_roi_c_values.horizontalHeader().setSectionResizeMode(c, QHeaderView.Interactive)
        self.table_roi_c_values.horizontalHeader().setStretchLastSection(True)

        total_new_rows = num_rois * len(target_series_list)
        if mode == "replace":
            start_row = 0
            self.table_roi_c_values.setRowCount(total_new_rows)
        else:
            start_row = self.table_roi_c_values.rowCount()
            self.table_roi_c_values.setRowCount(start_row + total_new_rows)

        curr_target_row = start_row

        for s_idx, s_data in target_series_list:
            s_idx_safe = s_idx if (s_idx is not None and isinstance(s_idx, int)) else 0
            s_num = s_data.get('SeriesNumber', str(s_idx_safe + 1)) if isinstance(s_data, dict) else str(s_idx_safe + 1)
            series_label = f"Series {s_num}"

            for row in range(num_rois):
                self.table_roi_c_values.setItem(curr_target_row, 0, QTableWidgetItem(series_label))
                
                try:
                    item_x = self.table_circ_roi.item(row, 0)
                    item_y = self.table_circ_roi.item(row, 1)
                    item_radius = self.table_circ_roi.item(row, 2)
                    sli_ini = self.table_circ_roi.item(row, 3)
                    sli_fin = self.table_circ_roi.item(row, 4)
                    if item_x is None or item_y is None or item_radius is None or sli_ini is None or sli_fin is None:
                        curr_target_row += 1
                        continue

                    center_x = float(item_x.text())
                    center_y = float(item_y.text())
                    radius = float(item_radius.text())
                    slice_ini_raw = int(float(sli_ini.text()))
                    slice_fin_raw = int(float(sli_fin.text()))
                except Exception as e:
                    print(f"Skipping row {row} due to invalid parameters: {e}")
                    curr_target_row += 1
                    continue

                for i, l in enumerate(active_layers):
                    if isinstance(s_data, dict) and '3DMatrix' in s_data and s_data['3DMatrix'] is not None:
                        ref_img = s_data['3DMatrix']
                    elif l in self.display_data:
                        ref_img = self.display_data[l]
                    else:
                        ref_img = None

                    if ref_img is None or not hasattr(ref_img, 'shape'):
                        self.table_roi_c_values.setItem(curr_target_row, 1 + i*3+0, QTableWidgetItem("0.0000"))
                        self.table_roi_c_values.setItem(curr_target_row, 1 + i*3+1, QTableWidgetItem("0.0000"))
                        self.table_roi_c_values.setItem(curr_target_row, 1 + i*3+2, QTableWidgetItem("0"))
                        continue

                    direction = item_x.data(Qt.UserRole + 1) if item_x is not None else "Axial"
                    if not direction:
                        direction = "Axial"

                    cx_i, cy_i = int(center_x), int(center_y)

                    if direction == "Sagittal":
                        max_slices = ref_img.shape[2]
                        slice_ini = max(0, min(slice_ini_raw, max_slices - 1))
                        slice_fin = max(0, min(slice_fin_raw, max_slices - 1))

                        mask = np.zeros(ref_img.shape, dtype=bool)
                        for x_idx in range(slice_ini, slice_fin + 1):
                            z, y = np.ogrid[-cy_i:ref_img.shape[0] - cy_i, -cx_i:ref_img.shape[1] - cx_i]
                            mask[z, y, x_idx] = z*z + y*y <= radius*radius
                    elif direction == "Coronal":
                        max_slices = ref_img.shape[1]
                        slice_ini = max(0, min(slice_ini_raw, max_slices - 1))
                        slice_fin = max(0, min(slice_fin_raw, max_slices - 1))

                        mask = np.zeros(ref_img.shape, dtype=bool)
                        for y_idx in range(slice_ini, slice_fin + 1):
                            z, x = np.ogrid[-cy_i:ref_img.shape[0] - cy_i, -cx_i:ref_img.shape[2] - cx_i]
                            mask[z, y_idx, x] = z*z + x*x <= radius*radius
                    else:
                        max_slices = ref_img.shape[0]
                        slice_ini = max(0, min(slice_ini_raw, max_slices - 1))
                        slice_fin = max(0, min(slice_fin_raw, max_slices - 1))

                        mask = np.zeros(ref_img.shape, dtype=bool)
                        for z in range(slice_ini, slice_fin + 1):
                            y, x = np.ogrid[-cy_i:ref_img.shape[1] - cy_i, -cx_i:ref_img.shape[2] - cx_i]
                            mask[z] = x*x + y*y <= radius*radius

                    masked_data = ref_img[mask]
                    if masked_data.size > 0:
                        mean_val = np.mean(masked_data)
                        std_val = np.std(masked_data)
                        n_vox = masked_data.size
                    else:
                        mean_val, std_val, n_vox = 0.0, 0.0, 0

                    self.table_roi_c_values.setItem(curr_target_row, 1 + i*3+0, QTableWidgetItem(f"{mean_val:.4f}"))
                    self.table_roi_c_values.setItem(curr_target_row, 1 + i*3+1, QTableWidgetItem(f"{std_val:.4f}"))
                    self.table_roi_c_values.setItem(curr_target_row, 1 + i*3+2, QTableWidgetItem(str(n_vox)))

                curr_target_row += 1