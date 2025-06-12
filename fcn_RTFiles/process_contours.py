import numpy as np
from skimage.draw import polygon
from skimage.measure import find_contours
from fcn_load.populate_dcm_list import populate_DICOM_tree
from PyQt5.QtWidgets import QMessageBox
from scipy.ndimage import gaussian_filter1d
from scipy.signal import savgol_filter

def create_contour_masks(self):
    data_dict = self.dicom_data[self.patientID_struct][self.studyID_struct][self.modality_struct][self.series_index_struct]
    target_series_dict = self.dicom_data[self.patientID][self.studyID][self.modality][self.series_index]

    volume_3d = target_series_dict.get('3DMatrix', None)
    if volume_3d is None:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Select a image series")
        msg_box.setText("Did you select the correct image series ? No image data found")
        msg_box.exec()
        return
    
    # Check if structures already exist clearly:
    existing_structures = target_series_dict.get('structures', {})
    existing_structure_count = len(existing_structures)

    # Progress bar - not accurate but gives a sense of progress
    self.progressBar.setValue(5)
    
    if existing_structures:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Structures Exist")
        msg_box.setText("Structures already exist. What would you like to do?")
        replace_button = msg_box.addButton("Replace", QMessageBox.AcceptRole)
        append_button = msg_box.addButton("Append", QMessageBox.RejectRole)
        msg_box.exec()

        if msg_box.clickedButton() == replace_button:
            # Replace: clear existing structures
            target_series_dict['structures'] = {}
            target_series_dict['structures_keys'] = []
            target_series_dict['structures_names'] = []
            current_structure_index = 1
        else:
            # Append: continue counting after existing structures
            current_structure_index = existing_structure_count + 1
    else:
        # No structures exist yet
        target_series_dict['structures'] = {}
        target_series_dict['structures_keys'] = []
        target_series_dict['structures_names'] = []
        current_structure_index = 1



    mask_shape = volume_3d.shape
    z_spacing = self.slice_thick[0]
    y_spacing, x_spacing = self.pixel_spac[0, :2]
    origin_x, origin_y, origin_z = self.Im_PatPosition[0, :3]

    spacing = (z_spacing, y_spacing, x_spacing)
    origin  = (origin_x, origin_y, origin_z)

    structures_keys = data_dict.get('structures_keys', [])
    structures_dict = data_dict.get('structures', {})
    structures_names = data_dict.get('structures_names', [])

    struc_names = target_series_dict['structures_names']
    struc_keys  = target_series_dict['structures_keys']

    self.progressBar.setValue(10)

    for idx, s_key in enumerate(structures_keys):
        structure = structures_dict.get(s_key)

        # Progress bar
        self.progressBar.setValue(int((idx / len(structures_keys)) * 100))

        widget = self.STRUCTlist.itemWidget(self.STRUCTlist.item(idx))
        if not widget.checkbox.isChecked():
            continue

        contour_seq = getattr(structure, 'ContourSequence', None)

        if not contour_seq:
            print(f"Structure '{structures_names[idx]}' has no ContourSequence. Creating empty mask explicitly.")
            mask_3d = np.zeros(mask_shape, dtype=np.uint8)
        else:
            mask_3d = create_3d_mask_for_structure_simple(self, structure, mask_shape, spacing, origin)
            if not mask_3d.any():
                print(f"Structure '{structures_names[idx]}' resulted in empty mask. Creating empty mask explicitly.")
                mask_3d = np.zeros(mask_shape, dtype=np.uint8)

        # Ensure names strictly follow the index
        name = structures_names[idx] if idx < len(structures_names) else f"Structure_{current_structure_index:03d}"
        new_s_key = f"Structure_{current_structure_index:03d}"

        struc_names.append(name)
        struc_keys.append(new_s_key)

        target_series_dict['structures'][new_s_key] = {
            'Mask3D': mask_3d,
            'Name': name
        }

        # --------------------------------------------------------
        # Generate & store contours (no VTK objects here!)
        # --------------------------------------------------------
        contours_2d = {'axial': {}, 'sagittal': {}, 'coronal': {}}

        for z_idx in range(mask_shape[0]):          # axial slices
            slice_2d = mask_3d[z_idx]
            contours = extract_contours_from_binary_slice(slice_2d)
            if contours:
                contours_2d['axial'][z_idx] = contours

        for x_idx in range(mask_shape[2]):          # sagittal
            slice_2d = mask_3d[:, :, x_idx]
            contours = extract_contours_from_binary_slice(slice_2d)
            if contours:
                contours_2d['sagittal'][x_idx] = contours

        for y_idx in range(mask_shape[1]):          # coronal
            slice_2d = mask_3d[:, y_idx, :]
            contours = extract_contours_from_binary_slice(slice_2d)
            if contours:
                contours_2d['coronal'][y_idx] = contours

        entry = {
            'Mask3D': mask_3d,
            'Name'  : name,
            'Contours2D': contours_2d,   # <── new, pickle-safe
            # 'VTKActors2D' will be added lazily at render-time
        }

        target_series_dict['structures'][new_s_key] = entry

        current_structure_index += 1

    # Update structure lists clearly
    target_series_dict['structures_keys'] = struc_keys
    target_series_dict['structures_names'] = struc_names

    self.progressBar.setValue(100)
    populate_DICOM_tree(self)



