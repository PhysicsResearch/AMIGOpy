import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication
from fcn_display.display_images  import displayaxial, displaycoronal, displaysagittal

def apply_gaussian_blur(self):
    # Initialize kernel_size as a list
    kernel_size = [0, 0]
    sigma       = [0, 0]
    kernel_size[0]= int(self.Proces_spinbox_01.value())
    kernel_size[1]= int(self.Proces_spinbox_02.value())
    sigma[0]      = int(self.Proces_spinbox_03.value())
    sigma[1]      = int(self.Proces_spinbox_04.value())
    # Retrieve selected direction
    direction = self.Process_set_box.currentText()
    # Determine the axis for averaging
    axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
    #
    num_slices = self.display_data.shape[axis]
    #
    self.progressBar.setValue(0)
    # Process Qt events to update GUI
    QApplication.processEvents()    
            
    # Apply Gaussian blur along the specified axis
    for i in range(num_slices):
        if axis == 0:
            self.display_data[i, :, :] = cv2.GaussianBlur(self.display_data[i, :, :], kernel_size, sigma[0],sigma[1])
        elif axis == 1:
            self.display_data[:, i, :] = cv2.GaussianBlur(self.display_data[:, i, :], kernel_size, sigma[0],sigma[1])
        elif axis == 2:
            self.display_data[:, :, i] = cv2.GaussianBlur(self.display_data[:, :, i], kernel_size, sigma[0],sigma[1])
        # Update progress bar every 10 slices
        if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
            progress_percentage = int((i + 1) / num_slices * 100)
            self.progressBar.setValue(progress_percentage)
            # Process Qt events to update GUI
            QApplication.processEvents()        
    # update display
    displayaxial(self)
    displaysagittal(self)
    displaycoronal(self)   

def apply_median_filtering(self):
    # Retrieve filter size from spin box
    filter_size = int(self.Proces_spinbox_01.value())  # Assuming odd integer value

    # Retrieve selected direction
    direction = self.Process_set_box.currentText()
    axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]

    num_slices = self.display_data.shape[axis]
    self.progressBar.setValue(0)

    for i in range(num_slices):
        slice_selector = [slice(None)] * 3  # Create a slice for all dimensions
        slice_selector[axis] = i  # Set the current slice for the specified axis
        self.display_data[tuple(slice_selector)] = cv2.medianBlur(self.display_data[tuple(slice_selector)], filter_size)

        # Update progress bar every 20 slices
        if i % 20 == 0 or i == num_slices - 1:
            self.progressBar.setValue(int((i + 1) / num_slices * 100))
            QApplication.processEvents()
    # update display
    displayaxial(self)
    displaysagittal(self)
    displaycoronal(self)  
    
def apply_bilateral_filtering(self):
    # Retrieve parameters from spin boxes
    d = int(self.Proces_spinbox_01.value())
    sigmaColor = int(self.Proces_spinbox_02.value())
    sigmaSpace = int(self.Proces_spinbox_03.value())
    # Save original data type and range
    original_dtype = self.display_data.dtype
    max_val = np.iinfo(original_dtype).max if np.issubdtype(original_dtype, np.integer) else 1.0
    
    # Normalize and convert image to float32 for processing
    image_float32 = (self.display_data / max_val).astype(np.float32)
    # Retrieve selected direction
    direction = self.Process_set_box.currentText()
    axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]

    num_slices = self.display_data.shape[axis]
    self.progressBar.setValue(0)

    # Apply Bilateral filtering along the specified axis
    for i in range(num_slices):
        if axis == 0:
            self.display_data[i, :, :] = cv2.bilateralFilter(image_float32[i, :, :], d, sigmaColor, sigmaSpace)
        elif axis == 1:
            self.display_data[:, i, :] = cv2.bilateralFilter(image_float32[:, i, :], d, sigmaColor, sigmaSpace)
        elif axis == 2:
            self.display_data[:, :, i] = cv2.bilateralFilter(image_float32[:, :, i], d, sigmaColor, sigmaSpace)

        # Update progress bar every 20 slices
        if i % 20 == 0 or i == num_slices - 1:
            progress_percentage = int((i + 1) / num_slices * 100)
            self.progressBar.setValue(progress_percentage)
            QApplication.processEvents()
            
    #Rescale the processed image back to its original range and data type
    self.display_data = (image_float32 * max_val).astype(original_dtype)

        
    # update display
    displayaxial(self)
    displaysagittal(self)
    displaycoronal(self)
    
    
def apply_non_local_means_denoising(self):
    # Retrieve parameters from spin boxes
    h = float(self.Proces_spinbox_01.value())
    templateWindowSize = int(self.Proces_spinbox_02.value())
    searchWindowSize = int(self.Proces_spinbox_03.value())

    # Retrieve selected direction
    direction = self.Process_set_box.currentText()
    axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]

    num_slices = self.display_data.shape[axis]
    self.progressBar.setValue(0)

    # Apply non-local means denoising along the specified axis
    for i in range(num_slices):
        if axis == 0:
            self.display_data[i, :, :] = cv2.fastNlMeansDenoising(self.display_data[i, :, :], None, h, templateWindowSize, searchWindowSize)
        elif axis == 1:
            self.display_data[:, i, :] = cv2.fastNlMeansDenoising(self.display_data[:, i, :], None, h, templateWindowSize, searchWindowSize)
        elif axis == 2:
            self.display_data[:, :, i] = cv2.fastNlMeansDenoising(self.display_data[:, :, i], None, h, templateWindowSize, searchWindowSize)

        # Update progress bar every 20 slices
        if i % 20 == 0 or i == num_slices - 1:
            progress_percentage = int((i + 1) / num_slices * 100)
            self.progressBar.setValue(progress_percentage)
            QApplication.processEvents()

    # update display
    displayaxial(self)
    displaysagittal(self)
    displaycoronal(self)    
    
    