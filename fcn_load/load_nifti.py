import os
import SimpleITK as sitk
import numpy as np
from PyQt5.QtWidgets import QFileDialog
from pathlib import Path

NIFTI_EXTS = ('.nii', '.nii.gz')

def _series_number_from_name(filename: str) -> str:
    """
    Strip .nii or .nii.gz from a filename for a human-friendly SeriesNumber.
    """
    fn = filename
    fl = filename.lower()
    if fl.endswith('.nii.gz'):
        return fn[:-7]
    if fl.endswith('.nii'):
        return fn[:-4]
    return fn

def read_nifti_series(path):
    """
    Read a NIfTI file (.nii or .nii.gz) with SimpleITK and return a series dict
    compatible with your DICOM-like structure.

    Notes:
      - Image voxels are cast to int16 (to match your workflow).
      - Volume is flipped along axis=1 (y) to match your CT/MR handling.
      - Geometry (Direction, Origin, Spacing) and NIfTI sform/qform rows
        are preserved in metadata so the exporter can round-trip exactly.
    """
    filename = os.path.basename(path)
    series_number = _series_number_from_name(filename)

    # ---- Read with SimpleITK ----
    reader = sitk.ImageFileReader()
    reader.SetImageIO("NiftiImageIO")
    reader.SetFileName(path)
    image = reader.Execute()

    # ---- Voxel data (cast + flip y) ----
    image = sitk.Cast(image, sitk.sitkInt16)
    vol = sitk.GetArrayFromImage(image)        # (z, y, x)
    vol = np.flip(vol, axis=1).astype(np.int16)

    # ---- Geometry ----
    spacing   = image.GetSpacing()             # (x, y, z)
    size      = image.GetSize()                # (x, y, z) ints
    origin    = image.GetOrigin()              # (x0, y0, z0)
    direction = image.GetDirection()           # len=9 row-major 3x3

    # ---- NIfTI header/meta (strings) ----
    try:
        nifti_meta = {k: image.GetMetaData(k) for k in image.GetMetaDataKeys()}
    except Exception:
        nifti_meta = {}

    # Normalize expected keys so exporter can always reuse exact affine
    # (leave as strings; exporter parses when needed)
    for k in ("srow_x", "srow_y", "srow_z", "qform_code", "sform_code"):
        nifti_meta.setdefault(k, nifti_meta.get(k, ""))

    # ---- Build series dict ----
    return {
        'SeriesNumber': series_number,
        'metadata': {
            # spacing[0:2] is ITK (x,y); SliceThickness from spacing[2]
            'PixelSpacing': spacing[0:2],
            'SliceThickness': spacing[2] if len(spacing) >= 3 else 1.0,

            # Full geometry for faithful export
            'Direction': tuple(direction),     # 9 numbers
            'ITKSpacing': tuple(spacing),      # (x,y,z)
            'ImagePositionPatient': origin,    # origin

            # Optional / placeholders kept for compatibility with your UI
            'ImageOrientationPatient': "N/A",
            'RescaleSlope': "N/A",
            'RescaleIntercept': "N/A",
            'WindowWidth': "N/A",
            'WindowCenter': "N/A",
            'SeriesDescription': series_number,
            'StudyDescription': '',
            'ImageComments': '',
            'DoseGridScaling': "N/A",
            'AcquisitionNumber': "N/A",
            'Modality': "Medical",
            'LUTLabel': "N/A",
            'LUTExplanation': "N/A",

            # Useful extras
            'size': size,
            'DataType': 'Nifti',
            'DCM_Info': None,
            'Nifiti_info': nifti_meta,         # original NIfTI fields
            'OriginalFilePath': path,          # for traceability
        },
        'images': {},
        'ImagePositionPatients': [],
        'SliceImageComments': {},
        '3DMatrix': vol,
    }

def load_nifti_files(self, path=None):
    """
    Load one or more NIfTI files directly into self.dicom_data so existing
    DICOM-tree code can handle them unchanged.
    """
    start_dir = getattr(self, 'last_nifti_dir', str(Path.home()))

    # File selection
    if path is None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open NIfTI files",
            start_dir,
            "NIfTI files (*.nii *.nii.gz);;All files (*)"
        )
    else:
        if os.path.isdir(path):
            paths = [
                os.path.join(path, f)
                for f in os.listdir(path)
                if f.lower().endswith(NIFTI_EXTS)
            ]
        elif os.path.isfile(path):
            paths = [path]
        else:
            paths = []

    if not paths:
        return

    # Ensure container dict
    if not hasattr(self, 'dicom_data') or not isinstance(self.dicom_data, dict):
        self.dicom_data = {}

    for fpath in paths:
        if not fpath.lower().endswith(NIFTI_EXTS):
            continue

        # Map to DICOM-like hierarchy
        patient_id = os.path.basename(os.path.dirname(fpath)) or "UnknownPatient"
        study_id   = "Imaging"
        modality   = "Medical"

        patient_data  = self.dicom_data.setdefault(patient_id, {})
        study_data    = patient_data.setdefault(study_id, {})
        modality_list = study_data.setdefault(modality, [])

        # Append series
        modality_list.append(read_nifti_series(fpath))

    # Remember last dir and refresh tree
    self.last_nifti_dir = str(Path(paths[0]).parent)

    from fcn_load.populate_dcm_list import populate_DICOM_tree
    populate_DICOM_tree(self)
