import numpy as np
import csv
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox, QInputDialog
from PySide6.QtGui import QColor
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QTableWidget, QVBoxLayout, QPushButton, QSpinBox, QLabel, QMessageBox,
    QCheckBox, QHBoxLayout
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import pandas as pd



def update_plan_tables(self):
    if 'Plan_Brachy_Channels' in self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']:
        N_channels = len(self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']['Plan_Brachy_Channels'])
        #
        self.brachy_N_channels.setText(f"{N_channels:.0f}")
        #
        # set spinbo min value
        self.brachy_spinBox_01.setMinimum(1)
        self.brachy_spinBox_02.setMinimum(1)
        # Set the maximum value
        self.brachy_spinBox_01.setMaximum(N_channels)
        self.brachy_spinBox_02.setMaximum(N_channels)
        # Set the current value
        self.brachy_spinBox_01.setValue(1)
        self.brachy_spinBox_02.setValue(1)
        #
        update_disp_brachy_plan(self)


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
                'Visible': False
            }]
            metadata['Plan_Dose_References'] = ref_points
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

    # Display air kerma strength
    AirKerma = metadata.get('ReferenceAirKermaRate')
    if AirKerma is not None:
        val = getattr(AirKerma, 'value', AirKerma)
        self.brachy_plan_Ac.setText(str(val))
    else:
        self.brachy_plan_Ac.setText("N/A")

    apply_alternating_row_colors(self)

    if selected_dw_ch != "Ref. Points":
        plot_brachy_dwell_channels(self)
        calculate_total_time(self)
    else:
        self.brachy_total_time.setText("N/A")
        self.brachy_ch_time.setText("N/A")

    from fcn_display.display_images import displayaxial, displaysagittal, displaycoronal
    displayaxial(self)
    displaysagittal(self)
    displaycoronal(self)
    

def calculate_total_time(self):
    """
    Calculates the total time across all channels by summing the "Time (s)" column
    of each channel's DwellInfo matrix. Additionally, calculates the total time for the
    specific channel indicated by the spinbox (self.brachy_spinBox_02).
    
    :return: None
    """
    channels = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']['Plan_Brachy_Channels']
    
    total_time = 0.0  # Initialize total time across all channels
    selected_channel_time = 0.0  # Initialize total time for the selected channel
    
    selected_channel_idx = self.brachy_spinBox_02.value() - 1  # Adjust for zero-based indexing
    
    for idx, channel in enumerate(channels):
        dwell_info = channel.get('DwellInfo')
        
        if dwell_info is None:
            print(f"Channel {idx + 1}: 'DwellInfo' is None. Skipping.")
            continue
        
        if not isinstance(dwell_info, np.ndarray):
            print(f"Channel {idx + 1}: 'DwellInfo' is not a NumPy array. Skipping.")
            continue
        
        if dwell_info.ndim != 2 or dwell_info.shape[1] < 3:
            print(f"Channel {idx + 1}: 'DwellInfo' does not have at least 3 columns. Skipping.")
            continue
        
        # Extract the "Time (s)" column (index 2)
        time_column = dwell_info[:, 2]
        
        # Handle NaN values by treating them as 0
        time_column = np.nan_to_num(time_column, nan=0.0)
        
        # Sum the "Time (s)" values for this channel
        channel_total = np.sum(time_column)
        total_time += channel_total
        
        # If this is the selected channel, save its total time
        if idx == selected_channel_idx:
            selected_channel_time = channel_total
    
    # Display the total time across all channels
    self.brachy_total_time.setText(f"{total_time:.4f} s")
    
    # Display the total time for the selected channel
    self.brachy_ch_time.setText(f"{selected_channel_time:.4f} s")
    

    
