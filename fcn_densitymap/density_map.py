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
from fcn_load.populate_dcm_list import populate_DICOM_tree

def display_message_box(msg):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle('Error')
    msg_box.setText(msg)
    msg_box.exec()

def create_density_map(self,use_mat_map=False):
    
    #Retrive CT_info
    if self.patientID:
        target_dict=self.dicom_data[self.patientID][self.studyID]
    else:
        display_message_box('No patient selected')
        return
    try:
        ct_matrix=target_dict['CT'][self.series_index]['3DMatrix']

    except:
        display_message_box('No ct Found')
        return
    #If using material map
    if use_mat_map:
        #Check if material maps exists
        mat_maps=target_dict['CT'][self.series_index].get('mat_maps',{})
        if not mat_maps:
            QMessageBox.critical(self, 'Error', 'No material maps found for this CT')
            return
        density_matrix=np.zeros(ct_matrix.shape)
        item, ok = QInputDialog.getItem(self, "Choose Material Map", "Select the material map:", list(mat_maps.keys()), 0, False)
        if item and ok:
            map_type, ok_2 = QInputDialog.getItem(self, "Choose Map type", "Choose the map type:", ['Density','RED','SPR'], 0, False)
            if map_type and ok_2:
                mat_map_matrix= target_dict['CT'][self.series_index]['mat_maps'][item]['3DMatrix']
                mat_used=target_dict['CT'][self.series_index]['mat_maps'][item]['Material_used']
                for mat_key in mat_used.keys():
                    material=mat_used[mat_key]  
                    mat_info=self.Mat_df[self.Mat_df['Name']==material]
                    if not len(mat_info):
                        QMessageBox.warning(self, 'Warning', f'Material {material} not found in the material database. Skipping')
                        continue 
                    if map_type=='Density':
                        value=mat_info['Den'].values[0]
                    else:
                        value=mat_info[map_type].values[0]
                    density_matrix[mat_map_matrix==mat_key]=value
                    
    else:
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
            display_message_box('the CT calibraion curve needs to have at least two rows!')
    
            return
    
        density_matrix=compute_density(ct_matrix, ct_cal)
    
        #Retriving the type of map (density, spr, RED)
        headers = []
        for col in range(col_count):
            item = self.ct_cal_table.item(0, col)
            headers.append(item.text() if item else f"Column{col}")
            
        map_type=headers[1]
        
        #check if the override density is checked
        if self.override_no_tissue.isChecked():
            #check if material maps exists
            mat_maps=mat_maps=target_dict['CT'][self.series_index].get('mat_maps',{})
            if mat_maps:
                item, ok = QInputDialog.getItem(self, "Choose Material Map", "Select the material map:", list(mat_maps.keys()), 0, False)
                if item and ok:
                    mat_map_matrix= target_dict['CT'][self.series_index]['mat_maps'][item]['3DMatrix']
                    mat_used=target_dict['CT'][self.series_index]['mat_maps'][item]['Material_used']
                    for mat_key in mat_used.keys():
                        material=mat_used[mat_key]  
                        mat_info=self.Mat_df[self.Mat_df['Name']==material]
                        if not len(mat_info):
                            QMessageBox.warning(self, 'Warning', f'Material {material} not found in the material database. Skipping')
                            continue 
                        if mat_info['Tissue']:
                            if map_type=='DENSITY':
                                value=mat_info['Den'].values[0]
                            else:
                                value=mat_info[map_type].values[0]
                            density_matrix[mat_map_matrix==mat_key]=value
                            
            else:
                QMessageBox.critical(self, 'Error', 'No material maps found for this CT')
                
    #Checking if there are already any maps
    target=target_dict['CT'][self.series_index]
    existing = target.get('density_maps', {})
    if not existing:
        target['density_maps']={}
    #Creating the density map dict to store the information
    entry={'3DMatrix':density_matrix,
           'type':map_type}
    
    target['density_maps'][f'map_{map_type}_{len(existing)}']=entry
    populate_DICOM_tree(self)

        
    
    

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

def del_density_map(self):
    #various checks
    if self.patientID:
        target_dict=self.dicom_data[self.patientID][self.studyID]
    else:
        QMessageBox.critical(self, 'Error', 'No Patient selected')
        return
    try:
        target=target_dict['CT'][self.series_index]

    except:
        QMessageBox.critical(self, 'Error', 'No CT found')
        return
    density_maps=target.get('density_maps',{})
    if not density_maps:
        QMessageBox.critical(self, 'Error', 'No material maps found for this CT')
        return
        
    items = list(density_maps.keys())
    items.append('All')
    item, ok = QInputDialog.getItem(self, "Delete Density Map", "Select the density map to delete:", items, 0, False)
    if ok and item:
    # Remove from dict or list
        if item=='All':
            target['density_maps'].clear()
            message='All density maps have been deleted.'
        else:
            target['density_maps'].pop(item)
            message=f"Densit map '{item}' has been deleted."
        
        populate_DICOM_tree(self)
        
        QMessageBox.information(self, "Deleted", message)