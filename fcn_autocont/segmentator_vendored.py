# fcn_autocont/segmentator_vendored.py
# -*- coding: utf-8 -*-
from __future__ import annotations

import os, sys, time, traceback, json, shutil, datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

# ---------------------------------------------------------------------------
# Make sure stdlib 'statistics' is used (avoid any vendored shadowing)
import statistics as _stdlib_statistics
sys.modules.setdefault("statistics", _stdlib_statistics)

# Optional Qt (for warnings shown on the GUI thread only)
try:
    from PySide6.QtWidgets import QMessageBox, QApplication
    from PySide6.QtCore import QThread
except Exception:
    QMessageBox = None
    QApplication = None
    QThread = None

# Third-party runtime imports
import numpy as np
import SimpleITK as sitk

# Your exporter
from fcn_export.export_nii import export_nifti


# ======================== vendor / worker discovery ==========================

def _worker_exists_in_bundle() -> bool:
    """True if we are frozen and a bundled worker exe is present."""
    if not getattr(sys, "frozen", False):
        return False
    base = Path(sys.executable).parent
    candidates = [
        base / ("segmentator_worker.exe" if os.name == "nt" else "segmentator_worker"),
        base / "workers" / "cpu" / ("segmentator_worker.exe" if os.name == "nt" else "segmentator_worker"),
        base / "workers" / "cuda" / ("segmentator_worker.exe" if os.name == "nt" else "segmentator_worker"),
    ]
    return any(p.exists() for p in candidates)

def _ensure_vendor_on_path() -> Path:
    """
    Dev convenience: if a local vendor tree exists, add it to sys.path.
    Packaged app: do NOT require a vendor tree (the worker exe has TS inside).
    Never raises.
    """
    # 1) explicit override
    env_dir = os.environ.get("AMIGO_TOTALSEG_VENDOR_DIR")
    if env_dir:
        p = Path(env_dir)
        if p.is_dir():
            if str(p) not in sys.path:
                sys.path.insert(0, str(p))
            return p

    # 2) packaged app with a bundled worker → nothing to add, just return app dir
    if _worker_exists_in_bundle():
        return Path(sys.executable).parent if getattr(sys, "frozen", False) else Path.cwd()

    # 3) dev mode: try project-local vendor tree (<repo>/third_party/TotalSegmentator)
    try:
        here = Path(__file__).resolve()
        dev_vendor = here.parents[1] / "third_party" / "TotalSegmentator"
        if dev_vendor.is_dir():
            if str(dev_vendor) not in sys.path:
                sys.path.insert(0, str(dev_vendor))
            return dev_vendor
    except Exception:
        pass

    # 4) last resort: do nothing; let an installed 'totalsegmentator' be importable from site-packages
    return Path.cwd()


# ============================== UI helpers ===================================

def _show_warn(title: str, text: str, details: str | None = None, parent=None):
    """Show a warning on the GUI thread; otherwise just log to console."""
    if QMessageBox is None or QApplication is None:
        print(f"[WARN] {title}: {text}")
        if details:
            print(details)
        return

    try:
        app = QApplication.instance()
        on_gui = bool(app and QThread and (app.thread() == QThread.currentThread()))
    except Exception:
        on_gui = False

    if not on_gui:
        print(f"[WARN] {title}: {text}")
        if details:
            print(details)
        return

    box = QMessageBox(QMessageBox.Warning, title, text, parent=parent)
    if details:
        box.setDetailedText(details)
    box.exec_()


def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p

