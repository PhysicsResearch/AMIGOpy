import numpy as np
import vtk
from copy import deepcopy
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, 
    QWidget, QLineEdit, QLabel, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,QHeaderView)

from PyQt5.QtCore import Qt  # Import Qt to use Qt.ItemIsEditable flag

import matplotlib.pyplot as plt
import pandas as pd



def load_ct_cal_curve(self):
    options = QFileDialog.Options()
    fileName, _ = QFileDialog.getOpenFileName(self, "Open the CT calibration curve ", "", "CSV Files (*.csv);;All Files (*)", options=options)
    if not fileName:
        return  # user canceled

    # Detect delimiter by reading the first non-header line
    with open(fileName, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) < 2:
            return  # file too short or empty
        delimiter = ',' if ',' in lines[1] else ';'
    data_ct_cal=pd.read_csv(fileName,skiprows=[0],delimiter=delimiter)
    ct_cal_name=fileName.split('/')[-1].split('.')[0]
    while ct_cal_name in self.ct_cal_curves.keys():
        ct_cal_name=f'{ct_cal_name}_1'
    self.ct_cal_curves[ct_cal_name]=data_ct_cal
    update_ct_cal_list(self)
    
    
    
def update_ct_cal_list(self):
    self.ct_cal_list.clear()
    names=[k for k in self.ct_cal_curves.keys()]
    self.ct_cal_list.addItems(names)


def update_ct_cal_table(self,ct_cal_data):
    self.ct_cal_table.clear()

    n_rows, n_cols = ct_cal_data.shape
    self.ct_cal_table.setRowCount(n_rows+1)
    self.ct_cal_table.setColumnCount(n_cols)
    
    # Set column headers (e.g., 'HU', 'Density', etc.)
    header = ct_cal_data.columns.tolist()
    item0 = QTableWidgetItem(header[0])
    item0.setFlags(item0.flags() & ~Qt.ItemIsEditable)  # Make (0, 0) uneditable
    self.ct_cal_table.setItem(0, 0, item0)

    item1 = QTableWidgetItem(header[1])
    self.ct_cal_table.setItem(0, 1, item1)  # Editable by default

    # Loop through all rows and columns to make all cells editable
    for row in range(n_rows):
        for col in range(n_cols):
            item = QTableWidgetItem(str(ct_cal_data.iloc[row, col]))
            self.ct_cal_table.setItem(row+1, col, item)

    self.ct_cal_table.resizeColumnsToContents()
    self.ct_cal_table.horizontalHeader().setVisible(False)
    self.ct_cal_table.verticalHeader().setVisible(False)
    

def update_ct_cal_view(self):
    selected_text = self.ct_cal_list.currentText()
    if selected_text not in self.ct_cal_curves.keys():
        return 
    ct_cal_data=self.ct_cal_curves[selected_text]
    update_ct_cal_table(self, ct_cal_data)

def save_changes(self):
    row_count = self.ct_cal_table.rowCount()
    col_count = self.ct_cal_table.columnCount()

    # Extract header from the first row
    headers = []
    for col in range(col_count):
        item = self.ct_cal_table.item(0, col)
        headers.append(item.text() if item else f"Column{col}")

    # Extract data starting from row 1
    data = []
    for row in range(1, row_count):
        row_data = []
        for col in range(col_count):
            item = self.ct_cal_table.item(row, col)
            row_data.append(item.text() if item else "")
        data.append(row_data)

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=headers)

    # Optional: Convert to numeric if needed
    df = df.apply(pd.to_numeric, errors='ignore')
    #getting the current table name:
    table_name=self.ct_cal_list.currentText()
    self.ct_cal_curves[table_name]=df
    update_ct_cal_list(self)
    update_ct_cal_view(self)


def export_ct_cal_to_csv(self):
    pass

def update_ct_cal_graph(self):
    pass


    

    
