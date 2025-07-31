# -*- coding: utf-8 -*-
import numpy as np
import vtk
from fcn_load.populate_dcm_list import populate_DICOM_tree
import fcn_load.load_dcm
from copy import deepcopy
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem,QTableWidgetItem
from scipy.ndimage import gaussian_filter1d
from scipy.signal import savgol_filter
from fcn_dosecalculations.general_fcn import scale_dose_to_CT
import matplotlib.pyplot as plt #ONLY FOR TESTING



def to_EQD2(D,fractions,ab):
    d=D/fractions
    dose_EQD2=D*((d+ab)/(2+ab))
    return dose_EQD2



def convert_dose_matrix_to_EQD2(dose_matrix,structures,ab_values,fractions,default_ab=3):
    #create ab matrix
    ab_matrix=np.full(dose_matrix.shape, default_ab)
    
    for structure,ab in zip(structures,ab_values):
        ab_matrix[structure==1]=ab
    #plt.imshow(ab_matrix[73,:,:])
    return to_EQD2(dose_matrix,fractions,ab_matrix)

def display_message_box(title,msg):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.exec()

def on_struct_list_change(self):
    if self.patientID:
        target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
        structure_selected = self.eqd2_struct_list.currentText()
        ab_dict=target_series_dict.get('ab_values')
        if structure_selected!='None' and ab_dict: 
            if structure_selected in ab_dict.keys():
                current_ab_val=target_series_dict['ab_values'][structure_selected]
                self.ab_input.setText(str(current_ab_val))
            else:
                self.ab_input.clear()
        else:
            self.ab_input.clear()
        

def add_ab(self):
    # Creating a dictionary reference for the target series
    if self.patientID:
        target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
        
        structure_selected = self.eqd2_struct_list.currentText()
        ab_selected = self.ab_input.text()
        
        if structure_selected!='None' and ab_selected:
    
            try:
                ab_value = float(ab_selected)  # Convert to float
            except ValueError:
                display_message_box('α/β values', 'please enter a valid α/β ratio')
                return  # Exit function if input is invalid
        
            # Ensure 'ab_values' exists in the dictionary
            if 'ab_values' not in target_series_dict:
                target_series_dict['ab_values'] = {}
        
            # Add/update the structure's alpha-beta value
            target_series_dict['ab_values'][structure_selected] = ab_value
        
            # Call function to update the table
            update_alpha_beta_table(self)
        else:
            display_message_box('missing input data', 'please select a valid structure and enter a valid valid α/β ratio')
    else:
        display_message_box('select patient', 'no active patient found')

def delete_ab(self):
    target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    
    structure_selected = self.eqd2_struct_list.currentText()
    
    if structure_selected!='None':
        #check if ab valuses exixt
        if 'ab_values' in target_series_dict:
            #check if the structure was already added
            if structure_selected in target_series_dict['ab_values']:
                target_series_dict['ab_values'].pop(structure_selected)
                update_alpha_beta_table(self)
            else:
                display_message_box('missing input data', 'The structure does not exist')
        else:
            display_message_box('missing input data', 'no structure found')
            
    else:
        display_message_box('missing input data', 'please select a valid structure to delete')
    


def update_alpha_beta_table(self):
    # Get the dictionary containing alpha-beta values
    target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    ab_values = target_series_dict.get('ab_values', {})

    # Clear table before updating
    self.ab_table.setRowCount(0)

    # Populate the table with updated values
    for row, (structure, ab_value) in enumerate(ab_values.items()):
        self.ab_table.insertRow(row)
        self.ab_table.setItem(row, 0, QTableWidgetItem(structure))
        self.ab_table.setItem(row, 1, QTableWidgetItem(str(ab_value)))

    self.ab_table.resizeColumnsToContents()

def update_doses_list(self):
    #Update dose list to list the dose of the current active patient and study
    if self.patientID and self.studyID:
        try:
            dose_list=self.dicom_data[self.patientID][self.studyID]['RTDOSE'] #TBF: not sure if it works if no dose is loaded
            if len(dose_list):
                labels=[f"{dose['metadata']['SeriesDescription']}_Series: {dose['SeriesNumber']}" for dose in dose_list]
                self.dose_list.clear()
                self.dose_list.addItems(['None'])
                self.dose_list.addItems(labels)
        except:
            return

