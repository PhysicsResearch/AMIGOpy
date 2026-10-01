import os
import gzip
import shutil
import tempfile
from pathlib import Path
import numpy as np
import SimpleITK as sitk
from PySide6.QtWidgets import QFileDialog

NIFTI_EXTS = ('.nii', '.nii.gz', '.gz')

def _norm_path(p: str | Path | None) -> str:
    """Canonicalize and normalize path for reliable matching across slashes, case, and symlinks."""
    if not p:
        return ""
    try:
        return os.path.normcase(os.path.abspath(os.path.realpath(os.fspath(p))))
    except Exception:
        return os.path.normcase(os.path.abspath(os.fspath(p)))

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

def _normalize_name(name: str) -> str:
    """Normalize string for robust matching across spaces/underscores/cases."""
    return "".join(c for c in str(name).lower() if c.isalnum())


def _normalize_name(name: str) -> str:
    """Normalize string for robust matching across spaces/underscores/cases."""
    return "".join(c for c in str(name).lower() if c.isalnum())


def find_matching_series_for_structure(parent_app, img_base: str = "", fpath: str = None):
    """
    Search loaded series in parent_app.medical_image for the series corresponding to img_base.
    Matches against:
      - OriginalFilePath stem
      - SeriesDescription
      - SeriesNumber
      - Folder proximity (same folder or subfolder)

    Returns:
        (patient_id, study_id, modality, series_index, series_dict) or None
    """
    if not hasattr(parent_app, 'medical_image') or not isinstance(parent_app.medical_image, dict):
        return None

    norm_target = _normalize_name(img_base) if img_base else ""
    fpath_dir = os.path.normcase(os.path.abspath(os.path.dirname(fpath))) if fpath else None

    best_match = None
    best_priority = -1

    for pat_id, pat_studies in parent_app.medical_image.items():
        if not isinstance(pat_studies, dict):
            continue
        for study_id, study_mods in pat_studies.items():
            if not isinstance(study_mods, dict):
                continue
            for modality, s_list in study_mods.items():
                if not isinstance(s_list, list):
                    continue
                for idx, s_series in enumerate(s_list):
                    if not isinstance(s_series, dict):
                        continue

                    orig_path = s_series.get('metadata', {}).get('OriginalFilePath', '')
                    orig_stem = _series_number_from_name(orig_path) if orig_path else ''
                    s_desc = str(s_series.get('metadata', {}).get('SeriesDescription', ''))
                    s_num = str(s_series.get('SeriesNumber', ''))

                    norm_orig = _normalize_name(orig_stem)
                    norm_desc = _normalize_name(s_desc)
                    norm_num = _normalize_name(s_num)

                    priority = -1
                    if norm_target and (norm_target == norm_orig or norm_target == norm_desc or norm_target == norm_num):
                        priority = 20
                    elif norm_target and (norm_target in norm_orig or norm_orig in norm_target):
                        priority = 10
                    elif not norm_target and fpath_dir and orig_path:
                        orig_dir = os.path.normcase(os.path.abspath(os.path.dirname(orig_path)))
                        if orig_dir == fpath_dir or fpath_dir.startswith(orig_dir) or orig_dir.startswith(fpath_dir):
                            priority = 15

                    if priority > 0 and fpath_dir and orig_path:
                        orig_dir = os.path.normcase(os.path.abspath(os.path.dirname(orig_path)))
                        if orig_dir == fpath_dir or fpath_dir.startswith(orig_dir):
                            priority += 10

                    if priority > best_priority:
                        best_priority = priority
                        best_match = (pat_id, study_id, modality, idx, s_series)

    # Fallback: if only one series exists in medical_image, associate with it
    if best_match is None and fpath:
        all_series = []
        for pat_id, pat_studies in parent_app.medical_image.items():
            if not isinstance(pat_studies, dict):
                continue
            for study_id, study_mods in pat_studies.items():
                if not isinstance(study_mods, dict):
                    continue
                for modality, s_list in study_mods.items():
                    if not isinstance(s_list, list):
                        continue
                    for idx, s_series in enumerate(s_list):
                        all_series.append((pat_id, study_id, modality, idx, s_series))
        if len(all_series) == 1:
            best_match = all_series[0]

    return best_match


