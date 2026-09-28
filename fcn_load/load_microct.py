"""
MicroCT image-stack loader (BMP / TIFF) with SkyScan / Bruker .log parsing.

Produces a ``medical_image`` dict identical in structure to the DICOM loader
so every downstream feature (display, segmentation, export, …) works unchanged.

Uses a background QThread to keep the GUI responsive during I/O-heavy loading,
pre-allocates the volume as int16, applies the vertical slice flip on the fly
(avoiding a duplicate 23+ GB array allocation), and dispatches results back to
the main GUI thread via a dedicated QObject receiver with Qt.QueuedConnection.
"""

import os
import re
from pathlib import Path

import numpy as np
from PIL import Image
from PySide6.QtWidgets import QFileDialog, QProgressDialog, QMessageBox
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt

from fcn_load.populate_med_image_list import populate_medical_image_tree


# ── helpers ─────────────────────────────────────────────────────────────

SLICE_EXTS = ('.bmp', '.tif', '.tiff')

_REC_NUM_RE = re.compile(r'_rec(\d+)', re.IGNORECASE)


def _extract_slice_index(filename: str) -> int:
    """
    Return the integer slice index embedded in the filename.
    Matches patterns like ``_rec0060``, ``_rec2648``.
    Falls back to trailing digits before the extension.
    """
    m = _REC_NUM_RE.search(filename)
    if m:
        return int(m.group(1))
    # fallback: last digits before extension
    stem = Path(filename).stem
    trailing = re.search(r'(\d+)$', stem)
    if trailing:
        return int(trailing.group(1))
    return 0


def _parse_skyscan_log(log_path: str) -> dict:
    """
    Parse a SkyScan / Bruker ``_rec.log`` file (INI-like format) and return
    a flat dict of all key = value pairs.  Section names are preserved as
    a ``__section__`` prefix when collisions exist.
    """
    meta = {}
    current_section = ''
    try:
        with open(log_path, 'r', encoding='utf-8', errors='replace') as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line:
                    continue
                # section header
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    continue
                # key = value
                if '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip()
                    meta[key] = value
                    # also store with section prefix for disambiguation
                    meta[f'{current_section}/{key}'] = value
    except Exception as exc:
        print(f'[microCT] Warning: could not parse log file {log_path}: {exc}')
    return meta


def _find_log_file(folder: str) -> str | None:
    """
    Walk the given folder *and* its parent looking for a ``_rec.log`` file.
    Prefer the one inside the folder, fall back to parent.
    """
    candidates = []
    for search_dir in [folder, str(Path(folder).parent)]:
        try:
            for fname in os.listdir(search_dir):
                if fname.lower().endswith('.log') and '_rec' in fname.lower():
                    # skip CTan analysis logs
                    if '.ctan.' in fname.lower():
                        continue
                    candidates.append(os.path.join(search_dir, fname))
        except OSError:
            pass
    # prefer the one in the same folder as the images
    for c in candidates:
        if Path(c).parent == Path(folder):
            return c
    return candidates[0] if candidates else None


