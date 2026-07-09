from fcn_brachy_sources.process_brachy_database import on_brachy_load_sources
import numpy as np
from scipy.ndimage import rotate, shift
from scipy.spatial.transform import Rotation as R
from fcn_load.populate_med_image_list import populate_medical_image_tree
from PySide6.QtWidgets import QMessageBox

def calculate_TG43_plan_dose(self):
    # if the TG43 parameters are not initialized, call the function to do so
    if self.TG43.activesource.DoseMatrix is None:
        on_brachy_init_tg43(self)
    # check if plan was laoded
    if not hasattr(self, 'patientID_plan') or not hasattr(self, 'studyID_plan'):
        QMessageBox.warning(self, "Missing Plan Data",
                            "Patient or Study ID for plan is not set.\n"
                            "Cannot load brachy channels.")
        return []

    # Reset progress bar for the actual dose calculation
    if hasattr(self, 'progressBar') and self.progressBar is not None:
        self.progressBar.setValue(0)

    # get the dwell times and positions to calculate the dose matrix
    # dwells: ndarray (N, 7): [X_mm, Y_mm, Z_mm, ThetaX, ThetaY, ThetaZ, Time]
    dwells = get_all_brachy_dwells(self)
    # if dwells is not None:
    #     print(dwells)
    #
    dws = np.array(dwells, copy=True)
    output_res_mm = float(self.brachy_tg43_dose_grid.currentText().strip())
    dose, meta = transform_and_sum_dose_matrix_centered_3D(
        dws, self.TG43.activesource.DoseMatrix, self.TG43.activesource.DoseMatrix_res_mm,
        output_margin_mm=100, output_res_mm=output_res_mm, parent=self
    )
    # account for Air kerma and h unit
    kerma_str   = self.brachy_plan_Ac.text()
    kerma_value = float(kerma_str)
    dose = (dose * kerma_value / 3600) / 100.0

    # Flip Y-axis (axis=1) to match the vertical flip applied to CT/MR/RTDOSE layers in load_dcm.py
    dose = np.flip(dose, axis=1)

    store_dose_to_medical_image(self, dose, meta)
    populate_medical_image_tree(self)
    if hasattr(self, 'progressBar') and self.progressBar is not None:
        self.progressBar.setValue(100)
    if hasattr(self, 'label_2') and self.label_2 is not None:
        self.label_2.setText("TG43 dose calculation completed")
        self.label_2.show()

 
def store_dose_to_medical_image(self, dose,meta):
    """
    Stores a dose matrix into self.medical_image under RTDOSE at a given index.
    
    If RTDOSE does not exist, it is created as a list.
    If the list has fewer elements than `index`, it is extended.
    """
    if self.patientID is None:
        self.patientID = 'TG43'
    if self.studyID is None:
        self.studyID = 'TG43_AMB'

    # Ensure patient level
    if self.patientID not in self.medical_image:
        self.medical_image[self.patientID] = {}

    # Ensure study level
    if self.studyID not in self.medical_image[self.patientID]:
        self.medical_image[self.patientID][self.studyID] = {}

    # Ensure RTDOSE list exists
    if 'RTDOSE' not in self.medical_image[self.patientID][self.studyID]:
        self.medical_image[self.patientID][self.studyID]['RTDOSE'] = []

    # Append 
    self.medical_image[self.patientID][self.studyID]['RTDOSE'].append({})
    #
    self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['3DMatrix']                      = dose
    self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['metadata']                      = {}
    self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['metadata']['SeriesDescription'] = 'TG43_AMIGOpy'
    self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['SeriesNumber']                  = 1
    self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['metadata']['WindowWidth']       = 10 
    self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['metadata']['WindowCenter']      = 5
    self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['metadata']['AcquisitionNumber'] = 1
    self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['metadata']['DCM_Info']          = {}
    self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['metadata']['StudyDescription']  = 'AMIGOpy'
    self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['metadata']['ImageComments']     = 'Not for clinical use'
    self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['metadata']['SliceThickness']    = meta['pixel_spacing_mm']
    self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['metadata']['PixelSpacing']      = [meta['pixel_spacing_mm'], meta['pixel_spacing_mm']]
    #
    # orig = np.array(meta['origin_mm'], dtype=float)  # turn into array
    # neg_orig = -orig                                 # elementwise negation
    # # If DICOM wants a tuple/list, convert back
    # self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['metadata']['ImagePositionPatient'] = tuple(neg_orig.tolist())
    self.medical_image[self.patientID][self.studyID]['RTDOSE'][-1]['metadata']['ImagePositionPatient'] = meta['origin_mm']


