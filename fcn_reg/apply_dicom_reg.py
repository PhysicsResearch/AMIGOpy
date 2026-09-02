import numpy as np
import copy
from scipy.ndimage import map_coordinates


def decompose_transform_matrix(matrix4x4):
    """
    Decomposes a 4x4 homogeneous transformation matrix into:
    - 4x4 numpy array M
    - 3x3 Rotation matrix R
    - 3x1 Translation vector T (in mm)
    - Euler rotation angles in degrees (Roll=X, Pitch=Y, Yaw=Z)
    - Determinant of rotation matrix
    """
    # test commit
    M = np.array(matrix4x4, dtype=float).reshape((4, 4))
    R = M[:3, :3]
    T = M[:3, 3]
    
    det = float(np.linalg.det(R))
    
    # Euler angles (XYZ convention in degrees)
    sy = np.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
    singular = sy < 1e-6
    if not singular:
        x = np.arctan2(R[2, 1], R[2, 2])
        y = np.arctan2(-R[2, 0], sy)
        z = np.arctan2(R[1, 0], R[0, 0])
    else:
        x = np.arctan2(-R[1, 2], R[1, 1])
        y = np.arctan2(-R[2, 0], sy)
        z = 0.0
    
    angles_deg = np.degrees([x, y, z])
    
    return {
        "Matrix": M,
        "Rotation": R,
        "Translation": T,
        "EulerAnglesDeg": angles_deg,
        "Determinant": det
    }


def find_all_image_series_in_patient(medical_image, patientID):
    """
    Returns all image series (CT, MR, PT) loaded in the patient.
    """
    series_list = []
    if not medical_image or patientID not in medical_image:
        return series_list
        
    patient_data = medical_image[patientID]
    for study_id, study_data in patient_data.items():
        if not isinstance(study_data, dict):
            continue
        for modality, mod_series in study_data.items():
            if modality in ['REG', 'RTPLAN', 'RTSTRUCT']:
                continue
            if not isinstance(mod_series, list):
                continue
            for idx, series in enumerate(mod_series):
                if not isinstance(series, dict) or series.get('3DMatrix') is None:
                    continue
                meta = series.get('metadata', {})
                series_list.append({
                    'patientID': patientID,
                    'studyID': study_id,
                    'modality': modality,
                    'series_index': idx,
                    'description': meta.get('SeriesDescription', '') or meta.get('ContentLabel', f"Series_{idx}"),
                    'for_uid': meta.get('FrameOfReferenceUID', ''),
                    'shape': series['3DMatrix'].shape,
                    'origin': meta.get('ImagePositionPatient', [0,0,0]),
                    'series_data': series
                })
    return series_list


