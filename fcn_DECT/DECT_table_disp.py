from PyQt5.QtWidgets     import  QTableWidgetItem, QMessageBox
from PyQt5.QtCore        import Qt
from PyQt5.QtGui         import QColor, QBrush
from fcn_DECT.load_mat_info       import create_dataframe
from fcn_DECT.calc_ref_parameters import calculate_mat_par
from fcn_DECT.constants import ATOMIC_NUMBER_TO_SYMBOL
import numpy as np

def update_mat_table_style(self):
    num_rows = self.MatInfoTable.rowCount()
    num_columns = self.MatInfoTable.columnCount()
    for i in range(num_rows):
        for j in range(num_columns):
            tableWidgetItem = self.MatInfoTable.item(i, j)
            if tableWidgetItem is None:  # Create item if it does not exist
                tableWidgetItem = QTableWidgetItem()
                self.MatInfoTable.setItem(i, j, tableWidgetItem)

            # Set text color to white
            tableWidgetItem.setForeground(QBrush(QColor(255, 255, 255)))

            # Set background color based on column index
            if j >= num_columns - 2:
                tableWidgetItem.setBackground(QBrush(QColor(0, 128, 255)) if j % 2 == 0 else QBrush(QColor(102, 0, 204)))
            elif j >= num_columns - 7:
                tableWidgetItem.setBackground(QBrush(QColor(255, 51, 153)) if j % 2 == 0 else QBrush(QColor(255, 102, 178)))
            elif j == 0:
                tableWidgetItem.setBackground(QBrush(QColor(255, 0, 127)))
            else:
                tableWidgetItem.setBackground(QBrush(QColor(0, 128, 255)) if j % 2 == 0 else QBrush(QColor(102, 0, 204)))
            # If it's not the first column, centralize the text
            if j != 0:
                tableWidgetItem.setTextAlignment(Qt.AlignCenter)
            
def load_data_mat_info(self,df):
    self.Mat_info_table =df;
    # Check if Mat_info_table is None
    if self.Mat_info_table is None:
        return
    self.MatInfoTable.setRowCount(len(self.Mat_info_table))
    self.MatInfoTable.setColumnCount(len(self.Mat_info_table.columns))
    # Setting the column headers
    self.MatInfoTable.setHorizontalHeaderLabels(self.Mat_info_table.columns)
    num_columns = len(self.Mat_info_table.columns)
    for i in range(len(self.Mat_info_table)):
        for j in range(num_columns):
            item = str(self.Mat_info_table.iloc[i, j])
            tableWidgetItem = QTableWidgetItem(item) 
            self.MatInfoTable.setItem(i, j, tableWidgetItem)
            
            
def reset_matTable(self):
    # Clear the existing data
    self.MatInfoTable.clear()
    self.MatInfoTable.setRowCount(3)  # Set the number of rows to 3
    self.MatInfoTable.setColumnCount(11)  # Set the number of columns to 11
    
    # Define the column headers
    headers = ['Name', 'H', 'C', 'O', 'Den.', 'RED', 'Zeff', 'Iv', 'SPR', 'HUlow','HUhigh']
    self.MatInfoTable.setHorizontalHeaderLabels(headers)
    
    # Add "New Row" to the Name column of all rows
    for row in range(self.MatInfoTable.rowCount()):
        newItem = QTableWidgetItem("New Row")
        self.MatInfoTable.setItem(row, 0, newItem)
    self.update_mat_table_style()  # Update the table style after removing the column        
    

def remove_coll2table(self):
# Getting the text from lineEdit
 text = self.lineEdit.text()

 # If the text is a digit, convert it to corresponding symbol
 if text.isdigit():
     atomic_number = int(text)
     text = ATOMIC_NUMBER_TO_SYMBOL.get(atomic_number, text)
     if not atomic_number:  # If no atomic numbers found for the symbol
        QMessageBox.critical(self, 'Error', 'Invalid element symbol!')
        return

 # Getting current column headers
 headers = [self.MatInfoTable.horizontalHeaderItem(i).text() for i in range(self.MatInfoTable.columnCount())]

 # Finding the index of the column to remove
 position = None
 for i, header in enumerate(headers):
     if header == text:
         position = i
         break
  # If the column is not found, show error message
 if position is None:
    QMessageBox.critical(self, 'Error', 'Element not found in the table!')
    return       
        
 # If the column is found, remove it
 if position is not None:
     self.MatInfoTable.removeColumn(position)
     update_mat_table_style(self)  # Update the table style after removing the column
    
   
def add_row2table(self):
    # Getting the current row count
    currentRowCount = self.MatInfoTable.rowCount()
    
    # Inserting a new row at the end of the table
    self.MatInfoTable.insertRow(currentRowCount)
    
    # Setting the text of the first item in the new row to "New Row"
    newItem = QTableWidgetItem("New Row")
    self.MatInfoTable.setItem(currentRowCount, 0, newItem)
    
    # Optionally, fill the remaining cells in the new row with default values
    for j in range(1, self.MatInfoTable.columnCount()):
        defaultItem = QTableWidgetItem("")
        self.MatInfoTable.setItem(currentRowCount, j, defaultItem)
    update_mat_table_style(self)  # Update the table style after removing the column

