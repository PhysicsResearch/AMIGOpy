import numpy as np
from scipy.ndimage import affine_transform
from math import  radians
from fcn_display.display_images import update_layer_view

from fcn_display.display_images  import displayaxial, displaycoronal, displaysagittal  

def update_view(self):
    displaycoronal(self)
    displaysagittal(self)
    displayaxial(self)
    update_layer_view(self)

def update_translation_x(self):
    idx = self.layer_selected.currentIndex()
    self.Im_PatPosition[idx,0]   =  float(self.Reg_manual_Tx.value())
    self.Im_Offset[idx,0]   = (self.Im_PatPosition[idx ,0]-self.Im_PatPosition[0,0])
    update_view(self)

def update_translation_y(self):    
    idx = self.layer_selected.currentIndex() 
    # Y spin box maps to Z coordinate (index 2)
    self.Im_PatPosition[idx,2]   =  float(self.Reg_manual_Ty.value())
    self.Im_Offset[idx,2]        = (self.Im_PatPosition[idx ,2]-self.Im_PatPosition[0,2])
    update_view(self)

def update_translation_z(self):
    idx = self.layer_selected.currentIndex()
    # Z spin box maps to Y coordinate (index 1) and is flipped
    self.Im_PatPosition[idx,1]   = -float(self.Reg_manual_Tz.value())
    self.Im_Offset[idx,1]        = (self.display_data[0].shape[1]*self.pixel_spac[0,0]-self.display_data[idx ].shape[1]*self.pixel_spac[idx ,0])-(self.Im_PatPosition[idx,1]-self.Im_PatPosition[0,1])
    update_view(self)

                 
def update_rotation_x(self):
    self._ax = float(self.Reg_manual_Rot_X.value())
    trigger_rotation_update(self)

def update_rotation_y(self):
    self._ay = float(self.Reg_manual_Rot_Y.value())
    trigger_rotation_update(self)

def update_rotation_z(self):
    self._az = float(self.Reg_manual_Rot_Z.value())
    trigger_rotation_update(self)

def trigger_rotation_update(self):
    idx = self.layer_selected.currentIndex()
    if not hasattr(self, 'patientID') or not self.patientID:
        return
    orig_vol = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix']
    
    # 1. Real-time fast low-res preview
    self.display_data[idx] = rotate_volume_center_aniso_fast(self, orig_vol, self._ax, self._ay, self._az, ds=3)
    
    # Recalculate offsets for LPS space alignment
    self.Im_Offset[idx, 0] = (self.Im_PatPosition[idx, 0] - self.Im_PatPosition[0, 0])
    self.Im_Offset[idx, 1] = (self.display_data[0].shape[1] * self.pixel_spac[0, 0] - self.display_data[idx].shape[1] * self.pixel_spac[idx, 0]) - (self.Im_PatPosition[idx, 1] - self.Im_PatPosition[0, 1])
    self.Im_Offset[idx, 2] = (self.Im_PatPosition[idx, 2] - self.Im_PatPosition[0, 2])
    
    update_view(self)
    
    # 2. Setup or start single-shot high-res timer
    if not hasattr(self, '_rotation_timer'):
        from PySide6.QtCore import QTimer
        self._rotation_timer = QTimer()
        self._rotation_timer.setSingleShot(True)
        self._rotation_timer.timeout.connect(lambda: perform_deferred_rotation(self))
        
    self._rotation_timer.start(250)

def perform_deferred_rotation(self):
    idx = self.layer_selected.currentIndex()
    if not hasattr(self, 'patientID') or not self.patientID:
        return
    orig_vol = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix']
    
    # High-quality rotation
    self.display_data[idx] = rotate_volume_center_aniso(self, orig_vol, self._ax, self._ay, self._az, order=0)
    
    # Recalculate offsets
    self.Im_Offset[idx, 0] = (self.Im_PatPosition[idx, 0] - self.Im_PatPosition[0, 0])
    self.Im_Offset[idx, 1] = (self.display_data[0].shape[1] * self.pixel_spac[0, 0] - self.display_data[idx].shape[1] * self.pixel_spac[idx, 0]) - (self.Im_PatPosition[idx, 1] - self.Im_PatPosition[0, 1])
    self.Im_Offset[idx, 2] = (self.Im_PatPosition[idx, 2] - self.Im_PatPosition[0, 2])
    
    update_view(self)

