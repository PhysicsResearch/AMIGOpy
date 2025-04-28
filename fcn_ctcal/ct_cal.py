import numpy as np
import vtk
from copy import deepcopy
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, 
    QWidget, QLineEdit, QLabel, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem)

import matplotlib.pyplot as plt
import pandas as pd



def load_ct_cal_curve(self):
    options = QFileDialog.Options()
    fileName, _ = QFileDialog.getOpenFileName(self, "Open the CT calibration curve ", "", "CSV Files (*.csv);;All Files (*)", options=options)
    data_ct_cal=pd.read_csv(fileName,skiprows=[0])
    ct_cal_name=fileName.split('/')[-1].split('.')[0]
    print(fileName)
    print(ct_cal_name)
    
    
def update_ct_cal_list(self):
    pass

    
