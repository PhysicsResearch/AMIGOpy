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

    # get the dwell times and positions to calculate the dose matrix
    # dwells: ndarray (N, 7): [X_mm, Y_mm, Z_mm, ThetaX, ThetaY, ThetaZ, Time]
    dwells = get_all_brachy_dwells(self)
    # if dwells is not None:
    #     print(dwells)
    #
    dws = np.array(dwells, copy=True)
    dose, meta = transform_and_sum_dose_matrix_centered_3D(
        dws, self.TG43.activesource.DoseMatrix,self.TG43.activesource.DoseMatrix_res_mm,
        output_margin_mm=100, output_res_mm=2.0
    )
    # account for Air kerma and h unit
    kerma_str   = self.brachy_plan_Ac.text()
    kerma_value = float(kerma_str)
    dose = dose * kerma_value / 3600 /3600
    store_dose_to_medical_image(self, dose, meta)
    populate_medical_image_tree(self)

 
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
        position[:, 1] *= -1           # Invert Y-axis for DICOM compatibility
        angles   = dwell_info[:, 6:9]  # shape (n, 3)

        # Reorder to match: [X, Y, Z, ThetaX, ThetaY, ThetaZ, Time]
        combined = np.hstack((position, angles, time))
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
    print("TG43 dose calculation initialized")
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
    dwells, reference_matrix_3d, ref_res_mm, output_margin_mm, output_res_mm
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

    # 3) Reference matrix shape & its center in voxels
    ref_nz, ref_ny, ref_nx = reference_matrix_3d.shape
    cx_ref = ref_nx // 2
    cy_ref = ref_ny // 2
    cz_ref = ref_nz // 2
    ref_center = np.array([cz_ref, cy_ref, cx_ref], dtype=np.float64)

    # Pre-compute: ratio between reference and output resolution
    scale = ref_res_mm / output_res_mm  # voxels-in-output per voxel-in-ref

    # 4) Loop dwells: rotate, translate, accumulate
    for x_mm, y_mm, z_mm, cosX, cosY, cosZ, dwell_time in dw:
        if dwell_time <= 0:
            continue

        # --- Build rotation matrix ---
        R = _rotation_matrix_from_direction(cosX, cosY, cosZ)

        # scipy affine_transform uses the INVERSE mapping:
        #   output[o] = input[ R_inv @ (o - center) + center ]
        # We need R_inv to map output voxel coords back to input voxel coords.
        # The rotation matrix maps ref-axis→source-axis, so the inverse
        # (transpose, since R is orthogonal) maps output coords back to ref coords.
        R_inv = R.T  # inverse of the rotation

        # For affine_transform: input[matrix @ output_coord + offset]
        # We want rotation about the center of the reference volume:
        #   input_coord = R_inv @ (output_coord - center) + center
        #                = R_inv @ output_coord + (center - R_inv @ center)
        aff_offset = ref_center - R_inv @ ref_center

        # Apply the rotation to the reference matrix (around its own center)
        rotated = affine_transform(
            reference_matrix_3d.astype(np.float64),
            R_inv,
            offset=aff_offset,
            output_shape=reference_matrix_3d.shape,
            order=1,        # bilinear interpolation
            mode='constant',
            cval=0.0
        ).astype(np.float32)

        # --- Place rotated matrix into output grid ---
        # convert dwell (mm) → output grid voxel index
        i = int(np.round((z_mm - z_min) / output_res_mm))
        j = int(np.round((y_mm - y_min) / output_res_mm))
        k = int(np.round((x_mm - x_min) / output_res_mm))

        # figure out where the ref-matrix will land in out[]
        z0 = i - cz_ref
        z1 = z0 + ref_nz
        y0 = j - cy_ref
        y1 = y0 + ref_ny
        x0 = k - cx_ref
        x1 = x0 + ref_nx

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
        'origin_mm': (x_min + offset[0], -y_max - offset[1], z_min + offset[2]),
        'pixel_spacing_mm': output_res_mm,
        'size_pixels': (nz, ny, nx),
        'description': 'Accumulated 3D TG-43 dose (with source orientation)'
    }

    return out, meta