def classify_nifti_file(fpath: str) -> dict:
    """
    Determine whether a NIfTI file is a primary medical image series
    or a structure mask / labelmap (from AMIGOpy, TotalSegmentator, 3D Slicer, nnUNet, etc.).
    """
    fn = os.path.basename(fpath)
    fl = fn.lower()
    parts = [p.lower() for p in Path(fpath).parts]

    # Clean stem
    stem = fn
    for ext in ('.nii.gz', '.nii', '.gz'):
        if fl.endswith(ext):
            stem = fn[:-len(ext)]
            break

    # 1. AMIGOpy naming convention: <OriginalFile>_ST_<Name>.nii.gz
    if "_ST_" in stem:
        s_parts = stem.split("_ST_")
        img_base = "_ST_".join(s_parts[:-1]).strip()
        st_name = s_parts[-1].strip()
        return {
            'is_structure': True,
            'associated_image_base': img_base,
            'structure_name': st_name,
            'is_multilabel': False,
        }

    # 2. Known subfolders: structures, masks, labels, segmentations
    is_in_struct_dir = any(p in ("structures", "masks", "labels", "segmentations") for p in parts[:-1])

    # 3. Known filename patterns from 3D Slicer, nnUNet, ITK-SNAP, etc.
    stem_lower = stem.lower()
    has_mask_keyword = any(kw in stem_lower for kw in (
        "_mask", "-mask", "mask_", "mask-",
        "_seg", "-seg", "seg_", "seg-",
        "_label", "-label", "label_", "label-",
        "segmentation", "labelmap", "totalsegmentator"
    ))

    # Fast header check using SimpleITK
    is_uint8 = False
    try:
        reader = sitk.ImageFileReader()
        reader.SetFileName(fpath)
        reader.ReadImageInformation()
        pixel_id = reader.GetPixelID()
        is_uint8 = (pixel_id in (sitk.sitkUInt8, sitk.sitkInt8))
    except Exception:
        pass

    from fcn_export.export_structures_dialog import clean_structure_name

    # If in struct folder or has mask keyword, it is definitely a structure
    if is_in_struct_dir or has_mask_keyword:
        return {
            'is_structure': True,
            'associated_image_base': "",
            'structure_name': clean_structure_name(stem),
            'is_multilabel': False,
        }

    # For general files, inspect voxel intensities to differentiate medical image
    # from a mask / labelmap
    try:
        reader = sitk.ImageFileReader()
        reader.SetFileName(fpath)
        img = reader.Execute()
        arr = sitk.GetArrayFromImage(img)
        min_val = float(np.min(arr))
        max_val = float(np.max(arr))

        # CT / baseline-subtracted MR images have negative values
        if min_val < 0:
            return {'is_structure': False, 'associated_image_base': "", 'structure_name': "", 'is_multilabel': False}

        # Subsample for speed on large volumes
        sub = arr[::3, ::3, ::3] if arr.size > 100000 else arr
        unique_vals = np.unique(sub)
        pos_vals = [int(v) for v in unique_vals if v > 0]

        # Binary mask (0 and 1, or 0 and 255, or uint8 mask)
        if len(pos_vals) == 1 and (pos_vals[0] == 1 or pos_vals[0] == 255 or is_uint8):
            return {
                'is_structure': True,
                'associated_image_base': "",
                'structure_name': clean_structure_name(stem),
                'is_multilabel': False,
            }

        # Multi-label segmentation (e.g. TotalSegmentator, 2 to 150 unique discrete integer labels)
        if 2 <= len(pos_vals) <= 150 and np.all(np.equal(np.mod(unique_vals, 1), 0)):
            if max_val <= 255 or len(pos_vals) < 50:
                return {
                    'is_structure': True,
                    'associated_image_base': "",
                    'structure_name': clean_structure_name(stem),
                    'is_multilabel': True,
                }
    except Exception:
        pass

    return {'is_structure': False, 'associated_image_base': "", 'structure_name': "", 'is_multilabel': False}