def resample_volume_with_matrix(moving_series, matrix4x4, reference_series=None):
    """
    Applies the 4x4 transformation matrix (mapping physical points from moving series FoR to target FoR)
    to resample moving_series into the target Frame of Reference space.
    
    Properly accounts for AMIGOpy's internal axis-1 flip.
    """
    M = np.array(matrix4x4, dtype=float).reshape((4, 4))
    M_inv = np.linalg.inv(M)
    
    vol_mov = moving_series.get('3DMatrix')
    if vol_mov is None:
        raise ValueError("Moving series does not contain a 3DMatrix.")
    
    meta_mov = moving_series.get('metadata', {})
    modality_mov = meta_mov.get('Modality', 'CT')
    cval = -1000.0 if modality_mov in ['CT', 'PT'] else 0.0
    
    ipp_mov = meta_mov.get('ImagePositionPatient', [0.0, 0.0, 0.0])
    x0_s, y0_s, z0_s = float(ipp_mov[0]), float(ipp_mov[1]), float(ipp_mov[2])
    
    ps_mov = meta_mov.get('PixelSpacing', [1.0, 1.0])
    dy_s, dx_s = float(ps_mov[0]), float(ps_mov[1])
    dz_s = float(meta_mov.get('SliceThickness', 1.0))
    if dz_s <= 0:
        dz_s = 1.0
        
    Nz_s, Ny_s, Nx_s = vol_mov.shape

    if reference_series is not None and reference_series.get('3DMatrix') is not None:
        # Resample onto reference grid
        vol_ref = reference_series['3DMatrix']
        meta_ref = reference_series.get('metadata', {})
        Nz_t, Ny_t, Nx_t = vol_ref.shape
        
        ipp_ref = meta_ref.get('ImagePositionPatient', [0.0, 0.0, 0.0])
        x0_t, y0_t, z0_t = float(ipp_ref[0]), float(ipp_ref[1]), float(ipp_ref[2])
        
        ps_ref = meta_ref.get('PixelSpacing', [1.0, 1.0])
        dy_t, dx_t = float(ps_ref[0]), float(ps_ref[1])
        dz_t = float(meta_ref.get('SliceThickness', 1.0))
        if dz_t <= 0:
            dz_t = 1.0
            
        out_shape = (Nz_t, Ny_t, Nx_t)
        new_vol = np.zeros(out_shape, dtype=np.float32)
        
        # Grid vectors in AMIGOpy coordinate system (accounting for axis-1 flip)
        # In AMIGOpy: row j=0 is at y_max = y0 + (Ny - 1)*dy, and row j=Ny-1 is at y_min = y0
        i_t_coords, j_t_coords = np.meshgrid(np.arange(Nx_t), np.arange(Ny_t))
        x_t_2d = x0_t + i_t_coords * dx_t
        y_t_2d = y0_t + (Ny_t - 1 - j_t_coords) * dy_t
        
        for k_t in range(Nz_t):
            z_t = z0_t + k_t * dz_t
            pts_t = np.stack([
                x_t_2d.ravel(),
                y_t_2d.ravel(),
                np.full(x_t_2d.size, z_t),
                np.ones(x_t_2d.size)
            ], axis=0) # (4, N)
            
            # Map target physical point to source physical point
            pts_s = M_inv @ pts_t
            
            i_s = (pts_s[0] - x0_s) / dx_s
            j_s = (Ny_s - 1) - (pts_s[1] - y0_s) / dy_s
            k_s = (pts_s[2] - z0_s) / dz_s
            
            coords = np.stack([k_s, j_s, i_s], axis=0)
            slice_resampled = map_coordinates(vol_mov, coords, order=1, cval=cval).reshape((Ny_t, Nx_t))
            new_vol[k_t] = slice_resampled
            
        new_origin = [x0_t, y0_t, z0_t]
        new_pixel_spacing = [dy_t, dx_t]
        new_slice_thickness = dz_t
        
        new_ipp_list = []
        for k in range(Nz_t):
            new_ipp_list.append([x0_t, y0_t, z0_t + k * dz_t])
            
    else:
        # Resample maintaining source resolution with transformed bounding box
        corners_s = np.array([
            [x0_s, y0_s, z0_s, 1.0],
            [x0_s + Nx_s * dx_s, y0_s, z0_s, 1.0],
            [x0_s, y0_s + Ny_s * dy_s, z0_s, 1.0],
            [x0_s + Nx_s * dx_s, y0_s + Ny_s * dy_s, z0_s, 1.0],
            [x0_s, y0_s, z0_s + Nz_s * dz_s, 1.0],
            [x0_s + Nx_s * dx_s, y0_s, z0_s + Nz_s * dz_s, 1.0],
            [x0_s, y0_s + Ny_s * dy_s, z0_s + Nz_s * dz_s, 1.0],
            [x0_s + Nx_s * dx_s, y0_s + Ny_s * dy_s, z0_s + Nz_s * dz_s, 1.0],
        ]).T # (4, 8)
        
        corners_t = M @ corners_s
        min_xyz = corners_t[:3].min(axis=1)
        max_xyz = corners_t[:3].max(axis=1)
        
        dx_t, dy_t, dz_t = dx_s, dy_s, dz_s
        Nx_t = int(np.ceil((max_xyz[0] - min_xyz[0]) / dx_t))
        Ny_t = int(np.ceil((max_xyz[1] - min_xyz[1]) / dy_t))
        Nz_t = int(np.ceil((max_xyz[2] - min_xyz[2]) / dz_t))
        
        x0_t, y0_t, z0_t = min_xyz[0], min_xyz[1], min_xyz[2]
        
        out_shape = (Nz_t, Ny_t, Nx_t)
        new_vol = np.zeros(out_shape, dtype=np.float32)
        
        i_t_coords, j_t_coords = np.meshgrid(np.arange(Nx_t), np.arange(Ny_t))
        x_t_2d = x0_t + i_t_coords * dx_t
        y_t_2d = y0_t + (Ny_t - 1 - j_t_coords) * dy_t
        
        for k_t in range(Nz_t):
            z_t = z0_t + k_t * dz_t
            pts_t = np.stack([
                x_t_2d.ravel(),
                y_t_2d.ravel(),
                np.full(x_t_2d.size, z_t),
                np.ones(x_t_2d.size)
            ], axis=0)
            
            pts_s = M_inv @ pts_t
            i_s = (pts_s[0] - x0_s) / dx_s
            j_s = (Ny_s - 1) - (pts_s[1] - y0_s) / dy_s
            k_s = (pts_s[2] - z0_s) / dz_s
            
            coords = np.stack([k_s, j_s, i_s], axis=0)
            slice_resampled = map_coordinates(vol_mov, coords, order=1, cval=cval).reshape((Ny_t, Nx_t))
            new_vol[k_t] = slice_resampled
            
        new_origin = [x0_t, y0_t, z0_t]
        new_pixel_spacing = [dy_t, dx_t]
        new_slice_thickness = dz_t
        
        new_ipp_list = []
        for k in range(Nz_t):
            new_ipp_list.append([x0_t, y0_t, z0_t + k * dz_t])

    return new_vol, new_origin, new_pixel_spacing, new_slice_thickness, new_ipp_list


