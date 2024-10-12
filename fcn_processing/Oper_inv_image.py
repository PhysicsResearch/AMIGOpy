import numpy as np
from fcn_display.display_images  import displayaxial, displaycoronal, displaysagittal


# Perform Im average
def invert_images(self):

    max_value     = self.Proces_spinbox_01.value()

    # Retrieve selected direction
    Norm_type = self.Process_set_box.currentText()
    # Determine the axis for averaging
    M_type = {'Data type': 0, 'Max. Value': 1, 'User': 2}[Norm_type]  
    if   M_type == 0:
        max_value = set_max_value_based_on_dtype(self.display_data)
    elif M_type == 1:
        max_value = np.max(self.display_data)
    
    for slice_index in range(self.display_data.shape[0]):
        self.display_data[slice_index, :, :] = max_value - self.display_data[slice_index, :, :]
        
    displayaxial(self)
    displaysagittal(self)
    displaycoronal(self)    
        

def set_max_value_based_on_dtype(image):
    if np.issubdtype(image.dtype, np.floating):
        # For floating point types (like float64, float32)
        max_value = np.max(image)
    elif np.issubdtype(image.dtype, np.integer):
        # For integer types (like int32, int64)
        max_value = np.iinfo(image.dtype).max
    else:
        max_value = np.max(image)
        raise TypeError("Unsupported data type")

    return max_value
