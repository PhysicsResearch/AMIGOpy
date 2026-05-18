import os
import numpy as np
from PySide6.QtWidgets import QFileDialog
from pathlib import Path

NPY_EXTS = ('.npy',)

def _series_number_from_npy(filename: str) -> str:
    """Strip .npy from a filename for a human-friendly SeriesNumber."""
    fn = filename
    fl = filename.lower()
    if fl.endswith('.npy'):
        return fn[:-4]
    return fn

def _suitable_dtype(dtype: np.dtype) -> np.dtype:
    """
    Choose a memory-efficient, widely-supported dtype without losing intent:
      - float64 -> float32 (common for imaging; saves memory, preserves floats)
      - int64   -> int32   (rarely needed for voxel intensities)
      - bool    -> uint8   (binary masks as 0/1)
      - otherwise keep original dtype
    """
    if dtype == np.float64:
        return np.float32
    if dtype == np.int64:
        return np.int32
    if dtype == np.bool_:
        return np.uint8
    return dtype

def _to_zyx_native(vol: np.ndarray) -> np.ndarray:
    """
    Ensure a 3D array shaped (z, y, x) and cast to a suitable dtype.
    - Squeezes singleton dims.
    - If 2D (y, x), adds a single z-slice.
    - If more than 3 dims remain after squeeze, raises ValueError.
    - Flips axis=1 (y) to align with your CT/MR handling.
    - Keeps data type unless it's an obvious heavy type (see _suitable_dtype).
    """
    vol = np.asarray(vol)
    vol = np.squeeze(vol)
    if vol.ndim == 2:           # (y, x) -> (1, y, x)
        vol = vol[np.newaxis, ...]
    if vol.ndim != 3:
        raise ValueError(f"Expected 2D or 3D array for NPY, got shape {vol.shape} (ndim={vol.ndim})")

    # Flip Y to match your existing visualization convention
    vol = np.flip(vol, axis=1)

    # Pick a practical dtype
    target_dtype = _suitable_dtype(vol.dtype)
    if vol.dtype != target_dtype:
        vol = vol.astype(target_dtype, copy=False)
    return vol

def read_npy_series(path):
    """
    Read a NumPy NPY file and return a series dict compatible with your
    DICOM-like structure, using dummy geometry:
      - PixelSpacing = (1.0, 1.0)
      - SliceThickness = 1.0
      - Origin (ImagePositionPatient) = (0.0, 0.0, 0.0)

    Notes:
      - Keeps original dtype where sensible (may downcast float64->float32,
        int64->int32, bool->uint8).
      - Volume interpreted as (z, y, x). 2D arrays are upgraded to (1, y, x).
      - Y axis is flipped to mirror your NIfTI loader behavior.
    """
    filename = os.path.basename(path)
    series_number = _series_number_from_npy(filename)

    # ---- Load numpy volume ----
    vol = np.load(path, mmap_mode='r')
    vol = _to_zyx_native(vol)  # (z, y, x) with suitable dtype

    # ---- Dummy geometry ----
    spacing = (1.0, 1.0, 1.0)               # (x, y, z)
    origin  = (0.0, 0.0, 0.0)               # (x0, y0, z0)
    size    = (vol.shape[2], vol.shape[1], vol.shape[0])  # (x, y, z)

    # ---- Build series dict ----
    return {
        'SeriesNumber': series_number,
        'metadata': {
            'PixelSpacing': spacing[0:2],
            'SliceThickness': spacing[2],
            'ImagePositionPatient': origin,
            # Optional / placeholders for compatibility with your UI
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
            'DataType': 'NPY',
            'DCM_Info': None,
            'Nifiti_info': {},                # keep key for exporter compatibility
            'OriginalFilePath': path,
            'ArrayDType': str(vol.dtype),     # explicit record of dtype used
        },
        'images': {},
        'ImagePositionPatients': [],
        'SliceImageComments': {},
        '3DMatrix': vol,
        'AM_name': None,  # auto name in tree
        'US_name': None,  # user-defined name in UI
    }

def load_npy_files(self, path=None):
    """
    Load one or more .npy volumes directly into self.medical_image so existing
    DICOM-tree code can handle them unchanged.
    """
    start_dir = getattr(self, 'last_npy_dir', str(Path.home()))

    # File selection
    if path is None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open NumPy volumes",
            start_dir,
            "NumPy files (*.npy);;All files (*)"
        )
    else:
        if os.path.isdir(path):
            paths = [
                os.path.join(path, f)
                for f in os.listdir(path)
                if f.lower().endswith(NPY_EXTS)
            ]
        elif os.path.isfile(path):
            paths = [path] if path.lower().endswith(NPY_EXTS) else []
        else:
            paths = []

    if not paths:
        return

    # Ensure container dict
    if not hasattr(self, 'medical_image') or not isinstance(self.medical_image, dict):
        self.medical_image = {}

    for fpath in paths:
        if not fpath.lower().endswith(NPY_EXTS):
            continue

        # Map to DICOM-like hierarchy
        patient_id = os.path.basename(os.path.dirname(fpath)) or "UnknownPatient"
        study_id   = "Imaging"
        modality   = "Medical"

        patient_data  = self.medical_image.setdefault(patient_id, {})
        study_data    = patient_data.setdefault(study_id, {})
        modality_list = study_data.setdefault(modality, [])

        # Append series
        try:
            modality_list.append(read_npy_series(fpath))
        except Exception as e:
            print(f"[NPY Loader] Skipped {fpath}: {e}")

    # Remember last dir and refresh tree
    self.last_npy_dir = str(Path(paths[0]).parent)

    from fcn_load.populate_med_image_list import populate_medical_image_tree
    populate_medical_image_tree(self)