def get_all_brachy_dwells(self):

    if not hasattr(self, 'patientID_plan') or not hasattr(self, 'studyID_plan'):
        QMessageBox.warning(self, "Missing Plan Data",
                            "Patient or Study ID for plan is not set.\n"
                            "Cannot load brachy channels.")
        return []


    try:
        channels = self.medical_image[self.patientID_plan][self.studyID_plan][self.modality_plan][self.series_index_plan]['metadata']['Plan_Brachy_Channels']
    except (KeyError, IndexError):
        QMessageBox.warning(self, "Warning", "Plan data is missing or corrupted.")
        return None

    all_dwells = []

    for channel in channels:
        dwell_info = channel.get('DwellInfo')
        if dwell_info is None or dwell_info.shape[1] < 9:
            continue  # skip invalid or incomplete data

        # Extract Time (col 3) and Position + Orientation (cols 4–9)
        # Result: (n, 7) → [X, Y, Z, ThetaX, ThetaY, ThetaZ, Time]
        time     = dwell_info[:, 2:3]  # shape (n, 1)
        position = dwell_info[:, 3:6].copy()
        angles   = dwell_info[:, 6:9]  # shape (n, 3)

        # Scale time weights to actual seconds if total time and final weight are available
        tot_time = channel.get('ChannelTotalTime', 1.0)
        final_weight = channel.get('FinalCumulativeTimeWeight', 1.0)
        
        try:
            tot_time = float(tot_time) if tot_time is not None and tot_time != 'N/A' else 1.0
        except ValueError:
            tot_time = 1.0
            
        try:
            final_weight = float(final_weight) if final_weight is not None and final_weight != 'N/A' else 1.0
        except ValueError:
            final_weight = 1.0
            
        scale_factor = tot_time / final_weight if final_weight > 0 else 1.0
        time_scaled = time * scale_factor

        # Reorder to match: [X, Y, Z, ThetaX, ThetaY, ThetaZ, Time]
        combined = np.hstack((position, angles, time_scaled))
        all_dwells.append(combined)

    if not all_dwells:
        QMessageBox.warning(self, "Warning", "No valid dwell data found.")
        return None

    # Stack all channels into one array
    all_dwells_array = np.vstack(all_dwells)
    return all_dwells_array


def on_brachy_init_tg43(self):
    # this part initializes the TG43 parameters and calculate the TG43 reference dose 
    # it needs to be done just once at the beginning of the program ... 
    if hasattr(self, 'label_2') and self.label_2 is not None:
        self.label_2.setText("TG43 dose calculation initialized")
        self.label_2.show()
    # set list menu to define the dose grid and matrix size
    # DoseGrid = ["0.5","1","2","3","4","5"]
    self.brachy_tg43_dose_grid.setCurrentIndex(1)
    #
    # MatrixSize = ["50x50","100x100","150x150","200x200"]
    self.brachy_tg43_matrix_size.setCurrentIndex(3)
    # Load sources
    on_brachy_load_sources(self)
    #
    # on_brachy_source_selection(self)
    # The code above will calculate the reference for the first loaded source ... if you want to calculate it for another source
    # change the list men u index and it will update automatically 
    self.brachy_source_list.setCurrentIndex(0)




