from scipy.ndimage import (gaussian_filter, median_filter, percentile_filter, maximum_filter, minimum_filter, fourier_gaussian, 
                           gaussian_gradient_magnitude,gaussian_laplace, sobel)
from scipy.signal import wiener
from skimage.restoration import denoise_wavelet, denoise_tv_chambolle, rolling_ball, denoise_nl_means, denoise_bilateral
from skimage.filters import prewitt
import numpy as np
#from bm3d import bm3d
from PyQt5.QtWidgets import QApplication


def apply_gaussian_filter(self):
    order     = int(self.Proces_spinbox_04.value())
    cval      = int(self.Proces_spinbox_05.value())
    truncate  = int(self.Proces_spinbox_06.value())
    mode      = self.Process_set_box2.currentText()
    idx       = self.layer_selection_box.currentIndex()
    # Initialize kernel_size as a list
    if    self.Process_set_box3.currentText() == "2D":
        sigma     = [0, 0]
        sigma[0]  = self.Proces_spinbox_01.value()
        sigma[1]  = self.Proces_spinbox_02.value()
        #    
        # Retrieve selected direction
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()    
                
        # Apply Gaussian blur along the specified axis
        for i in range(num_slices):
            if axis == 0:
                self.display_data[idx][i, :, :] = gaussian_filter(self.display_data[idx][i, :, :], sigma=sigma, order=order, mode=mode, cval=cval, truncate=truncate)
            elif axis == 1:
                self.display_data[idx][:, i, :] = gaussian_filter(self.display_data[idx][:, i, :], sigma=sigma, order=order, mode=mode, cval=cval, truncate=truncate)
            elif axis == 2:
                self.display_data[idx][:, :, i] = gaussian_filter(self.display_data[idx][:, :, i], sigma=sigma, order=order, mode=mode, cval=cval, truncate=truncate)
            # Update progress bar every 10 slices
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()     
    elif  self.Process_set_box3.currentText() == "3D":
        sigma     = [0, 0, 0]
        sigma[0]  = self.Proces_spinbox_01.value()
        sigma[1]  = self.Proces_spinbox_02.value()
        sigma[2]  = self.Proces_spinbox_03.value()
        self.display_data[idx] = gaussian_filter(self.display_data[idx], sigma=sigma, order=order, mode=mode, cval=cval, truncate=truncate)
    #
    

def apply_median_filter(self):
    origin   = int(self.Proces_spinbox_04.value())
    cval      = int(self.Proces_spinbox_05.value())
    mode      = self.Process_set_box2.currentText()
    idx       = self.layer_selection_box.currentIndex()
    # Initialize size as a list based on the dimensionality
    if self.Process_set_box3.currentText() == "2D":
        size = [
            int(self.Proces_spinbox_01.value()),
            int(self.Proces_spinbox_02.value())
        ]
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()    
                
        # Apply Gaussian blur along the specified axis
        for i in range(num_slices):
            if axis == 0:
                self.display_data[idx][i, :, :] = median_filter(self.display_data[idx][i, :, :], size=size, mode=mode, cval=cval, origin=origin)
            elif axis == 1:
                self.display_data[idx][:, i, :] = median_filter(self.display_data[idx][:, i, :], size=size, mode=mode, cval=cval, origin=origin)
            elif axis == 2:
                self.display_data[idx][:, :, i] = median_filter(self.display_data[idx][:, :, i], size=size, mode=mode, cval=cval, origin=origin)
            # Update progress bar every 10 slices
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()     

    elif self.Process_set_box3.currentText() == "3D":
        size = [
            int(self.Proces_spinbox_01.value()),
            int(self.Proces_spinbox_02.value()),
            int(self.Proces_spinbox_03.value())
        ]
        self.display_data[idx] = median_filter(self.display_data[idx], size=size, mode=mode, cval=cval, origin=origin)

