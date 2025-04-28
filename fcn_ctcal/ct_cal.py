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
    while ct_cal_name in self.ct_cal_curves.keys():
        ct_cal_name=f'{ct_cal_name}_1'
    self.ct_cal_curves[ct_cal_name]=data_ct_cal
    update_ct_cal_list(self)
    
    
    
def update_ct_cal_list(self):
    self.ct_cal_list.clear()
    names=[k for k in self.ct_cal_curves.keys()]
    self.ct_cal_list.addItems(names)


def update_ct_cal_table(self):
    pass

def save_changes(self):
    pass

def export_ct_cal_to_csv(self):
    pass

def update_ct_cal_graph(self):
    pass


    

    
