from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QPushButton
from PySide6.QtGui import QColor
import pandas as pd
import os
import numpy as np
import random
from fcn_display.display_images  import displayaxial, displaycoronal, displaysagittal
import vtk

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

def move_center_to_current(self):
    button = self.sender()
    if button is None:
        return
    # Find which row the button belongs to
    row = -1
    for r in range(self.table_circ_roi.rowCount()):
        if self.table_circ_roi.cellWidget(r, 9) == button:
            row = r
            break
    if row == -1:
        return
    
    # Update coordinates of this row
    idx = 0
    x_val = "0"
    y_val = "0"
    slice_val = "0"

    if hasattr(self, 'current_sagittal_slice_index') and isinstance(self.current_sagittal_slice_index, list) and 0 <= idx < len(self.current_sagittal_slice_index) and self.current_sagittal_slice_index[idx] != -1:
        x_val = str(self.current_sagittal_slice_index[idx])
    elif hasattr(self, 'SagittalSlider'):
        x_val = str(self.SagittalSlider.value())

    if hasattr(self, 'current_coronal_slice_index') and isinstance(self.current_coronal_slice_index, list) and 0 <= idx < len(self.current_coronal_slice_index) and self.current_coronal_slice_index[idx] != -1:
        y_val = str(self.current_coronal_slice_index[idx])
    elif hasattr(self, 'CoronalSlider'):
        y_val = str(self.CoronalSlider.value())

    if hasattr(self, 'current_axial_slice_index') and isinstance(self.current_axial_slice_index, list) and 0 <= idx < len(self.current_axial_slice_index) and self.current_axial_slice_index[idx] != -1:
        slice_val = str(self.current_axial_slice_index[idx])
    elif hasattr(self, 'AxialSlider'):
        slice_val = str(self.AxialSlider.value())

    # Temporarily disconnect signals to prevent intermediate updates
    self.table_circ_roi.blockSignals(True)
    self.table_circ_roi.setItem(row, 0, QTableWidgetItem(x_val))
    self.table_circ_roi.setItem(row, 1, QTableWidgetItem(y_val))
    self.table_circ_roi.setItem(row, 3, QTableWidgetItem(slice_val))
    self.table_circ_roi.setItem(row, 4, QTableWidgetItem(slice_val))
    self.table_circ_roi.blockSignals(False)

    # Redraw and get data
    displayaxial(self)
    displaycoronal(self)
    displaysagittal(self)
    c_roi_getdata(self)

def roi_c_add_row(self):
    # Temporarily disconnect the itemChanged signal to improve performance
    self.table_circ_roi.blockSignals(True)
    # Get the current number of rows in the table
    row_position = self.table_circ_roi.rowCount()
    # Insert a new row at the end
    self.table_circ_roi.insertRow(row_position)
    
    # Use index 0 as the display coordinates are tracked based on the base layer (index 0)
    idx = 0

    # Get current slice coordinates from sliders/variables
    x_val = "0"
    y_val = "0"
    
    # Default radius from spinbox
    rad_val = str(self.roi_default_pixel_size.value()) if hasattr(self, 'roi_default_pixel_size') else "10"
    
    # Slice val
    slice_val = "0"

    # Sagittal (X)
    if hasattr(self, 'current_sagittal_slice_index') and isinstance(self.current_sagittal_slice_index, list) and 0 <= idx < len(self.current_sagittal_slice_index) and self.current_sagittal_slice_index[idx] != -1:
        x_val = str(self.current_sagittal_slice_index[idx])
    elif hasattr(self, 'SagittalSlider'):
        x_val = str(self.SagittalSlider.value())

    # Coronal (Y)
    if hasattr(self, 'current_coronal_slice_index') and isinstance(self.current_coronal_slice_index, list) and 0 <= idx < len(self.current_coronal_slice_index) and self.current_coronal_slice_index[idx] != -1:
        y_val = str(self.current_coronal_slice_index[idx])
    elif hasattr(self, 'CoronalSlider'):
        y_val = str(self.CoronalSlider.value())

    # Axial (Z)
    if hasattr(self, 'current_axial_slice_index') and isinstance(self.current_axial_slice_index, list) and 0 <= idx < len(self.current_axial_slice_index) and self.current_axial_slice_index[idx] != -1:
        slice_val = str(self.current_axial_slice_index[idx])
    elif hasattr(self, 'AxialSlider'):
        slice_val = str(self.AxialSlider.value())

    # Range of axial slices based on spinbox
    num_slices = self.roi_slices.value() if hasattr(self, 'roi_slices') else 1
    try:
        init_slice = int(slice_val)
    except ValueError:
        init_slice = 0
    last_slice = init_slice + num_slices - 1

    # Generate a random RGB color (values rounded to 2 decimal places)
    r_val = f"{random.random():.2f}"
    g_val = f"{random.random():.2f}"
    b_val = f"{random.random():.2f}"

    # Set default values for the new row
    self.table_circ_roi.setItem(row_position, 0, QTableWidgetItem(x_val))
    self.table_circ_roi.setItem(row_position, 1, QTableWidgetItem(y_val))
    self.table_circ_roi.setItem(row_position, 2, QTableWidgetItem(rad_val))
    self.table_circ_roi.setItem(row_position, 3, QTableWidgetItem(str(init_slice)))
    self.table_circ_roi.setItem(row_position, 4, QTableWidgetItem(str(last_slice)))
    self.table_circ_roi.setItem(row_position, 5, QTableWidgetItem("0.5"))
    self.table_circ_roi.setItem(row_position, 6, QTableWidgetItem(r_val))
    self.table_circ_roi.setItem(row_position, 7, QTableWidgetItem(g_val))
    self.table_circ_roi.setItem(row_position, 8, QTableWidgetItem(b_val))

    # Add a "Move Center" button in column 9 (Actions column)
    btn = QPushButton("move center to current slice position")
    btn.clicked.connect(lambda: move_center_to_current(self))
    self.table_circ_roi.setCellWidget(row_position, 9, btn)

    # Update row color dynamically
    update_row_color(self, row_position)
        
    # Reconnect the itemChanged signal
    self.table_circ_roi.blockSignals(False)

    # Render updates to display
    displayaxial(self)
    displaycoronal(self)
    displaysagittal(self)

    # Automatically query and populate data values for the current slices
    c_roi_getdata(self)

