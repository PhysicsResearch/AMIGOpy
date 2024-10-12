from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QFileDialog
from PyQt5.QtGui import QColor
import pandas as pd
import numpy as np
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

def roi_c_add_row(self):
    # Temporarily disconnect the itemChanged signal to improve performance
    self.table_circ_roi.blockSignals(True)
    # Get the current number of rows in the table
    row_position = self.table_circ_roi.rowCount()
    # Insert a new row at the end
    self.table_circ_roi.insertRow(row_position)
    # Optionally, you can initialize the new row with default values
    for col in range(self.table_circ_roi.columnCount()):
        self.table_circ_roi.setItem(row_position, self.table_circ_roi.columnCount() - 4, QTableWidgetItem("0.2"))
        self.table_circ_roi.setItem(row_position, self.table_circ_roi.columnCount() - 3, QTableWidgetItem("1"))
        self.table_circ_roi.setItem(row_position, self.table_circ_roi.columnCount() - 2, QTableWidgetItem("0"))
        self.table_circ_roi.setItem(row_position, self.table_circ_roi.columnCount() - 1, QTableWidgetItem("0"))
        
    # Reconnect the itemChanged signal
    self.table_circ_roi.blockSignals(False)

def roi_c_remove_row(self):
    # Get the current number of rows in the table
    row_position = self.table_circ_roi.rowCount()
    # Remove the last row if the table is not empty
    if row_position > 0:
        self.table_circ_roi.removeRow(row_position - 1)
        
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
    # Open a dialog to select the folder
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    folder = QFileDialog.getExistingDirectory(self, "Select Folder", options=options)

    if folder:
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

        # Define the file path
        file_path = f"{folder}/roi_circles_coordinates.csv"

        # Save DataFrame to CSV
        df.to_csv(file_path, index=False, header=False)

        print(f"Table exported to {file_path}")
        
def export_roi_circ_values_to_csv(self):
    # Open a dialog to select the folder
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    folder = QFileDialog.getExistingDirectory(self, "Select Folder", options=options)

    if folder:
        # Prepare data for CSV
        data = []
        for row in range(self.table_roi_c_values.rowCount()):
            row_data = []
            for column in range(self.table_roi_c_values.columnCount()):
                item = self.table_roi_c_values.item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append('')
            data.append(row_data)

        # Convert data to a DataFrame
        df = pd.DataFrame(data)

        # Define the file path
        file_path = f"{folder}/roi_circles_values.csv"

        # Save DataFrame to CSV
        df.to_csv(file_path, index=False, header=False)

        print(f"Table exported to {file_path}")
        
        
def import_roi_circ_table(self):
    # Temporarily disconnect the itemChanged signal to improve performance
    # self.table_circ_roi.blockSignals(True)
    # Open a dialog to select the CSV file
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)

    if file_name:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_name, header=None)

        # Clear the table
        self.table_circ_roi.setRowCount(0)
        self.table_circ_roi.setColumnCount(df.shape[1])

        # Populate the table with the data
        for row in df.itertuples(index=False):
            row_position = self.table_circ_roi.rowCount()
            self.table_circ_roi.insertRow(row_position)
            for col, value in enumerate(row):
                self.table_circ_roi.setItem(row_position, col, QTableWidgetItem(str(value)))

        print(f"Table populated from {file_name}")
    # Restore connection
    # self.table_circ_roi.blockSignals(False)
    
def c_roi_getdata(self):
    # Check if the checkbox is checked - All imges within modality or single series
    if self.checkBox_circ_roi_data_01.isChecked():
        series_list = self.dicom_data[self.patientID][self.studyID][self.modality]
    else:
        series_list = [self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]]

    
    # Assuming the reference image is a 3D NumPy array
    reference_image = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix']
    series_number = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['SeriesNumber']

    # Clear the table before populating
    self.table_roi_c_values.setRowCount(0)
    self.table_roi_c_values.setColumnCount(4)  # Columns for Mean, STD, Voxels, and ROI Index

    self.table_roi_c_values.setHorizontalHeaderLabels(["Series Number", "Mean", "STD", "N"])
    
    
    for series_data in series_list:
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
                    mask[z] = x*x + y*y <= radius*radius
    
                # Apply the mask to the reference image
                masked_data = reference_image[mask]
    
                # Calculate statistics
                mean_value = np.mean(masked_data)
                std_value = np.std(masked_data)
                num_voxels = masked_data.size
    
                # Populate the statistics table
                row_position = self.table_roi_c_values.rowCount()
                self.table_roi_c_values.insertRow(row_position)
                self.table_roi_c_values.setItem(row_position, 0, QTableWidgetItem(str(series_number)))
                self.table_roi_c_values.setItem(row_position, 1, QTableWidgetItem(f"{mean_value:.4f}"))
                self.table_roi_c_values.setItem(row_position, 2, QTableWidgetItem(f"{std_value:.4f}"))
                self.table_roi_c_values.setItem(row_position, 3, QTableWidgetItem(str(num_voxels)))
    
    
            except ValueError:
                print(f'Skipping row {row} due to invalid data')
                continue