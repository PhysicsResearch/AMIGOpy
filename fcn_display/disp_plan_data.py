import numpy as np
import csv
from fcn_display.brachy_channel_edit import dicom_xyz, table_array, table_xyz
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox, QInputDialog
from PySide6.QtGui import QColor
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QTableWidget, QPushButton, QSpinBox, QLabel, QMessageBox,
    QCheckBox, QHBoxLayout
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt
import pandas as pd



def update_plan_tables(self):
    if not hasattr(self, 'brachy_spinBox_01'):
        return

    if 'Plan_Brachy_Channels' in self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']:
        # the plan as loaded (or last saved): to tell whether it was changed since
        from fcn_RTFiles.amigo_rtplan import ensure_saved_state
        ensure_saved_state(self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata'])
        N_channels = len(self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']['Plan_Brachy_Channels'])
        #
        # set spinbo min value
        self.brachy_spinBox_01.setMinimum(1)
        # Set the maximum value (a new plan has no catheters yet)
        self.brachy_spinBox_01.setMaximum(max(N_channels, 1))
        # Set the current value
        self.brachy_spinBox_01.setValue(1)
        #
        update_disp_brachy_plan(self)
        
        # Update 3D viewer if initialized
        if hasattr(self, '_3D_brachy_table'):
            from fcn_3Dview.brachy_3D_table import repopulate_3D_brachy_table
            repopulate_3D_brachy_table(self)


def update_disp_brachy_plan(self):
    # Check if plan-related attributes exist
    required_attrs = ['patientID_plan', 'studyID_plan', 'modality_plan', 'series_index_plan']
    if not all(hasattr(self, attr) for attr in required_attrs):
        QMessageBox.warning(self, "Warning", "No plan loaded.")
        return

    metadata = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']
    try:
        channels = metadata['Plan_Brachy_Channels']
    except KeyError:
        QMessageBox.warning(self, "Warning", "Plan data is missing or corrupted.")
        return

    # Clear and set up table
    clear_brachy_table(self)
    setup_brachy_table_headers(self)

    selected_dw_ch = self.brachy_combobox_01.currentText()

    ref_points = metadata.get('Plan_Dose_References', [])
    if selected_dw_ch == "Ref. Points":
        if not ref_points:
            ref_points = [{
                'DoseReferenceNumber': 1,
                'DoseReferenceStructureType': 'COORDINATE',
                'DoseReferenceDescription': 'Point 1',
                'DoseReferenceDescription ': 'Point 1',
                'DoseReferenceType': 'POINT',
                'TargetPrescriptionDose': 'N/A',
                'TargedPrescritionDose': 'N/A',
                'DoseReferencePointCoordinates': ['N/A', 'N/A', 'N/A'],
                'Visible': True
            }]
            metadata['Plan_Dose_References'] = ref_points
            # (a row to add points from, not a change of the plan)
            from fcn_RTFiles.amigo_rtplan import adopt_placeholder_ref
            adopt_placeholder_ref(metadata)
        rtdose_list = self.medical_image[self.patientID_plan][self.studyID_plan].get('RTDOSE', [])
        selected_rtdose = None
        if len(rtdose_list) == 1:
            selected_rtdose = rtdose_list[0]
        elif len(rtdose_list) > 1:
            items = []
            for idx, s in enumerate(rtdose_list):
                desc = s.get('metadata', {}).get('SeriesDescription', '')
                num = s.get('SeriesNumber', idx + 1)
                items.append(f"Series {num}: {desc}" if desc else f"Series {num}")
            
            selected_item, ok = QInputDialog.getItem(
                self, 
                "Select RT Dose", 
                "Multiple RT Dose series found. Please select one to use for dose calculation:", 
                items, 
                0, 
                False
            )
            if ok and selected_item:
                idx = items.index(selected_item)
                selected_rtdose = rtdose_list[idx]

        self.selected_rtdose_ref = selected_rtdose
        populate_brachy_table(self, ref_points)
        
        if selected_rtdose is not None:
            calculate_ref_points_dose(self, selected_rtdose)
    elif not channels:
        # a plan without catheters (a new plan): empty table
        populate_brachy_table(self, np.empty((0, 9 if selected_dw_ch == "Dwells" else 3), dtype=np.float32))
    else:
        try:
            current_ch = channels[self.brachy_spinBox_01.value() - 1]
        except IndexError:
            QMessageBox.warning(self, "Warning", "Invalid channel selected.")
            return

        if selected_dw_ch == "Dwells": 
            populate_brachy_table(self, current_ch.get('DwellInfo'))
        else:
            populate_brachy_table(self, current_ch.get('ChPos'))

    apply_alternating_row_colors(self)
    # Title, width and edit buttons of the View > PLAN > Brachy table
    from fcn_display.brachy_panel import update_brachy_table_header
    update_brachy_table_header(self)

    from fcn_display.display_images import displayaxial, displaysagittal, displaycoronal
    displayaxial(self)
    displaysagittal(self)
    displaycoronal(self)



def clear_brachy_table(self):
    """
    Clears all existing rows and columns from brachy_table_01.
    """
    table = getattr(self, 'brachy_table_01', None)
    if table is not None:
        table.blockSignals(True)
        try:
            table.clear()           # Clears the table content but retains headers
            table.setRowCount(0)    # Removes all rows
            table.setColumnCount(0) # Removes all columns
        finally:
            table.blockSignals(False)

# Coordinate columns in the user's axes, as the views and MCNP (table_xyz; the plan data stay DICOM)
HEADER_TIPS = {"X (mm)": "X = DICOM x: the sagittal slice position (\"Slice (X)\" in the views)",
               "Y (mm)": "Y = DICOM z (superior +): the axial slice position (\"Slice (Y)\" in the views)",
               "Z (mm)": "Z = -DICOM y (anterior +): the coronal slice position (\"Slice (Z)\" in the views), as MCNP Z",
               "Uy": "Source direction along Y (DICOM z)",
               "Uz": "Source direction along Z (-DICOM y)"}


def setup_brachy_table_headers(self):
    """
    Sets up the column headers for brachy_table_01.
    """
    selected_dw_ch = self.brachy_combobox_01.currentText()
    if selected_dw_ch == "Dwells":
        headers = ["IDX", "Rel. Pos (mm)", "Time (s)", "X (mm)", "Y (mm)", "Z (mm)", "Ux", "Uy", "Uz"]
    elif selected_dw_ch == "Channels":
        headers = ["X (mm)", "Y (mm)", "Z (mm)"]
    elif selected_dw_ch == "Ref. Points":
        headers = ["Ref. Num", "Structure Type", "Description", "Type", "Target Dose", "X (mm)", "Y (mm)", "Z (mm)", "Dose (cGy)", "Visible", "Go to Pt", "Get Slice Pt", "Delete"]
    else:
        headers = ["X (mm)", "Y (mm)", "Z (mm)"]

    table = getattr(self, 'brachy_table_01', None)
    if table is not None:
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        for c, text in enumerate(headers):
            if text in HEADER_TIPS:
                table.horizontalHeaderItem(c).setToolTip(HEADER_TIPS[text])
        table.resizeColumnsToContents()


    
def populate_brachy_table(self, table_info):
    """
    Populates brachy_table_01 with data from table_info.

    :param table_info: NumPy array with shape (n, 9) or list of dicts
    """
    
    self.brachy_table_01.blockSignals(True)
    try:
        if isinstance(table_info, list):
            num_rows = len(table_info)
            num_columns = 13  # Ref. Num, Structure Type, Description, Type, Target Dose, X, Y, Z, Dose (cGy), Visible, Go To, Get Plane, Delete/ADD

            # Set row count to num_rows + 1 for the extra "ADD" button row
            self.brachy_table_01.setRowCount(num_rows + 1)
            self.brachy_table_01.setColumnCount(num_columns)

            def trigger_go_to_pt(row_idx):
                if not hasattr(self, 'patientID_plan') or not self.patientID_plan:
                    return
                metadata = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']
                ref_points = metadata.get('Plan_Dose_References', [])
                if row_idx >= len(ref_points):
                    return
                coords = ref_points[row_idx].get('DoseReferencePointCoordinates')
                if not isinstance(coords, list) or len(coords) < 3:
                    return
                
                pt_x, pt_y, pt_z = coords[0], coords[1], coords[2]
                if pt_x == 'N/A' or pt_y == 'N/A' or pt_z == 'N/A':
                    return
                    
                idx = self.layer_selected.currentIndex()
                if idx not in self.display_data:
                    return
                    
                from fcn_display.mouse_move_slicechanges import change_sliceAxial, change_sliceSagittal, change_sliceCoronal
                
                # Axial slice index calculation:
                z_val = pt_z - self.Im_PatPosition[idx, 2] - self.Im_Offset[idx, 2]
                axial_index = int(round(z_val / self.slice_thick[idx]))
                axial_index = max(0, min(axial_index, self.display_data[idx].shape[0] - 1))
                self.current_axial_slice_index[idx] = axial_index
                
                # Coronal slice index calculation:
                y_val = (pt_y - self.Im_PatPosition[idx, 1] - self.Im_Offset[idx, 1]) / self.pixel_spac[idx, 0]
                coronal_index = int(round((self.display_data[idx].shape[1] - 1) - y_val))
                coronal_index = max(0, min(coronal_index, self.display_data[idx].shape[1] - 1))
                self.current_coronal_slice_index[idx] = coronal_index
                
                # Sagittal slice index calculation:
                x_val = pt_x - self.Im_PatPosition[idx, 0] - self.Im_Offset[idx, 0]
                sagittal_index = int(round(x_val / self.pixel_spac[idx, 1]))
                sagittal_index = max(0, min(sagittal_index, self.display_data[idx].shape[2] - 1))
                self.current_sagittal_slice_index[idx] = sagittal_index
                
                change_sliceAxial(self, 0)
                change_sliceCoronal(self, 0)
                change_sliceSagittal(self, 0)

            def trigger_get_slice_pt(row_idx):
                if not hasattr(self, 'patientID_plan') or not self.patientID_plan:
                    return
                idx = self.layer_selected.currentIndex()
                if idx not in self.display_data:
                    return
                    
                # Get current slices
                axial_index = self.current_axial_slice_index[idx]
                coronal_index = self.current_coronal_slice_index[idx]
                sagittal_index = self.current_sagittal_slice_index[idx]
                
                # Reverse calculation to physical space
                pt_z = self.Im_PatPosition[idx, 2] + axial_index * self.slice_thick[idx] + self.Im_Offset[idx, 2]
                pt_x = self.Im_PatPosition[idx, 0] + sagittal_index * self.pixel_spac[idx, 1] + self.Im_Offset[idx, 0]
                pt_y = self.Im_PatPosition[idx, 1] + (self.display_data[idx].shape[1] - 1 - coronal_index) * self.pixel_spac[idx, 0] + self.Im_Offset[idx, 1]
                
                pt_x = float(f"{pt_x:.2f}")
                pt_y = float(f"{pt_y:.2f}")
                pt_z = float(f"{pt_z:.2f}")
                
                # Update metadata
                metadata = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']
                ref_points = metadata.get('Plan_Dose_References', [])
                if row_idx >= len(ref_points):
                    return
                ref_points[row_idx]['DoseReferencePointCoordinates'] = [pt_x, pt_y, pt_z]
                
                # Update table items (block signals)
                table = self.brachy_table_01
                table.blockSignals(True)
                try:
                    tx, ty, tz = table_xyz(pt_x, pt_y, pt_z)   # X, Y, Z as the views name them
                    item_x = QTableWidgetItem(str(tx))
                    item_x.setTextAlignment(Qt.AlignCenter)
                    table.setItem(row_idx, 5, item_x)

                    item_y = QTableWidgetItem(str(ty))
                    item_y.setTextAlignment(Qt.AlignCenter)
                    table.setItem(row_idx, 6, item_y)

                    item_z = QTableWidgetItem(str(tz))
                    item_z.setTextAlignment(Qt.AlignCenter)
                    table.setItem(row_idx, 7, item_z)

                    # Recalculate dose if active RTDOSE exists
                    dose_str = 'N/A'
                    if hasattr(self, 'selected_rtdose_ref') and self.selected_rtdose_ref is not None:
                        dose_matrix = self.selected_rtdose_ref.get('3DMatrix')
                        meta = self.selected_rtdose_ref.get('metadata', {})
                        if dose_matrix is not None and isinstance(dose_matrix, np.ndarray):
                            origin = meta.get('ImagePositionPatient', [0.0, 0.0, 0.0])
                            x0, y0, z0 = origin[0], origin[1], origin[2]
                            
                            spacing = meta.get('PixelSpacing', [1.0, 1.0])
                            dx, dy = spacing[0], spacing[1]
                            dz = meta.get('SliceThickness', 1.0)
                            
                            Nz, Ny, Nx = dose_matrix.shape
                            
                            dicom_file = meta.get('DCM_Info')
                            grid_offset = getattr(dicom_file, 'GridFrameOffsetVector', None)
                            if grid_offset is not None:
                                z_grid = np.array([z0 + float(offset) for offset in grid_offset])
                            else:
                                z_grid = z0 + np.arange(Nz) * dz
                                
                            dose_matrix_work = np.flip(dose_matrix, axis=1)
                            y_grid = y0 + np.arange(Ny) * dy
                            x_grid = x0 + np.arange(Nx) * dx
                            
                            if len(z_grid) > 1 and z_grid[1] < z_grid[0]:
                                z_grid = z_grid[::-1]
                                dose_matrix_work = np.flip(dose_matrix_work, axis=0)
                                
                            if len(x_grid) > 1 and x_grid[1] < x_grid[0]:
                                x_grid = x_grid[::-1]
                                dose_matrix_work = np.flip(dose_matrix_work, axis=2)
                                
                            from scipy.interpolate import RegularGridInterpolator
                            interp = RegularGridInterpolator((z_grid, y_grid, x_grid), dose_matrix_work, bounds_error=False, fill_value=0.0)
                            
                            dose_Gy = float(interp([pt_z, pt_y, pt_x])[0])
                            dose_cGy = dose_Gy * 100.0
                            dose_str = f"{dose_cGy:.2f}"

                    d_item = QTableWidgetItem(dose_str)
                    d_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(row_idx, 8, d_item)
                finally:
                    table.blockSignals(False)
                    
                # Trigger display updates to refresh marker positions
                from fcn_display.brachy_tree import refresh_brachy_tree
                refresh_brachy_tree(self)
                from fcn_display.display_images import displayaxial, displaysagittal, displaycoronal
                displayaxial(self)
                displaysagittal(self)
                displaycoronal(self)

            def trigger_add_pt():
                if not hasattr(self, 'patientID_plan') or not self.patientID_plan:
                    return
                metadata = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']
                ref_points = metadata.get('Plan_Dose_References', [])
                new_num = len(ref_points) + 1
                new_pt = {
                    'DoseReferenceNumber': new_num,
                    'DoseReferenceStructureType': 'COORDINATE',
                    'DoseReferenceDescription': f'Point {new_num}',
                    'DoseReferenceDescription ': f'Point {new_num}',
                    'DoseReferenceType': 'POINT',
                    'TargetPrescriptionDose': 'N/A',
                    'TargedPrescritionDose': 'N/A',
                    'DoseReferencePointCoordinates': ['N/A', 'N/A', 'N/A'],
                    'Visible': True
                }
                ref_points.append(new_pt)
                populate_brachy_table(self, ref_points)
                if hasattr(self, 'selected_rtdose_ref') and self.selected_rtdose_ref is not None:
                    calculate_ref_points_dose(self, self.selected_rtdose_ref)
                from fcn_display.brachy_panel import update_brachy_table_header
                update_brachy_table_header(self)

            def trigger_delete_pt(row_idx):
                if not hasattr(self, 'patientID_plan') or not self.patientID_plan:
                    return
                metadata = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']
                ref_points = metadata.get('Plan_Dose_References', [])
                if row_idx < len(ref_points):
                    ref_points.pop(row_idx)
                    populate_brachy_table(self, ref_points)
                    if hasattr(self, 'selected_rtdose_ref') and self.selected_rtdose_ref is not None:
                        calculate_ref_points_dose(self, self.selected_rtdose_ref)
                    from fcn_display.brachy_panel import update_brachy_table_header
                    update_brachy_table_header(self)
                        
                    from fcn_display.display_images import displayaxial, displaysagittal, displaycoronal
                    displayaxial(self)
                    displaysagittal(self)
                    displaycoronal(self)
            
            for row, data_dict in enumerate(table_info):
                coords = data_dict.get('DoseReferencePointCoordinates', ['N/A', 'N/A', 'N/A'])
                if not isinstance(coords, list) or len(coords) < 3:
                    coords = ['N/A', 'N/A', 'N/A']
                
                row_values = [
                    data_dict.get('DoseReferenceNumber', 'N/A'),
                    data_dict.get('DoseReferenceStructureType', 'N/A'),
                    data_dict.get('DoseReferenceDescription', 'N/A'),
                    data_dict.get('DoseReferenceType', 'N/A'),
                    data_dict.get('TargetPrescriptionDose', 'N/A'),
                    *table_xyz(coords[0], coords[1], coords[2]),   # X, Y, Z as the views name them
                    'N/A'  # Dose (cGy) default
                ]
                
                for col, val in enumerate(row_values):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.brachy_table_01.setItem(row, col, item)

                # Add checkbox in the last column as an always-visible QCheckBox widget centered in the cell
                checkbox = QCheckBox()
                checkbox.setChecked(data_dict.get('Visible', True))
                layout = QHBoxLayout()
                layout.addWidget(checkbox)
                layout.setAlignment(Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                container = QWidget()
                container.setLayout(layout)
                self.brachy_table_01.setCellWidget(row, 9, container)

                # Add QPushButton widgets for Go To and Get Slice actions
                btn_goto = QPushButton("Go")
                btn_goto.clicked.connect(lambda _, r=row: trigger_go_to_pt(r))
                # colours from the button's role (fcn_create_gui/button_style.py)
                btn_goto.setStyleSheet("QPushButton { margin: 1px; padding: 2px; border-radius: 3px; font-weight: bold; }")
                self.brachy_table_01.setCellWidget(row, 10, btn_goto)

                btn_get = QPushButton("Get Plane")
                btn_get.clicked.connect(lambda _, r=row: trigger_get_slice_pt(r))
                btn_get.setStyleSheet("QPushButton { margin: 1px; padding: 2px; border-radius: 3px; font-weight: bold; }")
                self.brachy_table_01.setCellWidget(row, 11, btn_get)

                # Add Delete button in column index 12
                btn_delete = QPushButton("Delete")
                btn_delete.setStyleSheet("QPushButton { margin: 1px; padding: 2px; border-radius: 3px; font-weight: bold; }")
                btn_delete.clicked.connect(lambda _, r=row: trigger_delete_pt(r))
                self.brachy_table_01.setCellWidget(row, 12, btn_delete)

                # Connect state change to persist visibility selection and update VTK overlays
                def make_toggle_handler(pt_dict):
                    def handler(state):
                        pt_dict['Visible'] = (state == 2 or state == True) # Qt.Checked is 2
                        from fcn_display.brachy_tree import refresh_brachy_tree
                        refresh_brachy_tree(self)

                        # Refresh overlays on all slice views
                        from fcn_display.display_images import displayaxial, displaysagittal, displaycoronal
                        displayaxial(self)
                        displaysagittal(self)
                        displaycoronal(self)
                    return handler

                checkbox.stateChanged.connect(make_toggle_handler(data_dict))

            # Set empty items for columns 0 to 11 in the last row to look clean
            for col in range(12):
                item = QTableWidgetItem("")
                item.setFlags(Qt.NoItemFlags)
                self.brachy_table_01.setItem(num_rows, col, item)

            # ADD button in the last row, last column:
            btn_add = QPushButton("ADD")
            btn_add.setStyleSheet("QPushButton { margin: 1px; padding: 2px; border-radius: 3px; font-weight: bold; }")
            btn_add.clicked.connect(lambda: trigger_add_pt())
            self.brachy_table_01.setCellWidget(num_rows, 12, btn_add)
        else:
            num_rows = table_info.shape[0] if table_info is not None else 0
            num_columns = table_info.shape[1] if table_info is not None else 0

            self.brachy_table_01.setRowCount(num_rows)
            self.brachy_table_01.setColumnCount(num_columns)

            selected_dw_ch = self.brachy_combobox_01.currentText()
            if num_columns:
                # X, Y, Z (and Ux, Uy, Uz) in the user's axes; the plan data stay DICOM
                table_info = table_array(selected_dw_ch, table_info)
            for row in range(num_rows):
                for col in range(num_columns):
                    val = table_info[row, col]
                    if selected_dw_ch == "Dwells":
                        try:
                            if col in (3, 4, 5):
                                val = f"{float(val):.2f}"
                            elif col in (6, 7, 8):
                                val = f"{float(val):.4f}"
                        except ValueError:
                            pass
                    elif selected_dw_ch == "Channels":
                        try:
                            val = f"{float(val):.2f}"
                        except ValueError:
                            pass
                            
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.brachy_table_01.setItem(row, col, item)
            # "Go" buttons (slices through the point) in the View > PLAN > Brachy table
            from fcn_display.brachy_panel import add_brachy_goto_column
            add_brachy_goto_column(self)

        self.brachy_table_01.resizeColumnsToContents()
    finally:
        self.brachy_table_01.blockSignals(False)

def apply_alternating_row_colors(self):
    """
    Applies alternating blue and light blue colors to the table rows.
    """
    blue_color = QColor(0, 70, 184)
    light_blue_color = QColor(0, 104, 184)

    num_rows = self.brachy_table_01.rowCount()

    for row in range(num_rows):
        # Choose color based on even or odd row
        if row % 2 == 0:
            color = blue_color
        else:
            color = light_blue_color

        for col in range(self.brachy_table_01.columnCount()):
            item = self.brachy_table_01.item(row, col)
            if item:
                item.setBackground(color)



def export_all_brachy_channels_to_csv(self):
    # Check if plan is loaded
    required_attrs = ['patientID_plan', 'studyID_plan', 'modality_plan', 'series_index_plan']
    if not all(hasattr(self, attr) for attr in required_attrs):
        QMessageBox.warning(self, "Warning", "No plan loaded.")
        return

    try:
        channels = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']['Plan_Brachy_Channels']
    except (KeyError, IndexError):
        QMessageBox.warning(self, "Warning", "Plan data is missing or corrupted.")
        return

    # Ask user where to save the file
    file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
    if not file_path:
        return  # User cancelled

    try:
        with open(file_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)

            # --- Write DwellInfo block ---
            writer.writerow(["=== Dwell Positions per Channel ==="])
            writer.writerow([
                "ChannelNumber", "DwellIndex", "RelativePosition", "TimeWeight",
                "X", "Y", "Z", "OrientationX", "OrientationY", "OrientationZ"
            ])

            for ch in channels:
                channel_num = ch.get('ChannelNumber', 'N/A')
                dwell_info = ch.get('DwellInfo', None)

                if dwell_info is not None and dwell_info.shape[0] > 0:
                    for row in dwell_info:
                        writer.writerow([channel_num] + row.tolist())

            writer.writerow([])  # Empty row for separation

            # --- Write ChPos block ---
            writer.writerow(["=== Channel Geometry (ChPos) ==="])
            writer.writerow(["ChannelNumber", "X", "Y", "Z"])

            for ch in channels:
                channel_num = ch.get('ChannelNumber', 'N/A')
                ch_pos = ch.get('ChPos', None)

                if ch_pos is not None and ch_pos.shape[0] > 0:
                    for point in ch_pos:
                        writer.writerow([channel_num] + point.tolist())

        QMessageBox.information(self, "Export Complete", f"Data exported successfully to:\n{file_path}")
    except Exception as e:
        QMessageBox.critical(self, "Export Error", f"An error occurred:\n{str(e)}")


def calculate_ref_points_dose(self, rtdose_series):
    """
    Calculates the dose at each reference point in the table line-by-line using
    tri-linear interpolation on the RTDOSE matrix.
    """
    try:
        dose_matrix = rtdose_series.get('3DMatrix')
        meta = rtdose_series.get('metadata', {})
        if dose_matrix is None or not isinstance(dose_matrix, np.ndarray):
            return
        
        origin = meta.get('ImagePositionPatient', [0.0, 0.0, 0.0])
        x0, y0, z0 = origin[0], origin[1], origin[2]
        
        spacing = meta.get('PixelSpacing', [1.0, 1.0])
        dx, dy = spacing[0], spacing[1]
        dz = meta.get('SliceThickness', 1.0)
        
        Nz, Ny, Nx = dose_matrix.shape
        
        # Check GridFrameOffsetVector from DCM_Info
        dicom_file = meta.get('DCM_Info')
        grid_offset = getattr(dicom_file, 'GridFrameOffsetVector', None)
        if grid_offset is not None:
            z_grid = np.array([z0 + float(offset) for offset in grid_offset])
        else:
            z_grid = z0 + np.arange(Nz) * dz
            
        # Since dose_matrix in load_dcm.py was Y-flipped, flip it back to have Y-coordinates increasing:
        dose_matrix_work = np.flip(dose_matrix, axis=1)
        y_grid = y0 + np.arange(Ny) * dy
        x_grid = x0 + np.arange(Nx) * dx
        
        # Ensure z_grid is increasing
        if len(z_grid) > 1 and z_grid[1] < z_grid[0]:
            z_grid = z_grid[::-1]
            dose_matrix_work = np.flip(dose_matrix_work, axis=0)
            
        # Ensure x_grid is increasing
        if len(x_grid) > 1 and x_grid[1] < x_grid[0]:
            x_grid = x_grid[::-1]
            dose_matrix_work = np.flip(dose_matrix_work, axis=2)
            
        from scipy.interpolate import RegularGridInterpolator
        interp = RegularGridInterpolator((z_grid, y_grid, x_grid), dose_matrix_work, bounds_error=False, fill_value=0.0)
        
        # Loop over only actual reference point rows (excluding the last ADD button row if present)
        metadata = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']
        ref_points = metadata.get('Plan_Dose_References', [])
        num_rows = len(ref_points)
        for row in range(num_rows):
            # Coordinates are in columns 5, 6, 7 (X, Y, Z)
            item_x = self.brachy_table_01.item(row, 5)
            item_y = self.brachy_table_01.item(row, 6)
            item_z = self.brachy_table_01.item(row, 7)
            
            if item_x and item_y and item_z:
                val_x = item_x.text()
                val_y = item_y.text()
                val_z = item_z.text()
                
                if val_x != 'N/A' and val_y != 'N/A' and val_z != 'N/A':
                    try:
                        # table X, Y, Z (the user's axes) -> DICOM
                        x_phys, y_phys, z_phys = dicom_xyz(float(val_x), float(val_y), float(val_z))
                        
                        # Interpolate dose (Gy) and convert to cGy
                        dose_Gy = float(interp([z_phys, y_phys, x_phys])[0])
                        dose_cGy = dose_Gy * 100.0
                        
                        dose_str = f"{dose_cGy:.2f}"
                        
                        # Update brachy_table_01
                        d_item1 = QTableWidgetItem(dose_str)
                        d_item1.setTextAlignment(Qt.AlignCenter)
                        self.brachy_table_01.setItem(row, 8, d_item1)
                    except Exception as e:
                        print(f"Error calculating dose at row {row}: {e}")
    except Exception as e:
        print(f"Error setting up dose calculation: {e}")


def on_brachy_table_item_changed(self, table, item):
    """
    Called when a cell in brachy_table_01 is modified.
    If the modified cell is one of the coordinates (X, Y, Z at cols 5, 6, 7)
    during 'Ref. Points' mode, it adjusts the active metadata coordinate value
    and triggers a recalculation of the dose point at index 8.
    """
    if not hasattr(self, 'patientID_plan') or not self.patientID_plan:
        return
        
    selected_dw_ch = self.brachy_combobox_01.currentText()
    if selected_dw_ch != "Ref. Points":
        return
        
    row = item.row()
    col = item.column()
    
    # Description (col 2): the name of the reference point, as in the catheter list
    if col == 2:
        from fcn_display.brachy_tree import rename_ref_point
        rename_ref_point(self, row, item.text())
        return

    # We only care about X, Y, Z coordinates (cols 5, 6, 7)
    if col not in (5, 6, 7):
        return
        
    # Get metadata
    metadata = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']
    ref_points = metadata.get('Plan_Dose_References', [])
    if row >= len(ref_points):
        return
        
    # Temporarily block signals to prevent recursive update loops
    table.blockSignals(True)
    try:
        # Extract the X, Y, Z values from columns 5, 6, 7
        item_x = table.item(row, 5)
        item_y = table.item(row, 6)
        item_z = table.item(row, 7)
        
        if item_x and item_y and item_z:
            val_x = item_x.text().strip()
            val_y = item_y.text().strip()
            val_z = item_z.text().strip()
            
            if val_x != 'N/A' and val_y != 'N/A' and val_z != 'N/A' and val_x != '' and val_y != '' and val_z != '':
                try:
                    # table X, Y, Z (the user's axes) -> physical (DICOM) x, y, z
                    x, y, z = dicom_xyz(float(val_x), float(val_y), float(val_z))
                    
                    # Update coordinates in metadata
                    ref_points[row]['DoseReferencePointCoordinates'] = [x, y, z]
                    
                    # Recalculate dose if active RTDOSE exists
                    dose_str = 'N/A'
                    if hasattr(self, 'selected_rtdose_ref') and self.selected_rtdose_ref is not None:
                        dose_matrix = self.selected_rtdose_ref.get('3DMatrix')
                        meta = self.selected_rtdose_ref.get('metadata', {})
                        if dose_matrix is not None and isinstance(dose_matrix, np.ndarray):
                            origin = meta.get('ImagePositionPatient', [0.0, 0.0, 0.0])
                            x0, y0, z0 = origin[0], origin[1], origin[2]
                            
                            spacing = meta.get('PixelSpacing', [1.0, 1.0])
                            dx, dy = spacing[0], spacing[1]
                            dz = meta.get('SliceThickness', 1.0)
                            
                            Nz, Ny, Nx = dose_matrix.shape
                            
                            dicom_file = meta.get('DCM_Info')
                            grid_offset = getattr(dicom_file, 'GridFrameOffsetVector', None)
                            if grid_offset is not None:
                                z_grid = np.array([z0 + float(offset) for offset in grid_offset])
                            else:
                                z_grid = z0 + np.arange(Nz) * dz
                                
                            dose_matrix_work = np.flip(dose_matrix, axis=1)
                            y_grid = y0 + np.arange(Ny) * dy
                            x_grid = x0 + np.arange(Nx) * dx
                            
                            if len(z_grid) > 1 and z_grid[1] < z_grid[0]:
                                z_grid = z_grid[::-1]
                                dose_matrix_work = np.flip(dose_matrix_work, axis=0)
                                
                            if len(x_grid) > 1 and x_grid[1] < x_grid[0]:
                                x_grid = x_grid[::-1]
                                dose_matrix_work = np.flip(dose_matrix_work, axis=2)
                                
                            from scipy.interpolate import RegularGridInterpolator
                            interp = RegularGridInterpolator((z_grid, y_grid, x_grid), dose_matrix_work, bounds_error=False, fill_value=0.0)
                            
                            dose_Gy = float(interp([z, y, x])[0])
                            dose_cGy = dose_Gy * 100.0
                            dose_str = f"{dose_cGy:.2f}"
                            
                    # Update column 8 (Dose (cGy))
                    d_item1 = QTableWidgetItem(dose_str)
                    d_item1.setTextAlignment(Qt.AlignCenter)
                    table.setItem(row, 8, d_item1)

                    # Update VTK marker positions on image views
                    from fcn_display.brachy_tree import refresh_brachy_tree
                    refresh_brachy_tree(self)
                    from fcn_display.display_images import displayaxial, displaysagittal, displaycoronal
                    displayaxial(self)
                    displaysagittal(self)
                    displaycoronal(self)
                    
                except ValueError as e:
                    print(f"Non-numeric coordinates: {e}")
                except Exception as e:
                    print(f"Error on coordinate recalculation: {e}")
    finally:
        table.blockSignals(False)