def roi_c_remove_row(self):
    # Find which row is currently selected
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
            # Re-render display and update stats table
            displayaxial(self)
            displaycoronal(self)
            displaysagittal(self)
            c_roi_getdata(self)
    else:
        QMessageBox.information(None, "Information", "Please select a line in the circles ROI table to remove first.")
        
def on_roitable_item_changed(self, item):
    # Columns 6, 7, 8, and 9 correspond to transparency (6), R (7), G (8), and B (9)
    if item.column() in [5, 6, 7, 8]:
        try:
            value = float(item.text())
            if value < 0:
                item.setText("0")
            elif value > 1:
                item.setText("1")
        except ValueError:
            # If the value is not a valid float, reset it to a default value (e.g., 0)
            item.setText("0")
    elif item.column() in [1, 2, 3, 4]:
        try:
            value = float(item.text())
            if value < 0:
                item.setText("0")
        except ValueError:
            # If the value is not a valid float, reset it to a default value (e.g., 0)
            item.setText("0")  
    # Update the row color based on the RGB values
    update_row_color(self,item.row())        
    displayaxial(self)
    displaycoronal(self)
    displaysagittal(self)
    
def update_row_color(self, row):
    try:
        R_item = self.table_circ_roi.item(row, 6)
        G_item = self.table_circ_roi.item(row, 7)
        B_item = self.table_circ_roi.item(row, 8)
        transparency_item = self.table_circ_roi.item(row, 5)

        if R_item is None or G_item is None or B_item is None or transparency_item is None:
            return

        R = float(R_item.text())
        G = float(G_item.text())
        B = float(B_item.text())
        transparency = float(transparency_item.text())

        # Ensure the values are between 0 and 1
        R = min(max(R, 0), 1)
        G = min(max(G, 0), 1)
        B = min(max(B, 0), 1)
        transparency = min(max(transparency, 0), 1)

        # Convert to 0-255 range for QColor
        color = QColor(int(R * 255), int(G * 255), int(B * 255), int((transparency) * 255))


        for col in range(self.table_circ_roi.columnCount()):
            item = self.table_circ_roi.item(row, col)
            if item:
                item.setBackground(color)

    except ValueError:
        print(f'Skipping row {row} due to invalid data')
            
def export_roi_circ_table_to_csv(self):
    # Open a dialog to select the file path
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Save Coordinates CSV", "roi_circles_coordinates.csv", "CSV Files (*.csv)", options=options
    )

    if file_path:
        # Prepare data for CSV
        data = []
        for row in range(self.table_circ_roi.rowCount()):
            row_data = []
            for column in range(self.table_circ_roi.columnCount()):
                item = self.table_circ_roi.item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append('')
            data.append(row_data)

        # Convert data to a DataFrame
        df = pd.DataFrame(data)

        # Save DataFrame to CSV
        try:
            df.to_csv(file_path, index=False, header=False)
            print(f"Table exported to {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not write to {file_path}. Please close the file if it is open in another program.")
        
def export_roi_circ_values_to_csv(self):
    # Open a dialog to select the file path
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

        # Prepare data for CSV
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

        # Convert data to a DataFrame
        df = pd.DataFrame(data, columns=headers)

        # Save DataFrame to CSV
        try:
            df.to_csv(file_path, index=False)
            print(f"Values exported to {file_path}")
        except:
            QMessageBox.warning(None, "Warning", f"Could not write to {file_path}. Please close the file if it is open in another program.")
            return


