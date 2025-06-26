import numpy as np
import vtk
from copy import deepcopy
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, 
    QWidget, QLineEdit, QLabel, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,QHeaderView, QInputDialog, QMessageBox)

from PyQt5.QtCore import Qt  # Import Qt to use Qt.ItemIsEditable flag
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd



def create_density_map(self):
    
    #Retrive CT_info
    if self.patientID:
        target_dict=self.dicom_data[self.patientID][self.studyID]
    else:
        print('No ct selected')
        return
    try:
        ct_matrix=target_dict['CT'][self.series_index]['3DMatrix']
        print('ok')
    except:
        print('no ct found')
        return
    
    #Retrive CT_cal
    row_count = self.ct_cal_table.rowCount()
    col_count = self.ct_cal_table.columnCount()
    headers = []
    for col in range(col_count):
        item = self.ct_cal_table.item(0, col)
        headers.append(item.text() if item else f"Column{col}")
    data = []
    for row in range(1, row_count):
        row_data = []
        for col in range(col_count):
            item = self.ct_cal_table.item(row, col)
            row_data.append(item.text() if item else "")
        data.append(row_data)
    ct_cal = pd.DataFrame(data, columns=headers)
    ct_cal = ct_cal.apply(pd.to_numeric, errors='ignore')
    ct_cal=ct_cal.dropna()
    
    if ct_cal.size<4:
        print('the CT calibraion curve needs to have at least two rows!')
        return

    denisty_matrix=compute_density(ct_matrix, ct_cal)

    
    
    

def compute_density(ct_matrix,ct_cal_curve):
    HU=ct_cal_curve.iloc[:,0].to_numpy()
    density=ct_cal_curve.iloc[:,1].to_numpy()
    slopes = np.diff(density) / np.diff(HU)  # (ΔDensity / ΔHU)
    intercepts = density[:-1] - slopes * HU[:-1]  # Compute intercepts
    density_map = np.zeros_like(ct_matrix, dtype=np.float32)
    for i in range(len(slopes)):  # Loop over calibration segments
        mask = (ct_matrix >= HU[i]) & (ct_matrix < HU[i+1])  # Find values in range
        density_map[mask] = ct_matrix[mask] * slopes[i] + intercepts[i]
    mask_last = ct_matrix >= HU[-2]
    density_map[mask_last] = ct_matrix[mask_last] * slopes[-1] + intercepts[-1]
    
    # Apply lower and upper limits 
    density_map[density_map < density[0]] = density[0]  # Lower limit
    density_map[density_map > max(density[-1],2.9)] = max(density[-1],2.9)  # Upper limit
    
    return density_map

def get_ct_cal_curve():
    pass