def apply_percentile_filter(self):
    origin     = int(self.Proces_spinbox_04.value())
    cval       = int(self.Proces_spinbox_05.value())
    mode       = self.Process_set_box2.currentText()
    idx        = self.layer_selection_box.currentIndex()
    percentile = int(self.Proces_spinbox_06.value())  # Example: Add a spinbox for percentile    
    if percentile < 0 or percentile > 100:
        raise ValueError("Percentile must be between 0 and 100")
    #    
    # Initialize size as a list based on the dimensionality
    if self.Process_set_box3.currentText() == "2D":
        size = [
            int(self.Proces_spinbox_01.value()),
            int(self.Proces_spinbox_02.value())
        ]
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()    
                
        # Apply Gaussian blur along the specified axis
        for i in range(num_slices):
            if axis == 0:
                self.display_data[idx][i, :, :] = percentile_filter(self.display_data[idx][i, :, :], percentile=percentile, size=size, mode=mode, cval=cval, origin=origin)
            elif axis == 1:
                self.display_data[idx][:, i, :] = percentile_filter(self.display_data[idx][:, i, :], percentile=percentile, size=size, mode=mode, cval=cval, origin=origin)
            elif axis == 2:
                self.display_data[idx][:, :, i] = percentile_filter(self.display_data[idx][:, :, i], percentile=percentile, size=size, mode=mode, cval=cval, origin=origin)
            # Update progress bar every 10 slices
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()     
    elif self.Process_set_box3.currentText() == "3D":
        size = [
            int(self.Proces_spinbox_01.value()),
            int(self.Proces_spinbox_02.value()),
            int(self.Proces_spinbox_03.value())
        ]
        self.display_data[idx] = percentile_filter(self.display_data[idx], percentile=percentile, size=size, mode=mode, cval=cval, origin=origin)

def apply_maximum_filter(self):
    origin     = int(self.Proces_spinbox_04.value())
    cval       = int(self.Proces_spinbox_05.value())
    mode       = self.Process_set_box2.currentText()
    idx        = self.layer_selection_box.currentIndex()
    #    
    # Initialize size as a list based on the dimensionality
    if self.Process_set_box3.currentText() == "2D":
        size = [
            int(self.Proces_spinbox_01.value()),
            int(self.Proces_spinbox_02.value())
        ]
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()    
                
        # Apply Gaussian blur along the specified axis
        for i in range(num_slices):
            if axis == 0:
                self.display_data[idx][i, :, :] = maximum_filter(self.display_data[idx][i, :, :], size=size, mode=mode, cval=cval, origin=origin)
            elif axis == 1:
                self.display_data[idx][:, i, :] = maximum_filter(self.display_data[idx][:, i, :], size=size, mode=mode, cval=cval, origin=origin)
            elif axis == 2:
                self.display_data[idx][:, :, i] = maximum_filter(self.display_data[idx][:, :, i], size=size, mode=mode, cval=cval, origin=origin)
            # Update progress bar every 10 slices
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()     
    elif self.Process_set_box3.currentText() == "3D":
        size = [
            int(self.Proces_spinbox_01.value()),
            int(self.Proces_spinbox_02.value()),
            int(self.Proces_spinbox_03.value())
        ]
        self.display_data[idx] = maximum_filter(self.display_data[idx], size=size, mode=mode, cval=cval, origin=origin)

