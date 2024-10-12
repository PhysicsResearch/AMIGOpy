import pydicom
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton

def update_metadata_table(self,metadata):
    self.MetaViewTable.clear()
    self.MetaViewTable.setRowCount(len(metadata))
    self.MetaViewTable.setColumnCount(2)
    self.MetaViewTable.setHorizontalHeaderLabels(["Key", "Value"])

       
    for i, key in enumerate(metadata):
        self.MetaViewTable.setItem(i, 0, QTableWidgetItem(key))
        value = metadata[key]
        
    # Determine how to display the value
        if isinstance(value, (list, np.ndarray)):
            if len(value) <= 10:  # Adjust the number as needed
                # Display short lists or arrays as is
                display_value = ', '.join(str(v) for v in value)
            else:
                # For longer lists/arrays, display size and type
                display_value = f"Length: {len(value)}, Type: {type(value).__name__}"
        elif isinstance(value, str):
            if len(value) < 100:
                # Display short strings as is
                display_value = value
            else:
                # For longer strings, display length
                display_value = f"Length: {len(value)}, Type: str"
        elif isinstance(value, (int, float)):
            # Display numerical types as is
            display_value = str(value)
        else:
            # For other data types, display type
            display_value = f"Type: {type(value).__name__}"

        self.MetaViewTable.setItem(i, 1, QTableWidgetItem(display_value))

def update_meta_view_table_dicom(self, ds):
    headers_table = []
    
    for data_element in ds:
        group_number = data_element.tag.group
        headers_table.append([
            f"{group_number:X}", 
            f"{data_element.tag.element:X}", 
            data_element.name, 
            str(data_element.value)[:50]  # Truncate long values to avoid overly wide columns
        ])
    
    # Prepare the table for new data
    self.MetaViewTable.clear()
    self.MetaViewTable.setColumnCount(4)
    self.MetaViewTable.setHorizontalHeaderLabels(['Group', 'Element', 'Name', 'Value'])
    self.MetaViewTable.setRowCount(len(headers_table))
    
    for row, (group, element, name, value) in enumerate(headers_table):
        self.MetaViewTable.setItem(row, 0, QTableWidgetItem(group))
        self.MetaViewTable.setItem(row, 1, QTableWidgetItem(element))
        self.MetaViewTable.setItem(row, 2, QTableWidgetItem(name))
        self.MetaViewTable.setItem(row, 3, QTableWidgetItem(value))
    
    self.MetaViewTable.resizeColumnsToContents() 
    
def extract_dicom_hierarchy(dicom_file_path):
    ds = pydicom.dcmread(dicom_file_path, stop_before_pixels=True)
    headers_table = []
    
    for data_element in ds:
        group_number = data_element.tag.group
        headers_table.append([
            f"{group_number:X}", 
            f"{data_element.tag.element:X}", 
            data_element.name, 
            str(data_element.value)[:50]  # Truncate long values to avoid overly wide columns
        ])
    
    return headers_table