def clear_brachy_table(self):
    """
    Clears all existing rows and columns from the brachy_table_01.
    """
    self.brachy_table_01.blockSignals(True)
    self.brachy_table_02.blockSignals(True)
    try:
        self.brachy_table_01.clear()           # Clears the table content but retains headers
        self.brachy_table_01.setRowCount(0)    # Removes all rows
        self.brachy_table_01.setColumnCount(0) # Removes all columns
        #
        self.brachy_table_02.clear()   # Clears the table content but retains headers
        self.brachy_table_02.setRowCount(0)    # Removes all rows
        self.brachy_table_02.setColumnCount(0) # Removes all columns
    finally:
        self.brachy_table_01.blockSignals(False)
        self.brachy_table_02.blockSignals(False)
    
def setup_brachy_table_headers(self):
    """
    Sets up the column headers for brachy_table_01.
    """
    selected_dw_ch = self.brachy_combobox_01.currentText()
    if selected_dw_ch == "Dwells": 
        headers = ["IDX", "Rel. Pos (mm)", "Time (s)", "X (mm)", "Y (mm)", "Z(mm)", "Ux", "Uy", "Uz"]
    elif selected_dw_ch == "Channels":
        headers = ["X (mm)", "Y (mm)", "Z(mm)"]
    elif selected_dw_ch == "Ref. Points":
        headers = ["Ref. Num", "Structure Type", "Description", "Type", "Target Dose", "X (mm)", "Y (mm)", "Z (mm)", "Dose (cGy)", "Visible", "Go to Pt", "Get Slice Pt", "Delete"]
    else:
        headers = ["X (mm)", "Y (mm)", "Z(mm)"]
    
    self.brachy_table_01.setColumnCount(len(headers))
    self.brachy_table_01.setHorizontalHeaderLabels(headers)
    
    # Optional: Adjust column widths to fit content
    self.brachy_table_01.resizeColumnsToContents()
    #
    self.brachy_table_02.setColumnCount(len(headers))
    self.brachy_table_02.setHorizontalHeaderLabels(headers)
    
    # Optional: Adjust column widths to fit content
    self.brachy_table_02.resizeColumnsToContents()


    