def apply_minimum_filter(self):
    origin     = int(self.Proces_spinbox_04.value())
    cval       = int(self.Proces_spinbox_05.value())
    mode       = self.Process_set_box2.currentText()
    idx        = self.layer_selection_box.currentIndex() 
    #    
    # Initialize size as a list based on the dimensionality
    if self.Process_set_box3.currentText() == "2D":
        size = [
            int(self.Proces_spinbox_01.value()),
            int(self.Proces_spinbox_02.value())
        ]
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()    
                
        # Apply Gaussian blur along the specified axis
        for i in range(num_slices):
            if axis == 0:
                self.display_data[idx][i, :, :] = maximum_filter(self.display_data[idx][i, :, :], size=size, mode=mode, cval=cval, origin=origin)
            elif axis == 1:
                self.display_data[idx][:, i, :] = maximum_filter(self.display_data[idx][:, i, :], size=size, mode=mode, cval=cval, origin=origin)
            elif axis == 2:
                self.display_data[idx][:, :, i] = maximum_filter(self.display_data[idx][:, :, i], size=size, mode=mode, cval=cval, origin=origin)
            # Update progress bar every 10 slices
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()     
    elif self.Process_set_box3.currentText() == "3D":
        size = [
            int(self.Proces_spinbox_01.value()),
            int(self.Proces_spinbox_02.value()),
            int(self.Proces_spinbox_03.value())
        ]
        self.display_data[idx] = maximum_filter(self.display_data[idx], size=size, mode=mode, cval=cval, origin=origin)
        

def apply_wiener_filter(self):
    idx        = self.layer_selection_box.currentIndex() 
    # Get the noise value and set to None if negative
    noise = float(self.Proces_spinbox_04.value())
    if noise < 0:
        noise = None
    # Initialize mysize as a list based on the dimensionality
    if self.Process_set_box3.currentText() == "2D":
        size = [
            int(self.Proces_spinbox_01.value()),
            int(self.Proces_spinbox_02.value())
        ]
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()    
                
        # Apply Gaussian blur along the specified axis
        for i in range(num_slices):
            if axis == 0:
                self.display_data[idx][i, :, :] = wiener(self.display_data[idx][i, :, :], mysize=size, noise=noise)
            elif axis == 1:
                self.display_data[idx][:, i, :] = wiener(self.display_data[idx][:, i, :], mysize=size, noise=noise)
            elif axis == 2:
                self.display_data[idx][:, :, i] = wiener(self.display_data[idx][:, :, i], mysize=size, noise=noise)
            # Update progress bar every 10 slices
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()  
    elif self.Process_set_box3.currentText() == "3D":
        size = [
            int(self.Proces_spinbox_01.value()),
            int(self.Proces_spinbox_02.value()),
            int(self.Proces_spinbox_03.value())
        ]
        self.display_data[idx] = wiener(self.display_data[idx], mysize=size, noise=noise)

def apply_fourier_gaussian_filter(self):
    sigma = float(self.Proces_spinbox_01.value())  # Example: Add a spinbox for Gaussian sigma
    idx        = self.layer_selection_box.currentIndex() 
    # Get the noise value and set to None if negative
    noise = float(self.Proces_spinbox_04.value())
    if noise < 0:
        noise = None
    # Initialize mysize as a list based on the dimensionality
    if self.Process_set_box3.currentText() == "2D":
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()    
                
        # Apply Gaussian blur along the specified axis
        for i in range(num_slices):
            if axis == 0:
                f_transform = np.fft.fftn(self.display_data[idx][i, :, :])
                f_transform_filtered = fourier_gaussian(f_transform, sigma=sigma)
                self.display_data[idx][i, :, :] = np.real(np.fft.ifftn(f_transform_filtered))
            elif axis == 1:
                f_transform = np.fft.fftn(self.display_data[idx][:, i, :])
                f_transform_filtered = fourier_gaussian(f_transform, sigma=sigma)
                self.display_data[idx][:, i, :] = np.real(np.fft.ifftn(f_transform_filtered))
            elif axis == 2:
                f_transform = np.fft.fftn(self.display_data[idx][:, :, i])
                f_transform_filtered = fourier_gaussian(f_transform, sigma=sigma)
                self.display_data[idx][:, :, i] = np.real(np.fft.ifftn(f_transform_filtered))
            # Update progress bar every 10 slices
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()  
    elif self.Process_set_box3.currentText() == "3D":
        f_transform = np.fft.fftn(self.display_data[idx])
        f_transform_filtered = fourier_gaussian(f_transform, sigma=sigma)
        self.display_data[idx] = np.real(np.fft.ifftn(f_transform_filtered))


