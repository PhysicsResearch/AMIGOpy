import os
import gzip
import shutil
import tempfile
from pathlib import Path
import numpy as np
import SimpleITK as sitk
from PySide6.QtWidgets import QFileDialog

NIFTI_EXTS = ('.nii', '.nii.gz', '.gz')

def is_nifti_file(filename: str | Path) -> bool:
    fl = str(filename).lower()
    return fl.endswith('.nii') or fl.endswith('.nii.gz') or fl.endswith('.gz')

def _series_number_from_name(filename: str) -> str:
    """
    Strip .nii, .nii.gz, or .gz from a filename for a human-friendly SeriesNumber.
    """
    fn = os.path.basename(str(filename))
    fl = fn.lower()
    if fl.endswith('.nii.gz'):
        return fn[:-7]
    if fl.endswith('.nii'):
        return fn[:-4]
    if fl.endswith('.gz'):
        base = fn[:-3]
        if base.lower().endswith('.nii'):
            base = base[:-4]
        return base
    return fn

def read_nifti_series(path):
    """
    Read a NIfTI file (.nii, .nii.gz, or .gz) with SimpleITK and return a series dict
    compatible with your DICOM-like structure.
    Works directly with compressed .nii.gz without manual pre-decompression.

    Notes:
      - Image voxels are cast to int16 (to match your workflow).
      - Volume is flipped along axis=1 (y) to match your CT/MR handling.
      - Geometry (Direction, Origin, Spacing) and NIfTI sform/qform rows
        are preserved in metadata so the exporter can round-trip exactly.
    """
    path_str = os.fspath(path)
    filename = os.path.basename(path_str)
    series_number = _series_number_from_name(filename)

    temp_unpacked = None
    image = None

    # 1. Attempt standard direct SimpleITK read
    try:
        reader = sitk.ImageFileReader()
        reader.SetImageIO("NiftiImageIO")
        reader.SetFileName(path_str)
        image = reader.Execute()
    except Exception:
        # 2. Attempt generic auto-detected SimpleITK read
        try:
            image = sitk.ReadImage(path_str)
        except Exception:
            pass

    # 3. Fallback: if direct read failed (e.g. non-standard name like "file.nii 1.gz"),
    # check for gzip magic bytes and decompress on the fly to a temporary .nii
    if image is None:
        is_gzip = False
        try:
            with open(path_str, "rb") as test_f:
                magic = test_f.read(2)
                is_gzip = (magic == b"\x1f\x8b")
        except Exception:
            is_gzip = False

        if is_gzip:
            tmp_fd, temp_unpacked = tempfile.mkstemp(suffix=".nii")
            os.close(tmp_fd)
            with gzip.open(path_str, "rb") as f_in, open(temp_unpacked, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

            reader = sitk.ImageFileReader()
            reader.SetImageIO("NiftiImageIO")
            reader.SetFileName(temp_unpacked)
            image = reader.Execute()
        else:
            raise RuntimeError(f"Could not read NIfTI file: {path_str}")

    try:
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
        for k in ("srow_x", "srow_y", "srow_z", "qform_code", "sform_code"):
            nifti_meta.setdefault(k, nifti_meta.get(k, ""))

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
                'size': size,
                'DataType': 'Nifti',
                'DCM_Info': None,
                'Nifiti_info': nifti_meta,
                'OriginalFilePath': path_str,
            },
            'images': {},
            'ImagePositionPatients': [],
            'SliceImageComments': {},
            '3DMatrix': vol,
            'AM_name': None,
            'US_name': None,
        }
    finally:
        if temp_unpacked and os.path.exists(temp_unpacked):
            try:
                os.remove(temp_unpacked)
            except Exception:
                pass

def load_nifti_files(self, path=None):
    """
    Load one or more NIfTI files (.nii, .nii.gz, or .gz) directly into self.medical_image
    so existing DICOM-tree code can handle them unchanged.
    """
    start_dir = getattr(self, 'last_nifti_dir', str(Path.home()))

    # File selection
    if path is None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open NIfTI files",
            start_dir,
            "NIfTI files (*.nii *.nii.gz *.gz);;Compressed NIfTI (*.nii.gz *.gz);;Uncompressed NIfTI (*.nii);;All files (*)"
        )
    else:
        if os.path.isdir(path):
            paths = [
                os.path.join(path, f)
                for f in os.listdir(path)
                if is_nifti_file(f)
            ]
        elif os.path.isfile(path):
            paths = [path]
        elif isinstance(path, (list, tuple)):
            paths = list(path)
        else:
            paths = []

    if not paths:
        return

    # Ensure container dict
    if not hasattr(self, 'medical_image') or not isinstance(self.medical_image, dict):
        self.medical_image = {}

    loaded_any = False
    for fpath in paths:
        if not is_nifti_file(fpath):
            continue

        try:
            # Map to DICOM-like hierarchy
            patient_id = os.path.basename(os.path.dirname(fpath)) or "UnknownPatient"
            study_id   = "Imaging"
            modality   = "Medical"

            patient_data  = self.medical_image.setdefault(patient_id, {})
            study_data    = patient_data.setdefault(study_id, {})
            modality_list = study_data.setdefault(modality, [])

            # Append series
            modality_list.append(read_nifti_series(fpath))
            loaded_any = True
        except Exception as ex:
            print(f"[NIfTI] Error loading {fpath}: {ex}")

    if not loaded_any:
        return

    # Remember last dir and refresh tree
    if paths and os.path.exists(paths[0]):
        self.last_nifti_dir = str(Path(paths[0]).parent)

    self.DataType = "Nifti"
    from fcn_load.populate_med_image_list import populate_medical_image_tree
    populate_medical_image_tree(self)
