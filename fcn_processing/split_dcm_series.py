import numpy as np
from fcn_load.load_dcm import populate_DICOM_tree
import tkinter as tk
from tkinter import simpledialog
import copy
import pydicom
from pydicom.dataset import Dataset
from pydicom.dataelem import DataElement


def shift_and_split_3D_matrix(self):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    intervals = simpledialog.askinteger("Input", "Enter number of intervals:")
    root.destroy()
    if intervals is None:
        raise ValueError("No valid number of intervals provided")

    # Retrieve the original data
    original_matrix = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix']
    slice_image_comments = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['SliceImageComments']
    image_patient_positions = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]['ImagePositionPatients']

    # Determine the number of frames in each new matrix
    total_frames = original_matrix.shape[0]
    frames_per_matrix = total_frames // intervals

    # Ensure the matrix can be evenly split
    if total_frames % intervals != 0:
        raise ValueError(f"The data cannot be evenly split into {intervals} matrices.")
    
    # Split the original data into smaller segments
    split_matrices = np.array_split(original_matrix, intervals)
    split_slice_image_comments = np.array_split(slice_image_comments, intervals)
    split_image_patient_positions = np.array_split(image_patient_positions, intervals)
    
    # Copy the rest of the data from the original series index
    original_data = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index].copy()

    # Ensure the list is long enough to accommodate new indices
    required_length = len(self.dicom_data[self.patientID][self.studyID][self.modality]) + intervals
    while len(self.dicom_data[self.patientID][self.studyID][self.modality]) < required_length:
        self.dicom_data[self.patientID][self.studyID][self.modality].append(None)

    # Shift existing series indices down to make space
    for i in range(len(self.dicom_data[self.patientID][self.studyID][self.modality]) - 1, self.series_index, -1):
        if self.dicom_data[self.patientID][self.studyID][self.modality][i] is not None:
            self.dicom_data[self.patientID][self.studyID][self.modality][i + intervals] = self.dicom_data[self.patientID][self.studyID][self.modality][i]
            self.dicom_data[self.patientID][self.studyID][self.modality][i] = None
    #
    # Update the series index to reflect the new series
    orig_series_str = original_data['SeriesNumber']


    # Store the split data into new series indices
    for i in range(intervals):
        new_series_index = self.series_index + i
        self.dicom_data[self.patientID][self.studyID][self.modality][new_series_index] = copy.deepcopy(original_data)
        self.dicom_data[self.patientID][self.studyID][self.modality][new_series_index]['3DMatrix'] = split_matrices[i]
        self.dicom_data[self.patientID][self.studyID][self.modality][new_series_index]['SliceImageComments'] = split_slice_image_comments[i]
        self.dicom_data[self.patientID][self.studyID][self.modality][new_series_index]['ImagePositionPatients'] = split_image_patient_positions[i]
        self.dicom_data[self.patientID][self.studyID][self.modality][new_series_index]['metadata']['ImageComments'] = split_slice_image_comments[i][0]
        self.dicom_data[self.patientID][self.studyID][self.modality][new_series_index]['SeriesNumber']= f"{int(orig_series_str)}__{i}"
        image_comment = str(split_slice_image_comments[i][0])
        data_element = DataElement((0x0020, 0x4000), 'LO', image_comment)
        self.dicom_data[self.patientID][self.studyID][self.modality][new_series_index]['metadata']['DCM_Info']['ImageComments'] = data_element

        
    # Remove the original series index data
    self.dicom_data[self.patientID][self.studyID][self.modality].pop(self.series_index + intervals)
   
    populate_DICOM_tree(self)
  