def apply_gaussian_gradient_filter(self):
    sigma = float(self.Proces_spinbox_01.value())  # Example: Add a spinbox for Gaussian sigma
    idx        = self.layer_selection_box.currentIndex() 
    # Get the noise value and set to None if negative
    noise = float(self.Proces_spinbox_04.value())
    if noise < 0:
        noise = None
    # Initialize mysize as a list based on the dimensionality
    if self.Process_set_box3.currentText() == "2D":
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()    
                
        # Apply Gaussian blur along the specified axis
        for i in range(num_slices):
            if axis == 0:
               self.display_data[idx][i, :, :]  = gaussian_gradient_magnitude(self.display_data[idx][i, :, :], sigma=sigma)
            elif axis == 1:
               self.display_data[idx][:, i, :]  = gaussian_gradient_magnitude(self.display_data[idx][:, i, :], sigma=sigma)
            elif axis == 2:
               self.display_data[idx][:, :, i]  = gaussian_gradient_magnitude(self.display_data[idx][:, :, i], sigma=sigma)
            # Update progress bar every 10 slices
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()  
    elif self.Process_set_box3.currentText() == "3D":
       self.display_data[idx]  = gaussian_gradient_magnitude(self.display_data[idx], sigma=sigma)
       
       
       
def apply_gaussian_laplace_filter(self):
    sigma = float(self.Proces_spinbox_01.value())  # Example: Add a spinbox for Gaussian sigma
    idx        = self.layer_selection_box.currentIndex() 
    # Get the noise value and set to None if negative
    noise = float(self.Proces_spinbox_04.value())
    if noise < 0:
        noise = None
    # Initialize mysize as a list based on the dimensionality
    if self.Process_set_box3.currentText() == "2D":
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()    
                
        # Apply Gaussian blur along the specified axis
        for i in range(num_slices):
            if axis == 0:
               self.display_data[idx][i, :, :]  = gaussian_laplace(self.display_data[idx][i, :, :], sigma=sigma)
            elif axis == 1:
               self.display_data[idx][:, i, :]  = gaussian_laplace(self.display_data[idx][:, i, :], sigma=sigma)
            elif axis == 2:
               self.display_data[idx][:, :, i]  = gaussian_laplace(self.display_data[idx][:, :, i], sigma=sigma)
            # Update progress bar every 10 slices
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()  
    elif self.Process_set_box3.currentText() == "3D":
       self.display_data[idx]  = gaussian_laplace(self.display_data[idx], sigma=sigma)       
       
       
def apply_sobel_filter(self):
    axis = int(self.Proces_spinbox_01.value()) 
    idx  = self.layer_selection_box.currentIndex() 
    mode       = self.Process_set_box2.currentText()
    # Get the noise value and set to None if negative
    cval = float(self.Proces_spinbox_02.value())
    # Initialize mysize as a list based on the dimensionality
    if self.Process_set_box3.currentText() == "2D":
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()    
                
        # Apply Gaussian blur along the specified axis
        for i in range(num_slices):
            if axis == 0:
               self.display_data[idx][i, :, :]  = sobel(self.display_data[idx][i, :, :], axis=axis,mode=mode,cval=cval)
            elif axis == 1:
               self.display_data[idx][:, i, :]  = sobel(self.display_data[idx][:, i, :], axis=axis,mode=mode,cval=cval)
            elif axis == 2:
               self.display_data[idx][:, :, i]  = sobel(self.display_data[idx][:, :, i], axis=axis,mode=mode,cval=cval)
            # Update progress bar every 10 slices
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()  
    elif self.Process_set_box3.currentText() == "3D":
       self.display_data[idx]  = sobel(self.display_data[idx], axis=axis,mode=mode,cval=cval)
    
    
    