def populate_brachy_table(self, table_info):
    """
    Populates brachy_table_01 with data from table_info.

    :param table_info: NumPy array with shape (n, 9) or list of dicts
    """
    
    self.brachy_table_01.blockSignals(True)
    self.brachy_table_02.blockSignals(True)
    try:
        if isinstance(table_info, list):
            num_rows = len(table_info)
            num_columns = 13  # Ref. Num, Structure Type, Description, Type, Target Dose, X, Y, Z, Dose (cGy), Visible, Go To, Get Plane, Delete/ADD
            
            # Set row count to num_rows + 1 for the extra "ADD" button row
            self.brachy_table_01.setRowCount(num_rows + 1)
            self.brachy_table_01.setColumnCount(num_columns)
            self.brachy_table_02.setRowCount(num_rows + 1)
            self.brachy_table_02.setColumnCount(num_columns)

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
                coronal_space_z = (self.display_data[idx].shape[1] * self.pixel_spac[idx, 0]) - (pt_y - self.Im_PatPosition[idx, 1])
                coronal_index = int(round(coronal_space_z / self.pixel_spac[idx, 1]))
                coronal_index = max(0, min(coronal_index, self.display_data[idx].shape[1] - 1))
                self.current_coronal_slice_index[idx] = coronal_index
                
                # Sagittal slice index calculation:
                sagittal_space_z = pt_x - self.Im_PatPosition[idx, 0]
                sagittal_index = int(round(sagittal_space_z / self.pixel_spac[idx, 0]))
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
                pt_z = axial_index * self.slice_thick[idx] + self.Im_Offset[idx, 2] + self.Im_PatPosition[idx, 2]
                pt_x = sagittal_index * self.pixel_spac[idx, 0] + self.Im_PatPosition[idx, 0]
                pt_y = (self.display_data[idx].shape[1] * self.pixel_spac[idx, 0]) - (coronal_index * self.pixel_spac[idx, 1]) + self.Im_PatPosition[idx, 1]
                
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
                self.brachy_table_01.blockSignals(True)
                self.brachy_table_02.blockSignals(True)
                try:
                    for table in (self.brachy_table_01, self.brachy_table_02):
                        item_x = QTableWidgetItem(str(pt_x))
                        item_x.setTextAlignment(Qt.AlignCenter)
                        table.setItem(row_idx, 5, item_x)
                        
                        item_y = QTableWidgetItem(str(pt_z))
                        item_y.setTextAlignment(Qt.AlignCenter)
                        table.setItem(row_idx, 6, item_y)
                        
                        item_z = QTableWidgetItem(str(pt_y))
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
                            
                    for table in (self.brachy_table_01, self.brachy_table_02):
                        d_item = QTableWidgetItem(dose_str)
                        d_item.setTextAlignment(Qt.AlignCenter)
                        table.setItem(row_idx, 8, d_item)
                finally:
                    self.brachy_table_01.blockSignals(False)
                    self.brachy_table_02.blockSignals(False)
                    
                # Trigger display updates to refresh marker positions
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
                    'Visible': False
                }
                ref_points.append(new_pt)
                populate_brachy_table(self, ref_points)
                if hasattr(self, 'selected_rtdose_ref') and self.selected_rtdose_ref is not None:
                    calculate_ref_points_dose(self, self.selected_rtdose_ref)

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
                    coords[0],
                    coords[2],
                    coords[1],
                    'N/A'  # Dose (cGy) default
                ]
                
                for col, val in enumerate(row_values):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.brachy_table_01.setItem(row, col, item)
                    
                    item2 = QTableWidgetItem(str(val))
                    item2.setTextAlignment(Qt.AlignCenter)
                    self.brachy_table_02.setItem(row, col, item2)

                # Add checkbox in the last column as an always-visible QCheckBox widget centered in the cell
                checkbox1 = QCheckBox()
                checkbox1.setChecked(data_dict.get('Visible', False))
                layout1 = QHBoxLayout()
                layout1.addWidget(checkbox1)
                layout1.setAlignment(Qt.AlignCenter)
                layout1.setContentsMargins(0, 0, 0, 0)
                container1 = QWidget()
                container1.setLayout(layout1)
                self.brachy_table_01.setCellWidget(row, 9, container1)
                
                checkbox2 = QCheckBox()
                checkbox2.setChecked(data_dict.get('Visible', False))
                layout2 = QHBoxLayout()
                layout2.addWidget(checkbox2)
                layout2.setAlignment(Qt.AlignCenter)
                layout2.setContentsMargins(0, 0, 0, 0)
                container2 = QWidget()
                container2.setLayout(layout2)
                self.brachy_table_02.setCellWidget(row, 9, container2)

                # Add QPushButton widgets for Go To and Get Slice actions
                # Table 1:
                btn_goto1 = QPushButton("Go")
                btn_goto1.clicked.connect(lambda _, r=row: trigger_go_to_pt(r))
                btn_goto1.setStyleSheet("QPushButton { background-color: #1c5fa8; color: white; border: 1px solid #104277; margin: 1px; padding: 2px; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #2475cf; }")
                self.brachy_table_01.setCellWidget(row, 10, btn_goto1)

                btn_get1 = QPushButton("Get Plane")
                btn_get1.clicked.connect(lambda _, r=row: trigger_get_slice_pt(r))
                btn_get1.setStyleSheet("QPushButton { background-color: #a82e2e; color: white; border: 1px solid #751e1e; margin: 1px; padding: 2px; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #cf3c3c; }")
                self.brachy_table_01.setCellWidget(row, 11, btn_get1)

                # Table 2:
                btn_goto2 = QPushButton("Go")
                btn_goto2.clicked.connect(lambda _, r=row: trigger_go_to_pt(r))
                btn_goto2.setStyleSheet("QPushButton { background-color: #1c5fa8; color: white; border: 1px solid #104277; margin: 1px; padding: 2px; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #2475cf; }")
                self.brachy_table_02.setCellWidget(row, 10, btn_goto2)

                btn_get2 = QPushButton("Get Plane")
                btn_get2.clicked.connect(lambda _, r=row: trigger_get_slice_pt(r))
                btn_get2.setStyleSheet("QPushButton { background-color: #a82e2e; color: white; border: 1px solid #751e1e; margin: 1px; padding: 2px; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #cf3c3c; }")
                self.brachy_table_02.setCellWidget(row, 11, btn_get2)

                # Add Delete button in column index 12
                btn_delete1 = QPushButton("Delete")
                btn_delete1.setStyleSheet("QPushButton { background-color: black; color: red; border: 1px solid red; margin: 1px; padding: 2px; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #330000; }")
                btn_delete1.clicked.connect(lambda _, r=row: trigger_delete_pt(r))
                self.brachy_table_01.setCellWidget(row, 12, btn_delete1)

                btn_delete2 = QPushButton("Delete")
                btn_delete2.setStyleSheet("QPushButton { background-color: black; color: red; border: 1px solid red; margin: 1px; padding: 2px; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #330000; }")
                btn_delete2.clicked.connect(lambda _, r=row: trigger_delete_pt(r))
                self.brachy_table_02.setCellWidget(row, 12, btn_delete2)

                # Connect state change to persist visibility selection and update VTK overlays
                def make_toggle_handler(cb1, cb2, pt_dict):
                    def handler(state):
                        is_checked = (state == 2 or state == True) # Qt.Checked is 2
                        pt_dict['Visible'] = is_checked
                        
                        # Sync check state
                        cb1.blockSignals(True)
                        cb1.setChecked(is_checked)
                        cb1.blockSignals(False)
                        
                        cb2.blockSignals(True)
                        cb2.setChecked(is_checked)
                        cb2.blockSignals(False)
                        
                        # Refresh overlays on all slice views
                        from fcn_display.display_images import displayaxial, displaysagittal, displaycoronal
                        displayaxial(self)
                        displaysagittal(self)
                        displaycoronal(self)
                    return handler
                
                checkbox1.stateChanged.connect(make_toggle_handler(checkbox1, checkbox2, data_dict))
                checkbox2.stateChanged.connect(make_toggle_handler(checkbox1, checkbox2, data_dict))

            # Set empty items for columns 0 to 11 in the last row to look clean
            for col in range(12):
                item1 = QTableWidgetItem("")
                item1.setFlags(Qt.NoItemFlags)
                self.brachy_table_01.setItem(num_rows, col, item1)
                
                item2 = QTableWidgetItem("")
                item2.setFlags(Qt.NoItemFlags)
                self.brachy_table_02.setItem(num_rows, col, item2)
                
            # Table 1 ADD button in the last row, last column:
            btn_add1 = QPushButton("ADD")
            btn_add1.setStyleSheet("QPushButton { background-color: #28a745; color: white; border: 1px solid #1e7e34; margin: 1px; padding: 2px; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #218838; }")
            btn_add1.clicked.connect(lambda: trigger_add_pt())
            self.brachy_table_01.setCellWidget(num_rows, 12, btn_add1)
            
            # Table 2 ADD button in the last row, last column:
            btn_add2 = QPushButton("ADD")
            btn_add2.setStyleSheet("QPushButton { background-color: #28a745; color: white; border: 1px solid #1e7e34; margin: 1px; padding: 2px; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #218838; }")
            btn_add2.clicked.connect(lambda: trigger_add_pt())
            self.brachy_table_02.setCellWidget(num_rows, 12, btn_add2)
        else:
            num_rows = table_info.shape[0] if table_info is not None else 0
            num_columns = table_info.shape[1] if table_info is not None else 0
            
            self.brachy_table_01.setRowCount(num_rows)
            self.brachy_table_01.setColumnCount(num_columns)
            self.brachy_table_02.setRowCount(num_rows)
            self.brachy_table_02.setColumnCount(num_columns)
            
            selected_dw_ch = self.brachy_combobox_01.currentText()
            for row in range(num_rows):
                for col in range(num_columns):
                    val = table_info[row, col]
                    if selected_dw_ch == "Dwells":
                        if col == 4:
                            val = table_info[row, 5]
                        elif col == 5:
                            val = table_info[row, 4]
                        
                        try:
                            if col in (3, 4, 5):
                                val = f"{float(val):.2f}"
                            elif col in (6, 7, 8):
                                val = f"{float(val):.4f}"
                        except ValueError:
                            pass
                    elif selected_dw_ch == "Channels":
                        if col == 1:
                            val = table_info[row, 2]
                        elif col == 2:
                            val = table_info[row, 1]
                            
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.brachy_table_01.setItem(row, col, item)
                    
                    item2 = QTableWidgetItem(str(val))
                    item2.setTextAlignment(Qt.AlignCenter)
                    self.brachy_table_02.setItem(row, col, item2)

        self.brachy_table_01.resizeColumnsToContents()
        self.brachy_table_02.resizeColumnsToContents()
    finally:
        self.brachy_table_01.blockSignals(False)
        self.brachy_table_02.blockSignals(False)