def rotate_volume_center_aniso_fast(self, volume, ax_deg, ay_deg, az_deg, ds=3):
    idx = self.layer_selected.currentIndex()
    small_vol = volume[::ds, ::ds, ::ds]
    
    meta = self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']
    orig_thick = meta['SliceThickness']
    orig_spacing = meta['PixelSpacing']
    
    meta['SliceThickness'] = float(orig_thick) * ds
    meta['PixelSpacing'] = [float(orig_spacing[0]) * ds, float(orig_spacing[1]) * ds]
    
    try:
        out_small = rotate_volume_center_aniso(self, small_vol, ax_deg, ay_deg, az_deg, order=0)
    finally:
        meta['SliceThickness'] = orig_thick
        meta['PixelSpacing'] = orig_spacing
        
    # Scale spacing variables set by rotate_volume_center_aniso back to target resolution
    self.slice_thick[idx]   /= ds
    self.pixel_spac[idx, 0] /= ds
    self.pixel_spac[idx, 1] /= ds
    
    from scipy.ndimage import zoom
    zoom_factors = [
        volume.shape[0] / out_small.shape[0],
        volume.shape[1] / out_small.shape[1],
        volume.shape[2] / out_small.shape[2]
    ]
    out = zoom(out_small, zoom_factors, order=0)
    
    if out.shape != volume.shape:
        padded = np.zeros(volume.shape, dtype=out.dtype)
        z_min = min(out.shape[0], volume.shape[0])
        y_min = min(out.shape[1], volume.shape[1])
        x_min = min(out.shape[2], volume.shape[2])
        padded[:z_min, :y_min, :x_min] = out[:z_min, :y_min, :x_min]
        out = padded
        
    return out

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


def _set_spinbox_silent(sb, val):
    was = sb.blockSignals(True)
    sb.setValue(float(val))
    sb.blockSignals(was)