def apply_denoise_wavelet(self):
    idx  = self.layer_selection_box.currentIndex() 
    # sigma: Standard deviation of the noise.
    # wavelet: Type of wavelet to use (default is 'db1').
    sigma = float(self.Proces_spinbox_01.value())  
    # 
    if self.Process_set_box3.currentText() == "2D":
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()    
                
        # Apply Gaussian blur along the specified axis
        for i in range(num_slices):
            if axis == 0:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][i, :, :])
               denoised = denoise_wavelet(image, sigma=sigma)
               self.display_data[idx][i, :, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype)  
            elif axis == 1:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, i, :])
               denoised = denoise_wavelet(image, sigma=sigma)
               self.display_data[idx][:, i, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype)  
            elif axis == 2:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, :, i])
               denoised = denoise_wavelet(image, sigma=sigma)
               self.display_data[idx][:, :, i] = postprocess_image(denoised, min_val, ptp_val, original_dtype)  
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()  
    elif self.Process_set_box3.currentText() == "3D":
        # Preprocess, denoise, and postprocess
        image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx])
        denoised = denoise_wavelet(image, sigma=sigma)
        self.display_data[idx] = postprocess_image(denoised, min_val, ptp_val, original_dtype)  
    
    

def apply_denoise_tv_chambolle(self):
    idx  = self.layer_selection_box.currentIndex() 
    # weight: Denoising weight. Higher values remove more noise but also more details.
    weight = float(self.Proces_spinbox_01.value())  # Example: Add a spinbox for weight
    # 
    if self.Process_set_box3.currentText() == "2D":
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()    
                
        # Apply Gaussian blur along the specified axis
        for i in range(num_slices):
            if axis == 0:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][i, :, :])
               denoised = denoise_tv_chambolle(image, weight=weight)
               self.display_data[idx][i, :, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype) 
            elif axis == 1:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, i, :])
               denoised = denoise_tv_chambolle(image, weight=weight)
               self.display_data[idx][:, i, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype) 
            elif axis == 2:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, :, i])
               denoised = denoise_tv_chambolle(image, weight=weight)
               self.display_data[idx][:, :, i] = postprocess_image(denoised, min_val, ptp_val, original_dtype) 
            #   
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()  
    elif self.Process_set_box3.currentText() == "3D":
        # Preprocess, denoise, and postprocess
        image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx])
        denoised = denoise_tv_chambolle(image, weight=weight)
        self.display_data[idx] = postprocess_image(denoised, min_val, ptp_val, original_dtype) 

    
def apply_rolling_ball(self):
    idx  = self.layer_selection_box.currentIndex() 
    # radius: Radius of the ball. Larger values remove larger structures.
    radius = float(self.Proces_spinbox_01.value())  # Example: Add a spinbox for radius
    # 
    if self.Process_set_box3.currentText() == "2D":
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()            
        # 
        for i in range(num_slices):
            if axis == 0:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][i, :, :])
               denoised = rolling_ball(image, radius=radius)
               self.display_data[idx][i, :, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype) 
            elif axis == 1:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, i, :])
               denoised = rolling_ball(image, radius=radius)
               self.display_data[idx][:, i, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype) 
            elif axis == 2:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, :, i])
               denoised = rolling_ball(image, radius=radius)
               self.display_data[idx][:, :, i] = postprocess_image(denoised, min_val, ptp_val, original_dtype) 
            #   
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()  
    elif self.Process_set_box3.currentText() == "3D":
        # Preprocess, denoise, and postprocess
        image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx])
        denoised = rolling_ball(image, radius=radius)
        self.display_data[idx] = postprocess_image(denoised, min_val, ptp_val, original_dtype) 

    
