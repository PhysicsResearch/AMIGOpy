import numpy as np
from scipy.ndimage import affine_transform
from math import sin, cos, radians
from fcn_display.display_images import update_layer_view

from fcn_display.display_images  import displayaxial, displaycoronal, displaysagittal  

def update_view(self):
    displaycoronal(self)
    displaysagittal(self)
    displayaxial(self)
    update_layer_view(self)

def update_translation_x(self):
    self.Im_PatPosition[1,0]   =  float(self.Reg_manual_Tx.value())
    self.Im_Offset[1,0]   = (self.Im_PatPosition[1,0]-self.Im_PatPosition[0,0])
    update_view(self)

def update_translation_y(self):     
    self.Im_PatPosition[1,1]   =  float(self.Reg_manual_Ty.value())
    self.Im_Offset[1,1]        = (self.display_data[0].shape[1]*self.pixel_spac[0,0]-self.display_data[1].shape[1]*self.pixel_spac[1,0])-(self.Im_PatPosition[1,1]-self.Im_PatPosition[0,1])
    update_view(self)

def update_translation_z(self):
    self.Im_PatPosition[1,2]   =  float(self.Reg_manual_Tz.value())
    self.Im_Offset[1,2]        = (self.Im_PatPosition[1,2]-self.Im_PatPosition[0,2])
    update_view(self)

                 
def update_rotation_x(self):
    self._ax = float(self.Reg_manual_Rot_X.value())
    self.display_data[1] = rotate_volume_center_aniso(self, self._vol_orig, self._ax, self._ay, self._az, order=0)
    update_view(self)

def update_rotation_y(self):     
    self._ay = float(self.Reg_manual_Rot_Y.value())
    self.display_data[1] = rotate_volume_center_aniso(self, self._vol_orig, self._ax, self._ay, self._az,order=0)
    update_view(self)

def update_rotation_z(self):
    self._az = float(self.Reg_manual_Rot_Z.value())
    dz = float(self.slice_thick[1])
    dy = float(self.pixel_spac[1, 0])
    dx = float(self.pixel_spac[1, 1])
    self.display_data[1] = rotate_volume_center_aniso(self, self._vol_orig, self._ax, self._ay, self._az,order=0)
    update_view(self)

def set_transformation_step(self):
    for w in (
    self.Reg_manual_Tx, self.Reg_manual_Ty, self.Reg_manual_Tz,
    self.Reg_manual_Refx, self.Reg_manual_Refy, self.Reg_manual_Refz,
    self.Reg_manual_Rot_X, self.Reg_manual_Rot_Y, self.Reg_manual_Rot_Z
    ):
        w.blockSignals(False)

    # set step size for all spinboxes
    step = self.Manual_reg_step.value()  # QDoubleSpinBox current step size
    for w in (
        self.Reg_manual_Tx, self.Reg_manual_Ty, self.Reg_manual_Tz,
        self.Reg_manual_Refx, self.Reg_manual_Refy, self.Reg_manual_Refz,
        self.Reg_manual_Rot_X, self.Reg_manual_Rot_Y, self.Reg_manual_Rot_Z
    ):
        w.setSingleStep(step)
        w.setDecimals(3)              # optional
        w.setRange(-1e6, 1e6)         # optional: sensible range



import numpy as np
from math import radians
from scipy.ndimage import affine_transform