def remove_row2table(self):
    # Getting the selected rows
    selected_indexes = self.MatInfoTable.selectionModel().selectedRows()

    if selected_indexes:  # if any row is selected
        for index in sorted(selected_indexes, reverse=True):
            self.MatInfoTable.removeRow(index.row())
    else:  # if no row is selected, remove the last row
        last_row = self.MatInfoTable.rowCount() - 1
        if last_row >= 0:  # checking if there are any rows to remove
            self.MatInfoTable.removeRow(last_row)
    update_mat_table_style(self)  # Update the table style after removing the column  

def add_coll2table(self):
# Getting the text from lineEdit
    text = self.lineEdit.text()
    # If the text is a digit, convert it to corresponding symbol
    if text.isdigit():
        atomic_number = int(text)
        text = ATOMIC_NUMBER_TO_SYMBOL.get(atomic_number, text)
        if text == str(atomic_number):  # If atomic_number not in the dictionary
            QMessageBox.critical(self, 'Error', 'Invalid atomic number!')
            return
    else:
        # Converting symbol to atomic number for comparison
        atomic_number_list = [k for k, v in ATOMIC_NUMBER_TO_SYMBOL.items() if v.upper() == text.upper()]
        if not atomic_number_list:  # If no atomic numbers found for the symbol
            QMessageBox.critical(self, 'Error', 'Invalid element symbol!')
            return
        atomic_number = atomic_number_list[0]
                
    # Getting current column headers
    headers = [self.MatInfoTable.horizontalHeaderItem(i).text() for i in range(self.MatInfoTable.columnCount())]
    
    # Check if the column already exists
    if text in headers:
        # Optionally, show a message saying the column already exists
        QMessageBox.information(self, "Info", "Column already exists.")
        return  # Exit the function
    
    # Defining the range to search the position (from the second column until 7 columns before the end)
    search_range = range(1, len(headers) - 7)
    
    # Finding the correct position to insert new column
    position = None
    for i in search_range:
        current_header = headers[i]
        # Converting current header to atomic number for comparison
        current_atomic_number = [k for k, v in ATOMIC_NUMBER_TO_SYMBOL.items() if v == current_header][0]
        if atomic_number < current_atomic_number:
            position = i
            break
    
    if position is None:
        position = len(headers) - 7  # default to inserting 7 columns before the end if no position found
    
    # Inserting a new column at the found position
    self.MatInfoTable.insertColumn(position)
    
    # Setting the header for the new column
    headers.insert(position, text)
    self.MatInfoTable.setHorizontalHeaderLabels(headers)
    
    # Filling the new column with default values
    for i in range(self.MatInfoTable.rowCount()):
        defaultItem = QTableWidgetItem("")
        self.MatInfoTable.setItem(i, position, defaultItem) 
    update_mat_table_style(self)
    

# load csv material info
def load_csv_mat_info(self):            
    # Set the text of the QLabel named "label" (or whatever you named it in Qt Designer)
    df = create_dataframe(self)
    load_data_mat_info(self,df)
    update_mat_table_style(self)

def calc_material_parameters(self):     
    self.label.setText("....")
    calculate_mat_par(self)
    update_mat_table_style(self)
    self.label.setText("Done")       
    

def c_roi_getdata_HU_high_low(self):
    # Update HU_low
    selected_index = self.DECT_list_01.currentIndex()
    series_label, patient_id, study_id, modality, item_index = self.series_info_dict[selected_index]      
    # Assuming the reference image is a 3D NumPy array
    reference_image = self.dicom_data[patient_id][study_id][modality][item_index]['3DMatrix']
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
            # Populate the statistics table
            self.MatInfoTable.setItem(row, self.MatInfoTable.columnCount() -2,  QTableWidgetItem(f"{mean_value:.4f}"))
        except ValueError:
            print(f'Skipping row {row} due to invalid data')
            continue
    update_mat_table_style(self)
    # Update HU_high
    selected_index = self.DECT_list_02.currentIndex()
    series_label, patient_id, study_id, modality, item_index = self.series_info_dict[selected_index]      
    # Assuming the reference image is a 3D NumPy array
    reference_image = self.dicom_data[patient_id][study_id][modality][item_index]['3DMatrix']
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
            # Populate the statistics table
            self.MatInfoTable.setItem(row, self.MatInfoTable.columnCount() -1,  QTableWidgetItem(f"{mean_value:.4f}"))
        except ValueError:
            print(f'Skipping row {row} due to invalid data')
            continue
    update_mat_table_style(self)
    
# Function to handle comboBox selection
def on_DECT_list_selection_changed(self,index):
    if index in self.series_info_dict:
        series_label, patient_id, study_id, modality, item = self.series_info_dict[index]
        # Do something with the information
        print(f"Selected: {series_label}, Patient ID: {patient_id}, Study ID: {study_id}, Modality: {modality}")
        print(self.dicom_data[patient_id][study_id][modality][item])