def apply_and_duplicate_registered_series(
    parent,
    patientID,
    source_studyID,
    source_modality,
    source_series_idx,
    target_for_uid,
    matrix4x4,
    target_studyID=None,
    target_modality=None,
    target_series_idx=None,
    precomputed_volume=None,
    precomputed_origin=None,
    precomputed_spacing=None,
    precomputed_thick=None
):
    """
    Applies the registration matrix to the selected moving series, creates a registered
    duplicate series with target FrameOfReferenceUID, and inserts it into medical_image.
    """
    try:
        source_series = parent.medical_image[patientID][source_studyID][source_modality][source_series_idx]
    except (KeyError, IndexError):
        raise ValueError("Selected moving series was not found in medical_image.")
    
    reference_series = None
    if target_studyID is not None and target_modality is not None and target_series_idx is not None:
        try:
            reference_series = parent.medical_image[patientID][target_studyID][target_modality][target_series_idx]
        except Exception:
            reference_series = None

    if precomputed_volume is not None:
        # Use the already resampled, verified volume from the registration viewer
        orig_dtype = source_series['3DMatrix'].dtype
        new_vol = precomputed_volume.astype(orig_dtype)
        new_origin = list(np.array(precomputed_origin, dtype=float))
        new_pixel_spacing = list(np.array(precomputed_spacing, dtype=float))
        new_slice_thickness = float(precomputed_thick)
        new_ipp_list = []
        for k in range(new_vol.shape[0]):
            new_ipp_list.append([new_origin[0], new_origin[1], new_origin[2] + k * new_slice_thickness])
    else:
        # Resample volume using 4x4 matrix
        new_vol, new_origin, new_pixel_spacing, new_slice_thickness, new_ipp_list = resample_volume_with_matrix(
            source_series, matrix4x4, reference_series
        )
    
    # Deep copy metadata
    orig_meta = source_series.get('metadata', {})
    new_meta = copy.deepcopy(orig_meta)
    
    orig_desc = orig_meta.get('SeriesDescription', '') or orig_meta.get('ContentLabel', f"Series_{source_series_idx}")
    target_tag = f"Study {target_studyID}" if target_studyID else target_for_uid[-6:]
    new_desc = f"{orig_desc} [Reg -> {target_tag}]"
    
    new_meta['SeriesDescription'] = new_desc
    new_meta['FrameOfReferenceUID'] = target_for_uid
    new_meta['ImagePositionPatient'] = new_origin
    new_meta['PixelSpacing'] = new_pixel_spacing
    new_meta['SliceThickness'] = new_slice_thickness
    new_meta['SeriesInstanceUID'] = f"{orig_meta.get('SeriesInstanceUID', 'reg')}.{np.random.randint(1000, 9999)}"
    new_meta['IsRegistered'] = True
    new_meta['RegistrationProvenance'] = {
        'SourceStudyID': source_studyID,
        'SourceModality': source_modality,
        'SourceSeriesIndex': source_series_idx,
        'TargetFrameOfReferenceUID': target_for_uid,
        'TargetStudyID': target_studyID,
        'Matrix': matrix4x4
    }
    
    # Build registered series dictionary
    new_series_dict = {
        'SeriesNumber': source_series.get('SeriesNumber', source_series_idx) + 100,
        'metadata': new_meta,
        '3DMatrix': new_vol,
        'ImagePositionPatients': new_ipp_list,
        'images': {},
        'SliceImageComments': {}
    }
    
    # Add slice images dict
    for k, ipp in enumerate(new_ipp_list):
        new_series_dict['images'][k] = {
            'ImageData': new_vol[k],
            'ImagePositionPatient': ipp
        }

    # Append to study modality list
    parent.medical_image[patientID][source_studyID][source_modality].append(new_series_dict)
    
    # Also create a DICOM Spatial Registration (REG) entry in medical_image
    if 'REG' not in parent.medical_image[patientID][source_studyID]:
        parent.medical_image[patientID][source_studyID]['REG'] = []
    
    reg_series_num = 900 + len(parent.medical_image[patientID][source_studyID]['REG'])
    mat_flattened = list(np.array(matrix4x4, dtype=float).flatten())
    
    target_tag_study = f"Study {target_studyID}" if target_studyID is not None else "Reference"
    reg_entry = {
        'SeriesNumber': reg_series_num,
        'metadata': {
            'Modality': 'REG',
            'SeriesDescription': f"Spatial Reg [Study {source_studyID} -> {target_tag_study}]",
            'StudyDescription': orig_meta.get('StudyDescription', ''),
            'ContentLabel': 'REGISTRATION',
            'ContentDescription': f"Spatial Registration from Study {source_studyID} to {target_tag_study}",
            'SOPInstanceUID': f"1.2.840.10008.5.1.4.1.1.66.1.{np.random.randint(100000, 999999)}",
            'SeriesInstanceUID': f"1.2.840.10008.5.1.4.1.1.66.2.{np.random.randint(100000, 999999)}",
            'StudyInstanceUID': orig_meta.get('StudyInstanceUID', ''),
            'FrameOfReferenceUID': target_for_uid or orig_meta.get('FrameOfReferenceUID', ''),
            'StudyDate': orig_meta.get('StudyDate', ''),
            'SeriesDate': orig_meta.get('SeriesDate', ''),
            'RegistrationMatrixList': [{
                'TargetFrameOfReferenceUID': target_for_uid,
                'MatrixType': 'RIGID',
                'Matrix': mat_flattened
            }]
        },
        'images': {},
        'ImagePositionPatients': [],
        'SliceImageComments': {}
    }
    parent.medical_image[patientID][source_studyID]['REG'].append(reg_entry)

    # Refresh data tree if GUI is active
    if hasattr(parent, 'DataTreeView') and parent.DataTreeView is not None:
        from fcn_load.populate_med_image_list import populate_medical_image_tree
        populate_medical_image_tree(parent)
    
    return new_desc
