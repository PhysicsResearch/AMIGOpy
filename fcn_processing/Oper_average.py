from PyQt5.QtWidgets import QMessageBox
from fcn_load.load_dcm   import populate_DICOM_tree
from fcn_load.read_IrIS  import populate_IrIS_tree
import numpy as np
import re

# Perform Im average
def average_slices(self):
    initial_slice = self.Proces_spinbox_01.value()
    final_slice   = self.Proces_spinbox_02.value()
    num_intervals = self.Proces_spinbox_03.value()

    # Check if final slice is greater than initial slice
    if final_slice <= initial_slice:
        QMessageBox.warning(self, "Parameter Error", "Final slice must be greater than initial slice.")
        return

    # Check if the number of slices is divisible by the number of intervals
    if (final_slice - initial_slice + 1) % num_intervals != 0:
        QMessageBox.warning(self, "Parameter Error", "The total number of slices is not divisible by the number of intervals.")
        return
    
    # Check file name
    name = re.sub(r'[\s\W]+', '', self.NewImageName.text())

    # Check if the name was modified
    if name != self.NewImageName.text():
        QMessageBox.warning(self, "File Name Modified", "Spaces and symbols have been removed from the file name.")
        self.NewImageName.setText(name)
        
    # Retrieve selected direction
    direction = self.Process_set_box.currentText()
    # Determine the axis for averaging
    axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]  
    
    # Create a list to hold the averaged slices
    averaged_slices = []
    # Calculate step size for slicing based on intervals
    step = (final_slice - initial_slice) // num_intervals
    # Iterate over the slices
    for i in range(initial_slice, final_slice, step):
        # Extract slices and compute the average
        if axis == 0:
            slice_avg = np.mean(self.display_data[i:i + step, :, :], axis=axis)
        elif axis == 1:
            slice_avg = np.mean(self.display_data[:, i:i + step, :], axis=axis)
        else:
            slice_avg = np.mean(self.display_data[:, :, i:i + step], axis=axis)
        averaged_slices.append(slice_avg)
    # Convert the list of slices to a 3D array
    averaged_image = np.stack(averaged_slices, axis=axis)
    
    # check the data type to add
    if self.DataType == "DICOM":
        new_series_data = {
            'SeriesNumber': name,
            'metadata': {
                'PixelSpacing':self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing'],
                'SliceThickness': self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SliceThickness']*step,
                'LUTLabel': 'AVR',
                'LUTExplanation': step,
                'WindowCenter': self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['WindowCenter'],
                'WindowWidth': self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['WindowWidth'],
                'RescaleSlope': self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['RescaleSlope'],
                'RescaleIntercept': self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['RescaleIntercept'] 
                }
            }
        new_series_data['3DMatrix'] = averaged_image.astype(np.int16)
        #medical_image[patient_id][study_id][modality].append(new_series_data)
        self.medical_image[self.patientID][self.studyID][self.modality].append(new_series_data)
        populate_DICOM_tree(self)
    elif self.DataType == "IrIS":
        new_series_data = {
                    '3DMatrix': averaged_image.astype(np.int16),
                    'mode': self.IrIS_data[self.patientID]['mode'],
                    'VxVy': self.IrIS_data[self.patientID]['VxVy'],
                    'binning': self.IrIS_data[self.patientID]['binning'],
                    'panel': self.IrIS_data[self.patientID]['panel'],
                    'average':self.IrIS_data[self.patientID]['average'],
                    'average_skip': self.IrIS_data[self.patientID]['average_skip'],
                    'delay': self.IrIS_data[self.patientID]['delay'],
                    'FOV': self.IrIS_data[self.patientID]['FOV'],
                    'C_offset': self.IrIS_data[self.patientID]['C_offset'],
                    'C_sens': self.IrIS_data[self.patientID]['C_sens'],
                    'C_sum': self.IrIS_data[self.patientID]['C_sum'],
                    'C_N_sum': self.IrIS_data[self.patientID]['C_N_sum'],
                    'fps': self.IrIS_data[self.patientID]['fps'],
                    'fps_id': self.IrIS_data[self.patientID]['fps_id'],
                    'Resolution': self.IrIS_data[self.patientID]['Resolution'],
                    'Diff': self.IrIS_data[self.patientID]['Diff'],
                    'AcquisitionTime': self.IrIS_data[self.patientID]['AcquisitionTime']     
                }
        self.IrIS_data[name] = new_series_data
        populate_IrIS_tree(self)