def create_3d_mask_for_structure_simple(self, structure, mask_shape, spacing, origin):
    mask_3d     = np.zeros(mask_shape, dtype=np.uint8)
    contour_seq = getattr(structure, 'ContourSequence', [])

    if not contour_seq:
        print("No contour sequence found in structure.")
        return mask_3d

    z_spacing, y_spacing, x_spacing = spacing
    origin_x, origin_y, origin_z = origin

    # flip coordinate to match Y 
    origin_y = -origin_y

    for contour in contour_seq:
        geom_type = getattr(contour, 'ContourGeometricType', '').upper()
        if geom_type != 'CLOSED_PLANAR':
            continue

        contour_data = getattr(contour, 'ContourData', [])
        if len(contour_data) % 3 != 0:
            continue

        points = np.array(contour_data).reshape(-1, 3)

        # Need to flip y to match
        points[:, 1] = (self.display_data[0].shape[1] * self.pixel_spac[0, 0]) - points[:, 1]  # Y coordinate

        indices_float = (points - np.array([origin_x, origin_y, origin_z])) / [x_spacing, y_spacing, z_spacing]
        indices = indices_float.round().astype(int)

        slice_idx = indices[0, 2]
        if slice_idx < 0 or slice_idx >= mask_shape[0]:
            continue

        x_coords = indices[:, 0]
        y_coords = indices[:, 1]

        rr, cc = polygon(y_coords, x_coords, shape=mask_shape[1:])
        mask_3d[slice_idx, rr, cc] += 1

    mask_3d = np.mod(mask_3d, 2).astype(np.uint8)
    return mask_3d




def extract_contours_from_binary_slice(slice_2d, level=0.4, smooth=True, method="gaussian"):
    """
    Extracts and optionally smooths contours from a binary slice.

    Parameters:
        slice_2d (ndarray): Binary mask slice
        level (float): Contour extraction threshold
        smooth (bool): Whether to apply smoothing
        method (str): Smoothing method ("savgol" or "gaussian")

    Returns:
        list of np.array: Extracted (and optionally smoothed) contours
    """
    contours = find_contours(slice_2d, level=level)
    
    if smooth:
        contours = smooth_contours(contours, method=method)

    return contours

def smooth_contours(contours, method="savgol", window_length=5, polyorder=2, sigma=1.0):
    """
    Smooths extracted contours using either a Savitzky-Golay filter or Gaussian smoothing.

    Parameters:
        contours (list of np.array): List of contours (each contour is Nx2)
        method (str): "savgol" (Savitzky-Golay) or "gaussian" (Gaussian filter)
        window_length (int): Window size for Savitzky-Golay filter
        polyorder (int): Polynomial order for Savitzky-Golay filter
        sigma (float): Standard deviation for Gaussian smoothing

    Returns:
        list of np.array: Smoothed contours
    """
    smoothed_contours = []
    
    for contour in contours:
        x, y = contour[:, 0], contour[:, 1]  # Separate x and y coordinates
        
        if method == "savgol":
            x_smooth = savgol_filter(x, window_length=window_length, polyorder=polyorder, mode='nearest')
            y_smooth = savgol_filter(y, window_length=window_length, polyorder=polyorder, mode='nearest')
        elif method == "gaussian":
            x_smooth = gaussian_filter1d(x, sigma=sigma)
            y_smooth = gaussian_filter1d(y, sigma=sigma)
        else:
            x_smooth, y_smooth = x, y  # No smoothing
        
        smoothed_contours.append(np.column_stack((x_smooth, y_smooth)))
    
    return smoothed_contours