def _rotation_matrix_from_direction(cosX, cosY, cosZ):
    """
    Build a 3×3 rotation matrix that maps the reference axis [0, 0, 1]
    to the source orientation unit vector [cosX, cosY, cosZ].

    Uses Rodrigues' rotation formula:
        R = I + [v]_x + [v]_x^2 * (1 / (1 + c))
    where v = ref × target, c = ref · target.

    Edge cases:
        - If target ≈ [0, 0, 1]  → identity (no rotation needed)
        - If target ≈ [0, 0, -1] → 180° rotation around X axis
    """
    ref = np.array([0.0, 0.0, 1.0])
    tgt = np.array([cosX, cosY, cosZ], dtype=np.float64)
    norm = np.linalg.norm(tgt)
    if norm < 1e-12:
        return np.eye(3)
    tgt /= norm

    c = np.dot(ref, tgt)

    # Already aligned (within ~0.01°)
    if c > 1.0 - 1e-8:
        return np.eye(3)

    # Anti-parallel: 180° rotation around the X axis
    if c < -1.0 + 1e-8:
        return np.diag([1.0, -1.0, -1.0])

    v = np.cross(ref, tgt)  # rotation axis (un-normalised, |v| = sin(angle))

    # Skew-symmetric cross-product matrix of v
    vx = np.array([
        [ 0.0, -v[2],  v[1]],
        [ v[2],  0.0, -v[0]],
        [-v[1],  v[0],  0.0]
    ])

    R = np.eye(3) + vx + vx @ vx * (1.0 / (1.0 + c))
    return R