def rotate_volume_center_aniso(self,
    volume: np.ndarray,
    ax_deg: float, ay_deg: float, az_deg: float,
    order: int = 1,
    spacing_mode: str = "same"  # "same" or "effective"
) -> np.ndarray:
    """
    Rotate a 3D volume (Z,Y,X) around its *center* in physical space using anisotropic spacing.
    Output shape is resized to tightly contain the rotated volume (no cropping).
    spacing_mode:
        - "same"      -> keep voxel spacing equal to reference (recommended for resampling)
        - "effective" -> update voxel spacing to directional effective values after rotation
    """
    # --- reference spacings (do NOT mutate) ---
    dz0 = float(self.slice_thick_ref)     # spacing along Z
    dy0 = float(self.pixel_spac_ref[0])   # spacing along Y (row)
    dx0 = float(self.pixel_spac_ref[1])   # spacing along X (col)

    # --- angles (radians) ---
    ax, ay, az = map(radians, (ax_deg, ay_deg, az_deg))

    # --- rotation matrices in (Z,Y,X) indexing convention ---
    Rx = np.array([[ np.cos(ax), -np.sin(ax), 0.0],
                   [ np.sin(ax),  np.cos(ax), 0.0],
                   [    0.0    ,     0.0    , 1.0]], dtype=np.float32)
    Ry = np.array([[ np.cos(ay), 0.0,  np.sin(ay)],
                   [    0.0    , 1.0,     0.0   ],
                   [-np.sin(ay), 0.0,  np.cos(ay)]], dtype=np.float32)
    Rz = np.array([[1.0,    0.0     ,    0.0   ],
                   [0.0,  np.cos(az), -np.sin(az)],
                   [0.0,  np.sin(az),  np.cos(az)]], dtype=np.float32)

    # Compose rotations about fixed axes (Z -> Y -> X)
    R = Rx @ (Ry @ Rz)                 # physical-space rotation
    R_inv = R.T                        # inverse for pure rotation

    # --- spacing matrices from reference spacings ---
    S     = np.diag([dz0, dy0, dx0]).astype(np.float32)         # phys per index
    S_inv = np.diag([1.0/dz0, 1.0/dy0, 1.0/dx0]).astype(np.float32)

    # Backward (what SciPy needs): index_out -> index_in
    A = S_inv @ R_inv @ S              # 3x3
    # Forward (for bounding box): index_in -> index_out
    F = S_inv @ R @ S                  # 3x3

    # Center (in input index coords)
    D, H, W = map(float, volume.shape)  # Z,Y,X
    c = np.array([(D - 1.0)/2.0, (H - 1.0)/2.0, (W - 1.0)/2.0], dtype=np.float32)

    # Forward mapping with center rotation: q = F p + b,  where b = c - F c
    b = c - F @ c

    # Map the 8 input corners to output coords to get a tight axis-aligned bbox
    corners = np.array([
        [0.0,   0.0,   0.0  ],
        [D-1.0, 0.0,   0.0  ],
        [0.0,   H-1.0, 0.0  ],
        [0.0,   0.0,   W-1.0],
        [D-1.0, H-1.0, 0.0  ],
        [D-1.0, 0.0,   W-1.0],
        [0.0,   H-1.0, W-1.0],
        [D-1.0, H-1.0, W-1.0],
    ], dtype=np.float32)

    q = (F @ corners.T).T + b          # (8,3)
    q_min = q.min(axis=0)
    q_max = q.max(axis=0)

    # Output shape to contain all corners (add 1 because indices are inclusive)
    shape_out = tuple(np.ceil(q_max - q_min + 1.0).astype(int).tolist())  # (Z',Y',X')

    # We want output index 0 to map to q_min -> derive SciPy offset:
    # q = F p + b ; p = A q - A b ; with q := o + q_min => p = A o + A(q_min - b)
    offset = (A @ (q_min - b)).astype(np.float32)

    # --- resample ---
    vol_f32 = volume.astype(np.float32, copy=False)
    out = affine_transform(
        input=vol_f32,
        matrix=A,
        offset=offset,
        output_shape=shape_out,
        order=order,
        mode="constant",
        cval=self.reg_fill_value.value(),
        prefilter=(order > 1)
    )

    # --- update voxel spacing metadata ---
    if spacing_mode == "same":
        dz_eff, dy_eff, dx_eff = dz0, dy0, dx0
    elif spacing_mode == "effective":
        # Effective spacing along lab axes after rotation (directional resolution)
        # Δ_k = sqrt( sum_j ( R[k,j] * spacing_j )^2 ),  spacing_j = (dz0,dy0,dx0)
        dz_eff = float(np.sqrt((R[0,0]*dz0)**2 + (R[0,1]*dy0)**2 + (R[0,2]*dx0)**2))
        dy_eff = float(np.sqrt((R[1,0]*dz0)**2 + (R[1,1]*dy0)**2 + (R[1,2]*dx0)**2))
        dx_eff = float(np.sqrt((R[2,0]*dz0)**2 + (R[2,1]*dy0)**2 + (R[2,2]*dx0)**2))
    else:
        raise ValueError("spacing_mode must be 'same' or 'effective'")

    self.slice_thick[1]   = dz_eff
    self.pixel_spac[1, 0] = dy_eff
    self.pixel_spac[1, 1] = dx_eff

    return out.astype(volume.dtype, copy=False)

def apply_trasnformation(self):
    # Accessing the values
    self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SliceThickness']       = self.slice_thick[1]  
    self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing']         = self.pixel_spac[1, :2]
    self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['ImagePositionPatient'] = self.Im_PatPosition[1, :3] 
    self.display_data[1] = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix']  = self.display_data[1]