import os
import SimpleITK as sitk
import numpy as np
from PyQt5.QtWidgets import QFileDialog
from pathlib import Path

def read_nifti_series(path):
    """
    Read a NIfTI file and return a series dict compatible with your DICOM structure.
    """
    filename = os.path.basename(path)
    series_number = filename.removesuffix('.nii.gz')

    # Read image
    reader = sitk.ImageFileReader()
    reader.SetImageIO("NiftiImageIO")
    reader.SetFileName(path)
    image = reader.Execute()

    # Cast and convert to numpy (flip axis=1 to match CT/MR handling)
    image = sitk.Cast(image, sitk.sitkInt16)
    vol = sitk.GetArrayFromImage(image)
    vol = np.flip(vol, axis=1).astype(np.int16)

    # Spacing, size, origin
    spacing = image.GetSpacing()
    size    = image.GetSize()
    origin  = image.GetOrigin()

    # Full NIfTI header/meta as dict
    try:
        nifti_meta = {k: image.GetMetaData(k) for k in image.GetMetaDataKeys()}
    except Exception:
        nifti_meta = {}

    # Return DICOM-like series dict
    return {
        'SeriesNumber': series_number,
        'metadata': {
            'PixelSpacing': spacing[0:2],
            'SliceThickness': spacing[2] if len(spacing) >= 3 else 1.0,
            'ImageOrientationPatient': "N/A",
            'ImagePositionPatient': origin,
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
            'size': size,
            'DataType': 'Nifti',
            'DCM_Info': None,          # keep for compatibility
            'Nifiti_info': nifti_meta, # full NIfTI meta
        },
        'images': {},
        'ImagePositionPatients': [],
        'SliceImageComments': {},
        '3DMatrix': vol,
    }


def load_nifti_files(self, path=None):
    """
    Load NIfTI files directly into self.dicom_data so that all existing
    DICOM functions and tree population logic can handle them.
    """
    start_dir = getattr(self, 'last_nifti_dir', str(Path.home()))

    # Select files
    if path is None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Open NIfTI files", start_dir,
            "NIfTI files (*.nii.gz);;All files (*)"
        )
    else:
        if os.path.isdir(path):
            paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.nii.gz')]
        elif os.path.isfile(path):
            paths = [path]
        else:
            paths = []

    if not paths:
        return

    # Ensure dicom_data dict exists
    if not hasattr(self, 'dicom_data') or self.dicom_data is None or not isinstance(self.dicom_data, dict):
        self.dicom_data = {}

    for fpath in paths:
        if not fpath.endswith('.nii.gz'):
            continue

        # Map to DICOM-like hierarchy
        patient_id = os.path.basename(os.path.dirname(fpath)) or "UnknownPatient"
        study_id   = "Imaging"
        modality   = "Medical"

        patient_data  = self.dicom_data.setdefault(patient_id, {})
        study_data    = patient_data.setdefault(study_id, {})
        modality_list = study_data.setdefault(modality, [])

        # Read NIfTI as DICOM-like series and append
        modality_list.append(read_nifti_series(fpath))

    # Save last dir
    self.last_nifti_dir = str(Path(paths[0]).parent)


    # Populate using existing DICOM tree builder
    from fcn_load.populate_dcm_list import populate_DICOM_tree
    populate_DICOM_tree(self)
