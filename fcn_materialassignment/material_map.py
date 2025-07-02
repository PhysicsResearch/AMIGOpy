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
from fcn_load.populate_dcm_list import populate_DICOM_tree
from PyQt5.QtWidgets import QInputDialog, QMessageBox

def update_material_list(self):
    
    mat_names=self.Mat_df['Name'].to_numpy().tolist()
    self.Select_mat.clear()
    self.Select_mat.addItem('...Select material...')
    self.Select_mat.addItems(mat_names)
    


def mat2HU(self):
    if not hasattr(self, 'mat_HU'):
        self.mat_HU = {}
    # Get the text of the material selected
    mat_selected = self.Select_mat.currentText()
    if mat_selected == '...Select material...':
        QMessageBox.critical(self, 'Error', 'Select material')
        return
    # Retrieve the HU values
    try:
        max_HU = float(self.HU_high.text())
        min_HU = float(self.HU_low.text())
    except:
        QMessageBox.critical(self, 'Error', 'Enter valid HU values')
        return

    if min_HU >= max_HU:
        QMessageBox.critical(self, 'Error', 'Invalid range')
        return
    # Get the key from the dataframe
    try:
        key = self.Mat_df.index[self.Mat_df['Name'] == mat_selected][0]
    except IndexError:
        print('Material not found in dataframe')
        return
    self.mat_HU[mat_selected] = {'key': key, 'min': min_HU, 'max': max_HU}
    # Update the table after adding new data
    update_mat2HU_table(self)

def update_mat2HU_table(self):
    self.tableMatToHU.setRowCount(0)  # Clear table

    for row_idx, mat_name in enumerate(self.mat_HU.keys()):
        self.tableMatToHU.insertRow(row_idx)

        items = [
            QTableWidgetItem(mat_name),
            QTableWidgetItem(str(self.mat_HU[mat_name]['key'])),
            QTableWidgetItem(str(self.mat_HU[mat_name]['min'])),
            QTableWidgetItem(str(self.mat_HU[mat_name]['max']))
        ]

        for col_idx, item in enumerate(items):
            # Make all cells non-editable
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.tableMatToHU.setItem(row_idx, col_idx, item)

    self.tableMatToHU.resizeColumnsToContents()
    self.tableMatToHU.resizeRowsToContents()
    

def on_material_change(self):
    if hasattr(self, 'mat_HU'):
        current_text=self.Select_mat.currentText()
        if current_text in self.mat_HU.keys():
            self.HU_high.setText(str(self.mat_HU[current_text]['max']))
            self.HU_low.setText(str(self.mat_HU[current_text]['min']))
        else:
            self.HU_high.clear()
            self.HU_low.clear()
    else:
        self.HU_high.clear()
        self.HU_low.clear()
        
def check_mat2HU(self):
    #Sinc material assigned to HU values and Table
    #Check if materials have already been assigned
    if hasattr(self, 'mat_HU'):
        #Get backups
        keys_mat2HU = list(self.mat_HU.keys()) 
        keys_mat_tab=self.Mat_df['Name'].to_numpy()
        
        for key in keys_mat2HU:
            #If the key is in the material table, update he idx
            if key in keys_mat_tab:
                self.mat_HU[key]['key']=np.where(keys_mat_tab==key)[0].item()
            else:
                self.mat_HU.pop(key)
                QMessageBox.information(self, "Warning", f'The material {key} is no longer in the material table. Removing from assigned ranges')
        update_mat2HU_table(self)

def del_mat2HU(self):
    if hasattr(self, 'mat_HU'):
        selected_indexes = self.tableMatToHU.selectionModel().selectedRows()
        if selected_indexes:  # if any row is selected
            for index in sorted(selected_indexes, reverse=True):
                row = index.row()
                mat = self.tableMatToHU.item(row, 0).text()
                self.mat_HU.pop(mat, None)  # safer pop with default None
        else:  # if no row is selected, remove the last row
            last_row = self.tableMatToHU.rowCount() - 1
            if last_row >= 0:  # checking if there are any rows to remove
                mat = self.tableMatToHU.item(last_row, 0).text()
                self.mat_HU.pop(mat, None)

        update_mat2HU_table(self)
                
def generate_mat_map(self):

    #Retrive CT_info
    if self.patientID:
        target_dict=self.dicom_data[self.patientID][self.studyID]
    else:
        QMessageBox.critical(self, 'Error', 'No Patient selected')
        return
    try:
        ct_matrix=target_dict['CT'][self.series_index]['3DMatrix']

    except:
        QMessageBox.critical(self, 'Error', 'No CT found')
        return

    mat_used={}
    mat_map=np.full(ct_matrix.shape,-1,dtype=np.int16)
    
    #Assigning materials using HU ranges
    if hasattr(self,'mat_HU'):
        for mat in self.mat_HU.keys():
            min_val=self.mat_HU[mat]['min']
            max_val=self.mat_HU[mat]['max']
            ID= np.int16(self.mat_HU[mat]['key'])
            mat_map[(ct_matrix>=min_val) & (ct_matrix<max_val)]=ID
            mat_used[ID]=mat
    #Assign mat to structures: TBD
    #assigned unspecified voxels to water
    if len(mat_map[mat_map==-1])!=0:
        #Retriving index for water
        water_ID = np.int16(self.Mat_df.index[self.Mat_df['Name'] == 'Water'][0])
        mat_map[mat_map==-1]=water_ID
        mat_used[water_ID]='Water'
        QMessageBox.information(self,'Warning' ,'Unassigned voxels will be assigned to Water')
    
    #Store the material map
    target=target_dict['CT'][self.series_index]
    existing = target.get('mat_maps', {})
    if not existing:
        target['mat_maps']={}
    
    entry={'3DMatrix':mat_map,'Material_used':mat_used}
    target['mat_maps'][f'mat_map_{len(existing)}']=entry
    populate_DICOM_tree(self)
    

def update_mat_struct_list(self):
    target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    structure_names = target_series_dict.get('structures_names', [])
    if structure_names:
        self.Struct_list_mat.clear()
        self.Struct_list_mat.addItem('...Select Structure...')
        self.Struct_list_mat.addItems(structure_names)
    else:
        return
    

def delete_mat_map(self):
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
    mat_maps=target.get('mat_maps',{})
    if not mat_maps:
        QMessageBox.critical(self, 'Error', 'No material maps found for this CT')
        return
    items = list(mat_maps.keys())
    item, ok = QInputDialog.getItem(self, "Delete Material Map", "Select the material map to delete:", items, 0, False)
    if ok and item:
    # Remove from dict or list
        target['mat_maps'].pop(item)
        
        populate_DICOM_tree(self)
        
        QMessageBox.information(self, "Deleted", f"Material map '{item}' has been deleted.")