def transform_and_sum_dose_matrix_centered_3D(
    dwells, reference_matrix_3d, ref_res_mm, output_margin_mm, output_res_mm, parent=None
):
    """
    Accumulate TG-43 dose from all dwells into a single output volume.

    For each dwell the reference dose matrix is rotated so that its
    longitudinal axis (originally Z) aligns with the actual source
    orientation given by the direction-cosine vector [cosX, cosY, cosZ].
    """
    from scipy.ndimage import affine_transform

    # 1) Center dwells on first dwell
    offset = dwells[0, :3].copy()
    dw = dwells.copy()
    dw[:, :3] -= offset

    xs, ys, zs = dw[:,0], dw[:,1], dw[:,2]
    x_min, x_max = xs.min() - output_margin_mm, xs.max() + output_margin_mm
    y_min, y_max = ys.min() - output_margin_mm, ys.max() + output_margin_mm
    z_min, z_max = zs.min() - output_margin_mm, zs.max() + output_margin_mm

    # 2) Output grid size in voxels
    nx = int(np.round((x_max - x_min) / output_res_mm)) + 1
    ny = int(np.round((y_max - y_min) / output_res_mm)) + 1
    nz = int(np.round((z_max - z_min) / output_res_mm)) + 1

    out = np.zeros((nz, ny, nx), dtype=np.float32)

    # 3) Crop reference matrix to effective dose radius for performance
    ref_nz, ref_ny, ref_nx = reference_matrix_3d.shape
    c_z_idx, c_y_idx, c_x_idx = ref_nz // 2, ref_ny // 2, ref_nx // 2
    peak = float(np.max(np.abs(reference_matrix_3d)))
    if peak > 0:
        threshold = peak * 1e-4  # 0.01% of peak dose
        z_profile = np.abs(reference_matrix_3d[:, c_y_idx, c_x_idx])
        z_above = np.where(z_profile > threshold)[0]
        z_half = max(c_z_idx - z_above[0], z_above[-1] - c_z_idx) + 2 if len(z_above) > 0 else c_z_idx
        x_profile = np.abs(reference_matrix_3d[c_z_idx, c_y_idx, :])
        x_above = np.where(x_profile > threshold)[0]
        xy_half = max(c_x_idx - x_above[0], x_above[-1] - c_x_idx) + 2 if len(x_above) > 0 else c_x_idx
        z_half = max(min(z_half, c_z_idx), 10)
        xy_half = max(min(xy_half, c_y_idx, c_x_idx), 10)
        ref_cropped = reference_matrix_3d[
            c_z_idx - z_half:c_z_idx + z_half + 1,
            c_y_idx - xy_half:c_y_idx + xy_half + 1,
            c_x_idx - xy_half:c_x_idx + xy_half + 1
        ].astype(np.float32)
    else:
        ref_cropped = reference_matrix_3d.astype(np.float32)

    crop_nz, crop_ny, crop_nx = ref_cropped.shape
    c_ref = np.array([(crop_nz - 1) / 2.0, (crop_ny - 1) / 2.0, (crop_nx - 1) / 2.0], dtype=np.float64)

    # Ratio between output and reference resolution
    scale = output_res_mm / ref_res_mm

    # Resampled reference shape at output resolution
    out_nz = max(1, int(np.round(crop_nz / scale)))
    out_ny = max(1, int(np.round(crop_ny / scale)))
    out_nx = max(1, int(np.round(crop_nx / scale)))

    # Precompute coordinate permutation matrix (constant for all dwells)
    P = np.array([
        [0.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 0.0]
    ], dtype=np.float64)
    
    # 4) Loop dwells: rotate, resample to output resolution, translate, accumulate
    N = len(dw)
    for idx, (x_mm, y_mm, z_mm, cosX, cosY, cosZ, dwell_time) in enumerate(dw):
        if parent is not None and hasattr(parent, 'progressBar') and parent.progressBar is not None:
            progress_val = int((idx / N) * 100)
            parent.progressBar.setValue(progress_val)
            from PySide6.QtCore import QCoreApplication
            QCoreApplication.processEvents()

        if dwell_time <= 0:
            continue

        # --- Place rotated matrix into output grid ---
        # convert dwell (mm) → output grid voxel index
        i = int(np.round((z_mm - z_min) / output_res_mm))
        j = int(np.round((y_mm - y_min) / output_res_mm))
        k = int(np.round((x_mm - x_min) / output_res_mm))

        # figure out where the ref-matrix will land in out[]
        z0 = i - out_nz // 2
        z1 = z0 + out_nz
        y0 = j - out_ny // 2
        y1 = y0 + out_ny
        x0 = k - out_nx // 2
        x1 = x0 + out_nx

        # Calculate the exact fractional position of the dwell point in the output grid
        p_out = np.array([
            (z_mm - z_min) / output_res_mm,
            (y_mm - y_min) / output_res_mm,
            (x_mm - x_min) / output_res_mm
        ], dtype=np.float64)

        # Set the continuous center of rotation in the cropped sub-grid to match the exact fractional landing coordinates
        c_out_dwell = p_out - np.array([z0, y0, x0], dtype=np.float64)

        # --- Build rotation matrix ---
        R = _rotation_matrix_from_direction(cosX, cosY, cosZ)

        # scipy affine_transform uses the INVERSE mapping:
        #   r = scale * R_inv @ (o - c_out) + c_ref
        # But indices are in (Z, Y, X) order, while R_inv is in (X, Y, Z) order.
        # We must permute R_inv to (Z, Y, X) using P @ R_inv @ P where P swaps Z and X.
        R_inv = R.T
        R_inv_zyx = P @ R_inv @ P
        trans_matrix = scale * R_inv_zyx
        aff_offset = c_ref - trans_matrix @ c_out_dwell

        # Apply the rotation and scaling to the cropped reference matrix
        rotated = affine_transform(
            ref_cropped,
            trans_matrix,
            offset=aff_offset,
            output_shape=(out_nz, out_ny, out_nx),
            order=1,
            mode='constant',
            cval=0.0
        )

        # compute valid overlap with output bounds
        iz0, iy0, ix0 = max(0, z0), max(0, y0), max(0, x0)
        iz1, iy1, ix1 = min(nz, z1), min(ny, y1), min(nx, x1)

        # corresponding region within the rotated reference matrix
        rz0 = iz0 - z0
        ry0 = iy0 - y0
        rx0 = ix0 - x0
        rz1 = rz0 + (iz1 - iz0)
        ry1 = ry0 + (iy1 - iy0)
        rx1 = rx0 + (ix1 - ix0)

        # accumulate (dose rate × time)
        out[iz0:iz1, iy0:iy1, ix0:ix1] += (
            rotated[rz0:rz1, ry0:ry1, rx0:rx1]
            * dwell_time
        )

    meta = {
        'origin_mm': (x_min + offset[0], y_min + offset[1], z_min + offset[2]),
        'pixel_spacing_mm': output_res_mm,
        'size_pixels': (nz, ny, nx),
        'description': 'Accumulated 3D TG-43 dose (with source orientation)'
    }

    return out, meta