def apply_denoise_nl_means(self):
    idx  = self.layer_selection_box.currentIndex()
    # patch_size: Size of patches used for denoising.
    # patch_distance: Maximal distance in pixels where to search patches used for denoising.
    # h: Cut-off distance (in gray levels).
    patch_size = int(self.Proces_spinbox_01.value())  
    patch_distance = int(self.Proces_spinbox_02.value()) 
    h = float(self.Proces_spinbox_03.value()) 
    # 
    if self.Process_set_box3.currentText() == "2D":
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()            
        # 
        for i in range(num_slices):
            if axis == 0:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][i, :, :])
               denoised = denoise_nl_means(image, patch_size=patch_size, patch_distance=patch_distance, h=h)
               self.display_data[idx][i, :, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype)  
            elif axis == 1:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, i,:])
               denoised = denoise_nl_means(image, patch_size=patch_size, patch_distance=patch_distance, h=h)
               self.display_data[idx][:, i, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype) 
            elif axis == 2:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, :, i])
               denoised = denoise_nl_means(image, patch_size=patch_size, patch_distance=patch_distance, h=h)
               self.display_data[idx][:, :, i] = postprocess_image(denoised, min_val, ptp_val, original_dtype) 
            #   
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()  
    elif self.Process_set_box3.currentText() == "3D":
        # Preprocess, denoise, and postprocess
        image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx])
        denoised = denoise_nl_means(image, patch_size=patch_size, patch_distance=patch_distance, h=h)
        self.display_data[idx] = postprocess_image(denoised, min_val, ptp_val, original_dtype) 

 
def apply_denoise_bilateral(self):
    idx = self.layer_selection_box.currentIndex()
    sigma_color = float(self.Proces_spinbox_01.value())  # Example: Add a spinbox for sigma_color
    sigma_spatial = float(self.Proces_spinbox_02.value())  # Example: Add a spinbox for sigma_spatial

    if self.Process_set_box3.currentText() == "2D":
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        num_slices = self.display_data[idx].shape[axis]

        self.progressBar.setValue(0)
        QApplication.processEvents()
        for i in range(num_slices):
            if axis == 0:
                # Preprocess, denoise, and postprocess
                image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][i, :, :])
                denoised = denoise_bilateral(image, sigma_color=sigma_color, sigma_spatial=sigma_spatial)
                self.display_data[idx][i, :, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype)
            elif axis == 1:
                # Preprocess, denoise, and postprocess
                image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, i, :])
                denoised = denoise_bilateral(image, sigma_color=sigma_color, sigma_spatial=sigma_spatial)
                self.display_data[idx][:, i, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype)
            elif axis == 2:
                # Preprocess, denoise, and postprocess
                image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, :, i])
                denoised = denoise_bilateral(image, sigma_color=sigma_color, sigma_spatial=sigma_spatial)
                self.display_data[idx][:, :, i] = postprocess_image(denoised, min_val, ptp_val, original_dtype)    
            # Update progress bar
            if i % 20 == 0 or i == num_slices - 1:  # Update every 20 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                QApplication.processEvents()
            #
    elif self.Process_set_box3.currentText() == "3D":
        # Preprocess, denoise, and postprocess
        image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx])
        denoised = denoise_bilateral(image, sigma_color=sigma_color, sigma_spatial=sigma_spatial, multichannel=False)
        self.display_data[idx] = postprocess_image(denoised, min_val, ptp_val, original_dtype)
    
    
    
def apply_prewitt_filter(self):
    idx  = self.layer_selection_box.currentIndex()
    axis = int(self.Proces_spinbox_01.value()) 
    # 
    if self.Process_set_box3.currentText() == "2D":
        #
        direction = self.Process_set_box.currentText()
        # Determine the axis for averaging
        axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
        #
        num_slices = self.display_data[idx].shape[axis]
        #
        self.progressBar.setValue(0)
        # Process Qt events to update GUI
        QApplication.processEvents()            
        # 
        for i in range(num_slices):
            if axis == 0:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][i, :, :])
               denoised = prewitt(image, axis=axis)
               self.display_data[idx][i, :, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype)
            elif axis == 1:
               # Preprocess, denoise, and postprocess
               image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, i, :])
               denoised = prewitt(image, axis=axis)
               self.display_data[idx][:, i, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype)
            elif axis == 2:
                # Preprocess, denoise, and postprocess
                image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, :, i])
                denoised = prewitt(image, axis=axis)
                self.display_data[idx][:, :, i] = postprocess_image(denoised, min_val, ptp_val, original_dtype)
            #   
            if i % 20 == 0 or i == num_slices - 1:  # Update every 10 slices or on the last slice
                progress_percentage = int((i + 1) / num_slices * 100)
                self.progressBar.setValue(progress_percentage)
                # Process Qt events to update GUI
                QApplication.processEvents()  
    elif self.Process_set_box3.currentText() == "3D":
        # Preprocess, denoise, and postprocess
        image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx])
        denoised = prewitt(image, axis=axis)
        self.display_data[idx] = postprocess_image(denoised, min_val, ptp_val, original_dtype)
       