def _safe_float(value, default=1.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _read_single_slice(fpath: str) -> np.ndarray:
    """
    Read a BMP or TIFF slice using OpenCV's fast C++ imdecode if available,
    falling back to PIL. Returns 2D numpy array flipped vertically for VTK.
    """
    try:
        import cv2
        raw = np.fromfile(fpath, dtype=np.uint8)
        arr = cv2.imdecode(raw, cv2.IMREAD_UNCHANGED)
        if arr is not None:
            if arr.ndim == 3:
                arr = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
            return arr[::-1]
    except Exception:
        pass

    # Fallback to PIL
    with Image.open(fpath) as img:
        arr = np.array(img)
    if arr.ndim == 3:
        arr = (0.2989 * arr[..., 0].astype(np.float32) +
               0.5870 * arr[..., 1].astype(np.float32) +
               0.1140 * arr[..., 2].astype(np.float32))
    return arr[::-1]


# ── QThread worker & Main-Thread Receiver ──────────────────────────────

class _MicroCTReceiver(QObject):
    """
    QObject living on the main GUI thread.
    Slots decorated with @Slot ensure PySide executes them on the main
    thread via Qt's queued connection mechanism, preventing any cross-thread
    GUI widget access or OpenGL rendering crashes.
    """
    def __init__(self, parent, on_result, on_error):
        super().__init__(parent)
        self._on_result = on_result
        self._on_error = on_error

    @Slot(object)
    def handle_result(self, data):
        self._on_result(data)

    @Slot(str)
    def handle_error(self, msg):
        self._on_error(msg)


class _MicroCTLoadWorker(QObject):
    """Worker that reads BMP/TIFF slices in parallel using a thread pool."""
    progress  = Signal(int)          # 0-100
    status    = Signal(str)          # label text
    result    = Signal(object)       # (vol, slice_files)
    error     = Signal(str)
    finished  = Signal()

    def __init__(self, folder_path, slice_files):
        super().__init__()
        self.folder_path = folder_path
        self.slice_files = slice_files
        self._aborted = False

    def abort(self):
        self._aborted = True

    def run(self):
        import concurrent.futures
        executor = None
        try:
            n = len(self.slice_files)
            if n == 0:
                self.error.emit("No slices found.")
                return

            self.status.emit(f'Initializing {n} slices …')

            # Peek at first image to get dimensions
            first_path = os.path.join(self.folder_path, self.slice_files[0])
            first_slice = _read_single_slice(first_path)
            h, w = first_slice.shape[:2]

            # Pre-allocate the full volume as int16
            try:
                vol = np.empty((n, h, w), dtype=np.int16)
            except MemoryError:
                est_gb = n * h * w * 2 / (1024**3)
                self.error.emit(
                    f"Out of memory allocating volume: requested {n}x{h}x{w} int16 (~{est_gb:.1f} GB).\n"
                    f"Please close background applications or free up system RAM."
                )
                return

            vol[0] = first_slice
            del first_slice

            if n == 1:
                self.progress.emit(100)
                self.result.emit((vol, self.slice_files))
                return

            # Read remaining slices concurrently using ThreadPoolExecutor
            num_workers = min(32, max(4, os.cpu_count() or 4))
            self.status.emit(f'Loading {n} slices ({num_workers} threads) …')

            def _load_one(idx):
                if self._aborted:
                    return idx
                fpath = os.path.join(self.folder_path, self.slice_files[idx])
                vol[idx] = _read_single_slice(fpath)
                return idx

            completed = 1
            pct_step = max(1, n // 100)

            executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_workers)
            futures = [executor.submit(_load_one, i) for i in range(1, n)]

            for fut in concurrent.futures.as_completed(futures):
                if self._aborted:
                    executor.shutdown(wait=False, cancel_futures=True)
                    print('[microCT] Load cancelled by user.')
                    return

                fut.result()
                completed += 1
                if completed % pct_step == 0 or completed == n:
                    pct = int(completed / n * 100)
                    self.progress.emit(pct)
                    self.status.emit(f'Loaded {completed}/{n} slices ({pct}%) …')

            executor.shutdown(wait=True)
            executor = None

            if not self._aborted:
                self.result.emit((vol, self.slice_files))

        except Exception as exc:
            if executor:
                executor.shutdown(wait=False, cancel_futures=True)
            import traceback
            self.error.emit(f'{exc}\n{traceback.format_exc()}')
        finally:
            self.finished.emit()


# ── main loader ─────────────────────────────────────────────────────────

def load_microct_stack(self, folder_path=None):
    """
    Load a folder of BMP / TIFF slices produced by a microCT reconstructor
    (e.g. NRecon for Bruker SkyScan) and insert them into
    ``self.medical_image`` using the same hierarchy as the DICOM loader::

        medical_image[patient_id][study_id]['CT'][0]  →  series dict

    The accompanying ``_rec.log`` file is parsed for metadata such as voxel
    size, scanner model, acquisition parameters, etc.

    Loading runs in a background QThread with a progress dialog.
    Results are safely dispatched back to the main GUI thread via a QObject
    receiver with Qt.QueuedConnection.
    """

    # ── 1. folder selection ──────────────────────────────────────────
    start_dir = getattr(self, 'last_microct_dir', str(Path.home()))
    if folder_path is None:
        folder_path = QFileDialog.getExistingDirectory(
            self,
            'Select microCT reconstruction folder',
            start_dir,
        )
    if not folder_path or not os.path.isdir(folder_path):
        return

    self.last_microct_dir = folder_path

    # ── 2. collect slice files ───────────────────────────────────────
    all_files = sorted(
        [
            f for f in os.listdir(folder_path)
            if Path(f).suffix.lower() in SLICE_EXTS
        ],
        key=lambda f: _extract_slice_index(f),
    )

    # Keep only numbered _rec files (exclude _rec_spr.bmp etc.)
    slice_files = [f for f in all_files if _REC_NUM_RE.search(f)]

    if not slice_files:
        print('[microCT] No numbered BMP/TIFF slice files found in', folder_path)
        QMessageBox.warning(self, 'microCT Loader', f'No numbered slice files (_rec*.bmp/tif) found in:\n{folder_path}')
        return

    print(f'[microCT] Found {len(slice_files)} slice files in {folder_path}')

    # ── 3. parse log file ────────────────────────────────────────────
    log_path = _find_log_file(folder_path)
    log_meta = {}
    if log_path:
        log_meta = _parse_skyscan_log(log_path)
        print(f'[microCT] Parsed log: {log_path}')
    else:
        print('[microCT] Warning: no _rec.log file found – using defaults')

    # ── 4. extract key geometry from log ─────────────────────────────
    # Pixel Size in the log is in µm; convert to mm for DICOM compatibility
    pixel_size_um = _safe_float(log_meta.get('Pixel Size (um)'), 4.0)
    pixel_size_mm = pixel_size_um / 1000.0  # µm → mm
    slice_thickness_mm = pixel_size_mm      # isotropic voxel

    # ── 5. progress dialog ───────────────────────────────────────────
    n_slices = len(slice_files)
    est_mem_gb = n_slices * 2124 * 2124 * 2 / (1024**3)  # rough estimate
    dlg = QProgressDialog(
        f'Loading {n_slices} microCT slices (~{est_mem_gb:.1f} GB) …',
        'Cancel', 0, 100, self
    )
    dlg.setWindowModality(Qt.ApplicationModal)
    dlg.setWindowTitle('microCT loader')
    dlg.setMinimumDuration(0)
    dlg.setValue(0)
    dlg.setAutoClose(True)
    dlg.setAutoReset(False)

    # ── 6. launch background thread ──────────────────────────────────
    thread = QThread(self)
    worker = _MicroCTLoadWorker(folder_path, slice_files)
    worker.moveToThread(thread)

    def _on_result(data):
        try:
            vol, _ = data

            print(f'[microCT] Volume shape: {vol.shape}  '
                  f'voxel: {pixel_size_mm:.5f} mm isotropic  '
                  f'dtype: {vol.dtype}')

            # ── Window / level from data ─────────────────────────────
            p1  = float(np.percentile(vol[::4, ::4, ::4], 1))   # subsample for speed
            p99 = float(np.percentile(vol[::4, ::4, ::4], 99))
            window_width  = p99 - p1 if (p99 - p1) > 0 else 256.0
            window_center = (p1 + p99) / 2.0

            # ── identifiers ──────────────────────────────────────────
            folder_name  = Path(folder_path).name
            parent_name  = Path(folder_path).parent.name
            patient_id   = log_meta.get('Filename Prefix', parent_name).strip() or parent_name
            study_id     = log_meta.get('Study Date and Time', folder_name).strip() or folder_name
            series_desc  = folder_name
            scanner      = log_meta.get('Scanner', 'microCT')

            first_slice_idx = _extract_slice_index(slice_files[0])
            origin_z = first_slice_idx * pixel_size_mm
            origin = [0.0, 0.0, origin_z]

            # ── Build series dict (DICOM compatible) ─────────────────
            series_data = {
                'SeriesNumber': 1,
                'metadata': {
                    # Geometry (DICOM-compatible fields)
                    'PixelSpacing': [pixel_size_mm, pixel_size_mm],
                    'SliceThickness': slice_thickness_mm,
                    'ImageOrientationPatient': [1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
                    'ImagePositionPatient': origin,
                    'RescaleSlope': 'N/A',
                    'RescaleIntercept': 'N/A',
                    'WindowWidth': window_width,
                    'WindowCenter': window_center,

                    # Descriptors
                    'SeriesDescription': series_desc,
                    'StudyDescription': f'{scanner} – {patient_id}',
                    'ImageComments': '',
                    'AcquisitionNumber': 1,
                    'PatientPosition': 'N/A',
                    'AcquisitionPlane': 'AXIAL',

                    # UIDs (fabricated – needed by the tree / combo logic)
                    'SeriesInstanceUID': f'microCT.{hash(folder_path) & 0xFFFFFFFF:08X}.1',
                    'StudyInstanceUID':  f'microCT.{hash(folder_path) & 0xFFFFFFFF:08X}',
                    'FrameOfReferenceUID': f'microCT.{hash(folder_path) & 0xFFFFFFFF:08X}.FoR',
                    'SOPInstanceUID': f'microCT.{hash(folder_path) & 0xFFFFFFFF:08X}.SOP',
                    'StudyDate': log_meta.get('Study Date and Time', ''),
                    'SeriesDate': log_meta.get('Time and Date', ''),

                    # Type / modality
                    'DataType': 'microCT',
                    'Modality': 'CT',
                    'LUTExplanation': '',
                    'LUTLabel': 'N/A',
                    'DoseGridScaling': 'N/A',
                    'DoseSummationType': 'N/A',
                    'DoseType': 'N/A',
                    'ReferencedRTPlanSOPInstanceUID': 'N/A',
                    'ReferencedStructureSetSOPInstanceUID': 'N/A',

                    # No DICOM header object
                    'DCM_Info': None,
                    'size': (vol.shape[2], vol.shape[1], vol.shape[0]),
                    'Nifiti_info': None,
                    'OriginalFilePath': folder_path,

                    # ── microCT-specific metadata from log ──
                    'microCT_Log': log_meta,
                    'microCT_LogPath': log_path,
                    'microCT_PixelSize_um': pixel_size_um,
                    'microCT_Scanner': scanner,
                    'microCT_SourceVoltage_kV': log_meta.get('Source Voltage (kV)', 'N/A'),
                    'microCT_SourceCurrent_uA': log_meta.get('Source Current (uA)', 'N/A'),
                    'microCT_Exposure_ms': log_meta.get('Exposure (ms)', 'N/A'),
                    'microCT_Filter': log_meta.get('Filter', 'N/A'),
                    'microCT_RotationStep_deg': log_meta.get('Rotation Step (deg)', 'N/A'),
                    'microCT_NumberOfSlices': vol.shape[0],
                    'microCT_ResultFileType': log_meta.get('Result File Type', 'N/A'),
                    'microCT_SectionsCount': log_meta.get('Sections Count', 'N/A'),
                    'microCT_FirstSection': log_meta.get('First Section', 'N/A'),
                    'microCT_LastSection': log_meta.get('Last Section', 'N/A'),
                    'microCT_Smoothing': log_meta.get('Smoothing', 'N/A'),
                    'microCT_RingArtifactCorrection': log_meta.get('Ring Artifact Correction', 'N/A'),
                    'microCT_BeamHardeningCorrection': log_meta.get('Beam Hardening Correction (%)', 'N/A'),
                    'microCT_ReconstructionProgram': log_meta.get('Reconstruction Program', 'N/A'),
                },
                '3DMatrix': vol,
                'images': {},
                'ImagePositionPatients': [
                    [0.0, 0.0, float(origin_z + k * slice_thickness_mm)]
                    for k in range(vol.shape[0])
                ],
                'SliceImageComments': {},
                'AM_name': None,
                'US_name': None,
            }

            # ── Insert into self.medical_image ────────────────────────
            if not hasattr(self, 'medical_image') or self.medical_image is None or not isinstance(self.medical_image, dict):
                self.medical_image = {}

            pat = self.medical_image.setdefault(patient_id, {})
            stu = pat.setdefault(study_id, {})
            mod = stu.setdefault('CT', [])
            mod.append(series_data)

            if hasattr(self, 'segStructList') and self.segStructList is not None and hasattr(self.segStructList, 'clear'):
                self.segStructList.clear()

            self.DataType = 'microCT'
            # Safely populate tree and trigger display on main thread
            populate_medical_image_tree(self)
            print(f'[microCT] Successfully loaded: {patient_id} / {study_id} / CT series 1')

        except Exception as exc:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, 'microCT Display Error', f'Failed to process loaded volume:\n{exc}')

    def _on_error(msg):
        QMessageBox.critical(self, 'microCT Load Error', msg)
        print(f'[microCT] Error: {msg}')

    # Create receiver on the main GUI thread
    receiver = _MicroCTReceiver(self, _on_result, _on_error)

    # Wire signals with Qt.QueuedConnection to guarantee execution on the main GUI thread
    worker.progress.connect(dlg.setValue)
    worker.status.connect(dlg.setLabelText)
    worker.result.connect(receiver.handle_result, Qt.QueuedConnection)
    worker.error.connect(receiver.handle_error, Qt.QueuedConnection)
    worker.finished.connect(dlg.close)
    worker.finished.connect(thread.quit)
    worker.finished.connect(thread.deleteLater)
    thread.started.connect(worker.run)

    # Cancel support
    dlg.canceled.connect(worker.abort)

    # Keep references on MainWindow so Python garbage collector does not kill them
    self._microct_thread = thread
    self._microct_worker = worker
    self._microct_receiver = receiver
    self._microct_dialog = dlg

    thread.start()
