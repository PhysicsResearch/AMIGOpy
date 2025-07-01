# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 12:01:02 2025

@author: tommaso.siligardi
"""

import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
import csv, math
from PyQt5.QtGui         import QColor, QBrush
from PyQt5.QtCore        import Qt

def update_material_list(self):
    
    mat_names=self.Mat_df['Name'].to_numpy().tolist()
    self.Select_mat.clear()
    self.Select_mat.addItem('...Select material...')
    self.Select_mat.addItems(mat_names)
    


def mat2HU(self):
    pass

def generate_mat_map(self):
    pass
