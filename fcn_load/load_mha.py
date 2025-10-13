import os
import SimpleITK as sitk
import numpy as np
from PySide6.QtWidgets import QFileDialog
from pathlib import Path

MHA_EXTS = ('.mha', '.mhd')  # single-file .mha or header+raw .mhd

def _series_number_from_name_no_ext(filename: str) -> str:
    """
    Strip common medical-image extensions for a human-friendly SeriesNumber.
    """
    fl = filename.lower()
    for ext in ('.nii.gz', '.nii', '.mha', '.mhd'):
        if fl.endswith(ext):
            return filename[:-len(ext)]
    return filename

def read_mha_series(path):
    """
    Read a MetaImage file (.mha or .mhd) with SimpleITK and return a series dict
    compatible with your NIfTI/DICOM-like structure.

    Notes:
      - Voxels cast to int16 (to match your workflow).
      - Volume is flipped along axis=1 (y), like your NIfTI reader.
      - Geometry (Direction, Origin, Spacing) preserved.
      - All available MetaImage header fields are copied to metadata.
    """
    filename = os.path.basename(path)
    series_number = _series_number_from_name_no_ext(filename)

    # ---- Read with SimpleITK ----
    reader = sitk.ImageFileReader()
    reader.SetImageIO("MetaImageIO")
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

    # ---- MetaImage header/meta (strings) ----
    try:
        meta_keys = list(image.GetMetaDataKeys())
        meta_info = {k: image.GetMetaData(k) for k in meta_keys}
    except Exception:
        meta_info = {}

    # Normalize a few common keys so exporters can rely on their presence
    for k in ("ElementSpacing", "ElementType", "TransformMatrix", "Offset", "CenterOfRotation"):
        meta_info.setdefault(k, meta_info.get(k, ""))

    # ---- Build series dict ----
    return {
        'SeriesNumber': series_number,
        'metadata': {
            'PixelSpacing': spacing[0:2],
            'SliceThickness': spacing[2] if len(spacing) >= 3 else 1.0,
            'ImagePositionPatient': origin,
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
            'DataType': 'MetaImage',
            'DCM_Info': None,
            'MetaImage_info': meta_info,        # original MetaImage fields
            'Direction': direction,             # keeping explicit for completeness
            'OriginalFilePath': path,           # for traceability
        },
        'images': {},
        'ImagePositionPatients': [],
        'SliceImageComments': {},
        '3DMatrix': vol,
        'AM_name': None,
        'US_name': None,
    }

def load_mha_files(self, path=None):
    """
    Load one or more MetaImage files directly into self.medical_image so existing
    DICOM-tree code can handle them unchanged.
    """
    start_dir = getattr(self, 'last_mha_dir', str(Path.home()))

    # File selection
    if path is None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open MetaImage files",
            start_dir,
            "MetaImage files (*.mha *.mhd);;All files (*)"
        )
    else:
        if os.path.isdir(path):
            paths = [
                os.path.join(path, f)
                for f in os.listdir(path)
                if f.lower().endswith(MHA_EXTS)
            ]
        elif os.path.isfile(path):
            paths = [path]
        else:
            paths = []

    if not paths:
        return

    # Ensure container dict
    if not hasattr(self, 'medical_image') or not isinstance(self.medical_image, dict):
        self.medical_image = {}

    for fpath in paths:
        if not fpath.lower().endswith(MHA_EXTS):
            continue

        # Map to DICOM-like hierarchy (same as your NIfTI loader)
        patient_id = os.path.basename(os.path.dirname(fpath)) or "UnknownPatient"
        study_id   = "Imaging"
        modality   = "Medical"

        patient_data  = self.medical_image.setdefault(patient_id, {})
        study_data    = patient_data.setdefault(study_id, {})
        modality_list = study_data.setdefault(modality, [])

        # Append series
        modality_list.append(read_mha_series(fpath))

    # Remember last dir and refresh tree
    self.last_mha_dir = str(Path(paths[0]).parent)

    from fcn_load.populate_med_image_list import populate_medical_image_tree
    populate_medical_image_tree(self)