def apply_alternating_row_colors(self):
    """
    Applies alternating blue and light blue colors to the table rows.
    """
    blue_color = QColor(0, 70, 184)           
    light_blue_color = QColor(0, 104, 184) 
    
    num_rows = self.brachy_table_01.rowCount()
    num_rows = self.brachy_table_02.rowCount()
    
    for row in range(num_rows):
        # Choose color based on even or odd row
        if row % 2 == 0:
            color = blue_color
        else:
            color = light_blue_color
        
        for col in range(self.brachy_table_01.columnCount()):
            item  = self.brachy_table_01.item(row, col)
            item2 = self.brachy_table_02.item(row, col)
            if item:
                item.setBackground(color)
                item2.setBackground(color)








def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be a matplotlib color string, hex string, or RGB tuple.
    """
    try:
        c = mcolors.cnames[color]
    except:
        c = color
    c = mcolors.to_rgb(c)
    return mcolors.to_hex([min(1, c[i] + amount * (1 - c[i])) for i in range(3)])

def darken_color(color, amount=0.3):
    """
    Darkens the given color by multiplying its RGB values by the given amount.
    Input can be a matplotlib color string, hex string, or RGB tuple.
    """
    try:
        c = mcolors.cnames[color]
    except:
        c = color
    c = mcolors.to_rgb(c)
    return mcolors.to_hex([max(0, c[i] * (1 - amount)) for i in range(3)])

def plot_brachy_dwell_channels(self):
    plot_brachy_3D_dwell_channels(self)
    plot_brachy_bar_channels(self)
    
def plot_brachy_3D_dwell_channels(self):
    # Retrieve user-selected settings
    font_size = self.selected_font_size
    background_color = self.selected_background
    
    # Get the point color, line color, and special first point color from the combo boxes
    point_color = self.brachy_dw_sel_col.currentText()
    line_color = self.brachy_lin_sel_col.currentText()
    first_point_color = self.brachy_p1_sel_col.currentText()

    # Adjust the colors (lighten and darken)
    lighter_green = lighten_color("green", 0.4)  # Example: make green lighter
    point_color = lighter_green if point_color == "Green" else point_color

    # Get the point size, line width, and first point size from the spin boxes
    point_size = self.brachy_dw_size.value()  # Assuming it's an int spinbox
    line_width = self.brachy_ch_line_width.value()  # Assuming it's a double spinbox
    first_point_size = self.brachy_ch_size.value()  # Assuming it's a double spinbox
    
    # Determine text and label colors based on the background color
    if background_color.lower() == 'transparent':
        text_color = 'white'
        bg = 'transparent'
    elif background_color.lower() == 'white':
        text_color = 'black'
        bg = 'white'
    else:
        text_color = 'black'
        bg = background_color
    
    # Initialize the Matplotlib Figure if it doesn't exist
    if not hasattr(self, 'plot_Brachy_3D_ch_dw_fig'):
        self.plot_Brachy_3D_ch_dw_fig = Figure()
        self.plot_canvas = FigureCanvas(self.plot_Brachy_3D_ch_dw_fig)
        self.plot_toolbar = NavigationToolbar(self.plot_canvas, self)
        container = self.brachy_ax_02
        
        if container.layout() is None:
            layout = QVBoxLayout(container)
            container.setLayout(layout)
        else:
            while container.layout().count():
                child = container.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        container.layout().addWidget(self.plot_toolbar)
        container.layout().addWidget(self.plot_canvas)
    else:
        self.plot_Brachy_3D_ch_dw_fig.clf()
    
    ax = self.plot_Brachy_3D_ch_dw_fig.add_subplot(111, projection='3d')
    
    if bg.lower() == 'transparent':
        ax.set_facecolor((0, 0, 0, 0))
        self.plot_Brachy_3D_ch_dw_fig.patch.set_alpha(0.0)
    else:
        ax.set_facecolor(bg)
        self.plot_Brachy_3D_ch_dw_fig.patch.set_facecolor(bg)
    
    ax.tick_params(colors=text_color, labelsize=font_size)
    ax.set_xlabel("X (mm)", fontsize=font_size, color=text_color)
    ax.set_ylabel("Y (mm)", fontsize=font_size, color=text_color)
    ax.set_zlabel("Z (mm)", fontsize=font_size, color=text_color)
    
    # Retrieve channels from medical_image
    channels = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']['Plan_Brachy_Channels']
    
    # Determine whether to plot all channels or just the selected one
    if self.checkBox_dw_ch_plot.isChecked():
        # Show all channels
        channel_indices = range(len(channels))
    else:
        # Show only the selected channel from the spinbox
        selected_channel = self.brachy_spinBox_02.value() - 1  # Adjust for zero-based indexing
        if 0 <= selected_channel < len(channels):
            channel_indices = [selected_channel]
        else:
            # print(f"Selected channel {selected_channel + 1} is out of range.")
            return

    # Iterate through the selected channels to plot their points
    for idx in channel_indices:
        channel = channels[idx]
        dwell_info = channel.get('DwellInfo')
        chpos_info = channel.get('ChPos')
        
        if dwell_info is None or not isinstance(dwell_info, np.ndarray) or dwell_info.ndim != 2 or dwell_info.shape[1] < 7:
            continue

        # Filter dwell points based on dwell time > 0 if self.checkBox_show_dw_plot is selected
        if self.checkBox_show_dw_plot.isChecked():
            valid_dwell_indices = dwell_info[:, 2] > 0    #  column 2 is the "Time (s)" column
            dwell_info = dwell_info[valid_dwell_indices]  # Filter rows where time > 0

        # Ensure there's valid data after filtering
        if dwell_info.shape[0] == 0:
            continue

        # Extract the X, Y, Z coordinates (columns 3, 4, 5)
        x, y, z = dwell_info[:, 3], dwell_info[:, 4], dwell_info[:, 5]
        x, y, z = np.nan_to_num(x, nan=0.0), np.nan_to_num(y, nan=0.0), np.nan_to_num(z, nan=0.0)
        
        # Plot all valid points
        ax.scatter(x, y, z, c=point_color, marker='o', s=point_size, alpha=0.6, edgecolors=darken_color(point_color, 0.2))
        
        # Plot the line representing the channel's position if checkbox is selected
        if self.checkBox_show_ch_plot.isChecked() and chpos_info is not None and isinstance(chpos_info, np.ndarray) and chpos_info.ndim == 2 and chpos_info.shape[1] >= 3:
            ch_x, ch_y, ch_z = chpos_info[:, 0], chpos_info[:, 1], chpos_info[:, 2]
            ch_x, ch_y, ch_z = np.nan_to_num(ch_x, nan=0.0), np.nan_to_num(ch_y, nan=0.0), np.nan_to_num(ch_z, nan=0.0)
            
            ax.plot(ch_x, ch_y, ch_z, color=line_color, linewidth=line_width, label=f'Channel {idx + 1} Position')

    # After all points are plotted, plot the first point of each channel with the special color
    for idx in channel_indices:
        channel = channels[idx]
        dwell_info = channel.get('DwellInfo')
        
        if dwell_info is None or not isinstance(dwell_info, np.ndarray) or dwell_info.ndim != 2 or dwell_info.shape[1] < 7:
            continue

        # Filter first point if it has dwell time > 0, when self.checkBox_show_dw_plot is selected
        if self.checkBox_show_dw_plot.isChecked() and dwell_info[0, 2] <= 0:  # Assuming dwell time in column 2
            continue

        x, y, z = dwell_info[0, 3], dwell_info[0, 4], dwell_info[0, 5]
        ax.scatter(x, y, z, c=first_point_color, marker='o', s=first_point_size, alpha=1.0, edgecolors=darken_color(first_point_color, 0.2))
    
    ax.xaxis.pane.set_alpha(0.0)
    ax.yaxis.pane.set_alpha(0.0)
    ax.zaxis.pane.set_alpha(0.0)
    
    self.plot_canvas.setStyleSheet(f"background-color:{bg};")
    self.plot_canvas.draw()





def plot_brachy_bar_channels(self):
    # Retrieve user-selected settings
    font_size = self.selected_font_size
    background_color = self.selected_background
    
    # Get the selected channel from the spinbox
    selected_channel = self.brachy_spinBox_02.value()  # Integer spinbox value for selected channel
    
    # Get the container for the bar plot
    container = self.brachy_ax_01
    
    # Set the background color for the container itself
    if background_color.lower() == 'transparent':
        container.setStyleSheet("background-color: rgba(0, 0, 0, 0);")  # Transparent background for the entire container
    else:
        container.setStyleSheet(f"background-color: {background_color};")  # Set the background color for the entire container
    
    # Initialize the Matplotlib Figure if it doesn't exist
    if not hasattr(self, 'plot_Brachy_Bar_Fig'):
        self.plot_Brachy_Bar_Fig = Figure()
        self.plot_bar_canvas = FigureCanvas(self.plot_Brachy_Bar_Fig)
        self.plot_bar_toolbar = NavigationToolbar(self.plot_bar_canvas, self)
        
        # Set layout for the container if it doesn't have one
        if container.layout() is None:
            layout = QVBoxLayout(container)
            container.setLayout(layout)
        else:
            # Clear existing content in the container, if any
            while container.layout().count():
                child = container.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        # Add the toolbar and canvas to the container
        container.layout().addWidget(self.plot_bar_toolbar)
        container.layout().addWidget(self.plot_bar_canvas)
    else:
        # If the figure already exists, clear it for new plotting
        self.plot_Brachy_Bar_Fig.clf()

    # Create an axes for the bar plot
    ax = self.plot_Brachy_Bar_Fig.add_subplot(111)
    
    # Set plot and figure background based on user selection
    if background_color.lower() == 'transparent':
        ax.set_facecolor((0, 0, 0, 0))  # Transparent background for the plot itself
        self.plot_Brachy_Bar_Fig.patch.set_alpha(0.0)
    else:
        ax.set_facecolor(background_color)
        self.plot_Brachy_Bar_Fig.patch.set_facecolor(background_color)
    
    # Customize text and axes properties
    ax.tick_params(labelsize=font_size, colors='black' if background_color.lower() == 'white' else 'white')  # Adjust label color based on background
    ax.set_xlabel("Dwell Position", fontsize=font_size, color='black' if background_color.lower() == 'white' else 'white')
    ax.set_ylabel("Dwell Time (s)", fontsize=font_size, color='black' if background_color.lower() == 'white' else 'white')

    # Retrieve the channels from medical_image
    channels = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']['Plan_Brachy_Channels']
    
    # Check if the selected channel is valid
    channel_idx = selected_channel - 1  # Adjust to zero-based indexing
    if 0 <= channel_idx < len(channels):
        channel = channels[channel_idx]
        dwell_info = channel.get('DwellInfo')
        
        if dwell_info is None or not isinstance(dwell_info, np.ndarray):
            print(f"Channel {selected_channel}: 'DwellInfo' is not valid. Skipping.")
            return
        
        # Extract dwell times (assuming column 2 holds the dwell time)
        dwell_times = dwell_info[:, 2]  # Example: assuming the dwell times are in the 3rd column

        # Create labels for each dwell position
        bar_labels = [f"{i + 1}" for i in range(len(dwell_times))]
        bar_values = dwell_times
        
        # Plot the bar chart
        ax.bar(bar_labels, bar_values, color='blue')
        
    else:
        print(f"Selected channel {selected_channel} is out of range.")
        return

    # Draw the updated plot
    self.plot_bar_canvas.draw()


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
                        # Table X is physical X, Table Y is physical Z, Table Z is physical Y
                        x_phys = float(val_x)
                        y_phys = float(val_z)
                        z_phys = float(val_y)
                        
                        # Interpolate dose (Gy) and convert to cGy
                        dose_Gy = float(interp([z_phys, y_phys, x_phys])[0])
                        dose_cGy = dose_Gy * 100.0
                        
                        dose_str = f"{dose_cGy:.2f}"
                        
                        # Update brachy_table_01
                        d_item1 = QTableWidgetItem(dose_str)
                        d_item1.setTextAlignment(Qt.AlignCenter)
                        self.brachy_table_01.setItem(row, 8, d_item1)
                        
                        # Update brachy_table_02
                        d_item2 = QTableWidgetItem(dose_str)
                        d_item2.setTextAlignment(Qt.AlignCenter)
                        self.brachy_table_02.setItem(row, 8, d_item2)
                    except Exception as e:
                        print(f"Error calculating dose at row {row}: {e}")
    except Exception as e:
        print(f"Error setting up dose calculation: {e}")


def on_brachy_table_item_changed(self, table, item):
    """
    Called when a cell in brachy_table_01 or brachy_table_02 is modified.
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
    
    # We only care about X, Y, Z coordinates (cols 5, 6, 7)
    if col not in (5, 6, 7):
        return
        
    # Get metadata
    metadata = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']
    ref_points = metadata.get('Plan_Dose_References', [])
    if row >= len(ref_points):
        return
        
    other_table = self.brachy_table_02 if table is self.brachy_table_01 else self.brachy_table_01
    
    # Temporarily block signals to prevent recursive update loops
    other_table.blockSignals(True)
    table.blockSignals(True)
    try:
        # Synchronize value change to the other table
        other_item = other_table.item(row, col)
        if other_item:
            other_item.setText(item.text())
        else:
            other_item = QTableWidgetItem(item.text())
            other_item.setTextAlignment(Qt.AlignCenter)
            other_table.setItem(row, col, other_item)
            
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
                    # Table X is physical X, Table Y is physical Z, Table Z is physical Y
                    x = float(val_x) # physical X
                    y = float(val_z) # physical Y
                    z = float(val_y) # physical Z
                    
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
                    
                    d_item2 = QTableWidgetItem(dose_str)
                    d_item2.setTextAlignment(Qt.AlignCenter)
                    other_table.setItem(row, 8, d_item2)

                    # Update VTK marker positions on image views
                    from fcn_display.display_images import displayaxial, displaysagittal, displaycoronal
                    displayaxial(self)
                    displaysagittal(self)
                    displaycoronal(self)
                    
                except ValueError as e:
                    print(f"Non-numeric coordinates: {e}")
                except Exception as e:
                    print(f"Error on coordinate recalculation: {e}")
    finally:
        other_table.blockSignals(False)
        table.blockSignals(False)