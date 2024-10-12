import cv2
import numpy as np
from PyQt5.QtWidgets   import QApplication
from fcn_display.Data_tree_general import adjust_data_type_input
from fcn_display.display_images    import displayaxial, displaycoronal, displaysagittal
from fcn_processing.conver_clip_data  import convert_and_clip_data
from fcn_display.disp_data_type    import adjust_data_type_input

def normalize_image(self):
    """
    Normalizes the image to a specified range.

    :param alpha: Lower bound of the range. Default is 0.
    :param beta: Upper bound of the range. Default is 255.
    :param norm_type: Normalization type. Default is cv2.NORM_MINMAX.
    :return: Normalized image.
    """
    thres_L   = float(self.Proces_spinbox_01.value())
    thres_H   = float(self.Proces_spinbox_02.value())
    alpha     = self.Proces_spinbox_04.value()
    beta      = self.Proces_spinbox_05.value()
    # Convert to a floating-point type to handle negative values
    data_float = self.display_data.astype(np.float32)
    # Apply thresholds and subtraction
    data_float[data_float < thres_L] = thres_L
    data_float[data_float > thres_H] = thres_H
    data_float -= thres_L
    data_float /= (thres_H-thres_L)
    data_float += alpha
    data_float *= (beta-alpha)
    # #
    # data_uint16 = np.clip(data_float, 0, 65535).astype(np.uint16)
    # self.display_data = data_uint16
    self.display_data=convert_and_clip_data(data_float,self.Process_DataType_box.currentText())
    adjust_data_type_input(self)
    # # update display
    displayaxial(self)
    displaysagittal(self)
    displaycoronal(self) 
            
 

def equalize_histogram(self):
    """
    Applies histogram equalization to the image.

    :return: Image with equalized histogram.
    """
    # Converting to grayscale if the image is colored
    if len(self.display_data.shape) > 2:
        gray_image = cv2.cvtColor(self.display_data, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = self.display_data
    
    self.display_data = cv2.equalizeHist(gray_image)
    

def apply_clahe(self, clip_limit=2.0, tile_grid_size=(8, 8)):
    """
    Applies CLAHE to the image.

    :param clip_limit: Threshold for contrast limiting. Default is 2.0.
    :param tile_grid_size: Size of grid for histogram equalization. Default is (8, 8).
    :return: Image with applied CLAHE.
    """
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    if len(self.display_data.shape) > 2:
        # Converting to Lab color space for colored images
        lab = cv2.cvtColor(self.display_data, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = clahe.apply(l)
        merged_lab = cv2.merge((l, a, b))
        self.display_data = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)
    else:
        self.display_data = clahe.apply(self.display_data)




def standardize_image(self):
    """
    Standardizes the image by subtracting the mean and dividing by the standard deviation.

    :return: Standardized image.
    """
    mean, stddev = cv2.meanStdDev(self.display_data)
    self.display_data = (self.display_data - mean) / (stddev + 1e-6)
    