def apply_bm3d_denoising(self):
    idx = self.layer_selection_box.currentIndex()
    # sigma_psd  = float(self.Proces_spinbox_01.value())     # Standard deviation of the noise
    # #
    # if self.Process_set_box3.currentText() == "2D":
    #     direction = self.Process_set_box.currentText()
    #     # Determine the axis for averaging
    #     axis = {'Axial': 0, 'Sagittal': 2, 'Coronal': 1}[direction]
    #     num_slices = self.display_data[idx].shape[axis]

    #     self.progressBar.setValue(0)
    #     QApplication.processEvents()

    #     for i in range(num_slices):
    #         if axis == 0:
    #             # Preprocess, denoise, and postprocess
    #             image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][i, :, :])
    #             denoised = bm3d(image, sigma_psd)
    #             self.display_data[idx][i, :, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype)
    #         elif axis == 1:
    #             # Preprocess, denoise, and postprocess
    #             image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, i, :])
    #             denoised = bm3d(image, sigma_psd)
    #             self.display_data[idx][:, i, :] = postprocess_image(denoised, min_val, ptp_val, original_dtype)
    #         elif axis == 2:
    #             # Preprocess, denoise, and postprocess
    #             image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx][:, :, i])
    #             denoised = bm3d(image, sigma_psd)
    #             self.display_data[idx][:, :, i] = postprocess_image(denoised, min_val, ptp_val, original_dtype)
            
    #         # Update progress bar
    #         if i % 20 == 0 or i == num_slices - 1:  # Update every 20 slices or on the last slice
    #             progress_percentage = int((i + 1) / num_slices * 100)
    #             self.progressBar.setValue(progress_percentage)
    #             QApplication.processEvents()
                
    # elif self.Process_set_box3.currentText() == "3D":
    #     # Preprocess, denoise, and postprocess
    #     image, min_val, ptp_val, original_dtype = preprocess_image(self.display_data[idx])
    #     denoised = bm3d(image, sigma_psd, stage_arg=stage_arg, block=block, step=step, group_size=group_size, beta=beta)
    #     self.display_data[idx] = postprocess_image(denoised, min_val, ptp_val, original_dtype)

def preprocess_image(image):
    original_dtype = image.dtype
    image = image.astype(np.float64)
    
    # Normalize the image to [0, 1]
    min_val = np.min(image)
    ptp_val = np.ptp(image)  # peak-to-peak (max - min)
    if ptp_val == 0:
        ptp_val = 1  # Avoid division by zero
    image -= min_val
    image /= ptp_val
    
    return image, min_val, ptp_val, original_dtype

def postprocess_image(image, min_val, ptp_val, original_dtype):
    # Scale back to the original range
    image *= ptp_val
    image += min_val
    
    # Convert back to the original data type
    if np.issubdtype(original_dtype, np.integer):
        info = np.iinfo(original_dtype)  # Get the limits for integer types
        image = np.clip(image, info.min, info.max)
    elif np.issubdtype(original_dtype, np.floating):
        info = np.finfo(original_dtype)  # Get the limits for float types
        image = np.clip(image, info.min, info.max)
    
    return image.astype(original_dtype)
    
    
    
    
    