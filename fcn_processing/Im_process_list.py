import numpy as np
from fcn_processing.Oper_average    import average_slices
from fcn_processing.Oper_inv_image  import invert_images
from fcn_processing.denoise_methods import (apply_gaussian_filter, apply_median_filter, apply_percentile_filter, apply_maximum_filter, apply_minimum_filter, apply_wiener_filter, apply_fourier_gaussian_filter,
                                           apply_gaussian_gradient_filter, apply_gaussian_laplace_filter, apply_sobel_filter, apply_denoise_wavelet, apply_denoise_tv_chambolle, apply_rolling_ball, apply_denoise_nl_means,
                                           apply_denoise_bilateral, apply_prewitt_filter,apply_denoise_wavelet,apply_bm3d_denoising)

from fcn_processing.cv_norm_methods import normalize_image
from fcn_display.display_images     import displayaxial, displaycoronal, displaysagittal
from PyQt5.QtWidgets import QMessageBox

def on_operation_selected(self, index):
    # Dictionary mapping operations to their descriptions
    operation_descriptions = {
        "Average": "This function averages consecutive frames. The user needs to specify the first and last frame to average, along with the number of intervals.",
        "Invert Image": "This function inverts the colors of the image, transforming each pixel value to its opposite within the image's color space.",
        "Thresholding": "This operation applies a threshold to the image, segmenting it into parts based on pixel intensity. The user can define the threshold value.",
        "ROI Selection": "This tool allows users to select a Region of Interest (ROI) in the image. Users can draw a shape (rectangle, circle, etc.) to specify the ROI.",
        "Denoise Gaussian": "Apply Gaussian filter from scipy.ndimage for smoothing the image"
        # Add more operations and their descriptions as needed
    }

    # Get the selected operation
    selected_operation = self.process_list.currentText()

    # Update the QTextEdit with the description of the selected operation
    self.Func_description.setText(operation_descriptions.get(selected_operation, "No description available"))
    
    # reset all
    self.Proces_label_01.setText("")
    self.Proces_label_02.setText("")
    self.Proces_label_03.setText("")
    self.Proces_label_04.setText("")
    self.Proces_label_05.setText("")
    self.Proces_label_06.setText("")
    self.Process_set_box.clear()
    self.Process_set_box.setEnabled(False)
    self.Process_set_box2.clear()
    self.Process_set_box2.setEnabled(False)
    self.Process_set_box3.clear()
    self.Process_set_box3.setEnabled(False)
    #
    self.Proces_spinbox_01.setEnabled(False)
    self.Proces_spinbox_02.setEnabled(False)
    self.Proces_spinbox_03.setEnabled(False)
    self.Proces_spinbox_04.setEnabled(False)
    self.Proces_spinbox_05.setEnabled(False)
    self.Proces_spinbox_06.setEnabled(False)
    #
    self.Proces_spinbox_01.setValue(0)
    self.Proces_spinbox_02.setValue(0)
    self.Proces_spinbox_03.setValue(0)
    self.Proces_spinbox_04.setValue(0)
    self.Proces_spinbox_05.setValue(0)
    self.Proces_spinbox_06.setValue(0) 
    
    if selected_operation == "Invert Image":
        self.Proces_label_01.setText("Max. Value")
        direction = ["Data type", "Max. Value", "User"]
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        self.Proces_spinbox_01.setEnabled(True)
        #
    elif selected_operation == "Average":
        self.Proces_label_01.setText("Initial slice")
        self.Proces_label_02.setText("Final slice")
        self.Proces_label_03.setText("N intervals")

        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        
        self.Proces_spinbox_01.setEnabled(True)
        self.Proces_spinbox_02.setEnabled(True)
        self.Proces_spinbox_03.setEnabled(True)

    elif selected_operation == "Denoise Gaussian":
        self.Proces_label_01.setText("Sigma X")
        self.Proces_label_02.setText("Sigma Y")
        self.Proces_label_03.setText("Sigma Z")
        self.Proces_label_04.setText("Order")
        self.Proces_label_05.setText("cval")
        self.Proces_label_06.setText("truncate")
        
        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.clear()
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        
        mode = ["reflect", "constant", "nearest", "mirror", "wrap"]
        self.Process_set_box2.clear()
        self.Process_set_box2.addItems(mode)
        self.Process_set_box2.setEnabled(True)
        
        type_op = ["2D","3D"]
        self.Process_set_box3.clear()
        self.Process_set_box3.addItems(type_op)
        self.Process_set_box3.setEnabled(True)
        
        self.Proces_spinbox_01.setEnabled(True)
        self.Proces_spinbox_02.setEnabled(True)
        self.Proces_spinbox_03.setEnabled(True)
        self.Proces_spinbox_04.setEnabled(True)
        self.Proces_spinbox_05.setEnabled(True)
        self.Proces_spinbox_06.setEnabled(True)
        #
        self.Proces_spinbox_01.setValue(1)
        self.Proces_spinbox_02.setValue(1)
        self.Proces_spinbox_03.setValue(1)
        self.Proces_spinbox_04.setValue(0)
        self.Proces_spinbox_05.setValue(0)
        self.Proces_spinbox_06.setValue(4)
        #
    elif selected_operation == "Denoise Median":
        self.Proces_label_01.setText("Size X")
        self.Proces_label_02.setText("Size Y")
        self.Proces_label_03.setText("Size Z")
        self.Proces_label_04.setText("Origin")
        self.Proces_label_05.setText("cval")
        
        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        
        mode = ["reflect", "constant", "nearest", "mirror", "wrap"]
        self.Process_set_box2.addItems(mode)
        self.Process_set_box2.setEnabled(True)
        
        type_op = ["2D","3D"]
        self.Process_set_box3.clear()
        self.Process_set_box3.addItems(type_op)
        self.Process_set_box3.setEnabled(True)
        
        self.Proces_spinbox_01.setEnabled(True)
        self.Proces_spinbox_02.setEnabled(True)
        self.Proces_spinbox_03.setEnabled(True)
        self.Proces_spinbox_04.setEnabled(True)
        self.Proces_spinbox_05.setEnabled(True)
        #
        self.Proces_spinbox_01.setValue(5)
        self.Proces_spinbox_02.setValue(5)
        self.Proces_spinbox_03.setValue(5)
        self.Proces_spinbox_04.setValue(0)
        self.Proces_spinbox_05.setValue(0)
        #               
    elif selected_operation == "Denoise Percentile":
        self.Proces_label_01.setText("Size X")
        self.Proces_label_02.setText("Size Y")
        self.Proces_label_03.setText("Size Z")
        self.Proces_label_04.setText("Origin")
        self.Proces_label_05.setText("cval")
        self.Proces_label_06.setText("Percentile")
        
        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.clear()
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        
        mode = ["reflect", "constant", "nearest", "mirror", "wrap"]
        self.Process_set_box2.clear()
        self.Process_set_box2.addItems(mode)
        self.Process_set_box2.setEnabled(True)
        
        type_op = ["2D","3D"]
        self.Process_set_box3.clear()
        self.Process_set_box3.addItems(type_op)
        self.Process_set_box3.setEnabled(True)
        
        self.Proces_spinbox_01.setEnabled(True)
        self.Proces_spinbox_02.setEnabled(True)
        self.Proces_spinbox_03.setEnabled(True)
        self.Proces_spinbox_04.setEnabled(True)
        self.Proces_spinbox_05.setEnabled(True)
        self.Proces_spinbox_06.setEnabled(True)
        #
        self.Proces_spinbox_01.setValue(5)
        self.Proces_spinbox_02.setValue(5)
        self.Proces_spinbox_03.setValue(5)
        self.Proces_spinbox_04.setValue(0)
        self.Proces_spinbox_05.setValue(0)
        self.Proces_spinbox_06.setValue(90)        
    #    
    elif selected_operation == "Denoise Min." or selected_operation == "Denoise Max.":  
        self.Proces_label_01.setText("Size X")
        self.Proces_label_02.setText("Size Y")
        self.Proces_label_03.setText("Size Z")
        self.Proces_label_04.setText("Origin")
        self.Proces_label_05.setText("cval")
        self.Proces_label_06.setText("")
        
        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.clear()
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        
        mode = ["reflect", "constant", "nearest", "mirror", "wrap"]
        self.Process_set_box2.clear()
        self.Process_set_box2.addItems(mode)
        self.Process_set_box2.setEnabled(True)
        
        type_op = ["2D","3D"]
        self.Process_set_box3.clear()
        self.Process_set_box3.addItems(type_op)
        self.Process_set_box3.setEnabled(True)
        
        self.Proces_spinbox_01.setEnabled(True)
        self.Proces_spinbox_02.setEnabled(True)
        self.Proces_spinbox_03.setEnabled(True)
        self.Proces_spinbox_04.setEnabled(True)
        self.Proces_spinbox_05.setEnabled(True)
        #
        self.Proces_spinbox_01.setValue(5)
        self.Proces_spinbox_02.setValue(5)
        self.Proces_spinbox_03.setValue(5)
        self.Proces_spinbox_04.setValue(0)
        self.Proces_spinbox_05.setValue(0)       
        #    
    elif selected_operation == "Sobel":  
        self.Proces_label_01.setText("Axis")
        self.Proces_label_02.setText("cval")
        
        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        
        mode = ["reflect", "constant", "nearest", "mirror", "wrap"]
        self.Process_set_box2.addItems(mode)
        self.Process_set_box2.setEnabled(True)
        
        type_op = ["2D","3D"]
        self.Process_set_box3.clear()
        self.Process_set_box3.addItems(type_op)
        self.Process_set_box3.setEnabled(True)
        
        self.Proces_spinbox_01.setEnabled(True)
        self.Proces_spinbox_02.setEnabled(True)
        #
        self.Proces_spinbox_01.setValue(0)
        self.Proces_spinbox_02.setValue(0)    
    # 
    elif selected_operation == "Prewitt":  
        self.Proces_label_01.setText("Axis")        
        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.clear()
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        
        mode = ["reflect", "constant", "nearest", "mirror", "wrap"]
        self.Process_set_box2.addItems(mode)
        self.Process_set_box2.setEnabled(True)
        
        type_op = ["2D","3D"]
        self.Process_set_box3.addItems(type_op)
        self.Process_set_box3.setEnabled(True)
        self.Proces_spinbox_01.setEnabled(True)
        #
        self.Proces_spinbox_01.setValue(0)
        #
    elif selected_operation == "TV Chambolle":  
        self.Proces_label_01.setText("Weight")
        
        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.clear()
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        
        mode = ["reflect", "constant", "nearest", "mirror", "wrap"]
        self.Process_set_box2.addItems(mode)
        self.Process_set_box2.setEnabled(True)
        
        type_op = ["2D","3D"]
        self.Process_set_box3.clear()
        self.Process_set_box3.addItems(type_op)
        self.Process_set_box3.setEnabled(True)
        
        self.Proces_spinbox_01.setEnabled(True)
        #
        self.Proces_spinbox_01.setValue(0.1)
        #
    elif selected_operation == "Rolling ball":  
        self.Proces_label_01.setText("Radius")
        
        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.clear()
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        
        mode = ["reflect", "constant", "nearest", "mirror", "wrap"]
        self.Process_set_box2.clear()
        self.Process_set_box2.addItems(mode)
        self.Process_set_box2.setEnabled(True)
        
        type_op = ["2D","3D"]
        self.Process_set_box3.clear()
        self.Process_set_box3.addItems(type_op)
        self.Process_set_box3.setEnabled(True)
        
        self.Proces_spinbox_01.setEnabled(True)
        #
        self.Proces_spinbox_01.setValue(15)
        #
    elif selected_operation == "Bilateral":  
        self.Proces_label_01.setText("Sigma Col.")
        self.Proces_label_02.setText("Sigma Spa.")
        
        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.clear()
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
               
        type_op = ["2D","3D"]
        self.Process_set_box3.clear()
        self.Process_set_box3.addItems(type_op)
        self.Process_set_box3.setEnabled(True)
        
        self.Proces_spinbox_01.setEnabled(True)
        self.Proces_spinbox_02.setEnabled(True)
        #
        self.Proces_spinbox_01.setValue(0.2)
        self.Proces_spinbox_02.setValue(15)
        #
    elif selected_operation == "NL means":  
        self.Proces_label_01.setText("Patch size")
        self.Proces_label_02.setText("Patch dist.")
        self.Proces_label_03.setText("h")
        
        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        type_op = ["2D","3D"]
        self.Process_set_box3.addItems(type_op)
        self.Process_set_box3.setEnabled(True)
        #
        self.Proces_spinbox_01.setEnabled(True)
        self.Proces_spinbox_02.setEnabled(True)
        self.Proces_spinbox_03.setEnabled(True)
        #
        self.Proces_spinbox_01.setValue(7)
        self.Proces_spinbox_02.setValue(11)
        self.Proces_spinbox_03.setValue(0.1)
        #             
    elif selected_operation == "Wiener":  
        self.Proces_label_01.setText("Size X")
        self.Proces_label_02.setText("Size Y")
        self.Proces_label_03.setText("Size Z")
        self.Proces_label_04.setText("Noise")
        self.Proces_label_05.setText("")
        self.Proces_label_06.setText("")
        
        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.clear()
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        
        mode = ["reflect", "constant", "nearest", "mirror", "wrap"]
        self.Process_set_box2.clear()
        self.Process_set_box2.addItems(mode)
        self.Process_set_box2.setEnabled(True)
        
        type_op = ["2D","3D"]
        self.Process_set_box3.clear()
        self.Process_set_box3.addItems(type_op)
        self.Process_set_box3.setEnabled(True)
        
        self.Proces_spinbox_01.setEnabled(True)
        self.Proces_spinbox_02.setEnabled(True)
        self.Proces_spinbox_03.setEnabled(True)
        self.Proces_spinbox_04.setEnabled(True)
        self.Proces_spinbox_05.setEnabled(False)
        self.Proces_spinbox_06.setEnabled(False)
        #
        self.Proces_spinbox_01.setValue(1)
        self.Proces_spinbox_02.setValue(0)
        self.Proces_spinbox_03.setValue(0)
        self.Proces_spinbox_04.setValue(0)
        self.Proces_spinbox_05.setValue(0)
        self.Proces_spinbox_06.setValue(0)    
    #  
    elif selected_operation == "FFT Gaussian" or selected_operation == "Gaussian Grad." or selected_operation == "Gaussian Laplace" or selected_operation == "Wavelet":  
        self.Proces_label_01.setText("Sigma")

        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.clear()
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        
        self.Process_set_box2.clear()
        self.Process_set_box2.setEnabled(False)
        
        type_op = ["2D","3D"]
        self.Process_set_box3.clear()
        self.Process_set_box3.addItems(type_op)
        self.Process_set_box3.setEnabled(True)
        
        self.Proces_spinbox_01.setEnabled(True)
        #
        self.Proces_spinbox_01.setValue(1)
    elif selected_operation == "BM3D":
        self.Proces_label_01.setText("Sigma")
         
        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.clear()
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)

         
        type_op = ["2D","3D"]
        self.Process_set_box3.clear()
        self.Process_set_box3.addItems(type_op)
        self.Process_set_box3.setEnabled(True)
         
        self.Proces_spinbox_01.setEnabled(True)

        #
        self.Proces_spinbox_01.setValue(20)

        #
    elif selected_operation == "Normalize":
        self.Proces_label_01.setText("Thresh Min.")
        self.Proces_label_02.setText("Thresh Max.")
        self.Proces_label_03.setText("")
        self.Proces_label_04.setText("Norm. Min")
        self.Proces_label_05.setText("Norm. Max")
        self.Proces_label_06.setText("")
        
        direction = ["Axial", "Sagittal", "Coronal"]
        self.Process_set_box.clear()
        self.Process_set_box.addItems(direction)
        self.Process_set_box.setEnabled(True)
        
        self.Proces_spinbox_01.setEnabled(True)
        self.Proces_spinbox_02.setEnabled(True)
        self.Proces_spinbox_03.setEnabled(False)
        self.Proces_spinbox_04.setEnabled(True)
        self.Proces_spinbox_05.setEnabled(True)
        self.Proces_spinbox_06.setEnabled(False)
        
        self.Proces_spinbox_01.setValue(np.min(self.display_data))
        self.Proces_spinbox_02.setValue(np.max(self.display_data))
        self.Proces_spinbox_03.setValue(0)
        self.Proces_spinbox_04.setValue(0)
        self.Proces_spinbox_05.setValue(255)
        self.Proces_spinbox_06.setValue(0)      
        
        d_type = ["int8","uint8","int16","uint16","int32","uint32","int64","uint64","float","double"]
        self.Process_DataType_box.clear()
        self.Process_DataType_box.addItems(d_type)
        self.Process_DataType_box.setEnabled(True)
        
        
        
        
