import os
from pathlib import Path
import numpy as np
import SimpleITK as sitk
from PyQt5.QtWidgets import QFileDialog

def export_nifti(self, Patient, Study, Modality, Series,
                      output_folder=None, file_name=None):
    sdict = self.medical_image[Patient][Study][Modality][Series]
    vol = sdict["3DMatrix"]  # Already (z, y, x), flipped in Y during load
    md  = sdict.get("metadata", {})

    if not isinstance(vol, np.ndarray) or vol.ndim != 3:
        raise ValueError("3DMatrix must be a 3D numpy array")

    # ---- 1) Undo the Y-axis flip (that was done at import) ----
    unflipped = np.flip(vol, axis=1)  # Now matches original orientation

    # ---- 2) Create a SimpleITK image ----
    image = sitk.GetImageFromArray(unflipped)  # shape: (z, y, x)

    # ---- 3) Restore metadata ----
    spacing   = None
    sp        = self.medical_image[Patient][Study][Modality][Series]['metadata']['PixelSpacing']
    sx        = float(sp[0])
    sy        = float(sp[1])
    st        = self.medical_image[Patient][Study][Modality][Series]['metadata']['SliceThickness']
    spacing   = (sx, sy, st)
    origin    = self.medical_image[Patient][Study][Modality][Series]['metadata']['ImagePositionPatient']
    direction = [1.0, 0.0, 0.0,
                 0.0, 1.0, 0.0,
                 0.0, 0.0, 1.0]
    

    
    # spacing = md.get("ITKSpacing", (1.0, 1.0, 1.0))
    # origin  = md.get("ImagePositionPatient", (0.0, 0.0, 0.0))
    # direction = md.get("Direction", [1.0, 0.0, 0.0,
    #                                  0.0, 1.0, 0.0,
    #                                  0.0, 0.0, 1.0])

    image.SetSpacing(tuple(spacing))
    image.SetOrigin(tuple(origin))
    image.SetDirection(tuple(direction))

    # ---- 4) Save path ----
    if output_folder is None:
        default_name = f"{Patient}_{Study}_{Modality}_{Series}.nii.gz"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save NIfTI (SimpleITK)", default_name,
            "NIfTI compressed (*.nii.gz);;NIfTI (*.nii)"
        )
        if not path:
            return None
        out_path = Path(path)
    else:
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
        if not file_name:
            file_name = f"{Patient}_{Study}_{Modality}_{Series}.nii.gz"
        if not (str(file_name).endswith(".nii.gz") or str(file_name).endswith(".nii")):
            file_name = str(file_name) + ".nii.gz"
        out_path = output_folder / file_name

    # ---- 5) Save the image ----
    sitk.WriteImage(image, str(out_path))
    return str(out_path)