def update_structure_list(self):
    if self.patientID and self.studyID:
        if self.modality=='CT':
            target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
            structure_names = target_series_dict.get('structures_names', [])
            if structure_names:
                self.eqd2_struct_list.clear()
                self.eqd2_struct_list.addItems(['None'])
                self.eqd2_struct_list.addItems(structure_names)
            else:
                display_message_box('missing data', 'no structure found')
        else:
            display_message_box('select CT set', 'select CT set to procede')
    else:
       display_message_box('select patient', 'no active patient found')

def generate_eqd2_dose(self):
     #Retrive dose slected
     if self.patientID:
         target_dict=self.dicom_data[self.patientID][self.studyID]['RTDOSE']
         dose_selected = self.dose_list.currentText()
         struct_list=self.dicom_data[self.patientID][self.studyID]['CT'][self.series_index].get('ab_values',{})
         print(struct_list)
         if dose_selected!='None':
             if len(struct_list):
                 
                 dose_idx=dose_selected.split(':')[1].strip()
                 dose = next( d for d in target_dict if d['SeriesNumber'] == dose_idx)
                 dose_matrix=dose['3DMatrix']
                 #check the dimensions of the dose matrix, if they are not the same as the CT, scale it
                 if dose_matrix.size!=self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix'].size:
                     dose_matrix=scale_dose_to_CT(self,dose)
                     print('dose rescaled')
                 
                 #Retrive binary masks
                 masks = [s['Mask3D'] for s in self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['structures'].values() if s.get('Name') in struct_list]
                 ab_coeff=[v for v in struct_list.values()]
                 
                 #add here EQD2 
                 fractions=self.input_fractions.text()
                 if fractions:
                     try:
                         fractions=float(fractions)
                     except:
                         display_message_box('invalid input', 'select a valid number of fractions')
                         return
                
                     dose_matrix_eqd2=convert_dose_matrix_to_EQD2(dose_matrix,masks,ab_coeff,fractions,default_ab=3)
                     
                     #add dose to the tree
            
                     eqd2_dose=deepcopy(dose)
            
                     eqd2_dose['3DMatrix']=dose_matrix_eqd2
                     eqd2_dose['metadata']['SeriesDescription']=f"EQD2_{dose['metadata']['SeriesDescription']}"
                     ref_value = np.max(dose_matrix_eqd2)
                     eqd2_dose['metadata']['WindowWidth'] = ref_value*0.02
                     eqd2_dose['metadata']['WindowCenter']= ref_value*0.80
                     eqd2_dose['metadata']['PixelSpacing']=self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing']
                     eqd2_dose['metadata']['SliceThickness']=self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SliceThickness']
                     eqd2_dose['metadata']['ImagePositionPatient']=self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['ImagePositionPatient']
                     print(eqd2_dose['metadata']['ImagePositionPatient'])
                     target_dict.append(eqd2_dose)
                     populate_DICOM_tree(self)
                     print('dose added')
                 else:
                     display_message_box('missing input data', 'enter the number of fractions')
             else:
                display_message_box('missing input data', 'define α/β ratios first')
             
    
         else:
             display_message_box('missing input data', 'select a valid dose first')
     else:
        display_message_box('select patient', 'no active patient found')
     
     
def eqd2_calc(self):
    total_dose=self.input_total_dose.text()
    fractions=self.input_frac_calc.text()
    ab_value=self.input_ab_calculator.text()
    
    if total_dose and fractions and ab_value:
        try:
            total_dose=float(total_dose)
            fractions=float(fractions)
            ab_value=float(ab_value)
        except:
            display_message_box('invalid input', 'please insert valid values')
            return
        eqd2=to_EQD2(total_dose,fractions,ab_value)
        self.eqd2_out.display(np.round(eqd2,3))
    else:
        display_message_box('missing input', 'please insert valid values')
