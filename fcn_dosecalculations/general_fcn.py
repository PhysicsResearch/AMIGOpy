# -*- coding: utf-8 -*-
#General functions used for dose calculations file

import numpy as np
import vtk
from fcn_load.populate_med_image_list import populate_medical_image_tree
import fcn_load.load_dcm
from PyQt5.QtWidgets import QMessageBox
from scipy.ndimage import gaussian_filter1d
from scipy.signal import savgol_filter
#import SimpleITK as sitk
from scipy.interpolate import RegularGridInterpolator

def look_for_dose_data():
    pass

def scale_dose_to_CT(self,dose):
    
    #retriving information for scaling
    dose_spacing=np.array(dose['metadata']['PixelSpacing'])
    dose_spacing=np.append(dose_spacing,dose['metadata']['SliceThickness'])
    dose_matrix=dose['3DMatrix']
    dose_origin=np.array(dose['metadata']['ImagePositionPatient'])
    print(dose_origin)
    
    ct_spacing=np.array(self.medical_image[self.patientID][self.studyID]['CT'][self.series_index]['metadata']['PixelSpacing'])
    ct_spacing=np.append(ct_spacing,self.medical_image[self.patientID][self.studyID]['CT'][self.series_index]['metadata']['SliceThickness'])
    ct_origin=np.array(self.medical_image[self.patientID][self.studyID]['CT'][self.series_index]['metadata']['ImagePositionPatient'])
    ct_matrix=self.medical_image[self.patientID][self.studyID]['CT'][self.series_index]['3DMatrix']
    ct_shape=self.medical_image[self.patientID][self.studyID]['CT'][self.series_index]['3DMatrix'].shape
    print(f"Dose Origin: {dose_origin}")
    print(f"CT Origin: {ct_origin}")
    print(f"Dose Spacing: {dose_spacing}")
    print(f"CT Spacing: {ct_spacing}")
    #Creating dose simpleITK image 
    # dose_image = sitk.GetImageFromArray(dose_matrix[:,::-1,:])#Ask Gabriel?
    # dose_image.SetSpacing(dose_spacing)
    # dose_image.SetOrigin(dose_origin)

    # ct_image=sitk.GetImageFromArray(ct_matrix[:,::-1,:])#Ask Gabriel?
    # ct_image.SetSpacing(ct_spacing)
    # ct_image.SetOrigin(ct_origin)


    # # resampled_image = resampler.Execute(dose_image)
    # resampled_image = sitk.Resample(dose_image, ct_image)
    # #get back dose array
    # dose_array_resampled = sitk.GetArrayFromImage(resampled_image)


    # return dose_array_resampled[:,::-1,:]

