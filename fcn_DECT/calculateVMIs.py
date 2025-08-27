import numpy as np
import copy
from fcn_load.populate_med_image_list import populate_medical_image_tree
from pydicom.dataelem import DataElement
from PyQt5.QtWidgets import QMessageBox


def calculate_VMI(self):
    if getattr(self, 'DataType', None) != "DICOM":
        QMessageBox.warning(None, "Warning", "No DICOM data was found")
        return
    selected_index_L = self.scatter_plot_im_01.currentIndex()
    series_label_L, patient_id_L, study_id_L, modality_L, item_index_L = self.series_info_dict[selected_index_L]      
    # Get HU_High
    selected_index_H = self.scatter_plot_im_02.currentIndex()
    series_label_H, patient_id_H, study_id_H, modality_H, item_index_H = self.series_info_dict[selected_index_H]  
    # Assuming the reference image is a 3D NumPy array
    ct_low  = self.medical_image[patient_id_L][study_id_L][modality_L][item_index_L]['3DMatrix'].astype(np.float32)
    ct_high = self.medical_image[patient_id_H][study_id_H][modality_H][item_index_H]['3DMatrix'].astype(np.float32)


    # list of attenuation coefficients (NIST) --> replace with calibration values
    energies = np.arange(40, 200, 10)
    mu_water = np.array([
    0.2683,  # 40 keV
    0.2269,  # 50 keV
    0.2059,  # 60 keV
    0.1948,  # 70 keV (interp)
    0.1837,  # 80 keV
    0.1772,  # 90 keV (interp)
    0.1707,  # 100 keV
    0.1606,  # 110 keV (interp)
    0.1505,  # 120 keV (approx, between 100 & 150)
    0.1505,  # 130 keV (interp)
    0.1505,  # 140 keV (interp)
    0.1505,  # 150 keV
    0.1438,  # 160 keV (interp)
    0.1370,  # 170 keV (interp)
    0.1370,  # 180 keV (interp)
    0.1370   # 190 keV (interp)
    ])

    mu_iodine = np.array([
    22.10,  # 40 keV
    12.32,  # 50 keV
    7.579,  # 60 keV
    5.5445, # 70 keV (interp)
    3.510,  # 80 keV
    2.726,  # 90 keV (interp)
    1.942,  # 100 keV
    1.3199, # 110 keV (interp)
    0.6978, # 120 keV (approx)
    0.6978, # 130 keV (interp)
    0.6978, # 140 keV (interp)
    0.6978, # 150 keV
    0.5310, # 160 keV (interp)
    0.3663, # 170 keV (interp)
    0.3663, # 180 keV (interp)
    0.3663  # 190 keV (interp)
    ])

    # indicate energies of used for decomposition
    i_low, i_high = energies.tolist().index(60), energies.tolist().index(100) # 60 keV and 100 keV
    A = np.array([
        [mu_water[i_low], mu_iodine[i_low]],
        [mu_water[i_high], mu_iodine[i_high]]
    ])

    # HU --> attenuation coefficent (mu)
    mu_low = ((ct_low / 1000) + 1) * mu_water[i_low]
    mu_high = ((ct_high / 1000) + 1) * mu_water[i_high]

    muL = mu_low.reshape(-1)
    muH = mu_high.reshape(-1)
    B = np.stack([muL, muH])  # shape (2, N)

    X = np.linalg.solve(A, B)
    water_map = X[0, :].reshape(ct_low.shape)
    iodine_map = X[1, :].reshape(ct_low.shape)

    # Clip negative values
    water_map[water_map < 0] = 0
    iodine_map[iodine_map < 0] = 0
    
    # store iodine and water maps for visualization
    # copy the header of the low image ... in the future some tags will be adjusted
    original_data = self.dicom_data[patient_id_L][study_id_L][modality_L][item_index_L].copy()
    required_length = len(self.dicom_data[patient_id_L][study_id_L][modality_L]) + 1
    while len(self.dicom_data[patient_id_L][study_id_L][modality_L]) < required_length:
        self.dicom_data[patient_id_L][study_id_L][modality_L].append(None)
    # Store data into new series indice
    self.dicom_data[patient_id_L][study_id_L][modality_L][required_length-1]                              = copy.deepcopy(original_data)
    self.dicom_data[patient_id_L][study_id_L][modality_L][required_length-1]['3DMatrix']                  = water_map.astype(np.float32)
    self.dicom_data[patient_id_L][study_id_L][modality_L][required_length-1]['SliceImageComments']        = 'RED Calculated AMB'
    self.dicom_data[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['ImageComments'] = "RED Calculated AMB"
    image_comment = str('water map')
    data_element = DataElement((0x0020, 0x4000), 'LO', image_comment)
    self.dicom_data[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['DCM_Info']['ImageComments'] = data_element
    self.dicom_data[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['LUTLabel'] = ("Water map")
   
    required_length = len(self.dicom_data[patient_id_L][study_id_L][modality_L]) + 1
    while len(self.dicom_data[patient_id_L][study_id_L][modality_L]) < required_length:
        self.dicom_data[patient_id_L][study_id_L][modality_L].append(None)
    # Store data into new series indice
    self.dicom_data[patient_id_L][study_id_L][modality_L][required_length-1]                              = copy.deepcopy(original_data)
    self.dicom_data[patient_id_L][study_id_L][modality_L][required_length-1]['3DMatrix']                  = iodine_map.astype(np.float32)
    self.dicom_data[patient_id_L][study_id_L][modality_L][required_length-1]['SliceImageComments']        = 'RED Calculated AMB'
    self.dicom_data[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['ImageComments'] = "RED Calculated AMB"
    image_comment = str('iodine map')
    data_element = DataElement((0x0020, 0x4000), 'LO', image_comment)
    self.dicom_data[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['DCM_Info']['ImageComments'] = data_element
    self.dicom_data[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['LUTLabel'] = ("Iodine map")
    
    # generate VMIs
    Data = np.zeros(ct_low.shape, dtype=np.float32)  
    
    for i, E in enumerate(energies):
        mu   = mu_water[i] * water_map + mu_iodine[i] * iodine_map
        Data = (mu / mu_water[i] - 1) * 1000  # HU
        # copy the header of the low image ... in the future some tags will be adjusted
        original_data = self.medical_image[patient_id_L][study_id_L][modality_L][item_index_L].copy()
        # Ensure the list is long enough to accommodate new indices
        required_length = len(self.medical_image[patient_id_L][study_id_L][modality_L]) + 1
        while len(self.medical_image[patient_id_L][study_id_L][modality_L]) < required_length:
            self.medical_image[patient_id_L][study_id_L][modality_L].append(None)
        # Store data into new series indice
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]                              = copy.deepcopy(original_data)
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['3DMatrix']                  = Data.astype(np.float32)
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['SliceImageComments']        = 'RED Calculated AMB'
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['ImageComments'] = "RED Calculated AMB"
        image_comment = str('RED Calculated VMI')
        data_element = DataElement((0x0020, 0x4000), 'LO', image_comment)
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['DCM_Info']['ImageComments'] = data_element
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['LUTLabel'] = (f"Calculated VMI {E}")
        self.medical_image[patient_id_L][study_id_L][modality_L][required_length-1]['metadata']['LUTLabel'] = (f"VMI_{E}")
        #
        #
<<<<<<< HEAD
    
   
    populate_DICOM_tree(self)    
=======
    populate_medical_image_tree(self)   
>>>>>>> main
