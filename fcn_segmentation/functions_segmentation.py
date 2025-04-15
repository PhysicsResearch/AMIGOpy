import numpy as np
from fcn_load.populate_dcm_list import populate_DICOM_tree

def threshSeg(self):
    layer  = int(self.layer_selection_box.currentIndex())
    min_, max_ = self.threshMinSlider.value(), self.threshMaxSlider.value()
    mask_3d = (self.display_seg_data[layer] >= min_) * (self.display_seg_data[layer] <= max_)
    mask_3d = mask_3d.astype(np.uint8)
    
    target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    
    existing_structures = target_series_dict.get('structures', {})
    existing_structure_count = len(existing_structures)
    
    if existing_structure_count == 0:
        target_series_dict['structures'] = {}
        target_series_dict['structures_keys'] = []
        target_series_dict['structures_names'] = []

    current_structure_index = existing_structure_count + 1
        
    name = "tumor"
    # Create a new unique key for the structure clearly:
    new_s_key = f"Structure_{current_structure_index:03d}"

    # target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]
    target_series_dict['structures'][new_s_key] = {
        'Mask3D': mask_3d,
        'Name': "tumors"
    }
    target_series_dict['structures_keys'].append(new_s_key)
    target_series_dict['structures_names'].append(name)
    
    populate_DICOM_tree(self)
    print(target_series_dict['structures'][new_s_key]['Mask3D'].sum())
    im = target_series_dict['structures'][new_s_key]['Mask3D']
    import matplotlib.pyplot as plt
    plt.imshow(im[im.shape[0] // 2])
    plt.show()
    