def run_image_processing(self):
    idx = self.layer_selection_box.currentIndex()
    if idx not in self.display_data:
        QMessageBox.warning(None, "Warning", "No image data was found.")
        return
    self.display_data_undo = self.display_data[idx].copy()
    #
    if     self.process_list.currentText()== "Invert Image":
        invert_images(self)
    elif   self.process_list.currentText()== "Average":
        average_slices(self)
    elif self.process_list.currentText()== "Denoise Gaussian":  
        apply_gaussian_filter(self)
    elif self.process_list.currentText()== "Denoise Median":  
        apply_median_filter(self)
    elif self.process_list.currentText()== "Denoise Percentile":  
        apply_percentile_filter(self)
    elif self.process_list.currentText()== "Denoise Max.":  
        apply_maximum_filter(self) 
    elif self.process_list.currentText()== "Denoise Min.":  
        apply_minimum_filter(self)
    elif self.process_list.currentText()== "Wiener":  
        apply_wiener_filter(self)      
    elif self.process_list.currentText()== "FFT Gaussian": 
        apply_fourier_gaussian_filter(self) 
    elif self.process_list.currentText()== "Gaussian Grad.":  
        apply_gaussian_gradient_filter(self)      
    elif self.process_list.currentText()== "Gaussian Laplace": 
        apply_gaussian_laplace_filter(self)
    elif self.process_list.currentText()== "Sobel": 
        apply_sobel_filter(self) 
    elif self.process_list.currentText()== "Prewitt": 
        apply_prewitt_filter(self) 
    elif self.process_list.currentText()== "Wavelet": 
        apply_denoise_wavelet(self)      
    elif self.process_list.currentText()== "TV Chambolle": 
        apply_denoise_tv_chambolle(self)      
    elif self.process_list.currentText()== "Rolling ball": 
        apply_rolling_ball(self)      
    elif self.process_list.currentText()== "Bilateral": 
        apply_denoise_bilateral(self)      
    elif self.process_list.currentText()== "NL means": 
        apply_denoise_nl_means(self)
    elif self.process_list.currentText()== "BM3D": 
        apply_bm3d_denoising(self)               
    elif self.process_list.currentText()== "Normalize":  
        normalize_image(self)    
    # update display
    displayaxial(self)
    displaysagittal(self)
    displaycoronal(self)   

def image_processing_undo(self): 
    idx = self.layer_selection_box.currentIndex()
    self.display_data[idx] = self.display_data_undo.copy()
    if self.DataType == "IrIS":
        self.IrIS_data[self.patientID]['3DMatrix'] = self.display_data[idx]
    elif self.DataType == "DICOM" or self.DataType == "Nifti":
        self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix'] = self.display_data[idx]   
    # update display
    displayaxial(self)
    displaysagittal(self)
    displaycoronal(self)   