def _appdata_root() -> Path:
    base = os.getenv("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
    return _ensure_dir(Path(base) / "AMIGOpy")

def _work_paths() -> Dict[str, Path]:
    """
    Returns:
      root:   %LOCALAPPDATA%\AMIGOpy
      tmp:    %LOCALAPPDATA%\AMIGOpy\tmp
      models: %LOCALAPPDATA%\AMIGOpy\Models\TotalSegmentator  (unless TOTALSEG_HOME already set)
      logs:   %LOCALAPPDATA%\AMIGOpy\logs
    """
    root = _appdata_root()
    tmp  = _ensure_dir(root / "tmp")
    logs = _ensure_dir(root / "logs")

    env_home = os.getenv("TOTALSEG_HOME")
    models = _ensure_dir(Path(env_home)) if env_home else _ensure_dir(root / "Models" / "TotalSegmentator")

    return {"root": root, "tmp": tmp, "models": models, "logs": logs}


def _clean_tmp_dir(tmp: Path, keep_recent_minutes: int = 60, keep_last: int = 2) -> None:
    """
    Delete older items in the tmp folder, keeping the N most recent entries
    and anything modified in the last `keep_recent_minutes` minutes.
    Logs live under `logs/`, so they are unaffected.

    This is conservative: it keeps the two newest entries regardless of age,
    then removes older stuff (files or dirs) older than the cutoff.
    """
    try:
        if not tmp.exists():
            return

        entries = [p for p in tmp.iterdir() if p.exists()]
        # newest first
        entries.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        now = time.time()
        cutoff = now - (keep_recent_minutes * 60)

        kept = 0
        for p in entries:
            try:
                mtime = p.stat().st_mtime
                if kept < keep_last or mtime >= cutoff:
                    kept += 1
                    continue
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    try:
                        p.unlink()
                    except FileNotFoundError:
                        pass
            except Exception as ex:
                # best-effort; skip if locked/in-use
                print(f"[TS][tmp-clean] skip {p}: {ex}")
    except Exception as ex:
        print(f"[TS][tmp-clean] failed: {ex}")

# ========================= TS kwargs / env helpers ===========================

def _normalize_task(task: str) -> str:
    t = (task or "total").strip()
    return {"total_ct": "total"}.get(t, t)

def _targets_from_params(params: Dict[str, Any]) -> List[str]:
    trg = params.get("targets")
    if not trg:
        trg = params.get("ct_targets") or params.get("mr_targets")
    if not trg:
        return []
    if isinstance(trg, str):
        parts = [x.strip() for x in trg.split(",")]
    else:
        parts = list(trg)
    return [x for x in parts if x]

def _device_from_params(params: Dict[str, Any]) -> str:
    dev = (params.get("device") or "cpu").strip().lower()
    gpu_available = False
    gpu_name = ""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_available = True
            gpu_name = torch.cuda.get_device_name(0)
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            gpu_available = True
            gpu_name = "Apple Silicon MPS"
    except ImportError:
        pass

    if gpu_available:
        print(f"[TS] GPU Detected: {gpu_name or 'yes'}. Requested device: {dev}")
    else:
        print(f"[TS] GPU NOT Detected. Defaulting to CPU mode. Requested device: {dev}")

    if dev in ("gpu0", "gpu:0"):
        return "gpu:0"
    if dev not in ("cpu", "gpu", "mps") and not dev.startswith("gpu:"):
        return "cpu"
    return dev

def _write_json(p: Path, obj: Any):
    try:
        p.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    except Exception:
        pass

def _build_ts_kwargs(input_nii: Path, out_dir: Path, params: Dict[str, Any]) -> Dict[str, Any]:
    task    = _normalize_task(params.get("task", "total"))
    targets = _targets_from_params(params)
    fast    = bool(params.get("fast", False))
    fastest = bool(params.get("fastest", False))
    device  = _device_from_params(params)
    return dict(
        input=str(input_nii),
        output=str(out_dir),
        ml=False,                        # per-organ files
        task=task,
        fast=fast,
        fastest=fastest,
        roi_subset=targets if targets else None,
        output_type="nifti",             # we import masks ourselves
        device=device,
        quiet=True,
        verbose=False,
        no_derived_masks=False,
        skip_saving=False,
    )





# If these helpers already exist in your file, you can keep your originals and
# delete these guarded versions. The guards avoid duplicate definitions.
if '_ensure_series_containers' not in globals():
    def _ensure_series_containers(owner, patient_id: str, study_id: str, modality: str, series_index: int) -> Dict[str, Any]:
        dicom = getattr(owner, "medical_image", None)
        if dicom is None:
            dicom = {}
            setattr(owner, "medical_image", dicom)
        dicom.setdefault(patient_id, {}) \
             .setdefault(study_id, {}) \
             .setdefault(modality, [])
        lst = dicom[patient_id][study_id][modality]
        while len(lst) <= int(series_index):
            lst.append({})
        series = lst[int(series_index)]
        if not isinstance(series, dict):
            series = lst[int(series_index)] = {}

        series.setdefault("structures", {})
        series.setdefault("structures_keys", [])
        series.setdefault("structures_names", [])

        sk = series["structures_keys"]
        sn = series["structures_names"]
        if len(sn) < len(sk):
            sn.extend([""] * (len(sk) - len(sn)))
        elif len(sk) < len(sn):
            del sn[len(sk):]

        return series

if '_is_nii_path' not in globals():
    def _is_nii_path(p: Path) -> bool:
        """True for *.nii or *.nii.gz (robust)."""
        if p.suffix.lower() == ".nii":
            return True
        sfx = "".join(s.lower() for s in p.suffixes[-2:])
        return sfx == ".nii.gz"

def _import_masks_into_series(owner, out_dir: Path,
                              patient_id: str, study_id: str,
                              modality: str, series_index: int,
                              targets: Optional[List[str]] = None) -> int:
    """
    Import per-organ NIfTI masks from TotalSegmentator. If only a single
    multi-label file exists, split it into binary masks per label.
    Returns number of structures imported.
    """
    if not out_dir.is_dir():
        return 0

    series = _ensure_series_containers(owner, patient_id, study_id, modality, series_index)
    structures = series["structures"]
    keys_list: List[str] = series["structures_keys"]
    names_list: List[str] = series["structures_names"]

    start_idx = len(keys_list)

    files = sorted(p for p in out_dir.rglob("*") if _is_nii_path(p))

    # If targets were specified, restrict import to only the requested targets
    allowed_set = set()
    if targets:
        allowed_set = {str(t).strip().lower() for t in targets if str(t).strip()}

    # Debug: record what we saw
    if os.environ.get("AMIGO_DEBUG"):
        try:
            (out_dir / "_ts_import_seen.json").write_text(
                json.dumps({"files": [str(f) for f in files]}, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass

    palette = [
        "#E6194B", "#3CB44B", "#FFE119", "#4363D8", "#F58231",
        "#911EB4", "#46F0F0", "#F032E6", "#BCF60C", "#FABEBE",
        "#008080", "#E6BEFF", "#9A6324", "#FFFAC8", "#800000",
        "#AAFFC3", "#808000", "#FFD8B1", "#000075", "#808080"
    ]

    imported = 0

    # Path A: many per-organ files (typical TS 'nifti' output)
    for f in files:
        name = f.stem
        if name.endswith(".nii"):
            name = name[:-4]

        # If user specified targets, filter out non-matching files
        if allowed_set and name.lower() not in allowed_set:
            continue

        try:
            img = sitk.ReadImage(str(f))
            arr = sitk.GetArrayFromImage(img)  # (z, y, x)
            # Adjust orientation to match AMIGOpy display
            arr = np.flip(arr, axis=1)
            if not np.any(arr):
                continue
            mask = (arr > 0).astype(np.uint8)

            if name in names_list:
                s_key = keys_list[names_list.index(name)]
            else:
                existing_nums = []
                for k in keys_list:
                    if k.startswith("Structure_"):
                        suffix = k.split("_")[-1]
                        if suffix.isdigit():
                            existing_nums.append(int(suffix))
                next_num = (max(existing_nums) if existing_nums else len(keys_list)) + 1
                s_key = f"Structure_{next_num:03d}"
                keys_list.append(s_key)
                names_list.append(name)

            structures[s_key] = {
                "Mask3D": mask,
                "Name": name,
                "Modified": 0,
                "Contours2D": {'axial': {}, 'sagittal': {}, 'coronal': {}},
                "VTKActors2D": {},
            }
            imported += 1
        except Exception as e:
            print(f"[TS][import] Failed to import {f}: {e}")

    # Path B: fallback for a single multi-label file (e.g., segmentations.nii.gz)
    if imported == 0 and len(files) == 1:
        try:
            f = files[0]
            img = sitk.ReadImage(str(f))
            arr = sitk.GetArrayFromImage(img)
            arr = np.flip(arr, axis=1)
            labels = [int(v) for v in np.unique(arr) if int(v) > 0]
            for lv in labels:
                name = f"Label_{lv}"
                if allowed_set and name.lower() not in allowed_set:
                    continue
                m = (arr == lv).astype(np.uint8)
                if name in names_list:
                    s_key = keys_list[names_list.index(name)]
                else:
                    existing_nums = []
                    for k in keys_list:
                        if k.startswith("Structure_"):
                            suffix = k.split("_")[-1]
                            if suffix.isdigit():
                                existing_nums.append(int(suffix))
                    next_num = (max(existing_nums) if existing_nums else len(keys_list)) + 1
                    s_key = f"Structure_{next_num:03d}"
                    keys_list.append(s_key)
                    names_list.append(name)

                structures[s_key] = {
                    "Mask3D": m,
                    "Name": name,
                    "Modified": 0,
                    "Contours2D": {'axial': {}, 'sagittal': {}, 'coronal': {}},
                    "VTKActors2D": {},
                }
                imported += 1
        except Exception as e:
            print(f"[TS][import] Failed to split multi-label: {e}")

    # Ensure parallel appearance lists on series are aligned with structures_keys
    n_keys = len(keys_list)
    view_arr = series.setdefault('structures_view', [])
    color_arr = series.setdefault('structures_color', [])
    lw_arr = series.setdefault('structures_line_width', [])
    tr_arr = series.setdefault('structures_transparency', [])
    mtr_arr = series.setdefault('structures_mask_transparency', [])

    while len(view_arr) < n_keys:
        view_arr.append(0)
    while len(color_arr) < n_keys:
        idx = len(color_arr)
        s_name = names_list[idx] if idx < len(names_list) else ""
        if s_name.lower() in ("bone", "all_bone", "all bone"):
            color_arr.append("#E8E2D0")  # Bone/ivory color
        elif s_name.lower() in ("cortical_bone", "cortical bone", "cortical"):
            color_arr.append("#FFF8DC")  # Cornsilk / bright ivory cortical bone
        elif s_name.lower() in ("bone_marrow", "bone marrow", "marrow"):
            color_arr.append("#D35400")  # Marrow red / deep amber / hematoma red
        elif s_name.lower() in ("lungs", "lungs_merged", "lungs (merged)"):
            color_arr.append("#00E5FF")  # Bright cyan / lung
        elif s_name.lower() in ("lung_left", "lung left"):
            color_arr.append("#4FC3F7")  # Light blue
        elif s_name.lower() in ("lung_right", "lung right"):
            color_arr.append("#0288D1")  # Medium blue
        else:
            color_arr.append(palette[len(color_arr) % len(palette)])
    while len(lw_arr) < n_keys:
        lw_arr.append(3.0)
    while len(tr_arr) < n_keys:
        tr_arr.append(0.1)
    while len(mtr_arr) < n_keys:
        mtr_arr.append(0.5)

    # Clean empty subfolders (best effort)
    try:
        for root, _, _ in os.walk(out_dir, topdown=False):
            if not os.listdir(root):
                os.rmdir(root)
    except Exception:
        pass

    # Debug: write import count
    if os.environ.get("AMIGO_DEBUG"):
        try:
            (out_dir / "_ts_import_result.txt").write_text(f"imported={imported}\n", encoding="utf-8")
        except Exception:
            pass

    return imported


# ------------------------------- Bone Subroutine Targets & Merging ----------

ALL_BONE_TARGETS_CT = [
    "skull",
    "sacrum",
    "vertebrae_C1","vertebrae_C2","vertebrae_C3","vertebrae_C4","vertebrae_C5","vertebrae_C6","vertebrae_C7",
    "vertebrae_T1","vertebrae_T2","vertebrae_T3","vertebrae_T4","vertebrae_T5","vertebrae_T6","vertebrae_T7","vertebrae_T8","vertebrae_T9","vertebrae_T10","vertebrae_T11","vertebrae_T12",
    "vertebrae_L1","vertebrae_L2","vertebrae_L3","vertebrae_L4","vertebrae_L5","vertebrae_S1",
    "rib_left_1","rib_left_2","rib_left_3","rib_left_4","rib_left_5","rib_left_6",
    "rib_left_7","rib_left_8","rib_left_9","rib_left_10","rib_left_11","rib_left_12",
    "rib_right_1","rib_right_2","rib_right_3","rib_right_4","rib_right_5","rib_right_6",
    "rib_right_7","rib_right_8","rib_right_9","rib_right_10","rib_right_11","rib_right_12",
    "sternum",
    "costal_cartilages",
    "clavicula_left","clavicula_right",
    "scapula_left","scapula_right",
    "humerus_left","humerus_right",
    "hip_left","hip_right",
    "femur_left","femur_right",
]

ALL_BONE_TARGETS_MR = [
    "sacrum",
    "vertebrae",
    "intervertebral_discs",
    "clavicula_left","clavicula_right",
    "scapula_left","scapula_right",
    "humerus_left","humerus_right",
    "hip_left","hip_right",
    "femur_left","femur_right",
]


def _handle_all_bone_merge(
    out_dir: Path,
    input_nii: Optional[Path] = None,
    is_mr: bool = False,
    manual_targets: Optional[List[str]] = None,
    separate_cortical: bool = False,
    cortical_hu: int = 300,
    requested_types: Optional[List[str]] = None,
) -> None:
    """
    Merge all bone NIfTI masks found in out_dir into a single 'bone.nii.gz' and/or
    separate dense cortical bone ('cortical_bone.nii.gz') from inner bone marrow ('bone_marrow.nii.gz').
    If an individual bone component was not manually selected by the user, delete its file from out_dir.
    """
    import SimpleITK as sitk
    import numpy as np

    bone_list = ALL_BONE_TARGETS_MR if is_mr else ALL_BONE_TARGETS_CT
    bone_set = {b.lower() for b in bone_list}
    manual_set = {str(t).strip().lower() for t in (manual_targets or []) if str(t).strip()}

    # Find all bone files present in out_dir
    found_bone_files = []
    for f in sorted(out_dir.rglob("*")):
        if not _is_nii_path(f):
            continue
        stem = f.stem
        if stem.endswith(".nii"):
            stem = stem[:-4]
        if stem.lower() in bone_set:
            found_bone_files.append((stem.lower(), f))

    if not found_bone_files:
        return

    # Load and merge all found bone masks into a single array
    ref_img = None
    merged_arr = None

    for stem, f in found_bone_files:
        try:
            img = sitk.ReadImage(str(f))
            arr = sitk.GetArrayFromImage(img)
            if ref_img is None:
                ref_img = img
                merged_arr = np.zeros(arr.shape, dtype=np.uint8)
            merged_arr[arr > 0] = 1
        except Exception as e:
            print(f"[TS][all_bone] Error reading {f}: {e}")

    if ref_img is None or merged_arr is None:
        return

    req_set = {str(t).lower() for t in (requested_types or ["all_bone"])}
    save_whole_bone = ("all_bone" in req_set or "bone" in req_set or not separate_cortical)

    # 1. Optionally write the merged whole bone mask
    if save_whole_bone:
        try:
            merged_img = sitk.GetImageFromArray(merged_arr)
            merged_img.CopyInformation(ref_img)
            out_bone_path = out_dir / "bone.nii.gz"
            sitk.WriteImage(merged_img, str(out_bone_path))
            print(f"[TS][all_bone] Successfully created merged bone mask at {out_bone_path}")
        except Exception as e:
            print(f"[TS][all_bone] Error writing merged bone mask: {e}")

    # 2. Cortical bone & bone marrow separation via thresholding
    do_separate = separate_cortical or ("cortical_bone" in req_set) or ("bone_marrow" in req_set)
    if do_separate:
        if input_nii is not None and Path(input_nii).exists():
            try:
                scan_img = sitk.ReadImage(str(input_nii))
                # Ensure identical geometry to reference segmentation
                if (scan_img.GetSize() != ref_img.GetSize() or
                    scan_img.GetSpacing() != ref_img.GetSpacing() or
                    scan_img.GetDirection() != ref_img.GetDirection() or
                    scan_img.GetOrigin() != ref_img.GetOrigin()):
                    resample = sitk.ResampleImageFilter()
                    resample.SetReferenceImage(ref_img)
                    resample.SetInterpolator(sitk.sitkLinear)
                    resample.SetDefaultPixelValue(-1000.0 if not is_mr else 0.0)
                    scan_img = resample.Execute(scan_img)

                scan_arr = sitk.GetArrayFromImage(scan_img)
                scan_arr = np.nan_to_num(scan_arr, nan=-1000.0 if not is_mr else 0.0)

                if not is_mr:
                    # CT attenuation thresholding:
                    # Cortical bone: dense outer compact bone >= cortical_hu (default 300 HU)
                    cortical_mask = ((merged_arr > 0) & (scan_arr >= cortical_hu)).astype(np.uint8)
                    # Inner bone / marrow: voxels inside bone envelope below cortical_hu, excluding air (< -200 HU)
                    marrow_mask = ((merged_arr > 0) & (scan_arr < cortical_hu) & (scan_arr >= -200)).astype(np.uint8)
                else:
                    # MR signal intensity: cortical bone is hypointense, marrow is hyperintense
                    bone_voxels = scan_arr[merged_arr > 0]
                    if len(bone_voxels) > 0:
                        thresh = np.percentile(bone_voxels, 35)
                        cortical_mask = ((merged_arr > 0) & (scan_arr <= thresh)).astype(np.uint8)
                        marrow_mask = ((merged_arr > 0) & (scan_arr > thresh)).astype(np.uint8)
                    else:
                        cortical_mask = np.zeros_like(merged_arr)
                        marrow_mask = np.zeros_like(merged_arr)

                # Save cortical_bone if requested
                if ("cortical_bone" in req_set) or separate_cortical:
                    cort_img = sitk.GetImageFromArray(cortical_mask)
                    cort_img.CopyInformation(ref_img)
                    cort_path = out_dir / "cortical_bone.nii.gz"
                    sitk.WriteImage(cort_img, str(cort_path))
                    print(f"[TS][all_bone] Created cortical bone mask at {cort_path} ({int(np.sum(cortical_mask))} voxels)")

                # Save bone_marrow if requested
                if ("bone_marrow" in req_set) or (separate_cortical and "all_bone" in req_set):
                    marrow_img = sitk.GetImageFromArray(marrow_mask)
                    marrow_img.CopyInformation(ref_img)
                    marrow_path = out_dir / "bone_marrow.nii.gz"
                    sitk.WriteImage(marrow_img, str(marrow_path))
                    print(f"[TS][all_bone] Created bone marrow mask at {marrow_path} ({int(np.sum(marrow_mask))} voxels)")

            except Exception as e:
                print(f"[TS][all_bone] Error separating cortical bone and marrow: {e}")
        else:
            print(f"[TS][all_bone] Warning: input_nii not found at {input_nii}, cannot separate cortical bone")

    # 3. Delete individual bone parts that were NOT manually selected by the user
    for stem, f in found_bone_files:
        if stem not in manual_set:
            try:
                f.unlink()
                print(f"[TS][all_bone] Deleted unselected component: {stem}")
            except Exception as e:
                print(f"[TS][all_bone] Error deleting {f}: {e}")
        else:
            print(f"[TS][all_bone] Retaining manually selected component: {stem}")


# ------------------------------- Lung Subroutine Targets & Merging ----------

ALL_LUNG_TARGETS_CT_LEFT = [
    "lung_upper_lobe_left",
    "lung_lower_lobe_left",
]

ALL_LUNG_TARGETS_CT_RIGHT = [
    "lung_upper_lobe_right",
    "lung_middle_lobe_right",
    "lung_lower_lobe_right",
]

ALL_LUNG_TARGETS_CT = ALL_LUNG_TARGETS_CT_LEFT + ALL_LUNG_TARGETS_CT_RIGHT

ALL_LUNG_TARGETS_MR_LEFT = ["lung_left"]
ALL_LUNG_TARGETS_MR_RIGHT = ["lung_right"]
ALL_LUNG_TARGETS_MR = ALL_LUNG_TARGETS_MR_LEFT + ALL_LUNG_TARGETS_MR_RIGHT


def _handle_lung_merge(
    out_dir: Path,
    is_mr: bool = False,
    manual_targets: Optional[List[str]] = None,
    requested_types: Optional[List[str]] = None,
) -> None:
    """
    Merge lung lobe NIfTI masks found in out_dir:
      - 'lungs_merged': creates single mask for all lung structures -> 'lungs.nii.gz'
      - 'lungs_merged_side': creates two masks -> 'lung_left.nii.gz' and 'lung_right.nii.gz'
    If an individual lung lobe was not manually selected by the user, delete its file from out_dir.
    """
    import SimpleITK as sitk
    import numpy as np

    left_list = ALL_LUNG_TARGETS_MR_LEFT if is_mr else ALL_LUNG_TARGETS_CT_LEFT
    right_list = ALL_LUNG_TARGETS_MR_RIGHT if is_mr else ALL_LUNG_TARGETS_CT_RIGHT
    left_set = {t.lower() for t in left_list}
    right_set = {t.lower() for t in right_list}
    manual_set = {str(t).strip().lower() for t in (manual_targets or []) if str(t).strip()}

    req_set = {str(t).lower() for t in (requested_types or [])}
    do_merged = ("lungs_merged" in req_set or "lungs" in req_set)
    do_side = ("lungs_merged_side" in req_set or "lungs_side" in req_set)

    # Find all lung lobe files present in out_dir
    found_left = []
    found_right = []
    for f in sorted(out_dir.rglob("*")):
        if not _is_nii_path(f):
            continue
        stem = f.stem
        if stem.endswith(".nii"):
            stem = stem[:-4]
        stem_l = stem.lower()
        if stem_l in left_set:
            found_left.append((stem_l, f))
        elif stem_l in right_set:
            found_right.append((stem_l, f))

    if not found_left and not found_right:
        return

    ref_img = None
    left_arr = None
    right_arr = None

    # Load and combine left lung lobes
    for stem, f in found_left:
        try:
            img = sitk.ReadImage(str(f))
            arr = sitk.GetArrayFromImage(img)
            if ref_img is None:
                ref_img = img
            if left_arr is None:
                left_arr = np.zeros(arr.shape, dtype=np.uint8)
            left_arr[arr > 0] = 1
        except Exception as e:
            print(f"[TS][lung_merge] Error reading {f}: {e}")

    # Load and combine right lung lobes
    for stem, f in found_right:
        try:
            img = sitk.ReadImage(str(f))
            arr = sitk.GetArrayFromImage(img)
            if ref_img is None:
                ref_img = img
            if right_arr is None:
                right_arr = np.zeros(arr.shape, dtype=np.uint8)
            right_arr[arr > 0] = 1
        except Exception as e:
            print(f"[TS][lung_merge] Error reading {f}: {e}")

    if ref_img is None:
        return

    ref_shape = sitk.GetArrayFromImage(ref_img).shape
    if left_arr is None:
        left_arr = np.zeros(ref_shape, dtype=np.uint8)
    if right_arr is None:
        right_arr = np.zeros(ref_shape, dtype=np.uint8)

    # 1. 'Lungs (merged)' -> single mask for all lung structures: lungs.nii.gz
    if do_merged:
        try:
            merged_arr = np.zeros(ref_shape, dtype=np.uint8)
            merged_arr[(left_arr > 0) | (right_arr > 0)] = 1
            merged_img = sitk.GetImageFromArray(merged_arr)
            merged_img.CopyInformation(ref_img)
            out_path = out_dir / "lungs.nii.gz"
            sitk.WriteImage(merged_img, str(out_path))
            print(f"[TS][lung_merge] Successfully created merged lungs mask at {out_path} ({int(np.sum(merged_arr))} voxels)")
        except Exception as e:
            print(f"[TS][lung_merge] Error writing merged lungs mask: {e}")

    # 2. 'Lungs (merged/side)' -> two masks: lung_left.nii.gz and lung_right.nii.gz
    if do_side:
        try:
            left_img = sitk.GetImageFromArray(left_arr)
            left_img.CopyInformation(ref_img)
            left_path = out_dir / "lung_left.nii.gz"
            sitk.WriteImage(left_img, str(left_path))
            print(f"[TS][lung_merge] Successfully created lung_left mask at {left_path} ({int(np.sum(left_arr))} voxels)")

            right_img = sitk.GetImageFromArray(right_arr)
            right_img.CopyInformation(ref_img)
            right_path = out_dir / "lung_right.nii.gz"
            sitk.WriteImage(right_img, str(right_path))
            print(f"[TS][lung_merge] Successfully created lung_right mask at {right_path} ({int(np.sum(right_arr))} voxels)")
        except Exception as e:
            print(f"[TS][lung_merge] Error writing side lung masks: {e}")

    # 3. Delete individual lobe parts that were NOT manually selected by the user
    all_found = found_left + found_right
    for stem, f in all_found:
        if stem in ("lung_left", "lung_right") and do_side:
            continue
        if stem not in manual_set:
            try:
                if f.name not in ("lungs.nii.gz",):
                    f.unlink()
                    print(f"[TS][lung_merge] Deleted unselected lobe component: {stem}")
            except Exception as e:
                print(f"[TS][lung_merge] Error deleting {f}: {e}")
        else:
            print(f"[TS][lung_merge] Retaining manually selected lobe component: {stem}")


# =========================== subprocess runner ===============================

def _run_ts_subprocess(owner, kwargs, log_dir: Path, env_extra: Dict[str, str]):
    """
    Launch TotalSegmentator as a child process.
    - Dev: run a tiny runner via python/pythonw with a __main__ guard.
    - Frozen app: prefer segmentator_worker(.exe) next to sys.executable.
    - Windows: no popups; new process group; tree-kill with taskkill as last resort.
    - POSIX: new session (setsid); kill the group.
    """
    import subprocess

    # ---- environment for the child
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)

    # ---- paths
    args_json   = log_dir / "_ts_args.json"
    runner_py   = log_dir / "_ts_run.py"   # dev-mode runner (not used when frozen-worker exists)
    stdout_path = log_dir / "_ts_stdout.txt"
    stderr_path = log_dir / "_ts_stderr.txt"

    _write_json(args_json, kwargs)

    # ---- create a Windows-safe runner for dev mode (multiprocessing-friendly)
    runner_py.write_text(
        "import json, sys, os, sysconfig, importlib.util, multiprocessing\n"
        "if os.name == 'nt':\n"
        "    multiprocessing.freeze_support()\n"
        "stdlib_dir = sysconfig.get_paths().get('stdlib') or ''\n"
        "stats_path = os.path.join(stdlib_dir, 'statistics.py')\n"
        "if os.path.isfile(stats_path):\n"
        "    spec = importlib.util.spec_from_file_location('statistics', stats_path)\n"
        "    mod = importlib.util.module_from_spec(spec)\n"
        "    spec.loader.exec_module(mod)\n"
        "    sys.modules['statistics'] = mod\n"
        "else:\n"
        "    import statistics as mod\n"
        "    sys.modules['statistics'] = mod\n"
        "from totalsegmentator import python_api as ts\n"
        "def _main():\n"
        "    with open(sys.argv[1], 'r', encoding='utf-8') as f:\n"
        "        k = json.load(f)\n"
        "    ts.totalsegmentator(**k)\n"
        "if __name__ == '__main__':\n"
        "    _main()\n",
        encoding="utf-8"
    )

    # ---- choose child command
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
        worker_candidates = [
            base / ("segmentator_worker.exe" if os.name == "nt" else "segmentator_worker"),
            base / "workers" / "cpu" / ("segmentator_worker.exe" if os.name == "nt" else "segmentator_worker"),
            base / "workers" / "cuda" / ("segmentator_worker.exe" if os.name == "nt" else "segmentator_worker"),
        ]
        found_worker = next((p for p in worker_candidates if p.exists()), None)
        if found_worker:
            cmd = [str(found_worker), str(args_json)]
        else:
            raise RuntimeError(
                "Autocontouring worker (segmentator_worker.exe) was not found in the application directory. "
                "Please install the 'with TotalSegmentator' edition of AMIGOpy."
            )
    else:
        py = sys.executable
        if os.name == "nt":
            pyw = py.replace("python.exe", "pythonw.exe")
            if os.path.exists(pyw):
                py = pyw
        cmd = [py, str(runner_py), str(args_json)]

    # ---- launch flags (hide windows; isolate process group/session)
    creationflags = 0
    startupinfo = None
    preexec_fn = None
    if os.name == "nt":
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        CREATE_NO_WINDOW         = 0x08000000
        creationflags = CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
    else:
        import os as _os
        preexec_fn = _os.setsid  # new session for the child

    def _cancelled() -> bool:
        segwin = getattr(owner, "segwin", owner)
        return bool(getattr(segwin, "_seg_cancel", False))

    # ---- run
    with open(stdout_path, "w", encoding="utf-8") as so, open(stderr_path, "w", encoding="utf-8") as se:
        proc = subprocess.Popen(
            cmd,
            stdout=so, stderr=se, env=env,
            creationflags=creationflags,
            startupinfo=startupinfo,
            preexec_fn=preexec_fn,
            close_fds=True
        )

        try:
            while True:
                rc = proc.poll()
                if rc is not None:
                    break

                if _cancelled():
                    # 1) graceful terminate
                    try:
                        proc.terminate()
                    except Exception:
                        pass

                    # 2) brief wait
                    for _ in range(30):
                        if proc.poll() is not None:
                            break
                        time.sleep(0.1)

                    # 3) hard kill if still alive
                    if proc.poll() is None:
                        try:
                            proc.kill()
                        except Exception:
                            pass

                    # 4) Windows last resort: kill the whole tree (hidden)
                    if os.name == "nt" and proc.poll() is None:
                        try:
                            CREATE_NO_WINDOW = 0x08000000
                            si = subprocess.STARTUPINFO()
                            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                            si.wShowWindow = 0
                            subprocess.run(
                                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                check=False,
                                creationflags=CREATE_NO_WINDOW,
                                startupinfo=si
                            )
                        except Exception:
                            pass

                    return False, "Stopped by user"

                time.sleep(0.3)
        finally:
            pass

    if proc.returncode == 0:
        return True, "ok"

    # include last lines of stderr for diagnosis
    try:
        tail = "\n".join((stderr_path.read_text(encoding="utf-8", errors="ignore").splitlines())[-60:])
        return False, "TotalSegmentator failed:\n" + tail
    except Exception:
        return False, "TotalSegmentator failed (no stderr available)."


# ============================= top-level call ================================

def _run_totalseg(owner, input_nii: Path, out_dir: Path, params: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Returns (ok, message). On success, out_dir will contain per-organ NIfTI masks.
    Runs in a subprocess so it can be stopped mid-run.
    """
    _ensure_vendor_on_path()  # harmless if not present; worker exe has TS when frozen
    ap = _work_paths()

    env_extra: Dict[str, str] = {}
    if "TOTALSEG_HOME" not in os.environ:
        env_extra["TOTALSEG_HOME"] = str(ap["models"])

    # Tame thread counts on CPU-only systems
    if _device_from_params(params) == "cpu":
        env_extra.update({
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
            "ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS": "1",
            "TOTALSEG_NUM_WORKERS": "0",
            "NNUNET_NUM_THREADS_PREPROCESSING": "1",
            "NNUNET_NUM_THREADS_NIFTI": "1",
        })

    kwargs = _build_ts_kwargs(input_nii, out_dir, params)
    _write_json(out_dir / "_ts_call.json",
                {"kwargs": kwargs,
                 "env": {"TOTALSEG_HOME": env_extra.get("TOTALSEG_HOME",
                                                       os.getenv("TOTALSEG_HOME"))}})
    ok, msg = _run_ts_subprocess(owner, kwargs, out_dir, env_extra)
    return ok, msg


# ============================ public entry point =============================

def run_totalseg_for_series(owner, series_list: List[Dict[str, Any]], params: Dict[str, Any]) -> None:
    """
    Replaces the HTTP client call. Usage:
      run_totalseg_for_series(self, series_list, params)

    Each item of series_list:
      { "patient": <pid>, "study": <sid>, "modality": <mod>, "index": <series_index> }

    params example for CT total subset:
      { "task": "total", "fast": True, "targets": ["liver", "spleen"], "device": "cpu" }
    """
    ap = _work_paths()
    tmp  = ap["tmp"]

    _clean_tmp_dir(tmp, keep_recent_minutes=5, keep_last=2)

    for meta in series_list or []:
        # Respect cancel before starting a new series
        if getattr(getattr(owner, "segwin", owner), "_seg_cancel", False):
            break

        pid = meta["patient"]; sid = meta["study"]; mod = meta["modality"]; idx = int(meta["index"])
        tag = f"{pid}/{sid}/{mod}[{idx}]"
        try:
            # 1) export NIfTI
            req_dir   = _ensure_dir(tmp / f"ts_req_{int(time.time()*1000)}")
            input_nii = Path(str(req_dir / "input.nii.gz"))
            out_dir   = _ensure_dir(req_dir / "out")

            nii_path = export_nifti(
                owner, pid, sid, mod, idx,
                output_folder=str(req_dir),
                file_name="input.nii.gz"
            )
            if not nii_path or not Path(nii_path).exists():
                _show_warn("TotalSegmentator", f"Failed to export NIfTI for {tag}",
                           parent=getattr(owner, "segwin", None) or owner)
                continue

            # Respect cancel right before starting TS
            if getattr(getattr(owner, "segwin", owner), "_seg_cancel", False):
                break

            # 2) determine sub-jobs for this run (CT, MR, and/or subroutines)
            jobs = []
            ct_targets = (params or {}).get("ct_targets") or []
            mr_targets = (params or {}).get("mr_targets") or []
            subroutines = (params or {}).get("subroutines") or []
            direct_targets = (params or {}).get("targets") or []
            direct_task = (params or {}).get("task")

            if ct_targets:
                jobs.append({"task": "total", "targets": list(ct_targets)})
            if mr_targets:
                jobs.append({"task": "total_mr", "targets": list(mr_targets)})
            for sub in subroutines:
                jobs.append({"task": sub, "targets": None})

            if not jobs:
                jobs.append({
                    "task": direct_task or "total",
                    "targets": direct_targets if direct_targets else None
                })

            total_imported = 0
            for job in jobs:
                if getattr(getattr(owner, "segwin", owner), "_seg_cancel", False):
                    break
                job_params = dict(params or {})
                job_params["task"] = job["task"]
                job_params["targets"] = job["targets"]

                # run TS (subprocess, killable)
                ok, msg = _run_totalseg(owner, input_nii, out_dir, job_params)
                if not ok:
                    _show_warn("TotalSegmentator failed", msg,
                               parent=getattr(owner, "segwin", None) or owner)
                    continue

                # If all_bone custom subroutine was requested, merge bone parts and remove unselected components
                if params.get("all_bone") and job["task"] in ("total", "total_mr"):
                    is_mr_series = (str(mod).upper() in ("MR", "MRI")) or (job["task"] == "total_mr")
                    manual_targets = (params.get("manual_mr_targets") if is_mr_series else params.get("manual_ct_targets")) or []
                    _handle_all_bone_merge(
                        out_dir=out_dir,
                        input_nii=input_nii,
                        is_mr=is_mr_series,
                        manual_targets=manual_targets,
                        separate_cortical=params.get("separate_cortical", False),
                        cortical_hu=params.get("cortical_hu", 300),
                        requested_types=params.get("requested_bone_types"),
                    )

                # If lungs custom subroutine was requested, merge lung lobes and remove unselected components
                if (params.get("lungs_merged") or params.get("lungs_merged_side")) and job["task"] in ("total", "total_mr"):
                    is_mr_series = (str(mod).upper() in ("MR", "MRI")) or (job["task"] == "total_mr")
                    manual_targets = (params.get("manual_mr_targets") if is_mr_series else params.get("manual_ct_targets")) or []
                    _handle_lung_merge(
                        out_dir=out_dir,
                        is_mr=is_mr_series,
                        manual_targets=manual_targets,
                        requested_types=params.get("requested_lung_types"),
                    )

                # 3) import output masks (passing targets ensures ONLY requested structures are imported)
                import_targets = list(job["targets"]) if job["targets"] else []
                if params.get("all_bone") and import_targets:
                    req_types = params.get("requested_bone_types") or ["all_bone"]
                    if "all_bone" in req_types or "bone" in req_types or not params.get("separate_cortical"):
                        import_targets.append("bone")
                    if "cortical_bone" in req_types or params.get("separate_cortical"):
                        import_targets.append("cortical_bone")
                    if "bone_marrow" in req_types or (params.get("separate_cortical") and "all_bone" in req_types):
                        import_targets.append("bone_marrow")

                if (params.get("lungs_merged") or params.get("lungs_merged_side")) and import_targets:
                    req_lung_types = params.get("requested_lung_types") or []
                    if "lungs_merged" in req_lung_types:
                        import_targets.append("lungs")
                    if "lungs_merged_side" in req_lung_types:
                        if "lung_left" not in import_targets:
                            import_targets.append("lung_left")
                        if "lung_right" not in import_targets:
                            import_targets.append("lung_right")

                n = _import_masks_into_series(owner, out_dir, pid, sid, mod, idx, targets=import_targets if job["targets"] else None)
                total_imported += n

            print(f"[TS] Imported {total_imported} structures for {tag} from {out_dir}")

        except Exception as ex:
            tb = traceback.format_exc()
            _show_warn("TotalSegmentator error", f"{ex}", tb,
                       parent=getattr(owner, "segwin", None) or owner)


# ===================== folder batch runner (one-by-one) ======================

DEFAULT_COLORS = [
    "#E6194B", "#3CBA54", "#4885ED", "#F4C20D", "#911EB4",
    "#46F0F0", "#F032E6", "#BCF60C", "#FABEBE", "#008080",
    "#E6BEFF", "#9A6324", "#FFFAC8", "#800000", "#AAFFC3",
    "#808000", "#FFD8B1", "#000075", "#808080", "#FF5722",
]


def run_totalseg_for_folder_file(
    owner,
    input_nii: Path,
    base_folder: Path,
    params: Dict[str, Any]
) -> Tuple[bool, str, int]:
    """
    Process a single NIfTI file in Folder Batch mode:
    1. Create 'autocont' (or reuse 'autcont') inside base_folder.
    2. Inside 'autocont', create a subfolder named after the file stem:
       e.g. for 'patient01.nii.gz', create 'base_folder/autocont/patient01/'.
    3. Copy the original file inside that subfolder.
    4. Run TotalSegmentator jobs on the file.
    5. Run bone and lung merging subroutines if requested.
    6. Export all contour masks to the subfolder using standard AMIGO naming:
       <OriginalFile>_ST_<Name>.nii.gz
    7. Write 'structures.json' manifest in the subfolder.
    8. Clean up temporary working directory.
    9. Return (ok, message, count).
    """
    def _is_cancelled():
        segwin = getattr(owner, "segwin", None) or owner
        return bool(getattr(segwin, "_seg_cancel", False))

    if _is_cancelled():
        return False, "Stopped", 0

    if not input_nii.exists():
        return False, f"File does not exist: {input_nii.name}", 0

    # 1. Determine safe stem
    clean_stem = input_nii.name
    for ext in (".nii.gz", ".nii"):
        if clean_stem.lower().endswith(ext):
            clean_stem = clean_stem[:-len(ext)]
            break
    safe_stem = "".join(c for c in clean_stem if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    if not safe_stem:
        safe_stem = "case"

    # 2. Output directories: autocont/<safe_stem>/
    autocont_name = "autocont"
    if (base_folder / "autcont").is_dir():
        autocont_name = "autcont"
    autocont_dir = _ensure_dir(base_folder / autocont_name)
    case_dir = _ensure_dir(autocont_dir / safe_stem)

    # 3. Copy original NIfTI file into case directory
    copied_orig = case_dir / input_nii.name
    try:
        if input_nii.resolve() != copied_orig.resolve():
            shutil.copy2(str(input_nii), str(copied_orig))
    except Exception as e:
        return False, f"Failed to copy original file: {e}", 0

    if _is_cancelled():
        return False, "Stopped", 0

    # 4. Setup temporary working directory for TS outputs
    ap = _work_paths()
    tmp = ap["tmp"]
    ts_tmp = _ensure_dir(tmp / f"ts_batch_{safe_stem}_{int(time.time()*1000)}")
    ts_out = _ensure_dir(ts_tmp / "out")

    try:
        # 5. Determine TS jobs
        jobs = []
        ct_targets = (params or {}).get("ct_targets") or []
        mr_targets = (params or {}).get("mr_targets") or []
        subroutines = (params or {}).get("subroutines") or []
        direct_targets = (params or {}).get("targets") or []
        direct_task = (params or {}).get("task")

        if ct_targets:
            jobs.append({"task": "total", "targets": list(ct_targets)})
        if mr_targets:
            jobs.append({"task": "total_mr", "targets": list(mr_targets)})
        for sub in subroutines:
            jobs.append({"task": sub, "targets": None})

        if not jobs:
            jobs.append({
                "task": direct_task or "total",
                "targets": direct_targets if direct_targets else None
            })

        is_mr = bool(mr_targets) or (direct_task == "total_mr")

        # 6. Run TS for each job
        for job in jobs:
            if _is_cancelled():
                shutil.rmtree(str(ts_tmp), ignore_errors=True)
                return False, "Stopped", 0

            job_params = dict(params or {})
            job_params["task"] = job["task"]
            job_params["targets"] = job["targets"]

            ok, msg = _run_totalseg(owner, copied_orig, ts_out, job_params)
            if not ok:
                shutil.rmtree(str(ts_tmp), ignore_errors=True)
                return False, msg, 0

            # Bone merge subroutine
            if params.get("all_bone") and job["task"] in ("total", "total_mr"):
                manual_targets = (params.get("manual_mr_targets") if is_mr else params.get("manual_ct_targets")) or []
                _handle_all_bone_merge(
                    out_dir=ts_out,
                    input_nii=copied_orig,
                    is_mr=is_mr,
                    manual_targets=manual_targets,
                    separate_cortical=params.get("separate_cortical", False),
                    cortical_hu=params.get("cortical_hu", 300),
                    requested_types=params.get("requested_bone_types"),
                )

            # Lung merge subroutine
            if (params.get("lungs_merged") or params.get("lungs_merged_side")) and job["task"] in ("total", "total_mr"):
                manual_targets = (params.get("manual_mr_targets") if is_mr else params.get("manual_ct_targets")) or []
                _handle_lung_merge(
                    out_dir=ts_out,
                    is_mr=is_mr,
                    manual_targets=manual_targets,
                    requested_types=params.get("requested_lung_types"),
                )

        if _is_cancelled():
            shutil.rmtree(str(ts_tmp), ignore_errors=True)
            return False, "Stopped", 0

        # 7. Collect and export contour masks to case_dir
        manifest_structures = []
        exported_count = 0

        try:
            from fcn_operations.boolean_operations_dialog import DEFAULT_NEW_COLORS
            palette = DEFAULT_NEW_COLORS
        except Exception:
            palette = DEFAULT_COLORS

        out_files = sorted([
            p for p in ts_out.iterdir()
            if p.is_file() and (p.name.endswith(".nii.gz") or p.name.endswith(".nii"))
        ])

        for f in out_files:
            s_name = f.name
            for ext in (".nii.gz", ".nii"):
                if s_name.lower().endswith(ext):
                    s_name = s_name[:-len(ext)]
                    break
            clean_s_name = "".join(c for c in s_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
            dest_filename = f"{safe_stem}_ST_{clean_s_name}.nii.gz"
            dest_path = case_dir / dest_filename

            try:
                shutil.move(str(f), str(dest_path))
            except Exception:
                shutil.copy2(str(f), str(dest_path))

            color_hex = palette[len(manifest_structures) % len(palette)]
            manifest_structures.append({
                "name": clean_s_name,
                "filename": dest_filename,
                "color": color_hex,
            })
            exported_count += 1

        # 8. Write structures.json manifest
        manifest_data = {
            "amigo_version": "1.0",
            "exported_at": datetime.datetime.now().isoformat(),
            "parent_series": {
                "original_file": input_nii.name,
                "case_id": safe_stem,
                "modality": "MR" if is_mr else "CT",
            },
            "structures": manifest_structures,
        }
        manifest_path = case_dir / "structures.json"
        try:
            with open(manifest_path, "w", encoding="utf-8") as fp:
                json.dump(manifest_data, fp, indent=2)
        except Exception as ex:
            print(f"[TS Batch] Warning: could not write structures.json: {ex}")

        # 9. Clean up tmp
        shutil.rmtree(str(ts_tmp), ignore_errors=True)

        return True, f"Done ({exported_count} contours)", exported_count

    except Exception as ex:
        shutil.rmtree(str(ts_tmp), ignore_errors=True)
        return False, str(ex), 0