def import_roi_circ_table(self):
    # Open a dialog to select the CSV file
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)

    if file_name:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_name, header=None)

        # Clear the table
        self.table_circ_roi.setRowCount(0)
        self.table_circ_roi.setColumnCount(10)
        column_names = ["X Cent. (Px)", "Y Cent. (Px)", "Rad. (Px)", "Init. Slice", "Last. Slice", "Trasnp.","R","G","B", "Actions"]
        self.table_circ_roi.setHorizontalHeaderLabels(column_names)

        self.table_circ_roi.blockSignals(True)
        # Populate the table with the data
        for row in df.itertuples(index=False):
            row_position = self.table_circ_roi.rowCount()
            self.table_circ_roi.insertRow(row_position)
            for col, value in enumerate(row):
                if col < 9:
                    self.table_circ_roi.setItem(row_position, col, QTableWidgetItem(str(value)))
            # Create a "Move Center" button in the last column
            btn = QPushButton("move center to current slice position")
            btn.clicked.connect(lambda: move_center_to_current(self))
            self.table_circ_roi.setCellWidget(row_position, 9, btn)
            update_row_color(self, row_position)
        self.table_circ_roi.blockSignals(False)

        print(f"Table populated from {file_name}")
        displayaxial(self)
        displaycoronal(self)
        displaysagittal(self)
        c_roi_getdata(self)

def c_roi_getvoxels(self):
        # Check if the checkbox is checked - All imges within modality or single series
    if getattr(self, 'DataType', None) not in ["DICOM", "Nifti"]:
        QMessageBox.warning(None, "Warning", "No DICOM/NIfTI data was found")
        return
    if self.checkBox_circ_roi_data_01.isChecked():
        series_list = self.medical_image[self.patientID][self.studyID][self.modality]
    else:
        series_list = [self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]]

    if self.checkBox_circ_roi_data_01.isChecked() and self.holdOnROI.isChecked():
        QMessageBox.warning(None, "Warning", "The 'All image series' and 'Hold on' options cannot be used at the same time")
        return
    
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
    
                # Create a mask for the ROI
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
                # Apply the mask to the reference image
                masked_data = reference_image[mask]
                voxels_data[f'Series_{series_number}_ROI_{row}'] = masked_data.flatten()
    
            except ValueError:
                print(f'Skipping row {row} due to invalid data')
                continue

    return voxels_data

    
def c_roi_getdata(self):
    if not hasattr(self, 'display_data') or not self.display_data:
        QMessageBox.warning(None, "Warning", "No image data was found")
        return

    # Find all layers that have data
    active_layers = []
    for l in range(4):
        if l in self.display_data and self.display_data[l] is not None:
            active_layers.append(l)

    if not active_layers:
        QMessageBox.warning(None, "Warning", "No active layers with image data found")
        return

    # Clear the table before populating
    self.table_roi_c_values.setRowCount(self.table_circ_roi.rowCount())
    
    # Each active layer gets 3 columns: Mean_L{l}, STD_L{l}, N_L{l}
    self.table_roi_c_values.setColumnCount(3 * len(active_layers))

    horizontalLabels = []
    for l in active_layers:
        horizontalLabels.extend([f"Mean_L{l}", f"STD_L{l}", f"N_L{l}"])
    self.table_roi_c_values.setHorizontalHeaderLabels(horizontalLabels)

    for i, l in enumerate(active_layers):
        reference_image = self.display_data[l]
        
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
    
                # Ensure slice bounds are within the shape of the reference_image for layer l
                max_slices = reference_image.shape[0]
                slice_ini = max(0, min(slice_ini, max_slices - 1))
                slice_fin = max(0, min(slice_fin, max_slices - 1))

                # Create a mask for the ROI
                mask = np.zeros(reference_image.shape, dtype=bool)
                for z in range(slice_ini, slice_fin + 1):
                    y, x = np.ogrid[-center_y:reference_image.shape[1] - center_y, -center_x:reference_image.shape[2] - center_x]
                    mask[z] = x*x + y*y <= radius*radius
    
                # Apply the mask to the reference image
                masked_data = reference_image[mask]
    
                # Calculate statistics
                if masked_data.size > 0:
                    mean_value = np.mean(masked_data)
                    std_value = np.std(masked_data)
                    num_voxels = masked_data.size
                else:
                    mean_value = 0.0
                    std_value = 0.0
                    num_voxels = 0
    
                # Populate the statistics table
                self.table_roi_c_values.setItem(row, i*3+0, QTableWidgetItem(f"{mean_value:.4f}"))
                self.table_roi_c_values.setItem(row, i*3+1, QTableWidgetItem(f"{std_value:.4f}"))
                self.table_roi_c_values.setItem(row, i*3+2, QTableWidgetItem(str(num_voxels)))
    
            except Exception as e:
                print(f'Skipping row {row} in layer {l} due to error: {e}')
                continue