def load_nifti_files(self, path=None):
    """
    Load one or more NIfTI files (.nii, .nii.gz, or .gz) directly into self.medical_image
    so existing DICOM-tree code can handle them unchanged.
    Automatically recognizes:
      - *_ST_<strucname>.nii.gz files from AMIGOpy
      - Binary masks and multi-label segmentations from ANY software (TotalSegmentator, Slicer, etc.)
      - Structures inside subfolders or folders loaded as a complete package.
    """
    from fcn_export.export_structures_dialog import is_structure_nifti, import_structures_from_nifti

    start_dir = getattr(self, 'last_nifti_dir', str(Path.home()))

    # 1. File / Folder selection handling
    if path is None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open NIfTI files",
            start_dir,
            "NIfTI files (*.nii *.nii.gz *.gz);;Compressed NIfTI (*.nii.gz *.gz);;Uncompressed NIfTI (*.nii);;All files (*)"
        )
    else:
        if isinstance(path, (list, tuple)):
            paths = list(path)
        elif isinstance(path, (str, Path, os.PathLike)):
            p_str = os.fspath(path)
            if os.path.isdir(p_str):
                paths = []
                for root, _, files in os.walk(p_str):
                    for f in sorted(files):
                        if is_nifti_file(f):
                            paths.append(os.path.join(root, f))
            elif os.path.isfile(p_str):
                paths = [p_str]
            else:
                paths = []
        else:
            paths = []

    if not paths:
        return

    # Ensure container dict
    if not hasattr(self, 'medical_image') or not isinstance(self.medical_image, dict):
        self.medical_image = {}

    # 2. Classify files into primary images vs structure masks / labelmaps with canonical deduplication
    primary_paths = []
    primary_norm_set = set()
    structure_paths = []
    structure_norm_set = set()

    for fpath in paths:
        if not is_nifti_file(fpath):
            continue
        p_norm = _norm_path(fpath)
        info = classify_nifti_file(fpath)
        if info['is_structure']:
            if p_norm not in structure_norm_set:
                structure_norm_set.add(p_norm)
                structure_paths.append((fpath, info))
        else:
            if p_norm not in primary_norm_set:
                primary_norm_set.add(p_norm)
                primary_paths.append(fpath)

    # 3. Check for orphaned structure files whose parent image exists on disk in the same folder
    # but wasn't explicitly selected in paths
    def _is_parent_already_in_primary(img_base_str: str) -> bool:
        if not img_base_str:
            return False
        norm_b = _normalize_name(img_base_str)
        for p in primary_paths:
            if norm_b == _normalize_name(_series_number_from_name(p)):
                return True
        return False

    for spath, s_info in list(structure_paths):
        img_base = s_info.get('associated_image_base')
        if img_base:
            # If the parent scan is already in primary_paths, do NOT search disk or duplicate it
            if _is_parent_already_in_primary(img_base):
                continue

            # If parent scan is already loaded in self.medical_image, do NOT search disk
            match = find_matching_series_for_structure(self, img_base, spath)
            if not match:
                s_dir = os.path.dirname(spath)
                search_dirs = [s_dir]
                if os.path.basename(s_dir).lower() in ("structures", "masks", "labels", "segmentations"):
                    search_dirs.append(os.path.dirname(s_dir))

                found_parent = None
                for sdir in search_dirs:
                    for ext in ('.nii.gz', '.nii', '.gz'):
                        cand = os.path.join(sdir, f"{img_base}{ext}")
                        if os.path.isfile(cand):
                            found_parent = cand
                            break
                    if found_parent:
                        break

                if found_parent:
                    cand_norm = _norm_path(found_parent)
                    if cand_norm not in primary_norm_set:
                        primary_norm_set.add(cand_norm)
                        primary_paths.append(found_parent)

    # If no primary images were found in the folder/selection, check if any structure can attach to loaded series
    if not primary_paths and structure_paths:
        can_match_loaded = any(
            find_matching_series_for_structure(self, s_info.get('associated_image_base', ''), spath) is not None
            for spath, s_info in structure_paths
        )
        if not can_match_loaded:
            # Check if any parent image exists in the same directory on disk
            found_parents = []
            found_parents_norm = set()
            for spath, s_info in structure_paths:
                img_base = s_info.get('associated_image_base')
                if img_base:
                    s_dir = os.path.dirname(spath)
                    for cand_dir in (s_dir, os.path.dirname(s_dir)):
                        for ext in ('.nii.gz', '.nii', '.gz'):
                            cand = os.path.join(cand_dir, f"{img_base}{ext}")
                            cand_norm = _norm_path(cand)
                            if os.path.isfile(cand) and cand_norm not in found_parents_norm:
                                found_parents_norm.add(cand_norm)
                                found_parents.append(cand)
            if found_parents:
                primary_paths = found_parents
            else:
                # Fallback: load as primary images so user can inspect them
                primary_paths = [spath for spath, _ in structure_paths]
                structure_paths = []

    loaded_any = False

    # 4. Load primary image series
    for fpath in primary_paths:
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

            # Check if this exact file is already present in this modality list
            target_norm = _norm_path(fpath)
            existing_idx = None
            for s_i, existing_s in enumerate(modality_list):
                orig = existing_s.get('metadata', {}).get('OriginalFilePath')
                if orig and _norm_path(orig) == target_norm:
                    existing_idx = s_i
                    break

            if existing_idx is not None:
                series_dict = modality_list[existing_idx]
                series_idx = existing_idx
            else:
                series_dict = read_nifti_series(fpath)
                modality_list.append(series_dict)
                series_idx = len(modality_list) - 1
                loaded_any = True

            # Check for associated structures manifest (.json)
            f_dir = os.path.dirname(fpath)
            base_fn = _series_number_from_name(fpath)
            manifest_candidates = [
                os.path.join(f_dir, f"{base_fn}_structures.json"),
                os.path.join(f_dir, "structures", "structures.json"),
                os.path.join(f_dir, "structures.json"),
            ]
            for cand in manifest_candidates:
                if os.path.isfile(cand):
                    try:
                        import_structures_from_nifti(
                            self, patient_id, study_id, modality, series_idx, paths=[cand], show_message=False
                        )
                    except Exception as ex_st:
                        print(f"[NIfTI] Error auto-associating structures for {fpath}: {ex_st}")
                    break

        except Exception as ex:
            print(f"[NIfTI] Error loading {fpath}: {ex}")

    # 5. Attach structure mask files to their corresponding parent series
    for spath, s_info in structure_paths:
        try:
            img_base = s_info.get('associated_image_base', '')
            st_name = s_info.get('structure_name', '')
            target = None
            if img_base:
                target = find_matching_series_for_structure(self, img_base, spath)
            else:
                target = find_matching_series_for_structure(self, "", spath)

            if target:
                pat_id, study_id, modality, s_idx, s_series = target

                # Skip if this mask file was already imported (e.g. from structures.json manifest in Step 4)
                src_files = s_series.get('structures_source_files', set())
                if _norm_path(spath) in src_files:
                    continue

                cnt = import_structures_from_nifti(
                    self, pat_id, study_id, modality, s_idx, paths=[spath], show_message=False
                )
                if cnt > 0:
                    loaded_any = True
                    print(f"[NIfTI] Auto-associated structure '{st_name or os.path.basename(spath)}' with series {s_series.get('SeriesNumber')}")
            else:
                print(f"[NIfTI] Could not find parent series for structure file {spath}")
        except Exception as ex_st:
            print(f"[NIfTI] Error importing structure mask {spath}: {ex_st}")

    if not loaded_any:
        return

    # Remember last dir and refresh tree
    if paths and os.path.exists(paths[0]):
        self.last_nifti_dir = str(Path(paths[0]).parent)

    self.DataType = "Nifti"
    try:
        from fcn_load.populate_med_image_list import populate_medical_image_tree
        populate_medical_image_tree(self)
    except Exception as ex:
        print(f"[NIfTI] Note: Tree refresh failed/skipped: {ex}")