def rotate_volume_center_aniso(self,
    volume: np.ndarray,
    ax_deg: float, ay_deg: float, az_deg: float,
    order: int = 1,
    spacing_mode: str = "same"  # "same" or "effective"
) -> np.ndarray:
    dz0 = float(self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SliceThickness'])
    dy0 = float(self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing'][0])
    dx0 = float(self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing'][1])

    ax, ay, az = map(radians, (ax_deg, ay_deg, az_deg))

    Rx = np.array([[ np.cos(ax), -np.sin(ax), 0.0],
                   [ np.sin(ax),  np.cos(ax), 0.0],
                   [    0.0    ,     0.0    , 1.0]], dtype=np.float32)
    Ry = np.array([[ np.cos(ay), 0.0,  np.sin(ay)],
                   [    0.0    , 1.0,     0.0   ],
                   [-np.sin(ay), 0.0,  np.cos(ay)]], dtype=np.float32)
    Rz = np.array([[1.0,    0.0     ,    0.0   ],
                   [0.0,  np.cos(az), -np.sin(az)],
                   [0.0,  np.sin(az),  np.cos(az)]], dtype=np.float32)

    R = Rx @ (Ry @ Rz)
    R_inv = R.T

    S     = np.diag([dz0, dy0, dx0]).astype(np.float32)
    S_inv = np.diag([1.0/dz0, 1.0/dy0, 1.0/dx0]).astype(np.float32)

    # Backward (SciPy): index_out -> index_in, for resampling
    A = S_inv @ R_inv @ S
    # Forward (for bbox): index_in -> index_out
    F = S_inv @ R @ S

    D, H, W = map(float, volume.shape)  # (Z,Y,X)
    c_in = np.array([(D-1.0)/2.0, (H-1.0)/2.0, (W-1.0)/2.0], dtype=np.float32)

    # Forward mapping: q = F p + b with center-based rotation
    b = c_in - F @ c_in

    # Corners -> compute bbox in *output index* coords
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
    q = (F @ corners.T).T + b
    q_min = q.min(axis=0)
    q_max = q.max(axis=0)

    # New shape (tight bbox)
    shape_out = tuple(np.ceil(q_max - q_min + 1.0).astype(int).tolist())

    # ---------- CENTER ANCHORING ----------
    # Want: input center c_in maps to *output* center c_out
    c_out = (np.array(shape_out, dtype=np.float32) - 1.0) / 2.0
    # For backward map p = A q + d, enforce p(c_out) = c_in  => d = c_in - A @ c_out
    offset = (c_in - A @ c_out).astype(np.float32)
    # -------------------------------------

    # Resample
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

    # Spacing update
    if spacing_mode == "same":
        dz_eff, dy_eff, dx_eff = dz0, dy0, dx0
    elif spacing_mode == "effective":
        dz_eff = float(np.sqrt((R[0,0]*dz0)**2 + (R[0,1]*dy0)**2 + (R[0,2]*dx0)**2))
        dy_eff = float(np.sqrt((R[1,0]*dz0)**2 + (R[1,1]*dy0)**2 + (R[1,2]*dx0)**2))
        dx_eff = float(np.sqrt((R[2,0]*dz0)**2 + (R[2,1]*dy0)**2 + (R[2,2]*dx0)**2))
    else:
        raise ValueError("spacing_mode must be 'same' or 'effective'")
    idx = self.layer_selected.currentIndex() 
    self.slice_thick[idx]   = dz_eff
    self.pixel_spac[idx, 0] = dy_eff
    self.pixel_spac[idx, 1] = dx_eff

    # # ---------- UPDATE ORIGIN so the *center* stays fixed in patient space ----------
    # # Old center physical position:
    # # (Assuming axes-aligned directions; if you track DICOM direction cosines,
    # #  multiply by that 3x3 first—see note below.)
    # S_eff = np.array([dz_eff, dy_eff, dx_eff], dtype=np.float32)
    # # Old origin: self.Im_PatPosition[1] is in (X,Y,Z) mm
    # old_origin_xyz = self.Im_PatPosition[1, 0:3].astype(np.float32, copy=True)

    # # Index-to-phys in (Z,Y,X): phys_zyx = S_eff * index_zyx
    # old_center_phys_zyx = S_eff * c_in
    # new_center_phys_zyx = S_eff * c_out

    # # To keep centers coincident: new_origin_phys_zyx = old_origin_phys_zyx + old_center - new_center
    # delta_origin_zyx = (old_center_phys_zyx - new_center_phys_zyx)
    # # Convert to (X,Y,Z) ordering for ImagePositionPatient:
    # delta_origin_xyz = np.array([delta_origin_zyx[2], delta_origin_zyx[1], delta_origin_zyx[0]], dtype=np.float32)

    # Im_PatPosition_new = (old_origin_xyz + delta_origin_xyz).astype(np.float32, copy=True)

    # # 1) write the model
    # self.Im_PatPosition[1, 0:3] = Im_PatPosition_new

    # # 2) reflect it in the UI WITHOUT firing signals (prevents the second call)
    # _set_spinbox_silent(self.Reg_manual_Tx, Im_PatPosition_new[0])
    # _set_spinbox_silent(self.Reg_manual_Ty, Im_PatPosition_new[1])
    # _set_spinbox_silent(self.Reg_manual_Tz, Im_PatPosition_new[2])
    # print(self.Im_PatPosition[1, 0:3])
    # # -------------------------------------------------------------------------------

    # # (Optional) keep for debugging
    # self._last_rotation_shape_out = shape_out
    # self._last_rotation_center_anchor_shift_mm_xyz = delta_origin_xyz

    return out.astype(volume.dtype, copy=False)


def apply_trasnformation(self):
    # Accessing the values
    idx = self.layer_selected.currentIndex() 
    self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['SliceThickness']         = self.slice_thick[idx]  
    self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['PixelSpacing']           = self.pixel_spac[idx, :2]
    self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['metadata']['ImagePositionPatient']   = self.Im_PatPosition[idx, :3] 
    self.medical_image[self.patientID][self.studyID][self.modality][self.series_index]['3DMatrix']  = self.display_data[idx]

def flip_volume_x(self):
    idx = self.layer_selected.currentIndex()
    if idx in self.display_data and self.display_data[idx] is not None:
        self.display_data[idx] = np.flip(self.display_data[idx], axis=2)
        update_view(self)

def flip_volume_y(self):
    idx = self.layer_selected.currentIndex()
    if idx in self.display_data and self.display_data[idx] is not None:
        self.display_data[idx] = np.flip(self.display_data[idx], axis=0)
        update_view(self)

def flip_volume_z(self):
    idx = self.layer_selected.currentIndex()
    if idx in self.display_data and self.display_data[idx] is not None:
        self.display_data[idx] = np.flip(self.display_data[idx], axis=1)
        update_view(self)